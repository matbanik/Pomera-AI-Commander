"""
Notes Widget Module for Pomera

This module provides a Notes widget that allows saving INPUT/OUTPUT tab content
to a local SQLite database. The UI is modeled after prompt_mini but simplified
to only include Date Created, Date Modified, Title, INPUT, and OUTPUT fields.

Features:
- Save INPUT/OUTPUT tab content as notes
- Full-text search (FTS5) across Title, Input, Output
- Sortable treeview (ID, Created, Modified, Title)
- Send To feature for sending note content back to input tabs
- In-place editing mode
- Text statistics display

Author: Pomera AI Commander
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
import logging
import threading
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple, Generator
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, Future
import os
import re


class NotesWidget:
    """Notes widget for saving and managing INPUT/OUTPUT tab content."""
    
    def __init__(self, parent, logger=None, send_to_input_callback=None, dialog_manager=None):
        """
        Initialize the Notes widget.
        
        Args:
            parent: Parent tkinter widget
            logger: Logger instance for debugging
            send_to_input_callback: Callback function to send content to input tabs
            dialog_manager: DialogManager instance for configurable dialogs
        """
        self.parent = parent
        self.logger = logger or logging.getLogger(__name__)
        self.send_to_input_callback = send_to_input_callback
        self.dialog_manager = dialog_manager
        
        # Database path - use platform-appropriate data directory
        try:
            from core.data_directory import get_database_path
            self.db_path = get_database_path('notes.db')
        except ImportError:
            # Fallback to legacy behavior - same directory as Pomera
            db_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(db_dir, 'notes.db')
        
        # State management
        self.search_debounce_timer: Optional[str] = None
        self.selected_items: List[int] = []
        self.current_item: Optional[int] = None
        self.editing_mode: bool = False
        self.has_unsaved_changes: bool = False
        self.original_data: Optional[Dict] = None
        self.sort_column: Optional[str] = None
        self.sort_direction: Optional[str] = None
        self.note_cache: Dict[int, Tuple] = {}
        
        # Thread pool for cancellable searches
        self.search_executor = ThreadPoolExecutor(max_workers=1)
        self.current_search_future: Optional[Future] = None
        
        # Initialize database
        self.init_database()
        
        # Create UI
        self.create_ui()
        
        # Perform initial search
        self.perform_search(select_first=True)
    
    @contextmanager
    def get_db_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Provide a managed database connection."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            conn.row_factory = sqlite3.Row
            conn.execute('PRAGMA foreign_keys = ON')
            conn.execute('PRAGMA journal_mode=WAL')
            yield conn
        except Exception as e:
            self.logger.error(f"Database connection error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def _sanitize_text(self, text: str) -> str:
        """
        Sanitize text by removing invalid UTF-8 surrogate characters.
        
        Lone surrogates (U+D800 to U+DFFF) are invalid in UTF-8 and cause
        encoding errors when saving to the database. This can happen when
        pasting content from the clipboard that contains malformed data.
        
        Args:
            text: Input text that may contain invalid surrogates
            
        Returns:
            Sanitized text safe for UTF-8 encoding and database storage
        """
        if not text:
            return text
        
        try:
            # This two-step process handles lone surrogates:
            # 1. surrogatepass allows encoding surrogates (normally forbidden in UTF-8)
            # 2. errors='replace' replaces invalid sequences with replacement char
            sanitized = text.encode('utf-8', errors='surrogatepass').decode('utf-8', errors='replace')
            return sanitized
        except Exception:
            # Fallback: manually filter out surrogate characters
            return ''.join(c for c in text if not (0xD800 <= ord(c) <= 0xDFFF))
    
    def init_database(self) -> None:
        """Initialize the SQLite database and Full-Text Search (FTS5) table."""
        try:
            with self.get_db_connection() as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS notes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        Created DATETIME DEFAULT CURRENT_TIMESTAMP,
                        Modified DATETIME DEFAULT CURRENT_TIMESTAMP,
                        Title TEXT(255),
                        Input TEXT,
                        Output TEXT
                    )
                ''')
                
                # Drop legacy triggers and FTS table to ensure schema is correct
                for trigger in ['notes_after_insert', 'notes_after_delete', 'notes_after_update']:
                    conn.execute(f'DROP TRIGGER IF EXISTS {trigger}')
                conn.execute('DROP TABLE IF EXISTS notes_fts')
                
                conn.execute('''
                    CREATE VIRTUAL TABLE notes_fts USING fts5(
                        Title, Input, Output,
                        content='notes',
                        content_rowid='id'
                    )
                ''')
                
                conn.executescript('''
                    CREATE TRIGGER IF NOT EXISTS notes_after_insert AFTER INSERT ON notes BEGIN
                        INSERT INTO notes_fts(rowid, Title, Input, Output)
                        VALUES (new.id, new.Title, new.Input, new.Output);
                    END;
                    CREATE TRIGGER IF NOT EXISTS notes_after_delete AFTER DELETE ON notes BEGIN
                        INSERT INTO notes_fts(notes_fts, rowid, Title, Input, Output)
                        VALUES ('delete', old.id, old.Title, old.Input, old.Output);
                    END;
                    CREATE TRIGGER IF NOT EXISTS notes_after_update AFTER UPDATE ON notes BEGIN
                        INSERT INTO notes_fts(notes_fts, rowid, Title, Input, Output)
                        VALUES ('delete', old.id, old.Title, old.Input, old.Output);
                        INSERT INTO notes_fts(rowid, Title, Input, Output)
                        VALUES (new.id, new.Title, new.Input, new.Output);
                    END;
                ''')
                
                conn.execute('INSERT INTO notes_fts(notes_fts) VALUES("rebuild")')
                conn.commit()
            self.logger.info("Notes database initialized successfully")
        except Exception as e:
            self.logger.error(f"Database initialization error: {e}")
            if self.dialog_manager:
                self.dialog_manager.show_error("Database Error", f"Failed to initialize database: {e}")
            else:
                messagebox.showerror("Database Error", f"Failed to initialize database: {e}", parent=self.parent)
    
    def create_ui(self) -> None:
        """Create the main user interface components."""
        # Search frame
        search_frame = ttk.Frame(self.parent)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        help_btn = ttk.Button(search_frame, text="?", width=3, command=self.show_search_help)
        help_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self.on_search_change)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=80)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        search_btn = ttk.Button(search_frame, text="Search", command=lambda: self.perform_search())
        search_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Main frame with paned window
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        try:
            self.paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL, sashwidth=8, sashrelief=tk.RAISED)
        except tk.TclError:
            self.paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left frame - treeview
        left_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(left_frame, weight=7)
        
        columns = ('ID', 'Created', 'Modified', 'Title')
        self.tree = ttk.Treeview(left_frame, columns=columns, show='headings', selectmode='extended')
        
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
        
        self.tree.column('ID', width=40, minwidth=30, stretch=False)
        self.tree.column('Created', width=120, minwidth=100, stretch=False)
        self.tree.column('Modified', width=120, minwidth=100, stretch=False)
        self.tree.column('Title', width=200, minwidth=120)
        
        tree_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.tree.bind('<Double-1>', self.on_tree_double_click)
        
        # Right frame - detail view
        right_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(right_frame, weight=3)
        
        # Button frame
        self.btn_frame = ttk.Frame(right_frame)
        self.btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.new_btn = ttk.Button(self.btn_frame, text="New Note", command=self.new_note)
        self.duplicate_btn = ttk.Button(self.btn_frame, text="Duplicate", command=self.duplicate_note)
        self.change_btn = ttk.Button(self.btn_frame, text="Change", command=self.change_note)
        self.delete_btn = ttk.Button(self.btn_frame, text="Delete", command=self.delete_notes)
        self.save_btn = ttk.Button(self.btn_frame, text="Save", command=self.save_edits)
        self.cancel_btn = ttk.Button(self.btn_frame, text="Cancel", command=self.cancel_edits)
        
        self.update_action_buttons()
        
        # Display frame
        display_frame = ttk.Frame(right_frame)
        display_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_item_display(display_frame)
        
        # Status bar
        self.status_bar = ttk.Label(self.parent, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
    
    def create_item_display(self, parent: ttk.Frame) -> None:
        """Create the widgets for displaying a single note item."""
        # Date frame
        date_frame = ttk.Frame(parent)
        date_frame.pack(fill=tk.X, pady=(0, 5))
        self.created_label = ttk.Label(date_frame, text="Created: ", foreground="green")
        self.created_label.pack(side=tk.LEFT)
        self.modified_label = ttk.Label(date_frame, text="Modified: ", foreground="blue")
        self.modified_label.pack(side=tk.RIGHT)
        
        # Title frame
        self.title_frame = ttk.Frame(parent)
        self.title_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(self.title_frame, text="Title:").pack(side=tk.LEFT)
        self.title_display = ttk.Label(self.title_frame, text="", font=('TkDefaultFont', 9, 'bold'))
        self.title_display.pack(side=tk.LEFT, padx=(5, 0))
        
        # INPUT section
        input_label_frame = ttk.Frame(parent)
        input_label_frame.pack(fill=tk.X, pady=(0, 2))
        ttk.Label(input_label_frame, text="INPUT:", font=('TkDefaultFont', 9, 'bold')).pack(side=tk.LEFT)
        
        # Send To dropdown for INPUT
        self.input_send_var = tk.StringVar(value="Send To")
        self.input_send_menu_btn = ttk.Menubutton(input_label_frame, textvariable=self.input_send_var, direction="below")
        self.input_send_menu_btn.pack(side=tk.RIGHT, padx=(5, 0))
        self.input_send_dropdown = tk.Menu(self.input_send_menu_btn, tearoff=0)
        self.input_send_menu_btn.config(menu=self.input_send_dropdown)
        self._build_send_to_menu(self.input_send_dropdown, "input")
        
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        line_frame = ttk.Frame(input_frame)
        line_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.input_line_numbers = tk.Text(line_frame, width=4, padx=3, takefocus=0, border=0, state='disabled', wrap='none')
        self.input_line_numbers.pack(fill=tk.Y, expand=True)
        
        text_frame = ttk.Frame(input_frame)
        text_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.input_display = tk.Text(text_frame, wrap=tk.WORD, state='disabled', undo=True, maxundo=50)
        input_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        self.input_display.config(yscrollcommand=lambda *args: self.sync_scroll(input_scrollbar, self.input_line_numbers, *args))
        input_scrollbar.config(command=lambda *args: self.sync_scroll_command(self.input_display, self.input_line_numbers, *args))
        self.input_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        input_status_frame = ttk.Frame(parent)
        input_status_frame.pack(fill=tk.X, pady=(0, 5))
        self.input_status_label = ttk.Label(input_status_frame, text="Char: 0 | Word: 0 | Line: 0")
        self.input_status_label.pack(side=tk.LEFT)
        
        # OUTPUT section
        output_label_frame = ttk.Frame(parent)
        output_label_frame.pack(fill=tk.X, pady=(0, 2))
        ttk.Label(output_label_frame, text="OUTPUT:", font=('TkDefaultFont', 9, 'bold')).pack(side=tk.LEFT)
        
        # Send To dropdown for OUTPUT
        self.output_send_var = tk.StringVar(value="Send To")
        self.output_send_menu_btn = ttk.Menubutton(output_label_frame, textvariable=self.output_send_var, direction="below")
        self.output_send_menu_btn.pack(side=tk.RIGHT, padx=(5, 0))
        self.output_send_dropdown = tk.Menu(self.output_send_menu_btn, tearoff=0)
        self.output_send_menu_btn.config(menu=self.output_send_dropdown)
        self._build_send_to_menu(self.output_send_dropdown, "output")
        
        output_frame = ttk.Frame(parent)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        line_frame = ttk.Frame(output_frame)
        line_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.output_line_numbers = tk.Text(line_frame, width=4, padx=3, takefocus=0, border=0, state='disabled', wrap='none')
        self.output_line_numbers.pack(fill=tk.Y, expand=True)
        
        text_frame = ttk.Frame(output_frame)
        text_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.output_display = tk.Text(text_frame, wrap=tk.WORD, state='disabled', undo=True, maxundo=50)
        output_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        self.output_display.config(yscrollcommand=lambda *args: self.sync_scroll(output_scrollbar, self.output_line_numbers, *args))
        output_scrollbar.config(command=lambda *args: self.sync_scroll_command(self.output_display, self.output_line_numbers, *args))
        self.output_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        output_status_frame = ttk.Frame(parent)
        output_status_frame.pack(fill=tk.X, pady=(0, 5))
        self.output_status_label = ttk.Label(output_status_frame, text="Char: 0 | Word: 0 | Line: 0")
        self.output_status_label.pack(side=tk.LEFT)
    
    def _build_send_to_menu(self, menu: tk.Menu, content_type: str) -> None:
        """Build the Send To dropdown menu with Tab 1-7 options."""
        menu.delete(0, tk.END)
        for i in range(7):
            # Use a factory function to properly capture the variables
            def make_command(tab_idx, content_t):
                return lambda: self._send_to_input_tab(tab_idx, content_t)
            menu.add_command(
                label=f"Tab {i+1}",
                command=make_command(i, content_type)
            )
    
    def _send_to_input_tab(self, tab_index: int, content_type: str) -> None:
        """Send note content to a specific input tab."""
        if not self.send_to_input_callback:
            if self.dialog_manager:
                self.dialog_manager.show_warning("Warning", "Send to Input functionality is not available.")
            else:
                messagebox.showwarning("Warning", "Send to Input functionality is not available.", parent=self.parent)
            return
        
        # Get content based on type - ONLY get the specified type
        content = ""
        if content_type == "input":
            content = self.input_display.get("1.0", tk.END).strip()
            self.logger.debug(f"Sending INPUT content to tab {tab_index + 1} (length: {len(content)})")
        elif content_type == "output":
            content = self.output_display.get("1.0", tk.END).strip()
            self.logger.debug(f"Sending OUTPUT content to tab {tab_index + 1} (length: {len(content)})")
        else:
            self.logger.warning(f"Unknown content_type: {content_type}")
            return
        
        if not content:
            if self.dialog_manager:
                self.dialog_manager.show_warning("Warning", f"No {content_type.upper()} content available to send.")
            else:
                messagebox.showwarning("Warning", f"No {content_type.upper()} content available to send.", parent=self.parent)
            return
        
        # Send to input tab using callback - ONLY the selected content
        self.send_to_input_callback(tab_index, content)
        
        # Show success message
        content_name = content_type.upper()
        if self.dialog_manager:
            self.dialog_manager.show_info("Success", f"{content_name} content sent to Input Tab {tab_index + 1}")
        else:
            messagebox.showinfo("Success", f"{content_name} content sent to Input Tab {tab_index + 1}", parent=self.parent)
        self.logger.info(f"{content_name} content sent to input tab {tab_index + 1}")
    
    def sync_scroll(self, scrollbar: ttk.Scrollbar, line_numbers: tk.Text, *args: str) -> None:
        """Synchronize scrolling between a text widget and its line numbers."""
        scrollbar.set(*args)
        if len(args) >= 2:
            top = float(args[0])
            line_numbers.yview_moveto(top)
    
    def sync_scroll_command(self, main_text: tk.Text, line_numbers: tk.Text, *args: str) -> None:
        """Handle scrollbar commands to sync two text widgets."""
        main_text.yview(*args)
        line_numbers.yview(*args)
    
    def on_search_change(self, *args: Any) -> None:
        """Handle search input changes with debouncing."""
        if self.search_debounce_timer:
            self.parent.after_cancel(self.search_debounce_timer)
        self.search_debounce_timer = self.parent.after(300, lambda: self.perform_search())
    
    def perform_search(self, select_item_id: Optional[int] = None, select_first: bool = False) -> None:
        """Perform a cancellable search using a thread pool."""
        search_term = self.search_var.get().strip()
        
        if self.current_search_future and not self.current_search_future.done():
            self.current_search_future.cancel()
        
        if hasattr(self, 'status_bar'):
            self.status_bar.config(text="Searching...")
            self.parent.config(cursor="wait")
            self.parent.update_idletasks()
        
        def search_worker(term: str) -> List[Tuple]:
            try:
                with self.get_db_connection() as conn:
                    if term:
                        cursor = conn.execute('''
                            SELECT n.id, n.Created, n.Modified, n.Title, n.Input, n.Output
                            FROM notes n JOIN notes_fts fts ON n.id = fts.rowid
                            WHERE notes_fts MATCH ? ORDER BY rank
                        ''', (term + '*',))
                    else:
                        cursor = conn.execute('''
                            SELECT id, Created, Modified, Title, Input, Output
                            FROM notes ORDER BY Modified DESC
                        ''')
                    return cursor.fetchall()
            except Exception as e:
                self.logger.error(f"Search worker error: {e}")
                return []
        
        self.current_search_future = self.search_executor.submit(search_worker, search_term)
        self.current_search_future.add_done_callback(
            lambda future: self._safe_after(lambda: self._handle_search_results(future, select_item_id, select_first))
        )
    
    def _safe_after(self, callback, delay: int = 0) -> None:
        """Schedule a callback only if the parent widget still exists."""
        try:
            if self.parent.winfo_exists():
                self.parent.after(delay, callback)
        except Exception:
            # Widget was destroyed, ignore
            pass
    
    def _handle_search_results(self, future: Future, select_item_id: Optional[int] = None, select_first: bool = False) -> None:
        """Process search results in the main UI thread."""
        if future.cancelled():
            return
        
        # Check if widget still exists before updating
        try:
            if not self.parent.winfo_exists():
                return
        except Exception:
            return
        
        if hasattr(self, 'status_bar'):
            try:
                self.status_bar.config(text="Ready")
                self.parent.config(cursor="")
            except Exception:
                # Widget was destroyed, ignore
                return
        
        error = future.exception()
        if error:
            self.logger.error(f"Search failed: {error}")
            if self.dialog_manager:
                self.dialog_manager.show_error("Search Error", f"Search failed: {error}")
            else:
                messagebox.showerror("Search Error", f"Search failed: {error}", parent=self.parent)
            self.search_results = []
        else:
            self.search_results = future.result()
        
        self.refresh_search_view()
        
        if select_item_id:
            self._safe_after_idle(lambda: self._select_item_in_tree(select_item_id))
        elif select_first:
            self._safe_after_idle(self._select_first_item_in_tree)
    
    def _safe_after_idle(self, callback) -> None:
        """Schedule an idle callback only if the parent widget still exists."""
        try:
            if self.parent.winfo_exists():
                self.parent.after_idle(callback)
        except Exception:
            # Widget was destroyed, ignore
            pass
    
    def sort_by_column(self, column: str) -> None:
        """Sort the treeview by a specified column, cycling through directions."""
        if self.sort_column == column:
            if self.sort_direction == 'asc':
                self.sort_direction = 'desc'
            else:
                self.sort_column = None
                self.sort_direction = None
        else:
            self.sort_column = column
            self.sort_direction = 'asc'
        
        self.update_column_headers()
        self.refresh_search_view()
    
    def update_column_headers(self) -> None:
        """Update treeview column headers with sort direction indicators."""
        for col in ['ID', 'Created', 'Modified', 'Title']:
            text = col
            if col == self.sort_column:
                if self.sort_direction == 'asc':
                    text += " ↑"
                elif self.sort_direction == 'desc':
                    text += " ↓"
            self.tree.heading(col, text=text)
    
    def refresh_search_view(self) -> None:
        """Refresh the search results treeview, applying sorting if active."""
        self.tree.unbind('<<TreeviewSelect>>')
        try:
            self.tree.delete(*self.tree.get_children())
            
            display_results = getattr(self, 'search_results', [])
            
            if self.sort_column and self.sort_direction and display_results:
                col_index = self.tree['columns'].index(self.sort_column)
                reverse = (self.sort_direction == 'desc')
                
                def sort_key(row):
                    val = row[col_index]
                    if self.sort_column == 'ID':
                        return int(val) if val else 0
                    return (val or '').lower()
                
                display_results = sorted(display_results, key=sort_key, reverse=reverse)
            
            if display_results:
                for row in display_results:
                    self.tree.insert('', 'end', values=(
                        row['id'],
                        self.format_datetime(row['Created']),
                        self.format_datetime(row['Modified']),
                        (row['Title'] or '')[:50] + ("..." if len(row['Title'] or '') > 50 else "")
                    ))
        finally:
            self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
    
    def format_datetime(self, dt_str: Optional[str]) -> str:
        """Format a datetime string for display."""
        if not dt_str:
            return ""
        try:
            dt_str = dt_str.replace('Z', '+00:00')
            dt = datetime.fromisoformat(dt_str)
            return dt.strftime('%Y-%m-%d %I:%M %p')
        except (ValueError, TypeError):
            return dt_str
    
    def on_tree_select(self, event: Optional[tk.Event]) -> None:
        """Handle selection changes in the results treeview."""
        if self.editing_mode:
            if self.current_item:
                self._select_item_in_tree(self.current_item)
            return
        
        selection = self.tree.selection()
        self.selected_items = [self.tree.item(item)['values'][0] for item in selection]
        
        if len(self.selected_items) == 1:
            self.current_item = self.selected_items[0]
            self.update_item_display()
        else:
            self.current_item = None
            self.clear_item_display()
        
        self.update_action_buttons()
    
    def on_tree_double_click(self, event: tk.Event) -> None:
        """Handle double-click on a tree item to enter edit mode."""
        if self.current_item:
            self.change_note()
    
    def _select_item_in_tree(self, item_id: int) -> None:
        """Select an item in the tree by its ID."""
        for item in self.tree.get_children():
            if str(self.tree.item(item)['values'][0]) == str(item_id):
                self.tree.selection_set(item)
                self.tree.focus(item)
                self.tree.see(item)
                self.on_tree_select(None)
                return
        self._select_first_item_in_tree()
    
    def _select_first_item_in_tree(self) -> None:
        """Select the first item in the tree."""
        children = self.tree.get_children()
        if children:
            self.tree.selection_set(children[0])
            self.tree.focus(children[0])
            self.tree.see(children[0])
            self.on_tree_select(None)
    
    def update_item_display(self, force_refresh: bool = False) -> None:
        """Update the item display panel, using a cache for performance."""
        if not self.current_item:
            return
        
        try:
            row = self.note_cache.get(self.current_item) if not force_refresh else None
            if row:
                self.logger.debug(f"Using cached data for item {self.current_item}")
            else:
                with self.get_db_connection() as conn:
                    row = conn.execute('SELECT * FROM notes WHERE id = ?', (self.current_item,)).fetchone()
                    if not row:
                        return
                    
                    if len(self.note_cache) > 50:
                        del self.note_cache[next(iter(self.note_cache))]
                    
                    self.note_cache[self.current_item] = row
                    self.logger.debug(f"Fetched and cached data for item {self.current_item}")
            
            self.created_label.config(text=f"Created: {self.format_datetime(row['Created'])}")
            self.modified_label.config(text=f"Modified: {self.format_datetime(row['Modified'])}")
            self.title_display.config(text=row['Title'] or "")
            
            for widget in [self.input_display, self.output_display]:
                widget.config(state='normal')
                widget.delete(1.0, tk.END)
            
            if row['Input']:
                self.input_display.insert(1.0, row['Input'])
            if row['Output']:
                self.output_display.insert(1.0, row['Output'])
            
            for widget in [self.input_display, self.output_display]:
                widget.config(state='disabled')
            
            self.update_line_numbers(row['Input'] or "", self.input_line_numbers)
            self.update_line_numbers(row['Output'] or "", self.output_line_numbers)
            self.update_status(row['Input'] or "", self.input_status_label)
            self.update_status(row['Output'] or "", self.output_status_label)
            
        except Exception as e:
            self.logger.error(f"Error updating item display: {e}")
    
    def clear_item_display(self) -> None:
        """Clear all fields in the item display panel."""
        self.created_label.config(text="Created: ")
        self.modified_label.config(text="Modified: ")
        self.title_display.config(text="")
        
        for widget in [self.input_display, self.output_display, self.input_line_numbers, self.output_line_numbers]:
            widget.config(state='normal')
            widget.delete(1.0, tk.END)
            widget.config(state='disabled')
        
        self.input_status_label.config(text="Char: 0 | Word: 0 | Line: 0")
        self.output_status_label.config(text="Char: 0 | Word: 0 | Line: 0")
    
    def update_line_numbers(self, text: str, line_numbers_widget: tk.Text) -> None:
        """Update the line numbers displayed next to the text."""
        line_numbers_widget.config(state='normal')
        line_numbers_widget.delete(1.0, tk.END)
        if text:
            line_count = text.count('\n') + 1
            line_nums = '\n'.join(map(str, range(1, line_count + 1)))
            line_numbers_widget.insert(1.0, line_nums)
        line_numbers_widget.config(state='disabled')
    
    def _get_text_statistics(self, text: str) -> Dict[str, int]:
        """Calculate statistics for a given block of text."""
        if not text:
            return {'char_count': 0, 'word_count': 0, 'line_count': 0}
        
        char_count = len(text)
        word_count = len(text.split())
        line_count = text.count('\n') + 1
        
        return {'char_count': char_count, 'word_count': word_count, 'line_count': line_count}
    
    def update_status(self, text: str, status_label: ttk.Label) -> None:
        """Update the status label with text statistics."""
        stats = self._get_text_statistics(text)
        status_label.config(
            text=f"Char: {stats['char_count']} | Word: {stats['word_count']} | Line: {stats['line_count']}"
        )
    
    def show_search_help(self) -> None:
        """Show a dialog with FTS5 search syntax help."""
        help_text = """Search Tips:
