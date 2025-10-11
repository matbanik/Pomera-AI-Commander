"""
Asynchronous text processing framework for Promera AI Commander.
Handles heavy text operations in background threads to prevent UI freezing.
"""

import threading
import time
import queue
import hashlib
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable, Any, Tuple
from enum import Enum
import logging

class ProcessingMode(Enum):
    """Processing mode for different content sizes."""
    SYNC = "sync"           # Small content, process synchronously
    ASYNC = "async"         # Medium content, process asynchronously
    CHUNKED = "chunked"     # Large content, process in chunks

@dataclass
class TextProcessingContext:
    """Context information for text processing operations."""
    content: str
    content_hash: str
    size_bytes: int
    line_count: int
    processing_mode: ProcessingMode
    chunk_size: int = 50000
    tool_name: str = ""
    callback_id: str = ""
    
    @classmethod
    def from_content(cls, content: str, tool_name: str = "", callback_id: str = ""):
        """Create context from text content."""
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        size_bytes = len(content.encode('utf-8'))
        line_count = content.count('\n')
        
        # Determine processing mode based on content size
        if size_bytes < 10000:  # 10KB
            mode = ProcessingMode.SYNC
        elif size_bytes < 100000:  # 100KB
            mode = ProcessingMode.ASYNC
        else:
            mode = ProcessingMode.CHUNKED
        
        return cls(
            content=content,
            content_hash=content_hash,
            size_bytes=size_bytes,
            line_count=line_count,
            processing_mode=mode,
            tool_name=tool_name,
            callback_id=callback_id
        )
    
    @property
    def requires_async_processing(self) -> bool:
        """Check if content requires async processing."""
        return self.processing_mode in [ProcessingMode.ASYNC, ProcessingMode.CHUNKED]

@dataclass
class ProcessingResult:
    """Result of a text processing operation."""
    success: bool
    result: str
    error_message: Optional[str] = None
    processing_time_ms: float = 0.0
    chunks_processed: int = 1
    context: Optional[TextProcessingContext] = None

