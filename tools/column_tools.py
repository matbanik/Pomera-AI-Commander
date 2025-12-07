"""
Column/CSV Tools Module - Column manipulation utilities

This module provides column and CSV manipulation functionality
for the Pomera AI Commander application.

Features:
- Extract Column: Extract specific column by index
- Reorder Columns: Rearrange column order
- Delete Column: Remove column by index
- Transpose: Swap rows and columns
- CSV to Fixed Width: Convert to fixed-width format
"""

import tkinter as tk
from tkinter import ttk
import csv
import io


class ColumnToolsProcessor:
    """Column tools processor with various column manipulation capabilities."""
    
    @staticmethod
    def parse_csv(text, delimiter=",", quote_char='"'):
        """Parse CSV text into rows."""
        reader = csv.reader(io.StringIO(text), delimiter=delimiter, quotechar=quote_char)
        return list(reader)
    
    @staticmethod
    def format_csv(rows, delimiter=",", quote_char='"'):
        """Format rows back to CSV text."""
        output = io.StringIO()
        writer = csv.writer(output, delimiter=delimiter, quotechar=quote_char, quoting=csv.QUOTE_MINIMAL)
        writer.writerows(rows)
        return output.getvalue().strip()
    
    @staticmethod
    def extract_column(text, column_index, delimiter=",", quote_char='"'):
        """Extract a specific column by index (0-based)."""
        rows = ColumnToolsProcessor.parse_csv(text, delimiter, quote_char)
        result = []
        
        for row in rows:
            if column_index < len(row):
                result.append(row[column_index])
            else:
                result.append("")
        
        return '\n'.join(result)
    
    @staticmethod
    def reorder_columns(text, order, delimiter=",", quote_char='"'):
        """Reorder columns based on specified order (e.g., "2,0,1")."""
        rows = ColumnToolsProcessor.parse_csv(text, delimiter, quote_char)
        
        try:
            indices = [int(i.strip()) for i in order.split(',')]
        except ValueError:
            return "Error: Invalid column order format. Use comma-separated indices (e.g., '2,0,1')"
        
        result = []
        for row in rows:
            new_row = []
            for idx in indices:
                if idx < len(row):
                    new_row.append(row[idx])
                else:
                    new_row.append("")
            result.append(new_row)
        
        return ColumnToolsProcessor.format_csv(result, delimiter, quote_char)
    
    @staticmethod
    def delete_column(text, column_index, delimiter=",", quote_char='"'):
        """Delete a column by index."""
        rows = ColumnToolsProcessor.parse_csv(text, delimiter, quote_char)
        result = []
        
        for row in rows:
            new_row = [cell for i, cell in enumerate(row) if i != column_index]
            result.append(new_row)
        
        return ColumnToolsProcessor.format_csv(result, delimiter, quote_char)
    
    @staticmethod
    def add_column(text, column_index, value="", delimiter=",", quote_char='"'):
        """Add a new column at specified index."""
        rows = ColumnToolsProcessor.parse_csv(text, delimiter, quote_char)
        result = []
        
        for row in rows:
            new_row = list(row)
            # Ensure row is long enough
            while len(new_row) < column_index:
                new_row.append("")
            new_row.insert(column_index, value)
            result.append(new_row)
        
        return ColumnToolsProcessor.format_csv(result, delimiter, quote_char)
    
    @staticmethod
    def transpose(text, delimiter=",", quote_char='"'):
        """Transpose rows and columns."""
        rows = ColumnToolsProcessor.parse_csv(text, delimiter, quote_char)
        
        if not rows:
            return text
        
        # Find max columns
        max_cols = max(len(row) for row in rows)
        
        # Pad rows to same length
        padded = [row + [''] * (max_cols - len(row)) for row in rows]
        
        # Transpose
        transposed = list(map(list, zip(*padded)))
        
        return ColumnToolsProcessor.format_csv(transposed, delimiter, quote_char)
    
    @staticmethod
    def to_fixed_width(text, delimiter=",", quote_char='"', padding=2):
        """Convert CSV to fixed-width format."""
        rows = ColumnToolsProcessor.parse_csv(text, delimiter, quote_char)
        
        if not rows:
            return text
        
        # Find max width for each column
        max_cols = max(len(row) for row in rows)
        col_widths = [0] * max_cols
        
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Format with fixed widths
        result = []
        for row in rows:
            formatted_cells = []
            for i in range(max_cols):
                cell = row[i] if i < len(row) else ""
                formatted_cells.append(str(cell).ljust(col_widths[i] + padding))
            result.append(''.join(formatted_cells).rstrip())
        
        return '\n'.join(result)
    
    @staticmethod
    def get_column_count(text, delimiter=",", quote_char='"'):
        """Get the number of columns in the data."""
        rows = ColumnToolsProcessor.parse_csv(text, delimiter, quote_char)
        if rows:
            return max(len(row) for row in rows)
        return 0


