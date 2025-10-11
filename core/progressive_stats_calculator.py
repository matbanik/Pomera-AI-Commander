"""
Progressive Statistics Calculator for Pomera AI Commander.

This module provides progressive statistics calculation for large text content
without blocking the UI. It implements chunked processing, cancellable calculations,
and progress indicators for long-running operations.

Requirements addressed:
- 5.1: Calculate statistics in chunks for text exceeding 50,000 characters
- 5.2: Yield control to UI thread periodically during calculations
- 5.3: Show processing indicator for calculations taking longer than 100ms
- 5.4: Cancel and restart calculations when user continues typing
"""

import time
import threading
import hashlib
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
import re


class CalculationStatus(Enum):
    """Status of a progressive calculation."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class ProgressInfo:
    """Information about calculation progress."""
    calculation_id: str
    status: CalculationStatus
    progress_percent: float = 0.0
    chunks_processed: int = 0
    total_chunks: int = 0
    elapsed_time_ms: float = 0.0
    estimated_remaining_ms: float = 0.0
    
    @property
    def is_complete(self) -> bool:
        """Check if calculation is complete."""
        return self.status in [CalculationStatus.COMPLETED, CalculationStatus.CANCELLED, CalculationStatus.FAILED]
    
    @property
    def should_show_indicator(self) -> bool:
        """Check if progress indicator should be shown (>100ms)."""
        return self.elapsed_time_ms > 100.0


@dataclass
class TextStats:
    """Text statistics result."""
    char_count: int = 0
    word_count: int = 0
    sentence_count: int = 0
    line_count: int = 0
    token_count: int = 0
    
    # Metadata
    content_hash: str = ""
    calculation_time_ms: float = 0.0
    chunk_processed: bool = False
    processing_method: str = "full"
    
    def to_status_string(self) -> str:
        """Convert to status bar string format."""
        formatted_bytes = self._format_bytes(self.char_count)
        return f"Bytes: {formatted_bytes} | Word: {self.word_count} | Sentence: {self.sentence_count} | Line: {self.line_count} | Tokens: {self.token_count}"
    
    def _format_bytes(self, byte_count):
        """Format byte count with K/M suffixes for readability."""
        if byte_count >= 1000000:
            value = byte_count / 1000000
            formatted = f"{value:.1f}M"
        elif byte_count >= 1000:
            value = byte_count / 1000
            if round(value, 1) >= 1000:
                formatted = f"{value / 1000:.1f}M"
            else:
                formatted = f"{value:.1f}K"
        else:
            return str(byte_count)
        
        return formatted.rstrip('0').rstrip('.')


@dataclass
class CalculationTask:
    """A calculation task with cancellation support."""
    calculation_id: str
    text: str
    chunk_size: int
    callback: Optional[Callable]
    progress_callback: Optional[Callable]
    start_time: float = field(default_factory=time.time)
    cancelled: bool = False
    
    def cancel(self):
        """Cancel this calculation."""
        self.cancelled = True


class ProgressiveStatsCalculator:
    """
    Progressive statistics calculator for handling large text content without blocking UI.
    
    This calculator implements chunked processing for text exceeding 50,000 characters,
    yields control to the UI thread periodically, provides cancellable calculations,
    and shows processing indicators for long-running operations.
    """
    
    def __init__(self, chunk_size: int = 10000, progress_indicator_threshold_ms: float = 100.0):
        """
        Initialize the progressive statistics calculator.
        
        Args:
            chunk_size: Size of text chunks for processing (default: 10,000 characters)
            progress_indicator_threshold_ms: Threshold for showing progress indicator (default: 100ms)
        """
        self.chunk_size = chunk_size
        self.progress_indicator_threshold_ms = progress_indicator_threshold_ms
        
        # Active calculations
        self.active_calculations: Dict[str, CalculationTask] = {}
        self.calculation_lock = threading.RLock()
        
        # Regex patterns (compiled once for performance)
        self.word_pattern = re.compile(r'\b\w+\b')
        self.sentence_pattern = re.compile(r'[.!?]+')
        
        # Statistics
        self.stats = {
            'total_calculations': 0,
            'progressive_calculations': 0,
            'cancelled_calculations': 0,
            'completed_calculations': 0,
            'total_processing_time_ms': 0.0
        }
    
    def calculate_progressive(self, 
                            text: str,
                            callback: Optional[Callable[[TextStats], None]] = None,
                            progress_callback: Optional[Callable[[ProgressInfo], None]] = None,
                            widget_id: Optional[str] = None) -> str:
        """
        Calculate statistics progressively for large text content.
        
        Args:
            text: Text content to analyze
            callback: Optional callback to receive final results
            progress_callback: Optional callback to receive progress updates
            widget_id: Optional widget identifier for tracking
            
        Returns:
            Calculation ID for tracking and cancellation
        """
        # Track total calculations
        self.stats['total_calculations'] += 1
        
        # Generate calculation ID
        calculation_id = self._generate_calculation_id(text, widget_id)
        
        # Cancel any existing calculation for this widget
        if widget_id:
            self.cancel_calculation_for_widget(widget_id)
        
        # Check if text is large enough to require progressive calculation
        text_length = len(text)
        
        if text_length < 50000:
            # Small text - calculate immediately
            stats = self._calculate_stats_fast(text)
            self.stats['completed_calculations'] += 1
            if callback:
                callback(stats)
            return calculation_id
        
        # Large text - use progressive calculation
        self.stats['progressive_calculations'] += 1
        
        # Create calculation task
        task = CalculationTask(
            calculation_id=calculation_id,
            text=text,
            chunk_size=self.chunk_size,
            callback=callback,
            progress_callback=progress_callback
        )
        
        with self.calculation_lock:
            self.active_calculations[calculation_id] = task
        
        # Start calculation in background thread
        thread = threading.Thread(
            target=self._calculate_progressive_impl,
            args=(task,),
            daemon=True
        )
        thread.start()
        
        return calculation_id
    
    def _calculate_progressive_impl(self, task: CalculationTask) -> None:
        """
        Internal implementation of progressive calculation.
        
        Args:
            task: Calculation task to execute
        """
        start_time = time.time()
        text = task.text
        text_length = len(text)
        
        # Calculate number of chunks
        total_chunks = (text_length + task.chunk_size - 1) // task.chunk_size
        
        # Initialize accumulators
        total_char_count = 0
        total_word_count = 0
        total_sentence_count = 0
        total_line_count = 0
        
        try:
            # Process text in chunks
            for chunk_idx in range(total_chunks):
                # Check if cancelled
                if task.cancelled:
                    self._handle_cancellation(task)
                    return
                
                # Calculate chunk boundaries
                start_pos = chunk_idx * task.chunk_size
                end_pos = min(start_pos + task.chunk_size, text_length)
                chunk = text[start_pos:end_pos]
                
                # Process chunk
                chunk_stats = self._process_chunk(chunk, start_pos, end_pos, text_length)
                
                # Accumulate results
                total_char_count += chunk_stats['char_count']
                total_word_count += chunk_stats['word_count']
                total_sentence_count += chunk_stats['sentence_count']
                total_line_count += chunk_stats['line_count']
                
                # Calculate progress
                chunks_processed = chunk_idx + 1
                progress_percent = (chunks_processed / total_chunks) * 100.0
                elapsed_time_ms = (time.time() - start_time) * 1000.0
                
                # Estimate remaining time
                if chunks_processed > 0:
                    avg_time_per_chunk = elapsed_time_ms / chunks_processed
                    remaining_chunks = total_chunks - chunks_processed
                    estimated_remaining_ms = avg_time_per_chunk * remaining_chunks
                else:
                    estimated_remaining_ms = 0.0
                
                # Send progress update
                if task.progress_callback and elapsed_time_ms > self.progress_indicator_threshold_ms:
                    progress_info = ProgressInfo(
                        calculation_id=task.calculation_id,
                        status=CalculationStatus.RUNNING,
                        progress_percent=progress_percent,
                        chunks_processed=chunks_processed,
                        total_chunks=total_chunks,
                        elapsed_time_ms=elapsed_time_ms,
                        estimated_remaining_ms=estimated_remaining_ms
                    )
                    task.progress_callback(progress_info)
                
                # Yield control to UI thread periodically (every 2 chunks)
                if chunk_idx % 2 == 0:
                    time.sleep(0.001)  # Small sleep to yield control
            
            # Calculation complete
            calculation_time_ms = (time.time() - start_time) * 1000.0
            
            # Create final stats
            stats = TextStats(
                char_count=total_char_count,
                word_count=total_word_count,
                sentence_count=total_sentence_count,
                line_count=total_line_count,
                token_count=max(1, round(text_length / 4)),
                content_hash=self._generate_content_hash(text),
                calculation_time_ms=calculation_time_ms,
                chunk_processed=True,
                processing_method="progressive"
            )
            
            # Send final result
            if task.callback:
                task.callback(stats)
            
            # Update statistics
            self.stats['completed_calculations'] += 1
            self.stats['total_processing_time_ms'] += calculation_time_ms
            
            # Send completion progress update
            if task.progress_callback:
                progress_info = ProgressInfo(
                    calculation_id=task.calculation_id,
                    status=CalculationStatus.COMPLETED,
                    progress_percent=100.0,
                    chunks_processed=total_chunks,
                    total_chunks=total_chunks,
                    elapsed_time_ms=calculation_time_ms,
                    estimated_remaining_ms=0.0
                )
                task.progress_callback(progress_info)
        
        except Exception as e:
            # Handle calculation error
            print(f"Error in progressive calculation: {e}")
            
            if task.progress_callback:
                progress_info = ProgressInfo(
                    calculation_id=task.calculation_id,
                    status=CalculationStatus.FAILED,
                    progress_percent=0.0,
                    chunks_processed=0,
                    total_chunks=total_chunks,
                    elapsed_time_ms=(time.time() - start_time) * 1000.0,
                    estimated_remaining_ms=0.0
                )
                task.progress_callback(progress_info)
        
        finally:
            # Clean up
            with self.calculation_lock:
                self.active_calculations.pop(task.calculation_id, None)
    
    def _process_chunk(self, chunk: str, start_pos: int, end_pos: int, total_length: int) -> Dict[str, int]:
        """
        Process a single chunk of text.
        
        Args:
            chunk: Text chunk to process
            start_pos: Start position in original text
            end_pos: End position in original text
            total_length: Total length of original text
            
        Returns:
            Dictionary with chunk statistics
        """
        # Character count (bytes)
        char_count = len(chunk.encode('utf-8'))
        
        # Word count
        words = self.word_pattern.findall(chunk)
        word_count = len(words)
        
        # Sentence count
        sentences = self.sentence_pattern.findall(chunk)
        sentence_count = len(sentences)
        
        # Line count
        line_count = chunk.count('\n')
        
        # Adjust counts for chunk boundaries
        # Only count full lines for first and last chunks
        if start_pos == 0 and chunk.strip():
            line_count += 1  # Add first line
        
        return {
            'char_count': char_count,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'line_count': line_count
        }
    
    def _calculate_stats_fast(self, text: str) -> TextStats:
        """
        Fast calculation for small text content.
        
        Args:
            text: Text to analyze
            
        Returns:
            TextStats object
        """
        start_time = time.time()
        
        # Basic statistics
        char_count = len(text.encode('utf-8'))
        line_count = text.count('\n') + (1 if text.strip() else 0)
        
        # Word statistics
        words = self.word_pattern.findall(text)
        word_count = len(words)
        
        # Sentence statistics
        sentences = self.sentence_pattern.findall(text)
        sentence_count = len(sentences)
        
        # Token count (rough estimate: 1 token ≈ 4 characters)
        token_count = max(1, round(len(text) / 4))
        
        calculation_time_ms = (time.time() - start_time) * 1000.0
        
        return TextStats(
            char_count=char_count,
            word_count=word_count,
            sentence_count=sentence_count,
            line_count=line_count,
            token_count=token_count,
            content_hash=self._generate_content_hash(text),
            calculation_time_ms=calculation_time_ms,
            chunk_processed=False,
            processing_method="fast"
        )
    
    def cancel_calculation(self, calculation_id: str) -> bool:
        """
        Cancel a specific calculation.
        
        Args:
            calculation_id: ID of calculation to cancel
            
        Returns:
            True if calculation was cancelled, False if not found
        """
        with self.calculation_lock:
            task = self.active_calculations.get(calculation_id)
            if task:
                task.cancel()
                self.stats['cancelled_calculations'] += 1
                return True
            return False
    
    def cancel_calculation_for_widget(self, widget_id: str) -> int:
        """
        Cancel all calculations for a specific widget.
        
        Args:
            widget_id: Widget identifier
            
        Returns:
            Number of calculations cancelled
        """
        cancelled_count = 0
        
        with self.calculation_lock:
            # Find all calculations for this widget
            # Check if calculation_id contains the widget_id
            to_cancel = []
            for calc_id, task in self.active_calculations.items():
                # The calculation_id format is: {content_hash}_{timestamp}_{widget_id}
                # So we check if it ends with the widget_id
                if widget_id and calc_id.endswith(f"_{widget_id}"):
                    to_cancel.append(calc_id)
            
            # Cancel them
            for calc_id in to_cancel:
                task = self.active_calculations.get(calc_id)
                if task and not task.cancelled:
                    task.cancel()
                    self.stats['cancelled_calculations'] += 1
                    cancelled_count += 1
        
        return cancelled_count
    
    def cancel_all_calculations(self) -> int:
        """
        Cancel all active calculations.
        
        Returns:
            Number of calculations cancelled
        """
        with self.calculation_lock:
            calc_ids = list(self.active_calculations.keys())
            
            for calc_id in calc_ids:
                self.cancel_calculation(calc_id)
            
            return len(calc_ids)
    
    def _handle_cancellation(self, task: CalculationTask) -> None:
        """
        Handle calculation cancellation.
        
        Args:
            task: Cancelled task
        """
        # Send cancellation progress update
        if task.progress_callback:
            progress_info = ProgressInfo(
                calculation_id=task.calculation_id,
                status=CalculationStatus.CANCELLED,
                progress_percent=0.0,
                chunks_processed=0,
                total_chunks=0,
                elapsed_time_ms=(time.time() - task.start_time) * 1000.0,
                estimated_remaining_ms=0.0
            )
            task.progress_callback(progress_info)
        
        # Clean up
        with self.calculation_lock:
            self.active_calculations.pop(task.calculation_id, None)
    
    def _generate_calculation_id(self, text: str, widget_id: Optional[str] = None) -> str:
        """
        Generate a unique calculation ID.
        
        Args:
            text: Text content
            widget_id: Optional widget identifier
            
        Returns:
            Unique calculation ID
        """
        content_hash = self._generate_content_hash(text)
        timestamp = str(time.time())
        widget_part = f"_{widget_id}" if widget_id else ""
        
        id_string = f"{content_hash}_{timestamp}{widget_part}"
        return hashlib.md5(id_string.encode('utf-8')).hexdigest()[:16]
    
    def _generate_content_hash(self, text: str) -> str:
        """
        Generate a hash for content identification.
        
        Args:
            text: Text content
            
        Returns:
            Content hash
        """
        content_sample = text[:100] + text[-100:] if len(text) > 200 else text
        hash_input = f"{len(text)}_{content_sample}"
        return hashlib.md5(hash_input.encode('utf-8')).hexdigest()[:16]
    
    def get_active_calculations(self) -> List[str]:
        """
        Get list of active calculation IDs.
        
        Returns:
            List of calculation IDs
        """
        with self.calculation_lock:
            return list(self.active_calculations.keys())
    
    def get_calculation_progress(self, calculation_id: str) -> Optional[ProgressInfo]:
        """
        Get progress information for a calculation.
        
        Args:
            calculation_id: Calculation ID
            
        Returns:
            ProgressInfo or None if not found
        """
        with self.calculation_lock:
            task = self.active_calculations.get(calculation_id)
            if not task:
                return None
            
            elapsed_time_ms = (time.time() - task.start_time) * 1000.0
            
            return ProgressInfo(
                calculation_id=calculation_id,
                status=CalculationStatus.RUNNING if not task.cancelled else CalculationStatus.CANCELLED,
                progress_percent=0.0,  # Would need to track this in task
                chunks_processed=0,
                total_chunks=0,
                elapsed_time_ms=elapsed_time_ms,
                estimated_remaining_ms=0.0
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get calculator statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self.calculation_lock:
            stats = self.stats.copy()
            stats['active_calculations'] = len(self.active_calculations)
            
            # Calculate average processing time
            if stats['completed_calculations'] > 0:
                stats['avg_processing_time_ms'] = (
                    stats['total_processing_time_ms'] / stats['completed_calculations']
                )
            else:
                stats['avg_processing_time_ms'] = 0.0
            
            return stats
    
    def clear_statistics(self) -> None:
        """Clear all statistics."""
        self.stats = {
            'total_calculations': 0,
            'progressive_calculations': 0,
            'cancelled_calculations': 0,
            'completed_calculations': 0,
            'total_processing_time_ms': 0.0
        }


# Global instance for easy access
_global_progressive_calculator: Optional[ProgressiveStatsCalculator] = None


def get_progressive_stats_calculator() -> ProgressiveStatsCalculator:
    """Get the global progressive statistics calculator instance."""
    global _global_progressive_calculator
    if _global_progressive_calculator is None:
        _global_progressive_calculator = ProgressiveStatsCalculator()
    return _global_progressive_calculator


def create_progressive_stats_calculator(chunk_size: int = 10000,
                                       progress_indicator_threshold_ms: float = 100.0) -> ProgressiveStatsCalculator:
    """
    Create a new progressive statistics calculator instance.
    
    Args:
        chunk_size: Size of text chunks for processing
        progress_indicator_threshold_ms: Threshold for showing progress indicator
        
    Returns:
        New ProgressiveStatsCalculator instance
    """
    return ProgressiveStatsCalculator(chunk_size, progress_indicator_threshold_ms)
