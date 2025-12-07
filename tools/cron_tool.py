import tkinter as tk
from tkinter import ttk, messagebox
import re
from datetime import datetime, timedelta
import calendar

class CronTool:
    def __init__(self, parent_app):
        self.app = parent_app
        self.logger = parent_app.logger if hasattr(parent_app, 'logger') else None
        
        # Common cron patterns organized by category
        self.cron_presets = {
            "Frequent Intervals": {
                "Every minute": "* * * * *",
                "Every 2 minutes": "*/2 * * * *",
                "Every 5 minutes": "*/5 * * * *",
                "Every 10 minutes": "*/10 * * * *",
                "Every 15 minutes": "*/15 * * * *",
                "Every 30 minutes": "*/30 * * * *",
                "Every hour": "0 * * * *",
                "Every 2 hours": "0 */2 * * *",
                "Every 3 hours": "0 */3 * * *",
                "Every 6 hours": "0 */6 * * *"
            },
            "Daily Schedules": {
                "Daily at midnight": "0 0 * * *",
                "Daily at 6 AM": "0 6 * * *",
                "Daily at 9 AM": "0 9 * * *",
                "Daily at noon": "0 12 * * *",
                "Daily at 3 PM": "0 15 * * *",
                "Daily at 6 PM": "0 18 * * *",
                "Daily at 9 PM": "0 21 * * *",
                "Twice daily (6 AM, 6 PM)": "0 6,18 * * *",
                "Three times daily": "0 6,12,18 * * *"
            },
            "Weekday Schedules": {
                "Weekdays at 9 AM": "0 9 * * 1-5",
                "Weekdays at 5 PM": "0 17 * * 1-5",
                "Business hours every 15 min": "*/15 9-17 * * 1-5",
                "Business hours every 30 min": "*/30 9-17 * * 1-5",
                "Monday morning": "0 9 * * 1",
                "Friday evening": "0 17 * * 5",
                "Start of business week": "0 8 * * 1",
                "End of business week": "0 18 * * 5"
            },
            "Weekend Schedules": {
                "Saturday morning": "0 9 * * 6",
                "Sunday morning": "0 9 * * 0",
                "Weekend mornings": "0 9 * * 0,6",
                "Weekend evenings": "0 18 * * 0,6"
            },
            "Weekly Patterns": {
                "Weekly on Monday": "0 0 * * 1",
                "Weekly on Friday": "0 0 * * 5",
                "Weekly on Sunday": "0 0 * * 0",
                "Bi-weekly": "0 0 * * 1/2"
            },
            "Monthly Patterns": {
                "First day of month": "0 0 1 * *",
                "Last day of month": "0 0 L * *",
                "15th of each month": "0 0 15 * *",
                "First Monday of month": "0 0 * * 1#1",
                "Last Friday of month": "0 0 * * 5#5",
                "Monthly on 1st and 15th": "0 0 1,15 * *"
            },
            "Yearly Patterns": {
                "New Year's Day": "0 0 1 1 *",
                "Christmas": "0 0 25 12 *",
                "First day of each quarter": "0 0 1 1,4,7,10 *",
                "Yearly backup": "0 2 1 1 *"
            }
        }
        
        # Example expressions for demonstration
        self.example_expressions = [
            ("0 0 * * *", "Daily at midnight"),
            ("*/5 * * * *", "Every 5 minutes"),
            ("0 9 * * 1-5", "Business hours/weekdays"),
            ("0 6,12,18 * * *", "Multiple times per day"),
            ("0 0 1 * *", "First day of month"),
            ("*/15 9-17 * * 1-5", "Every 15 minutes during business hours")
        ]
    
    def get_default_settings(self):
        """Return default settings for the Cron tool."""
        return {
            "action": "parse_explain",
            "preset_category": "Daily Schedules",
            "preset_pattern": "Daily at midnight",
            "compare_expressions": "",
            "next_runs_count": 10
        }
    
    def create_widgets(self, parent, settings):
        """Create the Cron tool interface."""
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Store reference for font application
        self.main_frame = main_frame
        
        # Top row: Actions and Settings side by side
        top_row_frame = ttk.Frame(main_frame)
        top_row_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Left side - Actions
        actions_frame = ttk.LabelFrame(top_row_frame, text="Actions")
        actions_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.action_var = tk.StringVar(value=settings.get("action", "parse_explain"))
        
        actions = [
            ("parse_explain", "Parse and Explain"),
            ("generate", "Generate Expression"),
            ("validate", "Validate Expression"),
            ("next_runs", "Calculate Next Runs"),
            ("presets", "Common Patterns Library"),
            ("compare", "Compare Expressions")
        ]
        
        # Create action buttons in a grid
        for i, (value, text) in enumerate(actions):
            row = i // 2
            col = i % 2
            ttk.Radiobutton(actions_frame, text=text, variable=self.action_var, 
                          value=value, command=self.on_action_change).grid(
                          row=row, column=col, sticky="w", padx=5, pady=2)
        
        # Right side - Settings
        settings_frame = ttk.LabelFrame(top_row_frame, text="Settings")
        settings_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Next runs count
        runs_frame = ttk.Frame(settings_frame)
        runs_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(runs_frame, text="Next Runs Count:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.next_runs_var = tk.StringVar(value=str(settings.get("next_runs_count", 10)))
        ttk.Spinbox(runs_frame, from_=1, to=50, width=5, textvariable=self.next_runs_var).grid(row=0, column=1, sticky="w")
        
        # Preset selection (for generate action)
        self.preset_frame = ttk.Frame(settings_frame)
        self.preset_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.preset_frame, text="Category:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.preset_category_var = tk.StringVar(value=settings.get("preset_category", "Daily Schedules"))
        category_combo = ttk.Combobox(self.preset_frame, textvariable=self.preset_category_var, 
                                    values=list(self.cron_presets.keys()), state="readonly", width=15)
        category_combo.grid(row=0, column=1, sticky="w", padx=(0, 10))
        category_combo.bind("<<ComboboxSelected>>", self.on_category_change)
        
        ttk.Label(self.preset_frame, text="Pattern:").grid(row=1, column=0, sticky="w", padx=(0, 5))
        self.preset_pattern_var = tk.StringVar(value=settings.get("preset_pattern", "Daily at midnight"))
        self.pattern_combo = ttk.Combobox(self.preset_frame, textvariable=self.preset_pattern_var, 
                                        state="readonly", width=20)
        self.pattern_combo.grid(row=1, column=1, sticky="w")
        self.update_pattern_combo()
        
        # Examples frame (for parse_explain action)
        self.examples_frame = ttk.LabelFrame(main_frame, text="Example Expressions")
        self.examples_frame.pack(fill=tk.X, pady=(0, 10))
        
        examples_content = ttk.Frame(self.examples_frame)
        examples_content.pack(fill=tk.X, padx=5, pady=5)
        
        for i, (expr, desc) in enumerate(self.example_expressions):
            row = i // 2
            col = i % 2
            btn_text = f"{expr} - {desc}"
            ttk.Button(examples_content, text=btn_text, 
                      command=lambda e=expr: self.insert_example(e)).grid(
                      row=row, column=col, sticky="w", padx=5, pady=2)
        
        # Compare expressions frame (for compare action)
        self.compare_frame = ttk.LabelFrame(main_frame, text="Compare Multiple Expressions")
        self.compare_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.compare_frame, text="Enter multiple cron expressions (one per line):").pack(anchor="w", padx=5, pady=2)
        self.compare_text = tk.Text(self.compare_frame, height=4, wrap=tk.WORD)
        self.compare_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Process button and status
        process_frame = ttk.Frame(main_frame)
        process_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(process_frame, text="Process", command=self.process_data).pack(side=tk.LEFT)
        
        # Status label
        self.status_label = ttk.Label(process_frame, text="Ready", foreground="green")
        self.status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Apply current font settings if available
        try:
            if hasattr(self.app, 'get_best_font'):
                text_font_family, text_font_size = self.app.get_best_font("text")
                font_tuple = (text_font_family, text_font_size)
                
                # Apply to Text widgets
                self.compare_text.configure(font=font_tuple)
                
                # Apply to Entry widgets
                for child in main_frame.winfo_children():
                    self._apply_font_to_children(child, font_tuple)
        except:
            pass  # Use default font if font settings not available
        
        # Initially show/hide frames based on action
        self.on_action_change()
        
        return main_frame
    
    def _apply_font_to_children(self, widget, font_tuple):
        """Recursively apply font to Entry widgets."""
        try:
            if isinstance(widget, (tk.Entry, ttk.Entry)):
                widget.configure(font=font_tuple)
            
            # Recursively check children
            if hasattr(widget, 'winfo_children'):
                for child in widget.winfo_children():
                    self._apply_font_to_children(child, font_tuple)
        except:
            pass
    
    def apply_font_to_widgets(self, font_tuple):
        """Apply font to all text widgets in the tool."""
        try:
            # Apply to the main frame and all its children
            if hasattr(self, 'main_frame'):
                self._apply_font_to_children(self.main_frame, font_tuple)
                
            # Apply to compare text widget
            if hasattr(self, 'compare_text'):
                self.compare_text.configure(font=font_tuple)
        except Exception as e:
            if self.logger:
                self.logger.debug(f"Error applying font to Cron tool widgets: {e}")
    
    def on_action_change(self):
        """Handle action selection change."""
        action = self.action_var.get()
        
        # Show/hide frames based on action
        if action == "parse_explain":
            self.examples_frame.pack(fill=tk.X, pady=(0, 10))
            self.preset_frame.pack_forget()
            self.compare_frame.pack_forget()
        elif action == "generate" or action == "presets":
            self.preset_frame.pack(fill=tk.X, padx=5, pady=5)
            self.examples_frame.pack_forget()
            self.compare_frame.pack_forget()
        elif action == "compare":
            self.compare_frame.pack(fill=tk.X, pady=(0, 10))
            self.examples_frame.pack_forget()
            self.preset_frame.pack_forget()
        else:
            self.examples_frame.pack_forget()
            self.preset_frame.pack_forget()
            self.compare_frame.pack_forget()
    
    def on_category_change(self, event=None):
        """Handle preset category change."""
        self.update_pattern_combo()
    
    def update_pattern_combo(self):
        """Update pattern combobox based on selected category."""
        category = self.preset_category_var.get()
        if category in self.cron_presets:
            patterns = list(self.cron_presets[category].keys())
            self.pattern_combo['values'] = patterns
            if patterns:
                self.preset_pattern_var.set(patterns[0])
    
    def insert_example(self, expression):
        """Insert example expression into input tab."""
        try:
            current_input_tab = self.app.input_notebook.index(self.app.input_notebook.select())
            self.app.input_tabs[current_input_tab].text.delete("1.0", tk.END)
            self.app.input_tabs[current_input_tab].text.insert("1.0", expression)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error inserting example: {e}")
    
    def process_data(self):
        """Process the data based on selected action."""
        try:
            action = self.action_var.get()
            result = ""
            
            if action == "parse_explain":
                result = self.parse_and_explain()
            elif action == "generate":
                result = self.generate_expression()
            elif action == "validate":
                result = self.validate_expression()
            elif action == "next_runs":
                result = self.calculate_next_runs()
            elif action == "presets":
                result = self.show_presets_library()
            elif action == "compare":
                result = self.compare_expressions()
            
            # Set output text to current active output tab
            current_output_tab = self.app.output_notebook.index(self.app.output_notebook.select())
            self.app.output_tabs[current_output_tab].text.config(state="normal")
            self.app.output_tabs[current_output_tab].text.delete("1.0", tk.END)
            self.app.output_tabs[current_output_tab].text.insert("1.0", result)
            self.app.output_tabs[current_output_tab].text.config(state="disabled")
            self.status_label.config(text="Success", foreground="green")
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            # Set error message to output tab
            current_output_tab = self.app.output_notebook.index(self.app.output_notebook.select())
            self.app.output_tabs[current_output_tab].text.config(state="normal")
            self.app.output_tabs[current_output_tab].text.delete("1.0", tk.END)
            self.app.output_tabs[current_output_tab].text.insert("1.0", error_msg)
            self.app.output_tabs[current_output_tab].text.config(state="disabled")
            self.status_label.config(text="Error", foreground="red")
            if self.logger:
                self.logger.error(f"Cron Tool error: {e}")
    
    def parse_and_explain(self):
        """Parse and explain cron expression."""
        try:
            # Get input text from current active input tab
            current_input_tab = self.app.input_notebook.index(self.app.input_notebook.select())
            input_text = self.app.input_tabs[current_input_tab].text.get("1.0", tk.END).strip()
            
            if not input_text:
                return "Error: No cron expression provided. Please enter a cron expression in the input tab."
            
            # Parse the cron expression
            parts = input_text.split()
            if len(parts) != 5:
                return f"Error: Invalid cron expression format. Expected 5 fields, got {len(parts)}.\nFormat: minute hour day month weekday"
            
            minute, hour, day, month, weekday = parts
            
            result = f"Cron Expression: {input_text}\n"
            result += "=" * 50 + "\n\n"
            
            # Detailed breakdown
            result += "Field Breakdown:\n"
            result += f"• Minute:   {minute:10} - {self._explain_field(minute, 'minute')}\n"
            result += f"• Hour:     {hour:10} - {self._explain_field(hour, 'hour')}\n"
            result += f"• Day:      {day:10} - {self._explain_field(day, 'day')}\n"
            result += f"• Month:    {month:10} - {self._explain_field(month, 'month')}\n"
            result += f"• Weekday:  {weekday:10} - {self._explain_field(weekday, 'weekday')}\n\n"
            
            # Human readable explanation
            result += "Human Readable:\n"
            result += self._generate_human_readable(minute, hour, day, month, weekday) + "\n\n"
            
            # Next few runs
            result += "Next 5 Scheduled Runs:\n"
            next_runs = self._calculate_next_runs(input_text, 5)
            for i, run_time in enumerate(next_runs, 1):
                result += f"{i}. {run_time.strftime('%Y-%m-%d %H:%M:%S %A')}\n"
            
            return result
            
        except Exception as e:
            return f"Error parsing cron expression: {e}"
    
    def _explain_field(self, field, field_type):
        """Explain individual cron field."""
        if field == "*":
            return "Every " + field_type
        elif field.startswith("*/"):
            interval = field[2:]
            return f"Every {interval} {field_type}s"
        elif "," in field:
            values = field.split(",")
            return f"At {field_type}s: {', '.join(values)}"
        elif "-" in field and not field.startswith("*/"):
            start, end = field.split("-")
            return f"From {field_type} {start} to {end}"
        else:
            return f"At {field_type} {field}"
    
    def _generate_human_readable(self, minute, hour, day, month, weekday):
        """Generate human readable description."""
        description = "Runs "
        
        # Frequency
        if minute.startswith("*/"):
            interval = minute[2:]
            description += f"every {interval} minutes"
        elif minute == "*":
            description += "every minute"
        else:
            description += f"at minute {minute}"
        
        # Hour specification
        if hour != "*":
            if hour.startswith("*/"):
                interval = hour[2:]
                description += f", every {interval} hours"
            elif "," in hour:
                hours = hour.split(",")
                description += f", at hours {', '.join(hours)}"
            elif "-" in hour:
                start, end = hour.split("-")
                description += f", between {start}:00 and {end}:00"
            else:
                description += f", at {hour}:00"
        
        # Day/weekday specification
        if weekday != "*":
            weekday_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
            if "," in weekday:
                days = [weekday_names[int(d)] for d in weekday.split(",")]
                description += f", on {', '.join(days)}"
            elif "-" in weekday:
                start, end = weekday.split("-")
                description += f", from {weekday_names[int(start)]} to {weekday_names[int(end)]}"
            else:
                description += f", on {weekday_names[int(weekday)]}"
        elif day != "*":
            if day == "1":
                description += ", on the 1st day of the month"
            elif day == "L":
                description += ", on the last day of the month"
            else:
                description += f", on day {day} of the month"
        
        # Month specification
        if month != "*":
            month_names = ["", "January", "February", "March", "April", "May", "June",
                          "July", "August", "September", "October", "November", "December"]
            if "," in month:
                months = [month_names[int(m)] for m in month.split(",")]
                description += f", in {', '.join(months)}"
            else:
                description += f", in {month_names[int(month)]}"
        
        return description
    
    def generate_expression(self):
        """Generate cron expression from preset."""
        try:
            category = self.preset_category_var.get()
            pattern = self.preset_pattern_var.get()
            
            if category in self.cron_presets and pattern in self.cron_presets[category]:
                expression = self.cron_presets[category][pattern]
                
                result = f"Generated Cron Expression\n"
                result += "=" * 30 + "\n\n"
                result += f"Pattern: {pattern}\n"
                result += f"Category: {category}\n"
                result += f"Expression: {expression}\n\n"
                
                # Parse and explain the generated expression
                parts = expression.split()
                if len(parts) == 5:
                    minute, hour, day, month, weekday = parts
                    result += "Explanation:\n"
                    result += self._generate_human_readable(minute, hour, day, month, weekday) + "\n\n"
                    
                    # Next runs
                    result += "Next 5 Scheduled Runs:\n"
                    next_runs = self._calculate_next_runs(expression, 5)
                    for i, run_time in enumerate(next_runs, 1):
                        result += f"{i}. {run_time.strftime('%Y-%m-%d %H:%M:%S %A')}\n"
                
                return result
            else:
                return "Error: Selected preset not found."
                
        except Exception as e:
            return f"Error generating expression: {e}"
    
    def validate_expression(self):
        """Validate cron expression."""
        try:
            # Get input text
            current_input_tab = self.app.input_notebook.index(self.app.input_notebook.select())
            input_text = self.app.input_tabs[current_input_tab].text.get("1.0", tk.END).strip()
            
            if not input_text:
                return "Error: No cron expression provided."
            
            result = f"Cron Expression Validation\n"
            result += "=" * 30 + "\n\n"
            result += f"Expression: {input_text}\n\n"
            
            # Basic format validation
            parts = input_text.split()
            if len(parts) != 5:
                result += f"❌ INVALID: Expected 5 fields, got {len(parts)}\n"
                result += "Format: minute hour day month weekday\n"
                result += "Example: 0 9 * * 1-5 (weekdays at 9 AM)\n"
                return result
            
            minute, hour, day, month, weekday = parts
            errors = []
            warnings = []
            
            # Validate each field
            errors.extend(self._validate_field(minute, "minute", 0, 59))
            errors.extend(self._validate_field(hour, "hour", 0, 23))
            errors.extend(self._validate_field(day, "day", 1, 31))
            errors.extend(self._validate_field(month, "month", 1, 12))
            errors.extend(self._validate_field(weekday, "weekday", 0, 7))
            
            # Logic validation
            if day != "*" and weekday != "*":
                warnings.append("Both day-of-month and day-of-week are specified. This creates an OR condition.")
            
            if errors:
                result += "❌ VALIDATION FAILED:\n"
                for error in errors:
                    result += f"  • {error}\n"
            else:
                result += "✅ VALIDATION PASSED\n"
                result += "The cron expression is syntactically valid.\n"
            
            if warnings:
                result += "\n⚠️  WARNINGS:\n"
                for warning in warnings:
                    result += f"  • {warning}\n"
            
            if not errors:
                result += f"\nHuman Readable:\n"
                result += self._generate_human_readable(minute, hour, day, month, weekday)
            
            return result
            
        except Exception as e:
            return f"Error validating expression: {e}"
    
    def _validate_field(self, field, field_name, min_val, max_val):
        """Validate individual cron field."""
        errors = []
        
        if field == "*":
            return errors
        
        # Handle step values (*/n)
        if field.startswith("*/"):
            try:
                step = int(field[2:])
                if step <= 0:
                    errors.append(f"{field_name}: Step value must be positive")
                elif step > max_val:
                    errors.append(f"{field_name}: Step value {step} exceeds maximum {max_val}")
            except ValueError:
                errors.append(f"{field_name}: Invalid step value in '{field}'")
            return errors
        
        # Handle ranges and lists
        for part in field.split(","):
            if "-" in part:
                try:
                    start, end = part.split("-")
                    start_val, end_val = int(start), int(end)
                    if start_val < min_val or start_val > max_val:
                        errors.append(f"{field_name}: Range start {start_val} out of bounds ({min_val}-{max_val})")
                    if end_val < min_val or end_val > max_val:
                        errors.append(f"{field_name}: Range end {end_val} out of bounds ({min_val}-{max_val})")
                    if start_val > end_val:
                        errors.append(f"{field_name}: Invalid range {start_val}-{end_val}")
                except ValueError:
                    errors.append(f"{field_name}: Invalid range format '{part}'")
            else:
                try:
                    val = int(part)
                    if val < min_val or val > max_val:
                        errors.append(f"{field_name}: Value {val} out of bounds ({min_val}-{max_val})")
                except ValueError:
                    errors.append(f"{field_name}: Invalid value '{part}'")
        
        return errors
    
    def calculate_next_runs(self):
        """Calculate next scheduled runs."""
        try:
            # Get input text
            current_input_tab = self.app.input_notebook.index(self.app.input_notebook.select())
            input_text = self.app.input_tabs[current_input_tab].text.get("1.0", tk.END).strip()
            
            if not input_text:
                return "Error: No cron expression provided."
            
            count = int(self.next_runs_var.get())
            
            result = f"Next {count} Scheduled Runs\n"
            result += "=" * 30 + "\n\n"
            result += f"Expression: {input_text}\n\n"
            
            next_runs = self._calculate_next_runs(input_text, count)
            
            result += "Scheduled Times:\n"
            for i, run_time in enumerate(next_runs, 1):
                result += f"{i:2}. {run_time.strftime('%Y-%m-%d %H:%M:%S')} ({run_time.strftime('%A')})\n"
            
            # Add time until next run
            if next_runs:
                next_run = next_runs[0]
                now = datetime.now()
                time_diff = next_run - now
                
                days = time_diff.days
                hours, remainder = divmod(time_diff.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                result += f"\nTime until next run: "
                if days > 0:
                    result += f"{days} days, "
                result += f"{hours:02d}:{minutes:02d}:{seconds:02d}\n"
            
            return result
            
        except Exception as e:
            return f"Error calculating next runs: {e}"
    
    def _calculate_next_runs(self, cron_expr, count):
        """Calculate next run times for cron expression."""
        parts = cron_expr.split()
        if len(parts) != 5:
            return []
        
        minute, hour, day, month, weekday = parts
        
        runs = []
        current = datetime.now().replace(second=0, microsecond=0) + timedelta(minutes=1)
        
        # Simple implementation - can be enhanced for complex expressions
        attempts = 0
        max_attempts = count * 1000  # Prevent infinite loops
        
        while len(runs) < count and attempts < max_attempts:
            attempts += 1
            
            if self._matches_cron(current, minute, hour, day, month, weekday):
                runs.append(current)
            
            current += timedelta(minutes=1)
        
        return runs
    
    def _matches_cron(self, dt, minute, hour, day, month, weekday):
        """Check if datetime matches cron expression."""
        # Check minute
        if not self._matches_field(dt.minute, minute, 0, 59):
            return False
        
        # Check hour
        if not self._matches_field(dt.hour, hour, 0, 23):
            return False
        
        # Check month
        if not self._matches_field(dt.month, month, 1, 12):
            return False
        
        # Check day and weekday (OR condition)
        day_match = self._matches_field(dt.day, day, 1, 31)
        weekday_match = self._matches_field(dt.weekday() + 1 % 7, weekday, 0, 7)  # Convert to Sunday=0
        
        if day == "*" and weekday == "*":
            return True
        elif day == "*":
            return weekday_match
        elif weekday == "*":
            return day_match
        else:
            return day_match or weekday_match
    
    def _matches_field(self, value, pattern, min_val, max_val):
        """Check if value matches cron field pattern."""
        if pattern == "*":
            return True
        
        if pattern.startswith("*/"):
            step = int(pattern[2:])
            return value % step == 0
        
        for part in pattern.split(","):
            if "-" in part:
                start, end = map(int, part.split("-"))
                if start <= value <= end:
                    return True
            else:
                if value == int(part):
                    return True
        
        return False
    
    def show_presets_library(self):
        """Show common cron patterns library."""
        result = "Common Cron Patterns Library\n"
        result += "=" * 35 + "\n\n"
        
        for category, patterns in self.cron_presets.items():
            result += f"{category}:\n"
            result += "-" * len(category) + "\n"
            
            for name, expression in patterns.items():
                result += f"  {name:25} → {expression}\n"
            
            result += "\n"
        
        result += "Usage Instructions:\n"
        result += "1. Select a category from the dropdown\n"
        result += "2. Choose a pattern\n"
        result += "3. Click 'Generate Expression' to create the cron expression\n"
        result += "4. Use 'Parse and Explain' to understand any expression\n"
        
        return result
    
    def compare_expressions(self):
        """Compare multiple cron expressions."""
        try:
            expressions_text = self.compare_text.get("1.0", tk.END).strip()
            
            if not expressions_text:
                return "Error: No expressions provided for comparison."
            
            expressions = [expr.strip() for expr in expressions_text.split('\n') if expr.strip()]
            
            if len(expressions) < 2:
                return "Error: Please provide at least 2 expressions to compare."
            
            result = f"Cron Expression Comparison\n"
            result += "=" * 30 + "\n\n"
            
            # Validate all expressions first
            valid_expressions = []
            for i, expr in enumerate(expressions, 1):
                parts = expr.split()
                if len(parts) == 5:
                    valid_expressions.append((i, expr))
                    result += f"Expression {i}: {expr} ✅\n"
                else:
                    result += f"Expression {i}: {expr} ❌ (Invalid format)\n"
            
            result += "\n"
            
            if len(valid_expressions) < 2:
                result += "Error: Need at least 2 valid expressions to compare.\n"
                return result
            
            # Calculate next runs for each valid expression
            result += "Next 5 Runs Comparison:\n"
            result += "-" * 25 + "\n"
            
            all_runs = {}
            for expr_num, expr in valid_expressions:
                runs = self._calculate_next_runs(expr, 5)
                all_runs[expr_num] = runs
                result += f"\nExpression {expr_num} ({expr}):\n"
                for i, run_time in enumerate(runs, 1):
                    result += f"  {i}. {run_time.strftime('%Y-%m-%d %H:%M:%S %A')}\n"
            
            # Find overlaps
            result += "\nOverlap Analysis:\n"
            result += "-" * 16 + "\n"
            
            overlaps_found = False
            for i, (expr1_num, expr1) in enumerate(valid_expressions):
                for j, (expr2_num, expr2) in enumerate(valid_expressions[i+1:], i+1):
                    runs1 = set(run.replace(second=0, microsecond=0) for run in all_runs[expr1_num])
                    runs2 = set(run.replace(second=0, microsecond=0) for run in all_runs[expr2_num])
                    
                    overlaps = runs1.intersection(runs2)
                    if overlaps:
                        overlaps_found = True
                        result += f"\n⚠️  Overlap between Expression {expr1_num} and {expr2_num}:\n"
                        for overlap in sorted(overlaps):
                            result += f"   {overlap.strftime('%Y-%m-%d %H:%M:%S %A')}\n"
            
            if not overlaps_found:
                result += "✅ No overlaps detected in the next 5 runs.\n"
            
            return result
            
        except Exception as e:
            return f"Error comparing expressions: {e}"
    
    def get_settings(self):
        """Get current settings."""
        return {
            "action": self.action_var.get(),
            "preset_category": self.preset_category_var.get(),
            "preset_pattern": self.preset_pattern_var.get(),
            "compare_expressions": self.compare_text.get("1.0", tk.END).strip(),
            "next_runs_count": self.next_runs_var.get()
        }


# Static cron parsing functions for BaseTool
def _explain_cron_static(expression):
    """Explain a cron expression without UI dependencies."""
    parts = expression.strip().split()
    if len(parts) != 5:
        return f"Invalid cron expression: expected 5 fields, got {len(parts)}"
    
    minute, hour, day, month, weekday = parts
    field_names = ["minute", "hour", "day of month", "month", "day of week"]
    
    def explain_field(field, field_type):
        if field == "*":
            return f"every {field_type}"
        elif field.startswith("*/"):
            return f"every {field[2:]} {field_type}s"
        elif "," in field:
            return f"at {field_type}s {field}"
        elif "-" in field:
            return f"{field_type}s {field}"
        else:
            return f"at {field_type} {field}"
    
    explanations = []
    for i, (field, name) in enumerate(zip(parts, field_names)):
        if field != "*":
            explanations.append(explain_field(field, name))
    
    if not explanations:
        return "Runs every minute"
    
    return "Runs " + ", ".join(explanations)


def _validate_cron_static(expression):
    """Validate a cron expression without UI dependencies."""
    parts = expression.strip().split()
    if len(parts) != 5:
        return f"✗ Invalid: expected 5 fields, got {len(parts)}"
    
    ranges = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 7)]
    field_names = ["minute", "hour", "day", "month", "weekday"]
    
    for i, (field, (min_val, max_val), name) in enumerate(zip(parts, ranges, field_names)):
        if field == "*":
            continue
        if field.startswith("*/"):
            try:
                int(field[2:])
            except ValueError:
                return f"✗ Invalid {name}: {field}"
        elif field.isdigit():
            val = int(field)
            if not (min_val <= val <= max_val):
                return f"✗ Invalid {name}: {val} not in range {min_val}-{max_val}"
    
    return "✓ Valid cron expression"


# BaseTool-compatible wrapper
try:
    from tools.base_tool import ToolWithOptions
    from typing import Dict, Any
    
    class CronToolV2(ToolWithOptions):
        """
        BaseTool-compatible version of CronTool.
        """
        
        TOOL_NAME = "Cron Tool"
        TOOL_DESCRIPTION = "Parse and explain cron expressions"
        TOOL_VERSION = "2.0.0"
        
        OPTIONS = [
            ("Explain", "explain"),
            ("Validate", "validate"),
        ]
        OPTIONS_LABEL = "Action"
        DEFAULT_OPTION = "explain"
        
        def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
            """Process cron expression."""
            mode = settings.get("mode", "explain")
            
            if mode == "explain":
                return _explain_cron_static(input_text)
            elif mode == "validate":
                return _validate_cron_static(input_text)
            else:
                return input_text

except ImportError:
    pass