"""
Task Scheduler - Centralized background task management.

Consolidates multiple background threads into a single managed scheduler
to reduce overhead and improve resource management.

Author: Pomera AI Commander Team
"""

import threading
import time
import logging
from typing import Dict, Callable, Optional, Any, List
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, Future
from enum import Enum
import heapq
from datetime import datetime


class TaskPriority(Enum):
    """Task priority levels (lower value = higher priority)."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


class TaskState(Enum):
    """Task execution states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(order=True)
class ScheduledTask:
    """
    A scheduled task with timing and priority.
    
    Ordering is by (next_run, priority) for heap queue.
    """
    next_run: float = field(compare=True)
    priority: int = field(compare=True)
    task_id: str = field(compare=False)
    func: Callable = field(compare=False)
    interval_seconds: float = field(compare=False, default=0)
    is_recurring: bool = field(compare=False, default=False)
    args: tuple = field(compare=False, default_factory=tuple)
    kwargs: dict = field(compare=False, default_factory=dict)
    state: TaskState = field(compare=False, default=TaskState.PENDING)
    last_run: Optional[float] = field(compare=False, default=None)
    run_count: int = field(compare=False, default=0)
    error_count: int = field(compare=False, default=0)
    last_error: Optional[str] = field(compare=False, default=None)


