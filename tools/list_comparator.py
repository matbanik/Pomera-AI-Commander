import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
import json
import os
import csv
from itertools import zip_longest
import re

# Import context menu support
try:
    from core.context_menu import add_context_menu
    CONTEXT_MENU_AVAILABLE = True
except ImportError:
    try:
        from ..core.context_menu import add_context_menu
        CONTEXT_MENU_AVAILABLE = True
    except ImportError:
        CONTEXT_MENU_AVAILABLE = False
        print("Context menu module not available")

class LineNumberText(tk.Frame):
    """A text widget with line numbers on the right side."""
    
    def __init__(self, parent, wrap=tk.WORD, width=40, height=10, state="normal", **kwargs):
        super().__init__(parent)
        
        # Create the main text widget
        self.text = scrolledtext.ScrolledText(self, wrap=wrap, width=width, height=height, state=state, **kwargs)
        self.text.pack(side="left", fill="both", expand=True)
        
        # Create the line number widget
        self.line_numbers = tk.Text(self, width=4, height=height, state="disabled", 
                                   bg=DiffApp.LINE_NUMBER_BG, fg=DiffApp.LINE_NUMBER_FG, relief="flat", 
                                   font=self.text.cget("font"))
        self.line_numbers.pack(side="right", fill="y")
        
        # Performance optimization: track last line count to avoid unnecessary updates
        self._last_line_count = 0
        self._update_pending = False
        
        # Bind events to update line numbers
        self.text.bind("<KeyRelease>", self._on_text_change)
        self.text.bind("<Button-1>", self._on_text_change)
        self.text.bind("<MouseWheel>", self._on_scroll)
        self.text.bind("<Configure>", self._on_text_change)
        
        # Bind scroll synchronization
        self.text.bind("<MouseWheel>", self._on_scroll)
        self.line_numbers.bind("<MouseWheel>", self._on_scroll)
        
        # Initial line number update
        self._update_line_numbers()
    
    def _on_text_change(self, event=None):
        """Update line numbers when text changes."""
        if not self._update_pending:
            self._update_pending = True
            self.after_idle(self._update_line_numbers)
        return "break" if event and event.type == "2" else None  # KeyPress events
    
    def _on_scroll(self, event):
        """Handle scroll events and sync line numbers."""
        # Sync scrolling between text and line numbers
        if event.widget == self.text:
            self.line_numbers.yview_moveto(self.text.yview()[0])
        else:
            self.text.yview_moveto(self.line_numbers.yview()[0])
        return "break"
    
    def _update_line_numbers(self):
        """Update the line numbers display efficiently."""
        self._update_pending = False
        
        # Get the number of lines
        line_count = int(self.text.index("end-1c").split('.')[0])
        
        # Only update if line count changed
        if line_count != self._last_line_count:
            self._last_line_count = line_count
            
            # Create line number text more efficiently
            if line_count > 0:
                line_numbers_text = "\n".join(str(i) for i in range(1, line_count + 1))
            else:
                line_numbers_text = ""
            
            # Update the line numbers widget
            self.line_numbers.config(state="normal")
            self.line_numbers.delete("1.0", tk.END)
            if line_numbers_text:
                self.line_numbers.insert("1.0", line_numbers_text)
            self.line_numbers.config(state="disabled")
    
    def get(self, index1, index2=None):
        """Delegate to the text widget's get method."""
        return self.text.get(index1, index2)
    
    def insert(self, index, string):
        """Delegate to the text widget's insert method."""
        result = self.text.insert(index, string)
        self._update_line_numbers()
        return result
    
    def delete(self, index1, index2=None):
        """Delegate to the text widget's delete method."""
        result = self.text.delete(index1, index2)
        self._update_line_numbers()
        return result
    
    def config(self, **kwargs):
        """Delegate to the text widget's config method."""
        return self.text.config(**kwargs)
    
    def cget(self, key):
        """Delegate to the text widget's cget method."""
        return self.text.cget(key)