class ColumnToolsWidget(ttk.Frame):
    """Tabbed interface widget for column tools."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.processor = ColumnToolsProcessor()
        
        self.delimiter = tk.StringVar(value=",")
        self.quote_char = tk.StringVar(value='"')
        self.column_index = tk.IntVar(value=0)
        self.column_order = tk.StringVar(value="")
        self.new_column_value = tk.StringVar(value="")
        
        self.create_widgets()
        self.load_settings()
    
    def create_widgets(self):
        """Creates the tabbed interface for column tools."""
        # Common settings at top
        settings_frame = ttk.LabelFrame(self, text="CSV Settings", padding=5)
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="Delimiter:").pack(side=tk.LEFT)
        delimiter_combo = ttk.Combobox(settings_frame, textvariable=self.delimiter,
                                       values=[",", ";", "\t", "|", " "], width=3)
        delimiter_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(settings_frame, text="Quote:").pack(side=tk.LEFT, padx=(10, 0))
        quote_combo = ttk.Combobox(settings_frame, textvariable=self.quote_char,
                                   values=['"', "'", ""], width=3)
        quote_combo.pack(side=tk.LEFT, padx=5)
        
        # Notebook for operations
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.create_extract_tab()
        self.create_reorder_tab()
        self.create_delete_tab()
        self.create_transpose_tab()
        self.create_fixed_width_tab()
    
    def create_extract_tab(self):
        """Creates the Extract Column tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Extract")
        
        idx_frame = ttk.Frame(frame)
        idx_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Label(idx_frame, text="Column Index (0-based):").pack(side=tk.LEFT)
        ttk.Spinbox(idx_frame, from_=0, to=100, width=5,
                   textvariable=self.column_index).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame, text="Extract Column", 
                  command=lambda: self.process("extract")).pack(pady=10)
    
    def create_reorder_tab(self):
        """Creates the Reorder Columns tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Reorder")
        
        order_frame = ttk.Frame(frame)
        order_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Label(order_frame, text="New Order (e.g., 2,0,1):").pack(side=tk.LEFT)
        ttk.Entry(order_frame, textvariable=self.column_order, width=20).pack(side=tk.LEFT, padx=5)
        
        info = ttk.Label(frame, text="Enter column indices separated by commas.\n"
                        "Example: '2,0,1' moves column 2 first, then 0, then 1",
                        font=('TkDefaultFont', 8))
        info.pack(pady=5)
        
        ttk.Button(frame, text="Reorder Columns", 
                  command=lambda: self.process("reorder")).pack(pady=10)
    
    def create_delete_tab(self):
        """Creates the Delete Column tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Delete")
        
        idx_frame = ttk.Frame(frame)
        idx_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Label(idx_frame, text="Column Index to Delete:").pack(side=tk.LEFT)
        ttk.Spinbox(idx_frame, from_=0, to=100, width=5,
                   textvariable=self.column_index).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame, text="Delete Column", 
                  command=lambda: self.process("delete")).pack(pady=10)
    
    def create_transpose_tab(self):
        """Creates the Transpose tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Transpose")
        
        info = ttk.Label(frame, text="Swaps rows and columns.\n"
                        "Row 1 becomes Column 1, etc.",
                        justify=tk.CENTER)
        info.pack(pady=20)
        
        ttk.Button(frame, text="Transpose", 
                  command=lambda: self.process("transpose")).pack(pady=10)
    
    def create_fixed_width_tab(self):
        """Creates the Fixed Width tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Fixed Width")
        
        info = ttk.Label(frame, text="Converts CSV to fixed-width columns\n"
                        "for better readability.",
                        justify=tk.CENTER)
        info.pack(pady=20)
        
        ttk.Button(frame, text="Convert to Fixed Width", 
                  command=lambda: self.process("fixed_width")).pack(pady=10)
    
    def load_settings(self):
        """Load settings from the application."""
        settings = self.app.settings.get("tool_settings", {}).get("Column Tools", {})
        
        self.delimiter.set(settings.get("delimiter", ","))
        self.quote_char.set(settings.get("quote_char", '"'))
    
    def save_settings(self):
        """Save current settings to the application."""
        if "Column Tools" not in self.app.settings["tool_settings"]:
            self.app.settings["tool_settings"]["Column Tools"] = {}
        
        self.app.settings["tool_settings"]["Column Tools"].update({
            "delimiter": self.delimiter.get(),
            "quote_char": self.quote_char.get()
        })
        
        self.app.save_settings()
    
    def process(self, operation):
        """Process the input text."""
        active_input_tab = self.app.input_tabs[self.app.input_notebook.index(self.app.input_notebook.select())]
        input_text = active_input_tab.text.get("1.0", tk.END).rstrip('\n')
        
        if not input_text.strip():
            return
        
        delimiter = self.delimiter.get()
        if delimiter == "\\t":
            delimiter = "\t"
        quote_char = self.quote_char.get()
        
        if operation == "extract":
            result = ColumnToolsProcessor.extract_column(
                input_text, self.column_index.get(), delimiter, quote_char)
        elif operation == "reorder":
            result = ColumnToolsProcessor.reorder_columns(
                input_text, self.column_order.get(), delimiter, quote_char)
        elif operation == "delete":
            result = ColumnToolsProcessor.delete_column(
                input_text, self.column_index.get(), delimiter, quote_char)
        elif operation == "transpose":
            result = ColumnToolsProcessor.transpose(input_text, delimiter, quote_char)
        elif operation == "fixed_width":
            result = ColumnToolsProcessor.to_fixed_width(input_text, delimiter, quote_char)
        else:
            result = input_text
        
        active_output_tab = self.app.output_tabs[self.app.output_notebook.index(self.app.output_notebook.select())]
        active_output_tab.text.config(state="normal")
        active_output_tab.text.delete("1.0", tk.END)
        active_output_tab.text.insert("1.0", result)
        active_output_tab.text.config(state="disabled")
        
        self.save_settings()
        self.app.update_all_stats()