class AsyncTextProcessor:
    """Asynchronous text processor with background threading and chunking support."""
    
    def __init__(self, max_workers: int = 2, logger: Optional[logging.Logger] = None):
        self.max_workers = max_workers
        self.logger = logger or logging.getLogger(__name__)
        
        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="AsyncTextProcessor")
        
        # Task management
        self.active_tasks: Dict[str, Future] = {}
        self.task_callbacks: Dict[str, Callable] = {}
        self.task_contexts: Dict[str, TextProcessingContext] = {}
        
        # Progress tracking
        self.progress_callbacks: Dict[str, Callable] = {}
        
        # Shutdown flag
        self._shutdown = False
        
        self.logger.info(f"AsyncTextProcessor initialized with {max_workers} workers")
    
    def process_text_async(self, 
                          context: TextProcessingContext,
                          processor_func: Callable[[str], str],
                          callback: Callable[[ProcessingResult], None],
                          progress_callback: Optional[Callable[[int, int], None]] = None) -> str:
        """
        Process text asynchronously with callback when complete.
        
        Args:
            context: Text processing context
            processor_func: Function to process the text
            callback: Callback function for when processing is complete
            progress_callback: Optional callback for progress updates (current, total)
            
        Returns:
            Task ID for tracking/cancellation
        """
        if self._shutdown:
            raise RuntimeError("AsyncTextProcessor is shut down")
        
        task_id = f"{context.tool_name}_{context.callback_id}_{int(time.time() * 1000000)}"
        
        # Store callback and context
        self.task_callbacks[task_id] = callback
        self.task_contexts[task_id] = context
        if progress_callback:
            self.progress_callbacks[task_id] = progress_callback
        
        # Submit task based on processing mode
        if context.processing_mode == ProcessingMode.CHUNKED:
            future = self.executor.submit(self._process_chunked, context, processor_func, task_id)
        else:
            future = self.executor.submit(self._process_single, context, processor_func, task_id)
        
        self.active_tasks[task_id] = future
        
        # Set up completion callback
        future.add_done_callback(lambda f: self._on_task_complete(task_id, f))
        
        self.logger.debug(f"Started async processing: {task_id} ({context.processing_mode.value})")
        return task_id
    
    def _process_single(self, context: TextProcessingContext, processor_func: Callable, task_id: str) -> ProcessingResult:
        """Process text in a single operation."""
        start_time = time.time()
        
        try:
            result = processor_func(context.content)
            processing_time = (time.time() - start_time) * 1000
            
            return ProcessingResult(
                success=True,
                result=result,
                processing_time_ms=processing_time,
                chunks_processed=1,
                context=context
            )
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self.logger.error(f"Error in single processing {task_id}: {e}")
            
            return ProcessingResult(
                success=False,
                result="",
                error_message=str(e),
                processing_time_ms=processing_time,
                context=context
            )
    
    def _process_chunked(self, context: TextProcessingContext, processor_func: Callable, task_id: str) -> ProcessingResult:
        """Process text in chunks for large content."""
        start_time = time.time()
        
        try:
            chunks = self.chunk_large_text(context.content, context.chunk_size)
            processed_chunks = []
            
            for i, chunk in enumerate(chunks):
                if self._is_task_cancelled(task_id):
                    return ProcessingResult(
                        success=False,
                        result="",
                        error_message="Task cancelled",
                        processing_time_ms=(time.time() - start_time) * 1000,
                        context=context
                    )
                
                # Process chunk
                processed_chunk = processor_func(chunk)
                processed_chunks.append(processed_chunk)
                
                # Update progress
                if task_id in self.progress_callbacks:
                    try:
                        self.progress_callbacks[task_id](i + 1, len(chunks))
                    except Exception as e:
                        self.logger.warning(f"Progress callback error: {e}")
            
            # Combine results
            result = self._combine_chunks(processed_chunks, context.tool_name)
            processing_time = (time.time() - start_time) * 1000
            
            return ProcessingResult(
                success=True,
                result=result,
                processing_time_ms=processing_time,
                chunks_processed=len(chunks),
                context=context
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self.logger.error(f"Error in chunked processing {task_id}: {e}")
            
            return ProcessingResult(
                success=False,
                result="",
                error_message=str(e),
                processing_time_ms=processing_time,
                context=context
            )
    
    def chunk_large_text(self, text: str, chunk_size: int = 50000) -> List[str]:
        """
        Break large text into processable chunks.
        Tries to break at word boundaries when possible.
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            if end >= len(text):
                # Last chunk
                chunks.append(text[start:])
                break
            
            # Try to break at word boundary
            break_point = end
            for i in range(end, max(start, end - 100), -1):
                if text[i] in ' \n\t':
                    break_point = i
                    break
            
            chunks.append(text[start:break_point])
            start = break_point
        
        return chunks
    
    def _combine_chunks(self, chunks: List[str], tool_name: str) -> str:
        """Combine processed chunks back into a single result."""
        if tool_name in ["Number Sorter", "Alphabetical Sorter"]:
            # For sorting tools, we need to sort the combined result
            combined = '\n'.join(chunks)
            lines = combined.splitlines()
            # Remove empty lines that might have been introduced
            lines = [line for line in lines if line.strip()]
            return '\n'.join(lines)
        else:
            # For most tools, simple concatenation works
            return ''.join(chunks)
    
    def _on_task_complete(self, task_id: str, future: Future):
        """Handle task completion."""
        try:
            result = future.result()
            callback = self.task_callbacks.get(task_id)
            
            if callback:
                try:
                    callback(result)
                except Exception as e:
                    self.logger.error(f"Callback error for task {task_id}: {e}")
            
            self.logger.debug(f"Completed async processing: {task_id} "
                            f"({result.processing_time_ms:.1f}ms, "
                            f"{result.chunks_processed} chunks)")
            
        except Exception as e:
            self.logger.error(f"Task completion error for {task_id}: {e}")
            
            # Create error result
            result = ProcessingResult(
                success=False,
                result="",
                error_message=str(e),
                context=self.task_contexts.get(task_id)
            )
            
            callback = self.task_callbacks.get(task_id)
            if callback:
                try:
                    callback(result)
                except Exception as callback_error:
                    self.logger.error(f"Callback error for failed task {task_id}: {callback_error}")
        
        finally:
            # Clean up
            self.active_tasks.pop(task_id, None)
            self.task_callbacks.pop(task_id, None)
            self.task_contexts.pop(task_id, None)
            self.progress_callbacks.pop(task_id, None)
    
    def cancel_processing(self, task_id: str) -> bool:
        """
        Cancel an ongoing processing operation.
        
        Args:
            task_id: ID of the task to cancel
            
        Returns:
            True if task was cancelled, False if not found or already complete
        """
        if task_id in self.active_tasks:
            future = self.active_tasks[task_id]
            cancelled = future.cancel()
            
            if cancelled:
                self.logger.info(f"Cancelled task: {task_id}")
                # Clean up immediately for cancelled tasks
                self.active_tasks.pop(task_id, None)
                self.task_callbacks.pop(task_id, None)
                self.task_contexts.pop(task_id, None)
                self.progress_callbacks.pop(task_id, None)
            
            return cancelled
        
        return False
    
    def _is_task_cancelled(self, task_id: str) -> bool:
        """Check if a task has been cancelled."""
        if task_id in self.active_tasks:
            return self.active_tasks[task_id].cancelled()
        return False
    
    def cancel_all_tasks(self):
        """Cancel all active tasks."""
        task_ids = list(self.active_tasks.keys())
        cancelled_count = 0
        
        for task_id in task_ids:
            if self.cancel_processing(task_id):
                cancelled_count += 1
        
        self.logger.info(f"Cancelled {cancelled_count} tasks")
        return cancelled_count
    
    def get_active_task_count(self) -> int:
        """Get the number of currently active tasks."""
        return len(self.active_tasks)
    
    def get_active_task_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about active tasks."""
        info = {}
        
        for task_id, future in self.active_tasks.items():
            context = self.task_contexts.get(task_id)
            info[task_id] = {
                'tool_name': context.tool_name if context else 'unknown',
                'content_size': context.size_bytes if context else 0,
                'processing_mode': context.processing_mode.value if context else 'unknown',
                'is_done': future.done(),
                'is_cancelled': future.cancelled()
            }
        
        return info
    
    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for all active tasks to complete.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if all tasks completed, False if timeout occurred
        """
        if not self.active_tasks:
            return True
        
        try:
            futures = list(self.active_tasks.values())
            for future in as_completed(futures, timeout=timeout):
                pass  # Just wait for completion
            return True
        except TimeoutError:
            return False
    
    def shutdown(self, wait: bool = True, timeout: Optional[float] = None):
        """
        Shutdown the async processor.
        
        Args:
            wait: Whether to wait for active tasks to complete
            timeout: Maximum time to wait for shutdown
        """
        self._shutdown = True
        
        if wait:
            self.wait_for_completion(timeout)
        else:
            self.cancel_all_tasks()
        
        self.executor.shutdown(wait=wait)
        self.logger.info("AsyncTextProcessor shut down")

# Global async processor instance
_global_async_processor = None

def get_async_text_processor() -> AsyncTextProcessor:
    """Get the global async text processor instance."""
    global _global_async_processor
    if _global_async_processor is None:
        _global_async_processor = AsyncTextProcessor()
    return _global_async_processor

def shutdown_async_processor():
    """Shutdown the global async processor."""
    global _global_async_processor
    if _global_async_processor is not None:
        _global_async_processor.shutdown()
        _global_async_processor = None