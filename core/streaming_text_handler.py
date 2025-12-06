"""
Streaming Text Handler Module

Provides efficient handling of streaming text content, particularly for AI responses.
Implements progressive text insertion with minimal UI blocking and diff-based updates.

Key Components:
- StreamingTextHandler: Handles progressive text insertion for streaming AI responses
- IncrementalTextUpdater: Uses diff algorithm for efficient large text updates
"""

import tkinter as tk
from typing import Optional, Callable, List, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import difflib
import time
import threading
from queue import Queue, Empty
import logging

logger = logging.getLogger(__name__)


class StreamState(Enum):
    """State of the streaming handler."""
    IDLE = "idle"
    STREAMING = "streaming"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class StreamConfig:
    """Configuration for streaming behavior."""
    chunk_delay_ms: int = 10  # Delay between chunk insertions
    batch_size: int = 5  # Number of chunks to batch before UI update
    max_buffer_size: int = 1000  # Maximum chunks to buffer
    auto_scroll: bool = True  # Auto-scroll to end during streaming
    highlight_new_text: bool = False  # Temporarily highlight new text
    highlight_duration_ms: int = 500  # Duration of highlight
    use_threading: bool = True  # Use background thread for processing


@dataclass
class StreamMetrics:
    """Metrics for streaming performance."""
    total_chunks: int = 0
    total_characters: int = 0
    start_time: float = 0.0
    end_time: float = 0.0
    ui_updates: int = 0
    
    @property
    def duration(self) -> float:
        """Get streaming duration in seconds."""
        if self.end_time > 0:
            return self.end_time - self.start_time
        elif self.start_time > 0:
            return time.time() - self.start_time
        return 0.0
    
    @property
    def chars_per_second(self) -> float:
        """Get characters per second rate."""
        duration = self.duration
        if duration > 0:
            return self.total_characters / duration
        return 0.0