class ColumnTools:
    """Main class for Column Tools integration."""
    
    def __init__(self):
        self.processor = ColumnToolsProcessor()
    
    def create_widget(self, parent, app):
        """Create and return the Column Tools widget."""
        return ColumnToolsWidget(parent, app)
    
    def get_default_settings(self):
        """Return default settings for Column Tools."""
        return {
            "delimiter": ",",
            "quote_char": '"',
            "has_header": True
        }


# BaseTool-compatible wrapper
try:
    from tools.base_tool import ToolWithOptions
    from typing import Dict, Any
    import tkinter as tk
    from tkinter import ttk
    
    class ColumnToolsV2(ToolWithOptions):
        """
        BaseTool-compatible version of ColumnTools.
        """
        
        TOOL_NAME = "Column Tools"
        TOOL_DESCRIPTION = "Manipulate CSV/column data"
        TOOL_VERSION = "2.0.0"
        
        OPTIONS = [
            ("Extract Column", "extract"),
            ("Delete Column", "delete"),
            ("Transpose", "transpose"),
            ("To Fixed Width", "fixed_width"),
        ]
        OPTIONS_LABEL = "Operation"
        USE_DROPDOWN = True
        DEFAULT_OPTION = "extract"
        
        def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
            """Process CSV/column data."""
            mode = settings.get("mode", "extract")
            delimiter = settings.get("delimiter", ",")
            column_index = settings.get("column_index", 0)
            
            if mode == "extract":
                return ColumnToolsProcessor.extract_column(input_text, column_index, delimiter)
            elif mode == "delete":
                return ColumnToolsProcessor.delete_column(input_text, column_index, delimiter)
            elif mode == "transpose":
                return ColumnToolsProcessor.transpose(input_text, delimiter)
            elif mode == "fixed_width":
                return ColumnToolsProcessor.to_fixed_width(input_text, delimiter)
            else:
                return input_text

except ImportError:
    pass