@dataclass
class TaskResult:
    """Result of a task execution."""
    task_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class TaskScheduler:
    """
    Centralized task scheduler for background operations.
    
    Consolidates:
    - Periodic cleanup tasks (stats cache, backup manager)
    - Async text processing
    - Backup operations
    - Any other background work
    
    Benefits:
    - Single thread pool instead of multiple daemon threads
    - Proper shutdown handling
    - Task prioritization
    - Better resource utilization
    - Task monitoring and statistics
    
    Usage:
        scheduler = TaskScheduler()
        scheduler.start()
        
        # One-time task
        scheduler.schedule_once('cleanup', cleanup_func, delay_seconds=60)
        
        # Recurring task
        scheduler.schedule_recurring('backup', backup_func, interval_seconds=300)
        
        # Later...
        scheduler.stop()
    """
    
    def __init__(self, 
                 max_workers: int = 4, 
                 logger: Optional[logging.Logger] = None,
                 name: str = "TaskScheduler"):
        """
        Initialize the task scheduler.
        
        Args:
            max_workers: Maximum concurrent worker threads
            logger: Logger instance (creates one if not provided)
            name: Name for the scheduler (used in thread names)
        """
        self.name = name
        self.logger = logger or logging.getLogger(__name__)
        self.max_workers = max_workers
        
        # Thread pool for task execution
        self._executor: Optional[ThreadPoolExecutor] = None
        
        # Scheduled tasks
        self._task_queue: List[ScheduledTask] = []  # heap queue
        self._tasks: Dict[str, ScheduledTask] = {}
        self._task_lock = threading.RLock()
        
        # Scheduler thread
        self._scheduler_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._running = False
        
        # Active futures
        self._active_futures: Dict[str, Future] = {}
        
        # Task results history
        self._results_history: List[TaskResult] = []
        self._max_results_history = 100
        
        # Statistics
        self._stats = {
            'tasks_executed': 0,
            'tasks_failed': 0,
            'tasks_cancelled': 0,
            'total_execution_time': 0.0,
            'started_at': None,
            'stopped_at': None
        }
        
        # Callbacks
        self._on_task_complete: Optional[Callable[[TaskResult], None]] = None
        self._on_task_error: Optional[Callable[[str, Exception], None]] = None
    
    def start(self) -> None:
        """Start the scheduler."""
        if self._running:
            self.logger.warning(f"{self.name} is already running")
            return
        
        self._stop_event.clear()
        self._running = True
        self._stats['started_at'] = datetime.now()
        self._stats['stopped_at'] = None
        
        # Create thread pool
        self._executor = ThreadPoolExecutor(
            max_workers=self.max_workers,
            thread_name_prefix=f"{self.name}-Worker"
        )
        
        # Start scheduler thread
        self._scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            daemon=True,
            name=f"{self.name}-Main"
        )
        self._scheduler_thread.start()
        
        self.logger.info(f"{self.name} started with {self.max_workers} workers")
    
    def stop(self, wait: bool = True, timeout: float = 10.0) -> None:
        """
        Stop the scheduler.
        
        Args:
            wait: Whether to wait for running tasks to complete
            timeout: Maximum time to wait for shutdown
        """
        if not self._running:
            return
        
        self.logger.info(f"Stopping {self.name}...")
        self._stop_event.set()
        self._running = False
        self._stats['stopped_at'] = datetime.now()
        
        # Wait for scheduler thread
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            self._scheduler_thread.join(timeout=timeout)
        
        # Shutdown thread pool
        if self._executor:
            self._executor.shutdown(wait=wait, cancel_futures=not wait)
            self._executor = None
        
        self.logger.info(f"{self.name} stopped")
    
    def schedule_once(self,
                      task_id: str,
                      func: Callable,
                      delay_seconds: float = 0,
                      priority: TaskPriority = TaskPriority.NORMAL,
                      *args, **kwargs) -> str:
        """
        Schedule a one-time task.
        
        Args:
            task_id: Unique identifier for the task
            func: Function to execute
            delay_seconds: Delay before execution
            priority: Task priority
            *args, **kwargs: Arguments to pass to func
            
        Returns:
            Task ID
        """
        task = ScheduledTask(
            next_run=time.time() + delay_seconds,
            priority=priority.value,
            task_id=task_id,
            func=func,
            interval_seconds=0,
            is_recurring=False,
            args=args,
            kwargs=kwargs
        )
        
        self._add_task(task)
        self.logger.debug(f"Scheduled one-time task: {task_id} (delay: {delay_seconds}s)")
        return task_id
    
    def schedule_recurring(self,
                           task_id: str,
                           func: Callable,
                           interval_seconds: float,
                           priority: TaskPriority = TaskPriority.NORMAL,
                           initial_delay: float = 0,
                           *args, **kwargs) -> str:
        """
        Schedule a recurring task.
        
        Args:
            task_id: Unique identifier for the task
            func: Function to execute
            interval_seconds: Interval between executions
            priority: Task priority
            initial_delay: Delay before first execution
            *args, **kwargs: Arguments to pass to func
            
        Returns:
            Task ID
        """
        task = ScheduledTask(
            next_run=time.time() + initial_delay,
            priority=priority.value,
            task_id=task_id,
            func=func,
            interval_seconds=interval_seconds,
            is_recurring=True,
            args=args,
            kwargs=kwargs
        )
        
        self._add_task(task)
        self.logger.debug(
            f"Scheduled recurring task: {task_id} "
            f"(interval: {interval_seconds}s, initial delay: {initial_delay}s)"
        )
        return task_id
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a scheduled task.
        
        Args:
            task_id: ID of task to cancel
            
        Returns:
            True if task was found and cancelled
        """
        with self._task_lock:
            if task_id in self._tasks:
                self._tasks[task_id].state = TaskState.CANCELLED
                del self._tasks[task_id]
                self._stats['tasks_cancelled'] += 1
                self.logger.debug(f"Cancelled task: {task_id}")
                return True
            
            # Also try to cancel active future
            if task_id in self._active_futures:
                future = self._active_futures[task_id]
                if future.cancel():
                    self._stats['tasks_cancelled'] += 1
                    self.logger.debug(f"Cancelled running task: {task_id}")
                    return True
        
        return False
    
    def pause_task(self, task_id: str) -> bool:
        """
        Pause a recurring task (skips next executions until resumed).
        
        Args:
            task_id: ID of task to pause
            
        Returns:
            True if task was found and paused
        """
        with self._task_lock:
            if task_id in self._tasks:
                # Move next_run far into the future
                self._tasks[task_id].next_run = float('inf')
                self.logger.debug(f"Paused task: {task_id}")
                return True
        return False
    
    def resume_task(self, task_id: str) -> bool:
        """
        Resume a paused task.
        
        Args:
            task_id: ID of task to resume
            
        Returns:
            True if task was found and resumed
        """
        with self._task_lock:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                task.next_run = time.time()
                # Re-add to queue
                heapq.heappush(self._task_queue, task)
                self.logger.debug(f"Resumed task: {task_id}")
                return True
        return False
    
    def run_now(self, task_id: str) -> bool:
        """
        Run a scheduled task immediately (doesn't affect schedule).
        
        Args:
            task_id: ID of task to run
            
        Returns:
            True if task was found and triggered
        """
        with self._task_lock:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                # Create a copy for immediate execution
                self._execute_task(task)
                return True
        return False
    
    def get_task_info(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a task.
        
        Args:
            task_id: ID of task
            
        Returns:
            Task information dictionary, or None if not found
        """
        with self._task_lock:
            if task_id not in self._tasks:
                return None
            
            task = self._tasks[task_id]
            return {
                'task_id': task.task_id,
                'state': task.state.value,
                'is_recurring': task.is_recurring,
                'interval_seconds': task.interval_seconds,
                'priority': TaskPriority(task.priority).name,
                'next_run': datetime.fromtimestamp(task.next_run).isoformat() 
                           if task.next_run != float('inf') else 'paused',
                'last_run': datetime.fromtimestamp(task.last_run).isoformat() 
                           if task.last_run else None,
                'run_count': task.run_count,
                'error_count': task.error_count,
                'last_error': task.last_error
            }
    
    def _add_task(self, task: ScheduledTask) -> None:
        """Add a task to the scheduler."""
        with self._task_lock:
            # Cancel existing task with same ID
            if task.task_id in self._tasks:
                self.cancel_task(task.task_id)
            
            self._tasks[task.task_id] = task
            heapq.heappush(self._task_queue, task)
    
    def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        while not self._stop_event.is_set():
            try:
                self._process_due_tasks()
                # Sleep briefly to avoid busy-waiting
                self._stop_event.wait(0.1)
            except Exception as e:
                self.logger.error(f"Scheduler loop error: {e}", exc_info=True)
    
    def _process_due_tasks(self) -> None:
        """Process all tasks that are due."""
        current_time = time.time()
        
        with self._task_lock:
            while self._task_queue:
                # Peek at next task
                task = self._task_queue[0]
                
                # Check if task was cancelled
                if task.task_id not in self._tasks:
                    heapq.heappop(self._task_queue)
                    continue
                
                # Check if task is paused
                if task.next_run == float('inf'):
                    heapq.heappop(self._task_queue)
                    continue
                
                # Check if task is due
                if task.next_run > current_time:
                    break
                
                # Pop and execute
                heapq.heappop(self._task_queue)
                self._execute_task(task)
    
    def _execute_task(self, task: ScheduledTask) -> None:
        """Execute a task in the thread pool."""
        if not self._executor or not self._running:
            return
        
        def task_wrapper():
            start_time = time.time()
            result = TaskResult(task_id=task.task_id, success=False)
            
            try:
                task.state = TaskState.RUNNING
                ret_value = task.func(*task.args, **task.kwargs)
                
                result.success = True
                result.result = ret_value
                task.state = TaskState.COMPLETED
                task.run_count += 1
                self._stats['tasks_executed'] += 1
                
            except Exception as e:
                result.success = False
                result.error = str(e)
                task.state = TaskState.FAILED
                task.error_count += 1
                task.last_error = str(e)
                self._stats['tasks_failed'] += 1
                self.logger.error(f"Task {task.task_id} failed: {e}")
                
                if self._on_task_error:
                    try:
                        self._on_task_error(task.task_id, e)
                    except Exception:
                        pass
            
            finally:
                execution_time = time.time() - start_time
                result.execution_time = execution_time
                task.last_run = time.time()
                self._stats['total_execution_time'] += execution_time
                
                # Store result
                self._results_history.append(result)
                if len(self._results_history) > self._max_results_history:
                    self._results_history = self._results_history[-self._max_results_history:]
                
                # Clean up future reference
                self._active_futures.pop(task.task_id, None)
                
                # Reschedule if recurring
                if task.is_recurring and task.task_id in self._tasks:
                    task.next_run = time.time() + task.interval_seconds
                    task.state = TaskState.PENDING
                    with self._task_lock:
                        heapq.heappush(self._task_queue, task)
                
                # Callback
                if self._on_task_complete:
                    try:
                        self._on_task_complete(result)
                    except Exception:
                        pass
        
        try:
            future = self._executor.submit(task_wrapper)
            self._active_futures[task.task_id] = future
        except Exception as e:
            self.logger.error(f"Failed to submit task {task.task_id}: {e}")
    
    def set_on_task_complete(self, callback: Callable[[TaskResult], None]) -> None:
        """Set callback for task completion."""
        self._on_task_complete = callback
    
    def set_on_task_error(self, callback: Callable[[str, Exception], None]) -> None:
        """Set callback for task errors."""
        self._on_task_error = callback
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        with self._task_lock:
            return {
                **self._stats,
                'pending_tasks': len(self._tasks),
                'active_tasks': len(self._active_futures),
                'is_running': self._running,
                'uptime_seconds': (
                    (datetime.now() - self._stats['started_at']).total_seconds()
                    if self._stats['started_at'] and self._running else 0
                )
            }
    
    def get_pending_tasks(self) -> List[str]:
        """Get list of pending task IDs."""
        with self._task_lock:
            return list(self._tasks.keys())
    
    def get_recent_results(self, count: int = 10) -> List[TaskResult]:
        """Get recent task results."""
        return self._results_history[-count:]
    
    @property
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._running


# Global scheduler instance
_scheduler: Optional[TaskScheduler] = None


def get_task_scheduler() -> TaskScheduler:
    """
    Get the global task scheduler instance.
    
    Creates one if it doesn't exist.
    
    Returns:
        Global TaskScheduler instance
    """
    global _scheduler
    if _scheduler is None:
        _scheduler = TaskScheduler()
    return _scheduler


def init_task_scheduler(max_workers: int = 4, 
                        logger: Optional[logging.Logger] = None,
                        auto_start: bool = True) -> TaskScheduler:
    """
    Initialize the global task scheduler.
    
    Args:
        max_workers: Maximum concurrent workers
        logger: Logger instance
        auto_start: Whether to start the scheduler immediately
        
    Returns:
        Initialized TaskScheduler
    """
    global _scheduler
    _scheduler = TaskScheduler(max_workers=max_workers, logger=logger)
    if auto_start:
        _scheduler.start()
    return _scheduler


def shutdown_task_scheduler(wait: bool = True) -> None:
    """
    Shutdown the global task scheduler.
    
    Args:
        wait: Whether to wait for running tasks
    """
    global _scheduler
    if _scheduler is not None:
        _scheduler.stop(wait=wait)
        _scheduler = None