• Use simple keywords to search all fields.
• Use "quotes" for exact phrases: "machine learning".
• Use AND/OR/NOT operators: python AND tutorial.
• Use wildcards: web* (matches web, website, etc.).
• Search specific columns: Title:refactor OR Input:code.
• Leave empty to show all records."""
        if self.dialog_manager:
            self.dialog_manager.show_info("Search Help", help_text, parent=self.parent)
        else:
            messagebox.showinfo("Search Help", help_text, parent=self.parent)
        
        # Return focus to Notes window after dialog closes
        try:
            self.parent.focus_force()
            self.search_entry.focus_set()
        except Exception:
            pass  # Widget may not exist
    
    def new_note(self) -> None:
        """Create a new note."""
        self.current_item = None
        self.clear_item_display()
        self.enter_editing_mode()
    
    def duplicate_note(self) -> None:
        """Duplicate the currently selected note."""
        if self.current_item:
            try:
                with self.get_db_connection() as conn:
                    row = conn.execute('SELECT * FROM notes WHERE id = ?', (self.current_item,)).fetchone()
                    if row:
                        now = datetime.now().isoformat()
                        # Sanitize text to prevent UTF-8 surrogate errors
                        conn.execute('''
                            INSERT INTO notes (Created, Modified, Title, Input, Output)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (now, now, self._sanitize_text(row['Title']), 
                              self._sanitize_text(row['Input']), self._sanitize_text(row['Output'])))
                        conn.commit()
                        self.perform_search(select_first=True)
                        self.logger.info(f"Duplicated note {self.current_item}")
            except Exception as e:
                self.logger.error(f"Error duplicating note: {e}")
                if self.dialog_manager:
                    self.dialog_manager.show_error("Error", f"Failed to duplicate note: {e}")
                else:
                    messagebox.showerror("Error", f"Failed to duplicate note: {e}", parent=self.parent)
    
    def change_note(self) -> None:
        """Enter in-place editing mode for the selected note."""
        if self.current_item and not self.editing_mode:
            self.enter_editing_mode()
    
    def delete_notes(self) -> None:
        """Delete one or more selected notes."""
        if not self.selected_items:
            return
        
        count = len(self.selected_items)
        # Ensure dialog is modal to the Notes widget window
        if self.dialog_manager:
            confirmed = self.dialog_manager.ask_yes_no("Confirm Delete", f"Delete {count} item(s)? This cannot be undone.", "confirmation", parent=self.parent)
        else:
            confirmed = messagebox.askyesno("Confirm Delete", f"Delete {count} item(s)? This cannot be undone.", parent=self.parent)
        
        if confirmed:
            try:
                with self.get_db_connection() as conn:
                    item_ids = tuple(self.selected_items)
                    conn.execute(f"DELETE FROM notes WHERE id IN ({','.join('?' for _ in item_ids)})", item_ids)
                    for item_id in item_ids:
                        if item_id in self.note_cache:
                            del self.note_cache[item_id]
                    conn.commit()
                
                self.current_item = None
                self.selected_items = []
                self.clear_item_display()
                self.perform_search(select_first=True)
                self.logger.info(f"Deleted {count} items")
            except Exception as e:
                self.logger.error(f"Delete error: {e}")
                if self.dialog_manager:
                    self.dialog_manager.show_error("Delete Error", f"Failed to delete: {e}")
                else:
                    messagebox.showerror("Delete Error", f"Failed to delete: {e}", parent=self.parent)
    
    def update_action_buttons(self) -> None:
        """Centralized state machine for managing action buttons."""
        for btn in [self.new_btn, self.duplicate_btn, self.change_btn, self.delete_btn, self.save_btn, self.cancel_btn]:
            btn.pack_forget()
        
        if self.editing_mode:
            self.save_btn.pack(side=tk.LEFT, padx=(0, 5))
            self.cancel_btn.pack(side=tk.LEFT, padx=5)
        else:
            self.new_btn.pack(side=tk.LEFT, padx=(0, 5))
            
            num_selected = len(self.selected_items)
            
            self.duplicate_btn.config(state='normal' if num_selected == 1 else 'disabled')
            self.change_btn.config(state='normal' if num_selected == 1 else 'disabled')
            self.duplicate_btn.pack(side=tk.LEFT, padx=5)
            self.change_btn.pack(side=tk.LEFT, padx=5)
            
            self.delete_btn.config(state='normal' if num_selected > 0 else 'disabled')
            self.delete_btn.config(text=f"Delete ({num_selected})" if num_selected > 1 else "Delete")
            self.delete_btn.pack(side=tk.LEFT, padx=(20, 0))
    
    def save_edits(self) -> None:
        """Save in-place edits to the database."""
        if not self.editing_mode:
            return
        
        try:
            # Sanitize text to prevent UTF-8 surrogate errors from clipboard paste
            title = self._sanitize_text(self.title_entry.get() if hasattr(self, 'title_entry') else "")
            input_content = self._sanitize_text(self.input_display.get(1.0, tk.END).strip())
            output_content = self._sanitize_text(self.output_display.get(1.0, tk.END).strip())
            
            now = datetime.now().isoformat()
            
            with self.get_db_connection() as conn:
                if self.current_item:
                    # Update existing note
                    conn.execute('''
                        UPDATE notes SET Modified = ?, Title = ?, Input = ?, Output = ?
                        WHERE id = ?
                    ''', (now, title, input_content, output_content, self.current_item))
                    if self.current_item in self.note_cache:
                        del self.note_cache[self.current_item]
                else:
                    # Create new note
                    cursor = conn.execute('''
                        INSERT INTO notes (Created, Modified, Title, Input, Output)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (now, now, title, input_content, output_content))
                    self.current_item = cursor.lastrowid
                conn.commit()
            
            self.exit_editing_mode()
            self.perform_search(select_item_id=self.current_item)
            self.logger.info(f"Saved note {self.current_item}")
        except Exception as e:
            self.logger.error(f"Error saving edits: {e}")
            if self.dialog_manager:
                self.dialog_manager.show_error("Save Error", f"Failed to save changes: {e}")
            else:
                messagebox.showerror("Save Error", f"Failed to save changes: {e}", parent=self.parent)
    
    def cancel_edits(self) -> None:
        """Cancel in-place editing and restore original content."""
        if self.editing_mode:
            if self.has_unsaved_changes:
                if self.dialog_manager:
                    result = self.dialog_manager.ask_yes_no("Unsaved Changes", 
                        "You have unsaved changes. Are you sure you want to cancel?", "confirmation", parent=self.parent)
                else:
                    result = messagebox.askyesno("Unsaved Changes", 
                        "You have unsaved changes. Are you sure you want to cancel?", parent=self.parent)
                if not result:
                    return
            self.exit_editing_mode()
            if self.current_item:
                self.update_item_display(force_refresh=True)
            else:
                self.clear_item_display()
    
    def enter_editing_mode(self) -> None:
        """Switch the UI to in-place editing mode."""
        if self.editing_mode:
            return
        
        try:
            if self.current_item:
                with self.get_db_connection() as conn:
                    row = conn.execute('SELECT * FROM notes WHERE id = ?', (self.current_item,)).fetchone()
                    if not row:
                        return
                
                self.original_data = {
                    'Title': row['Title'] or "",
                    'Input': row['Input'] or "",
                    'Output': row['Output'] or ""
                }
            else:
                self.original_data = {'Title': "", 'Input': "", 'Output': ""}
            
            self.editing_mode = True
            self.has_unsaved_changes = False
            self.update_action_buttons()
            
            self.tree.configure(selectmode='none')
            if hasattr(self, 'status_bar'):
                self.status_bar.config(text="EDITING MODE - Selection locked")
            
            for widget in [self.input_display, self.output_display]:
                widget.config(state='normal')
            
            # Replace title display with entry
            self.title_display.pack_forget()
            self.title_entry = ttk.Entry(self.title_frame, font=('TkDefaultFont', 9, 'bold'))
            if self.current_item:
                self.title_entry.insert(0, self.original_data['Title'])
            self.title_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
            self.title_entry.bind('<KeyRelease>', self.on_edit_change)
            
            # Bind change events to text widgets
            for widget in [self.input_display, self.output_display]:
                widget.bind('<KeyRelease>', self.on_edit_change)
                widget.bind('<Button-1>', self.on_edit_change)
            
        except Exception as e:
            self.logger.error(f"Error entering editing mode: {e}")
            if self.dialog_manager:
                self.dialog_manager.show_error("Edit Error", f"Failed to enter editing mode: {e}")
            else:
                messagebox.showerror("Edit Error", f"Failed to enter editing mode: {e}", parent=self.parent)
            self.exit_editing_mode()
    
    def on_edit_change(self, event=None) -> None:
        """Track changes in editing mode and update status bar."""
        if not self.editing_mode or not self.original_data:
            return
        
        current_data = {
            'Title': self.title_entry.get() if hasattr(self, 'title_entry') else "",
            'Input': self.input_display.get(1.0, tk.END).rstrip('\n'),
            'Output': self.output_display.get(1.0, tk.END).rstrip('\n')
        }
        
        has_changes = any(current_data[key] != self.original_data[key] for key in current_data)
        
        if has_changes != self.has_unsaved_changes:
            self.has_unsaved_changes = has_changes
            if hasattr(self, 'status_bar'):
                if has_changes:
                    self.status_bar.config(text="EDITING MODE - NOTE NEEDS TO BE SAVED", font=('TkDefaultFont', 9, 'bold'))
                else:
                    self.status_bar.config(text="EDITING MODE - Selection locked", font=('TkDefaultFont', 9, 'normal'))
        
        # Update statistics in real-time
        if hasattr(self, 'input_display'):
            input_text = self.input_display.get(1.0, tk.END)
            self.update_line_numbers(input_text, self.input_line_numbers)
            self.update_status(input_text, self.input_status_label)
        
        if hasattr(self, 'output_display'):
            output_text = self.output_display.get(1.0, tk.END)
            self.update_line_numbers(output_text, self.output_line_numbers)
            self.update_status(output_text, self.output_status_label)
    
    def exit_editing_mode(self) -> None:
        """Exit editing mode and restore the view-only UI."""
        if not self.editing_mode:
            return
        
        self.editing_mode = False
        self.has_unsaved_changes = False
        self.original_data = None
        
        self.tree.configure(selectmode='extended')
        
        self.update_action_buttons()
        if hasattr(self, 'status_bar'):
            self.status_bar.config(text="Ready", font=('TkDefaultFont', 9, 'normal'))
        
        for widget in [self.input_display, self.output_display]:
            widget.config(state='disabled')
            widget.unbind('<KeyRelease>')
            widget.unbind('<Button-1>')
        
        if hasattr(self, 'title_entry'):
            self.title_entry.destroy()
            delattr(self, 'title_entry')
        self.title_display.pack(side=tk.LEFT, padx=(5, 0))
    
    def save_note(self, title: str, input_content: str, output_content: str) -> Optional[int]:
        """
        Save a new note to the database.
        
        Args:
            title: Note title
            input_content: INPUT tab content
            output_content: OUTPUT tab content
            
        Returns:
            The ID of the created note, or None on error
        """
        try:
            # Sanitize text to prevent UTF-8 surrogate errors
            sanitized_title = self._sanitize_text(title)
            sanitized_input = self._sanitize_text(input_content)
            sanitized_output = self._sanitize_text(output_content)
            
            now = datetime.now().isoformat()
            with self.get_db_connection() as conn:
                cursor = conn.execute('''
                    INSERT INTO notes (Created, Modified, Title, Input, Output)
                    VALUES (?, ?, ?, ?, ?)
                ''', (now, now, sanitized_title, sanitized_input, sanitized_output))
                note_id = cursor.lastrowid
                conn.commit()
            
            self.logger.info(f"Saved new note with ID {note_id}")
            return note_id
        except Exception as e:
            self.logger.error(f"Error saving note: {e}")
            return None