class DiffApp:
    SETTINGS_FILE = "settings.json"
    
    # UI Constants
    WINDOW_TITLE = "Advanced List Comparison Tool"
    WINDOW_GEOMETRY = "1200x800"
    TEXT_WIDGET_WIDTH = 40
    TEXT_WIDGET_HEIGHT = 10
    RESULT_WIDGET_WIDTH = 30
    PATH_ENTRY_WIDTH = 50
    
    # Colors and styling
    LINE_NUMBER_BG = "#f0f0f0"
    LINE_NUMBER_FG = "#666666"

    def __init__(self, root, dialog_manager=None, send_to_input_callback=None):
        self.root = root
        self.dialog_manager = dialog_manager
        self.send_to_input_callback = send_to_input_callback
        self.root.title(self.WINDOW_TITLE)
        self.root.geometry(self.WINDOW_GEOMETRY)

        # --- Variables ---
        self.case_insensitive = tk.BooleanVar()
        self.output_path = tk.StringVar()
        self.default_downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        if not os.path.exists(self.default_downloads_path):
             self.default_downloads_path = os.path.expanduser('~') # Fallback to home dir
        self.output_path.set(self.default_downloads_path)


        # --- Main Frames ---
        top_frame = tk.Frame(root, pady=5)
        top_frame.pack(fill="x", padx=10)

        input_frame = tk.Frame(root)
        input_frame.pack(pady=5, padx=10, fill="both", expand=True)

        results_frame = tk.Frame(root)
        results_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # --- Configuration Section ---
        config_labelframe = tk.LabelFrame(top_frame, text="Configuration")
        config_labelframe.pack(fill="x", expand="yes", side="left", padx=5)

        case_checkbox = tk.Checkbutton(config_labelframe, text="Case Insensitive", variable=self.case_insensitive)
        case_checkbox.pack(side="left", padx=5, pady=5)
        
        tk.Label(config_labelframe, text="Output Path:").pack(side="left", padx=(10,0))
        path_entry = tk.Entry(config_labelframe, textvariable=self.output_path, width=self.PATH_ENTRY_WIDTH)
        path_entry.pack(side="left", fill="x", expand=True, padx=5)
        select_path_button = tk.Button(config_labelframe, text="Select...", command=self.select_output_path)
        select_path_button.pack(side="left", padx=5)


        # --- Buttons Section ---
        button_frame = tk.Frame(top_frame)
        button_frame.pack(side="right", padx=5)

        compare_button = tk.Button(button_frame, text="Compare & Save", command=self.run_comparison_and_save)
        compare_button.pack(side="left", padx=5)

        self.export_button = tk.Button(button_frame, text="Export to CSV", command=self.export_to_csv, state="disabled")
        self.export_button.pack(side="left", padx=5)

        clear_button = tk.Button(button_frame, text="Clear All", command=self.clear_all_fields)
        clear_button.pack(side="left", padx=5)
        
        # Send to Input button (if callback is available)
        print(f"[DEBUG] List Comparator: send_to_input_callback = {self.send_to_input_callback}")
        if self.send_to_input_callback:
            self.send_to_input_var = tk.StringVar(value="Send to Input")
            self.send_to_input_menu = ttk.Menubutton(button_frame, textvariable=self.send_to_input_var, direction="below")
            self.send_to_input_menu.pack(side="left", padx=5)
            
            # Create the dropdown menu
            self.send_dropdown_menu = tk.Menu(self.send_to_input_menu, tearoff=0)
            self.send_to_input_menu.config(menu=self.send_dropdown_menu)
            
            # Build the menu
            self._build_send_to_input_menu()
        
        # --- Input Lists Section ---
        left_input_frame = tk.Frame(input_frame)
        left_input_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        tk.Label(left_input_frame, text="List A").pack()
        self.text_list_a = LineNumberText(left_input_frame, wrap=tk.WORD, width=self.TEXT_WIDGET_WIDTH, height=self.TEXT_WIDGET_HEIGHT)
        self.text_list_a.pack(fill="both", expand=True)
        # Stats bar for List A
        self.stats_list_a = tk.Label(left_input_frame, text="Lines: 0 | Chars: 0", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.stats_list_a.pack(side="bottom", fill="x")
        # Add context menu
        if CONTEXT_MENU_AVAILABLE:
            add_context_menu(self.text_list_a.text)

        right_input_frame = tk.Frame(input_frame)
        right_input_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        tk.Label(right_input_frame, text="List B").pack()
        self.text_list_b = LineNumberText(right_input_frame, wrap=tk.WORD, width=self.TEXT_WIDGET_WIDTH, height=self.TEXT_WIDGET_HEIGHT)
        self.text_list_b.pack(fill="both", expand=True)
        # Stats bar for List B
        self.stats_list_b = tk.Label(right_input_frame, text="Lines: 0 | Chars: 0", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.stats_list_b.pack(side="bottom", fill="x")
        # Add context menu
        if CONTEXT_MENU_AVAILABLE:
            add_context_menu(self.text_list_b.text)

        # --- Results Display Section ---
        # --- Only in List A ---
        left_result_frame = tk.Frame(results_frame)
        left_result_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        tk.Label(left_result_frame, text="Only in List A").pack()
        self.text_only_a = LineNumberText(left_result_frame, wrap=tk.WORD, width=self.RESULT_WIDGET_WIDTH, height=self.TEXT_WIDGET_HEIGHT, state="disabled")
        self.text_only_a.pack(fill="both", expand=True)
        self.status_only_a = tk.Label(left_result_frame, text="Count: 0", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_only_a.pack(side="bottom", fill="x")
        # Add context menu
        if CONTEXT_MENU_AVAILABLE:
            add_context_menu(self.text_only_a.text)

        # --- Only in List B ---
        middle_result_frame = tk.Frame(results_frame)
        middle_result_frame.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(middle_result_frame, text="Only in List B").pack()
        self.text_only_b = LineNumberText(middle_result_frame, wrap=tk.WORD, width=self.RESULT_WIDGET_WIDTH, height=self.TEXT_WIDGET_HEIGHT, state="disabled")
        self.text_only_b.pack(fill="both", expand=True)
        self.status_only_b = tk.Label(middle_result_frame, text="Count: 0", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_only_b.pack(side="bottom", fill="x")
        # Add context menu
        if CONTEXT_MENU_AVAILABLE:
            add_context_menu(self.text_only_b.text)

        # --- In Both Lists ---
        right_result_frame = tk.Frame(results_frame)
        right_result_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))
        tk.Label(right_result_frame, text="In Both Lists").pack()
        self.text_in_both = LineNumberText(right_result_frame, wrap=tk.WORD, width=self.RESULT_WIDGET_WIDTH, height=self.TEXT_WIDGET_HEIGHT, state="disabled")
        self.text_in_both.pack(fill="both", expand=True)
        self.status_in_both = tk.Label(right_result_frame, text="Count: 0", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_in_both.pack(side="bottom", fill="x")
        # Add context menu
        if CONTEXT_MENU_AVAILABLE:
            add_context_menu(self.text_in_both.text)


        # --- Load settings on startup and save on exit ---
        self.load_settings()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Bind text change events to update stats
        self.text_list_a.text.bind("<KeyRelease>", lambda e: self._update_stats(self.text_list_a, self.stats_list_a))
        self.text_list_b.text.bind("<KeyRelease>", lambda e: self._update_stats(self.text_list_b, self.stats_list_b))
        
        # Initial stats update
        self._update_stats(self.text_list_a, self.stats_list_a)
        self._update_stats(self.text_list_b, self.stats_list_b)
    
    def _show_info(self, title, message, category="success"):
        """Show info dialog using DialogManager if available, otherwise use messagebox."""
        if self.dialog_manager:
            return self.dialog_manager.show_info(title, message, category, parent=self.root)
        else:
            messagebox.showinfo(title, message, parent=self.root)
            return True
    
    def _show_warning(self, title, message, category="warning"):
        """Show warning dialog using DialogManager if available, otherwise use messagebox."""
        if self.dialog_manager:
            return self.dialog_manager.show_warning(title, message, category, parent=self.root)
        else:
            messagebox.showwarning(title, message, parent=self.root)
            return True
    
    def _show_error(self, title, message):
        """Show error dialog using DialogManager if available, otherwise use messagebox."""
        if self.dialog_manager:
            return self.dialog_manager.show_error(title, message, parent=self.root)
        else:
            messagebox.showerror(title, message, parent=self.root)
            return True
    
    def _ask_yes_no(self, title, message, category="confirmation"):
        """Show confirmation dialog using DialogManager if available, otherwise use messagebox."""
        if self.dialog_manager:
            return self.dialog_manager.ask_yes_no(title, message, category, parent=self.root)
        else:
            return messagebox.askyesno(title, message, parent=self.root)

    def select_output_path(self):
        """Opens a dialog to select an output folder."""
        path = filedialog.askdirectory(title="Select Output Folder", initialdir=self.output_path.get(), parent=self.root)
        if path:
            self.output_path.set(path)

    def get_lists(self):
        """Gets the text from the input boxes and splits it into lines."""
        try:
            list1 = self.text_list_a.text.get("1.0", tk.END).strip().splitlines()
            list2 = self.text_list_b.text.get("1.0", tk.END).strip().splitlines()
            
            # Filter out empty lines and strip whitespace
            list1 = [line.strip() for line in list1 if line.strip()]
            list2 = [line.strip() for line in list2 if line.strip()]
            
            return list1, list2
        except Exception as e:
            raise ValueError(f"Error reading input lists: {e}")

    def run_comparison_and_save(self):
        """Compares the lists, displays results, and saves settings."""
        try:
            list1, list2 = self.get_lists()
            
            # Perform comparison
            results = self._compare_lists(list1, list2)
            
            # Update UI with results
            self._update_results_display(results)
            
            # Update export button state
            self._update_export_button_state(results)
            
            # Save settings
            self.save_settings()
            self._show_info("Success", "Comparison complete and settings saved.")
            
        except Exception as e:
            self._show_error("Comparison Error", f"An error occurred during comparison:\n{e}")
    
    def _compare_lists(self, list1, list2):
        """Compare two lists and return results dictionary."""
        # Handle case-insensitivity more efficiently
        if self.case_insensitive.get():
            # Create case-insensitive sets while preserving original casing
            set1_lower = {item.lower() for item in list1}
            set2_lower = {item.lower() for item in list2}
            
            # Create mapping from lowercase to original (preserving first occurrence)
            map1 = {item.lower(): item for item in reversed(list1)}
            map2 = {item.lower(): item for item in reversed(list2)}
            
            # Find differences using lowercase sets
            unique_to_a_lower = set1_lower - set2_lower
            unique_to_b_lower = set2_lower - set1_lower
            in_both_lower = set1_lower & set2_lower
            
            # Map back to original casing
            unique_to_a = sorted([map1[item] for item in unique_to_a_lower])
            unique_to_b = sorted([map2[item] for item in unique_to_b_lower])
            in_both = sorted([map1.get(item, map2.get(item)) for item in in_both_lower])
        else:
            # Case-sensitive comparison
            set1, set2 = set(list1), set(list2)
            unique_to_a = sorted(list(set1 - set2))
            unique_to_b = sorted(list(set2 - set1))
            in_both = sorted(list(set1 & set2))
        
        return {
            'unique_to_a': unique_to_a,
            'unique_to_b': unique_to_b,
            'in_both': in_both
        }
    
    def _update_results_display(self, results):
        """Update the result text widgets and status bars."""
        # Update Only in List A
        self.update_result_text(self.text_only_a, "\n".join(results['unique_to_a']))
        self.status_only_a.config(text=f"Count: {len(results['unique_to_a'])}")
        
        # Update Only in List B
        self.update_result_text(self.text_only_b, "\n".join(results['unique_to_b']))
        self.status_only_b.config(text=f"Count: {len(results['unique_to_b'])}")
        
        # Update In Both Lists
        self.update_result_text(self.text_in_both, "\n".join(results['in_both']))
        self.status_in_both.config(text=f"Count: {len(results['in_both'])}")
    
    def _update_export_button_state(self, results):
        """Update export button state based on results."""
        has_results = any(results.values())
        self.export_button.config(state="normal" if has_results else "disabled")

    def export_to_csv(self):
        """Exports the content of all 5 text boxes to a CSV file."""
        try:
            output_dir = self.output_path.get().strip()
            if not output_dir:
                self._show_error("Error", "Output path is empty. Please select a valid output directory.")
                return
                
            if not os.path.isdir(output_dir):
                self._show_error("Error", f"Output path does not exist:\n{output_dir}")
                return
            
            # Check if directory is writable
            if not os.access(output_dir, os.W_OK):
                self._show_error("Error", f"Output directory is not writable:\n{output_dir}")
                return
            
            # Generate unique filename if file already exists
            base_filename = "comparison_results.csv"
            output_file = os.path.join(output_dir, base_filename)
            counter = 1
            while os.path.exists(output_file):
                name, ext = os.path.splitext(base_filename)
                output_file = os.path.join(output_dir, f"{name}_{counter}{ext}")
                counter += 1

            # Get data from all 5 lists with validation
            list_a = self._get_text_content(self.text_list_a)
            list_b = self._get_text_content(self.text_list_b)
            only_a = self._get_text_content(self.text_only_a)
            only_b = self._get_text_content(self.text_only_b)
            in_both = self._get_text_content(self.text_in_both)

            # Use zip_longest to handle lists of different lengths
            export_data = list(zip_longest(list_a, list_b, only_a, only_b, in_both, fillvalue=""))
            
            headers = ["List A (Input)", "List B (Input)", "Only in List A", "Only in List B", "In Both Lists"]

            with open(output_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(export_data)
            
            self._show_info("Success", f"Data successfully exported to:\n{output_file}")

        except PermissionError:
            self._show_error("Export Failed", "Permission denied. The file may be open in another application.")
        except OSError as e:
            self._show_error("Export Failed", f"File system error: {e}")
        except Exception as e:
            self._show_error("Export Failed", f"An unexpected error occurred while exporting to CSV:\n{e}")
    
    def _get_text_content(self, text_widget):
        """Safely get text content from a text widget."""
        try:
            content = text_widget.text.get("1.0", tk.END).strip()
            return [line.strip() for line in content.splitlines() if line.strip()] if content else []
        except Exception:
            return []

    def update_result_text(self, text_widget, content):
        """Helper function to update the read-only result widgets."""
        text_widget.text.config(state="normal")
        text_widget.text.delete("1.0", tk.END)
        text_widget.text.insert("1.0", content)
        text_widget.text.config(state="disabled")

    def clear_all_fields(self):
        """Clears all input and result fields and resets status bars."""
        self.text_list_a.text.delete("1.0", tk.END)
        self.text_list_b.text.delete("1.0", tk.END)
        self.update_result_text(self.text_only_a, "")
        self.update_result_text(self.text_only_b, "")
        self.update_result_text(self.text_in_both, "")
        self.status_only_a.config(text="Count: 0")
        self.status_only_b.config(text="Count: 0")
        self.status_in_both.config(text="Count: 0")
        self.export_button.config(state="disabled")

    def save_settings(self):
        """Saves the content of all text boxes and config to a JSON file."""
        try:
            settings = {
                "case_insensitive": self.case_insensitive.get(),
                "output_path": self.output_path.get().strip(),
                "list_a": self.text_list_a.text.get("1.0", tk.END).strip(),
                "list_b": self.text_list_b.text.get("1.0", tk.END).strip(),
                "only_a": self.text_only_a.text.get("1.0", tk.END).strip(),
                "only_b": self.text_only_b.text.get("1.0", tk.END).strip(),
                "in_both": self.text_in_both.text.get("1.0", tk.END).strip()
            }
            
            # Validate settings before saving
            if not self._validate_settings(settings):
                return False
                
            with open(self.SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            return True
            
        except PermissionError:
            print(f"Permission denied: Cannot save settings to {self.SETTINGS_FILE}")
            return False
        except OSError as e:
            print(f"File system error saving settings: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error saving settings: {e}")
            return False
    
    def _validate_settings(self, settings):
        """Validate settings data before saving."""
        try:
            # Check if output path is valid
            output_path = settings.get("output_path", "")
            if output_path and not os.path.isdir(output_path):
                print(f"Warning: Output path does not exist: {output_path}")
                # Don't fail validation, just warn
            
            # Check if boolean values are valid
            if not isinstance(settings.get("case_insensitive"), bool):
                print("Warning: Invalid case_insensitive value")
                return False
                
            return True
        except Exception as e:
            print(f"Settings validation error: {e}")
            return False

    def load_settings(self):
        """Loads settings from the JSON file if it exists."""
        if not os.path.exists(self.SETTINGS_FILE):
            return
            
        try:
            with open(self.SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
            
            # Load configuration settings with validation
            self.case_insensitive.set(settings.get("case_insensitive", False))
            
            output_path = settings.get("output_path", "").strip()
            if output_path and os.path.isdir(output_path):
                self.output_path.set(output_path)
            else:
                self.output_path.set(self.default_downloads_path)
            
            # Load text content safely
            self._load_text_content(self.text_list_a, settings.get("list_a", ""))
            self._load_text_content(self.text_list_b, settings.get("list_b", ""))
            
            # Process result fields, handling old format with counts
            self.process_loaded_result(self.text_only_a, self.status_only_a, settings.get("only_a", ""))
            self.process_loaded_result(self.text_only_b, self.status_only_b, settings.get("only_b", ""))
            self.process_loaded_result(self.text_in_both, self.status_in_both, settings.get("in_both", ""))

            # Enable export button if there are results
            if settings.get("only_a") or settings.get("only_b") or settings.get("in_both"):
                self.export_button.config(state="normal")

        except json.JSONDecodeError as e:
            print(f"Invalid JSON in settings file: {e}")
        except PermissionError:
            print(f"Permission denied: Cannot read settings file {self.SETTINGS_FILE}")
        except OSError as e:
            print(f"File system error loading settings: {e}")
        except Exception as e:
            print(f"Unexpected error loading settings: {e}")
    
    def _load_text_content(self, text_widget, content):
        """Safely load text content into a text widget."""
        try:
            if content and isinstance(content, str):
                text_widget.text.insert("1.0", content)
        except Exception as e:
            print(f"Error loading text content: {e}")

    def process_loaded_result(self, text_widget, status_label, content):
        """Processes loaded result content, separating count from list for backward compatibility."""
        lines = content.splitlines()
        # Check if the first line matches the old "Count: X" format
        if lines and re.match(r'^Count: \d+$', lines[0]):
            status_label.config(text=lines[0])
            # The list content starts after the count and a blank line
            list_content = "\n".join(lines[2:])
            self.update_result_text(text_widget, list_content)
        else:
            # New format or empty, just load content and update count based on lines
            self.update_result_text(text_widget, content)
            item_count = len(lines) if content else 0
            status_label.config(text=f"Count: {item_count}")


    def on_closing(self):
        """Handles the window closing event."""
        self.save_settings()
        self.root.destroy()
    
    def _update_stats(self, text_widget, stats_label):
        """Update stats bar with line and character counts."""
        try:
            content = text_widget.text.get("1.0", tk.END)
            # Count lines (excluding the final empty line that tkinter adds)
            lines = content.splitlines()
            line_count = len([line for line in lines if line.strip()])
            # Count characters (excluding trailing newline)
            char_count = len(content.rstrip('\n'))
            stats_label.config(text=f"Lines: {line_count} | Chars: {char_count}")
        except Exception as e:
            print(f"Error updating stats: {e}")
    
    def _build_send_to_input_menu(self):
        """Build the Send to Input dropdown menu."""
        try:
            # Clear existing menu
            self.send_dropdown_menu.delete(0, tk.END)
            
            # Add options for each text area
            self.send_dropdown_menu.add_command(
                label="List A → Input Tab 1",
                command=lambda: self._send_content_to_input(0, self.text_list_a)
            )
            self.send_dropdown_menu.add_command(
                label="List B → Input Tab 2",
                command=lambda: self._send_content_to_input(1, self.text_list_b)
            )
            
            self.send_dropdown_menu.add_separator()
            
            self.send_dropdown_menu.add_command(
                label="Only in A → Input Tab 3",
                command=lambda: self._send_content_to_input(2, self.text_only_a)
            )
            self.send_dropdown_menu.add_command(
                label="Only in B → Input Tab 4",
                command=lambda: self._send_content_to_input(3, self.text_only_b)
            )
            self.send_dropdown_menu.add_command(
                label="In Both → Input Tab 5",
                command=lambda: self._send_content_to_input(4, self.text_in_both)
            )
            
            self.send_dropdown_menu.add_separator()
            
            # Add option to send all results
            self.send_dropdown_menu.add_command(
                label="All Results → Input Tab 6",
                command=self._send_all_results_to_input
            )
            
        except Exception as e:
            print(f"Error building send to input menu: {e}")
    
    def _send_content_to_input(self, tab_index, text_widget):
        """Send content from a text widget to an input tab."""
        try:
            if not self.send_to_input_callback:
                self._show_warning("Warning", "Send to Input functionality is not available.")
                return
            
            # Get content from text widget
            content = text_widget.text.get("1.0", tk.END).strip()
            
            if not content:
                self._show_warning("No Content", "The selected text area is empty.")
                return
            
            # Send to input tab using callback
            self.send_to_input_callback(tab_index, content)
            
            # Show success message
            self._show_info("Success", f"Content sent to Input Tab {tab_index + 1}", category="success")
            
        except Exception as e:
            self._show_error("Error", f"Failed to send content to input:\n{str(e)}")
    
    def _send_all_results_to_input(self):
        """Send all comparison results to an input tab."""
        try:
            if not self.send_to_input_callback:
                self._show_warning("Warning", "Send to Input functionality is not available.")
                return
            
            # Build combined results
            only_a = self.text_only_a.text.get("1.0", tk.END).strip()
            only_b = self.text_only_b.text.get("1.0", tk.END).strip()
            in_both = self.text_in_both.text.get("1.0", tk.END).strip()
            
            if not any([only_a, only_b, in_both]):
                self._show_warning("No Results", "No comparison results to send. Run a comparison first.")
                return
            
            # Format combined results
            combined = []
            if only_a:
                combined.append("=== Only in List A ===")
                combined.append(only_a)
                combined.append("")
            if only_b:
                combined.append("=== Only in List B ===")
                combined.append(only_b)
                combined.append("")
            if in_both:
                combined.append("=== In Both Lists ===")
                combined.append(in_both)
            
            content = "\n".join(combined)
            
            # Send to input tab 6
            self.send_to_input_callback(5, content)
            
            # Show success message
            self._show_info("Success", "All results sent to Input Tab 6", category="success")
            
        except Exception as e:
            self._show_error("Error", f"Failed to send results to input:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DiffApp(root)
    root.mainloop()