class StreamingTextHandler:
    """
    Handles progressive text insertion for streaming content.
    
    Designed for AI response streaming where text arrives in chunks
    and needs to be displayed progressively without blocking the UI.
    
    Usage:
        handler = StreamingTextHandler(text_widget)
        handler.start_stream()
        for chunk in ai_response_stream:
            handler.add_chunk(chunk)
        handler.end_stream()
    """
    
    def __init__(
        self,
        text_widget: tk.Text,
        config: Optional[StreamConfig] = None,
        on_progress: Optional[Callable[[int, int], None]] = None,
        on_complete: Optional[Callable[[StreamMetrics], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None
    ):
        """
        Initialize the streaming text handler.
        
        Args:
            text_widget: The Tkinter Text widget to insert text into
            config: Configuration for streaming behavior
            on_progress: Callback for progress updates (chars_received, total_chars)
            on_complete: Callback when streaming completes
            on_error: Callback when an error occurs
        """
        self.text_widget = text_widget
        self.config = config or StreamConfig()
        self.on_progress = on_progress
        self.on_complete = on_complete
        self.on_error = on_error
        
        self._state = StreamState.IDLE
        self._metrics = StreamMetrics()
        self._chunk_queue: Queue = Queue(maxsize=self.config.max_buffer_size)
        self._buffer: List[str] = []
        self._insert_position: str = "end"
        self._stream_tag = "streaming_text"
        self._processing_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        
        # Configure text tag for highlighting new text
        if self.config.highlight_new_text:
            self.text_widget.tag_configure(
                self._stream_tag,
                background="#e6f3ff"  # Light blue highlight
            )
    
    @property
    def state(self) -> StreamState:
        """Get current streaming state."""
        return self._state
    
    @property
    def metrics(self) -> StreamMetrics:
        """Get current streaming metrics."""
        return self._metrics
    
    @property
    def is_streaming(self) -> bool:
        """Check if currently streaming."""
        return self._state == StreamState.STREAMING
    
    def start_stream(
        self,
        clear_existing: bool = True,
        insert_position: str = "end"
    ) -> bool:
        """
        Start a new streaming session.
        
        Args:
            clear_existing: Whether to clear existing text in widget
            insert_position: Position to insert text ("end" or index)
            
        Returns:
            True if stream started successfully
        """
        if self._state == StreamState.STREAMING:
            logger.warning("Stream already in progress")
            return False
        
        try:
            with self._lock:
                # Reset state
                self._state = StreamState.STREAMING
                self._metrics = StreamMetrics()
                self._metrics.start_time = time.time()
                self._buffer.clear()
                self._insert_position = insert_position
                self._stop_event.clear()
                
                # Clear the queue
                while not self._chunk_queue.empty():
                    try:
                        self._chunk_queue.get_nowait()
                    except Empty:
                        break
                
                # Clear existing text if requested
                if clear_existing:
                    self.text_widget.config(state=tk.NORMAL)
                    self.text_widget.delete("1.0", tk.END)
                
                # Start processing thread if configured
                if self.config.use_threading:
                    self._processing_thread = threading.Thread(
                        target=self._process_queue,
                        daemon=True
                    )
                    self._processing_thread.start()
                
                logger.debug("Stream started")
                return True
                
        except Exception as e:
            self._state = StreamState.ERROR
            logger.error(f"Failed to start stream: {e}")
            if self.on_error:
                self.on_error(e)
            return False
    
    def add_chunk(self, chunk: str) -> bool:
        """
        Add a text chunk to the stream.
        
        Args:
            chunk: Text chunk to add
            
        Returns:
            True if chunk was added successfully
        """
        if self._state != StreamState.STREAMING:
            logger.warning(f"Cannot add chunk in state: {self._state}")
            return False
        
        if not chunk:
            return True
        
        try:
            self._metrics.total_chunks += 1
            self._metrics.total_characters += len(chunk)
            
            if self.config.use_threading:
                # Add to queue for background processing
                self._chunk_queue.put(chunk, timeout=1.0)
            else:
                # Direct insertion
                self._insert_chunk(chunk)
            
            # Progress callback
            if self.on_progress:
                self.on_progress(
                    self._metrics.total_characters,
                    -1  # Unknown total
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add chunk: {e}")
            if self.on_error:
                self.on_error(e)
            return False
    
    def end_stream(self) -> StreamMetrics:
        """
        End the streaming session.
        
        Returns:
            Final streaming metrics
        """
        if self._state != StreamState.STREAMING:
            logger.warning(f"Cannot end stream in state: {self._state}")
            return self._metrics
        
        try:
            with self._lock:
                self._stop_event.set()
                
                # Wait for processing thread to finish
                if self._processing_thread and self._processing_thread.is_alive():
                    self._processing_thread.join(timeout=2.0)
                
                # Process any remaining chunks
                self._flush_buffer()
                
                # Finalize
                self._metrics.end_time = time.time()
                self._state = StreamState.COMPLETED
                
                # Remove highlight tag if used
                if self.config.highlight_new_text:
                    self.text_widget.tag_remove(
                        self._stream_tag,
                        "1.0",
                        tk.END
                    )
                
                logger.debug(
                    f"Stream completed: {self._metrics.total_characters} chars "
                    f"in {self._metrics.duration:.2f}s"
                )
                
                # Completion callback
                if self.on_complete:
                    self.on_complete(self._metrics)
                
                return self._metrics
                
        except Exception as e:
            self._state = StreamState.ERROR
            logger.error(f"Failed to end stream: {e}")
            if self.on_error:
                self.on_error(e)
            return self._metrics
    
    def pause_stream(self) -> bool:
        """Pause the streaming."""
        if self._state == StreamState.STREAMING:
            self._state = StreamState.PAUSED
            return True
        return False
    
    def resume_stream(self) -> bool:
        """Resume a paused stream."""
        if self._state == StreamState.PAUSED:
            self._state = StreamState.STREAMING
            return True
        return False
    
    def cancel_stream(self) -> None:
        """Cancel the current stream."""
        self._stop_event.set()
        self._state = StreamState.IDLE
        self._metrics.end_time = time.time()
        
        # Clear queue
        while not self._chunk_queue.empty():
            try:
                self._chunk_queue.get_nowait()
            except Empty:
                break
    
    def _process_queue(self) -> None:
        """Background thread for processing chunk queue."""
        while not self._stop_event.is_set():
            try:
                # Collect batch of chunks
                batch = []
                for _ in range(self.config.batch_size):
                    try:
                        chunk = self._chunk_queue.get(timeout=0.05)
                        batch.append(chunk)
                    except Empty:
                        break
                
                if batch:
                    # Schedule UI update on main thread
                    combined = "".join(batch)
                    self.text_widget.after(0, self._insert_chunk, combined)
                    
            except Exception as e:
                logger.error(f"Error processing queue: {e}")
                break
    
    def _insert_chunk(self, chunk: str) -> None:
        """Insert a chunk into the text widget."""
        try:
            self.text_widget.config(state=tk.NORMAL)
            
            # Get current end position for highlighting
            start_index = self.text_widget.index(tk.END + "-1c")
            
            # Insert text
            self.text_widget.insert(self._insert_position, chunk)
            self._metrics.ui_updates += 1
            
            # Apply highlight if configured
            if self.config.highlight_new_text:
                end_index = self.text_widget.index(tk.END + "-1c")
                self.text_widget.tag_add(
                    self._stream_tag,
                    start_index,
                    end_index
                )
                # Schedule highlight removal
                self.text_widget.after(
                    self.config.highlight_duration_ms,
                    lambda: self._remove_highlight(start_index, end_index)
                )
            
            # Auto-scroll if configured
            if self.config.auto_scroll:
                self.text_widget.see(tk.END)
            
        except tk.TclError as e:
            logger.error(f"Tkinter error inserting chunk: {e}")
    
    def _remove_highlight(self, start: str, end: str) -> None:
        """Remove highlight from a text range."""
        try:
            self.text_widget.tag_remove(self._stream_tag, start, end)
        except tk.TclError:
            pass  # Widget may have been destroyed
    
    def _flush_buffer(self) -> None:
        """Flush any remaining buffered chunks."""
        while not self._chunk_queue.empty():
            try:
                chunk = self._chunk_queue.get_nowait()
                self._insert_chunk(chunk)
            except Empty:
                break


class IncrementalTextUpdater:
    """
    Efficient text updater using diff algorithm.
    
    Instead of replacing all text, computes the minimal set of changes
    needed to transform the current text to the new text.
    
    Usage:
        updater = IncrementalTextUpdater(text_widget)
        updater.update_text(new_text)
    """
    
    def __init__(
        self,
        text_widget: tk.Text,
        min_diff_ratio: float = 0.3,
        on_update: Optional[Callable[[int, int], None]] = None
    ):
        """
        Initialize the incremental text updater.
        
        Args:
            text_widget: The Tkinter Text widget to update
            min_diff_ratio: Minimum similarity ratio to use diff (0-1)
                           Below this, full replacement is used
            on_update: Callback after update (insertions, deletions)
        """
        self.text_widget = text_widget
        self.min_diff_ratio = min_diff_ratio
        self.on_update = on_update
        self._lock = threading.Lock()
    
    def update_text(
        self,
        new_text: str,
        preserve_cursor: bool = True,
        preserve_scroll: bool = True
    ) -> Tuple[int, int]:
        """
        Update text widget content efficiently using diff.
        
        Args:
            new_text: The new text content
            preserve_cursor: Try to preserve cursor position
            preserve_scroll: Try to preserve scroll position
            
        Returns:
            Tuple of (insertions, deletions) count
        """
        with self._lock:
            try:
                self.text_widget.config(state=tk.NORMAL)
                
                # Get current state
                current_text = self.text_widget.get("1.0", tk.END + "-1c")
                cursor_pos = self.text_widget.index(tk.INSERT) if preserve_cursor else None
                scroll_pos = self.text_widget.yview() if preserve_scroll else None
                
                # Check if diff is worthwhile
                if not current_text:
                    # Empty widget, just insert
                    self.text_widget.insert("1.0", new_text)
                    return (1, 0)
                
                # Calculate similarity
                matcher = difflib.SequenceMatcher(None, current_text, new_text)
                ratio = matcher.ratio()
                
                if ratio < self.min_diff_ratio:
                    # Too different, do full replacement
                    self.text_widget.delete("1.0", tk.END)
                    self.text_widget.insert("1.0", new_text)
                    insertions, deletions = 1, 1
                else:
                    # Apply incremental changes
                    insertions, deletions = self._apply_diff(
                        current_text, new_text, matcher
                    )
                
                # Restore cursor position
                if cursor_pos and preserve_cursor:
                    try:
                        self.text_widget.mark_set(tk.INSERT, cursor_pos)
                    except tk.TclError:
                        pass
                
                # Restore scroll position
                if scroll_pos and preserve_scroll:
                    try:
                        self.text_widget.yview_moveto(scroll_pos[0])
                    except tk.TclError:
                        pass
                
                # Callback
                if self.on_update:
                    self.on_update(insertions, deletions)
                
                return (insertions, deletions)
                
            except Exception as e:
                logger.error(f"Error updating text: {e}")
                # Fallback to full replacement
                self.text_widget.delete("1.0", tk.END)
                self.text_widget.insert("1.0", new_text)
                return (1, 1)
    
    def _apply_diff(
        self,
        old_text: str,
        new_text: str,
        matcher: difflib.SequenceMatcher
    ) -> Tuple[int, int]:
        """
        Apply diff operations to transform old text to new text.
        
        Returns:
            Tuple of (insertions, deletions) count
        """
        insertions = 0
        deletions = 0
        
        # Get opcodes and process in reverse order to maintain indices
        opcodes = list(matcher.get_opcodes())
        
        for tag, i1, i2, j1, j2 in reversed(opcodes):
            if tag == 'equal':
                continue
            
            # Convert character indices to Tkinter indices
            start_idx = self._char_to_index(i1)
            end_idx = self._char_to_index(i2)
            
            if tag == 'replace':
                # Delete old text and insert new
                self.text_widget.delete(start_idx, end_idx)
                self.text_widget.insert(start_idx, new_text[j1:j2])
                insertions += 1
                deletions += 1
                
            elif tag == 'delete':
                # Delete text
                self.text_widget.delete(start_idx, end_idx)
                deletions += 1
                
            elif tag == 'insert':
                # Insert new text
                self.text_widget.insert(start_idx, new_text[j1:j2])
                insertions += 1
        
        return (insertions, deletions)
    
    def _char_to_index(self, char_pos: int) -> str:
        """Convert character position to Tkinter text index."""
        # Get text up to position to count lines
        text = self.text_widget.get("1.0", tk.END + "-1c")
        
        if char_pos >= len(text):
            return tk.END
        
        # Count newlines to get line number
        line = text[:char_pos].count('\n') + 1
        
        # Get column (position within line)
        last_newline = text.rfind('\n', 0, char_pos)
        if last_newline == -1:
            col = char_pos
        else:
            col = char_pos - last_newline - 1
        
        return f"{line}.{col}"
    
    def get_diff_preview(
        self,
        new_text: str,
        context_lines: int = 3
    ) -> str:
        """
        Get a preview of changes without applying them.
        
        Args:
            new_text: The new text to compare
            context_lines: Number of context lines in diff
            
        Returns:
            Unified diff string
        """
        current_text = self.text_widget.get("1.0", tk.END + "-1c")
        
        diff = difflib.unified_diff(
            current_text.splitlines(keepends=True),
            new_text.splitlines(keepends=True),
            fromfile='current',
            tofile='new',
            n=context_lines
        )
        
        return ''.join(diff)


class StreamingTextManager:
    """
    High-level manager for streaming text operations.
    
    Combines StreamingTextHandler and IncrementalTextUpdater
    for comprehensive text handling.
    """
    
    def __init__(
        self,
        text_widget: tk.Text,
        stream_config: Optional[StreamConfig] = None
    ):
        """
        Initialize the streaming text manager.
        
        Args:
            text_widget: The Tkinter Text widget to manage
            stream_config: Configuration for streaming
        """
        self.text_widget = text_widget
        self.stream_handler = StreamingTextHandler(
            text_widget,
            config=stream_config
        )
        self.incremental_updater = IncrementalTextUpdater(text_widget)
        self._accumulated_text = ""
    
    def start_streaming(
        self,
        clear_existing: bool = True,
        on_progress: Optional[Callable[[int, int], None]] = None,
        on_complete: Optional[Callable[[StreamMetrics], None]] = None
    ) -> bool:
        """
        Start a streaming session.
        
        Args:
            clear_existing: Clear existing text
            on_progress: Progress callback
            on_complete: Completion callback
            
        Returns:
            True if started successfully
        """
        self._accumulated_text = ""
        self.stream_handler.on_progress = on_progress
        self.stream_handler.on_complete = on_complete
        return self.stream_handler.start_stream(clear_existing)
    
    def add_stream_chunk(self, chunk: str) -> bool:
        """Add a chunk to the stream."""
        self._accumulated_text += chunk
        return self.stream_handler.add_chunk(chunk)
    
    def end_streaming(self) -> StreamMetrics:
        """End the streaming session."""
        return self.stream_handler.end_stream()
    
    def get_accumulated_text(self) -> str:
        """Get all text accumulated during streaming."""
        return self._accumulated_text
    
    def update_text_incrementally(
        self,
        new_text: str,
        preserve_state: bool = True
    ) -> Tuple[int, int]:
        """
        Update text using incremental diff.
        
        Args:
            new_text: New text content
            preserve_state: Preserve cursor and scroll
            
        Returns:
            Tuple of (insertions, deletions)
        """
        return self.incremental_updater.update_text(
            new_text,
            preserve_cursor=preserve_state,
            preserve_scroll=preserve_state
        )
    
    @property
    def is_streaming(self) -> bool:
        """Check if currently streaming."""
        return self.stream_handler.is_streaming
    
    def cancel(self) -> None:
        """Cancel any ongoing operation."""
        self.stream_handler.cancel_stream()


# Convenience function for simple streaming
def stream_text_to_widget(
    text_widget: tk.Text,
    text_generator,
    clear_existing: bool = True,
    on_complete: Optional[Callable[[StreamMetrics], None]] = None
) -> StreamMetrics:
    """
    Stream text from a generator to a widget.
    
    Args:
        text_widget: Target text widget
        text_generator: Generator yielding text chunks
        clear_existing: Clear existing text first
        on_complete: Callback when complete
        
    Returns:
        Streaming metrics
    """
    handler = StreamingTextHandler(
        text_widget,
        on_complete=on_complete
    )
    
    handler.start_stream(clear_existing)
    
    try:
        for chunk in text_generator:
            if not handler.add_chunk(chunk):
                break
    except Exception as e:
        logger.error(f"Error during streaming: {e}")
    
    return handler.end_stream()
