import tkinter as tk
from tkinter import ttk, messagebox
import json
import xml.etree.ElementTree as ET
import xml.dom.minidom
import re
from collections import OrderedDict

try:
    import jsonpath_ng
    JSONPATH_AVAILABLE = True
except ImportError:
    JSONPATH_AVAILABLE = False

try:
    import lxml.etree as lxml_ET
    LXML_AVAILABLE = True
except ImportError:
    LXML_AVAILABLE = False

class JSONXMLTool:
    def __init__(self, parent_app):
        self.app = parent_app
        self.logger = parent_app.logger if hasattr(parent_app, 'logger') else None
        
    def get_default_settings(self):
        """Return default settings for the JSON/XML tool."""
        return {
            "operation": "json_to_xml",
            "json_indent": 2,
            "xml_indent": 2,
            "preserve_attributes": True,
            "sort_keys": False,
            "array_wrapper": "item",
            "root_element": "root",
            "jsonpath_query": "$",
            "xpath_query": "//*"
        }
    
    def create_widgets(self, parent, settings):
        """Create the JSON/XML tool interface."""
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Store reference for font application
        self.main_frame = main_frame
        
        # Top row: Operation and Settings side by side
        top_row_frame = ttk.Frame(main_frame)
        top_row_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Left side - Operation selection
        operation_frame = ttk.LabelFrame(top_row_frame, text="Operation")
        operation_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.operation_var = tk.StringVar(value=settings.get("operation", "json_to_xml"))
        
        operations = [
            ("json_to_xml", "JSON to XML"),
            ("xml_to_json", "XML to JSON"),
            ("json_prettify", "JSON Prettify"),
            ("xml_prettify", "XML Prettify"),
            ("json_validate", "JSON Validate"),
            ("xml_validate", "XML Validate"),
            ("json_minify", "JSON Minify"),
            ("xml_minify", "XML Minify"),
            ("jsonpath_query", "JSONPath Query"),
            ("xpath_query", "XPath Query")
        ]
        
        # Create operation buttons in a grid
        for i, (value, text) in enumerate(operations):
            row = i // 2
            col = i % 2
            ttk.Radiobutton(operation_frame, text=text, variable=self.operation_var, 
                          value=value, command=self.on_operation_change).grid(
                          row=row, column=col, sticky="w", padx=5, pady=2)
        
        # Right side - Settings frame
        settings_frame = ttk.LabelFrame(top_row_frame, text="Settings")
        settings_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # JSON/XML formatting settings
        format_frame = ttk.Frame(settings_frame)
        format_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(format_frame, text="JSON Indent:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.json_indent_var = tk.StringVar(value=str(settings.get("json_indent", 2)))
        ttk.Spinbox(format_frame, from_=0, to=8, width=5, textvariable=self.json_indent_var).grid(row=0, column=1, sticky="w", padx=(0, 10))
        
        ttk.Label(format_frame, text="XML Indent:").grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.xml_indent_var = tk.StringVar(value=str(settings.get("xml_indent", 2)))
        ttk.Spinbox(format_frame, from_=0, to=8, width=5, textvariable=self.xml_indent_var).grid(row=0, column=3, sticky="w")
        
        # Element naming
        naming_frame = ttk.Frame(settings_frame)
        naming_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(naming_frame, text="Array Item Name:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.array_wrapper_var = tk.StringVar(value=settings.get("array_wrapper", "item"))
        ttk.Entry(naming_frame, textvariable=self.array_wrapper_var, width=8).grid(row=0, column=1, sticky="w", padx=(0, 10))
        
        ttk.Label(naming_frame, text="Root Element:").grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.root_element_var = tk.StringVar(value=settings.get("root_element", "root"))
        ttk.Entry(naming_frame, textvariable=self.root_element_var, width=8).grid(row=0, column=3, sticky="w")
        
        # Options frame (full width below)
        options_frame = ttk.LabelFrame(main_frame, text="Options")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Conversion options and AI generation buttons
        options_content_frame = ttk.Frame(options_frame)
        options_content_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Left side - checkboxes
        checkbox_frame = ttk.Frame(options_content_frame)
        checkbox_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.preserve_attributes_var = tk.BooleanVar(value=settings.get("preserve_attributes", True))
        ttk.Checkbutton(checkbox_frame, text="Preserve XML Attributes", 
                       variable=self.preserve_attributes_var).pack(anchor="w", pady=2)
        
        self.sort_keys_var = tk.BooleanVar(value=settings.get("sort_keys", False))
        ttk.Checkbutton(checkbox_frame, text="Sort JSON Keys", 
                       variable=self.sort_keys_var).pack(anchor="w", pady=2)
        
        # Right side - AI generation buttons
        ai_frame = ttk.Frame(options_content_frame)
        ai_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Button(ai_frame, text="Generate JSON with AI", 
                  command=self.generate_json_with_ai).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(ai_frame, text="Generate XML with AI", 
                  command=self.generate_xml_with_ai).pack(side=tk.LEFT)
        
        # Query frame (for JSONPath and XPath)
        self.query_frame = ttk.LabelFrame(main_frame, text="Query")
        self.query_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.query_frame, text="JSONPath:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.jsonpath_var = tk.StringVar(value=settings.get("jsonpath_query", "$"))
        ttk.Entry(self.query_frame, textvariable=self.jsonpath_var, width=40).grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        ttk.Label(self.query_frame, text="XPath:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.xpath_var = tk.StringVar(value=settings.get("xpath_query", "//*"))
        ttk.Entry(self.query_frame, textvariable=self.xpath_var, width=40).grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        self.query_frame.columnconfigure(1, weight=1)
        
        # Process button
        process_frame = ttk.Frame(main_frame)
        process_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(process_frame, text="Process", command=self.process_data).pack(side=tk.LEFT)
        
        # Status label
        self.status_label = ttk.Label(process_frame, text="Ready", foreground="green")
        self.status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Initially hide query frame
        self.on_operation_change()
        
        # Apply current font settings if available
        try:
            if hasattr(self.app, 'get_best_font'):
                text_font_family, text_font_size = self.app.get_best_font("text")
                font_tuple = (text_font_family, text_font_size)
                
                # Apply to Entry widgets
                for child in main_frame.winfo_children():
                    self._apply_font_to_children(child, font_tuple)
        except:
            pass  # Use default font if font settings not available
        
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
        """Apply font to all Entry widgets in the tool."""
        try:
            # Apply to the main frame and all its children
            if hasattr(self, 'main_frame'):
                self._apply_font_to_children(self.main_frame, font_tuple)
        except Exception as e:
            if self.logger:
                self.logger.debug(f"Error applying font to JSON/XML tool widgets: {e}")
    
    def generate_json_with_ai(self):
        """Switch to AI Tools and generate JSON with AI."""
        try:
            # Switch to AI Tools
            self.app.tool_var.set("AI Tools")
            self.app.on_tool_selected()
            
            # Find next empty input tab
            next_tab = self._find_next_empty_tab()
            if next_tab is not None:
                # Switch to the empty tab
                self.app.input_notebook.select(next_tab)
                
                # Insert the prompt
                prompt = "Please generate Identity JSON file"
                self.app.input_tabs[next_tab].text.delete("1.0", tk.END)
                self.app.input_tabs[next_tab].text.insert("1.0", prompt)
                
                if self.logger:
                    self.logger.info("Switched to AI Tools with JSON generation prompt")
            else:
                # Use current tab if no empty tab found
                current_tab = self.app.input_notebook.index(self.app.input_notebook.select())
                prompt = "Please generate Identity JSON file"
                self.app.input_tabs[current_tab].text.delete("1.0", tk.END)
                self.app.input_tabs[current_tab].text.insert("1.0", prompt)
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error switching to AI Tools for JSON generation: {e}")
    
    def generate_xml_with_ai(self):
        """Switch to AI Tools and generate XML with AI."""
        try:
            # Switch to AI Tools
            self.app.tool_var.set("AI Tools")
            self.app.on_tool_selected()
            
            # Find next empty input tab
            next_tab = self._find_next_empty_tab()
            if next_tab is not None:
                # Switch to the empty tab
                self.app.input_notebook.select(next_tab)
                
                # Insert the prompt
                prompt = "Please generate Identity XML file"
                self.app.input_tabs[next_tab].text.delete("1.0", tk.END)
                self.app.input_tabs[next_tab].text.insert("1.0", prompt)
                
                if self.logger:
                    self.logger.info("Switched to AI Tools with XML generation prompt")
            else:
                # Use current tab if no empty tab found
                current_tab = self.app.input_notebook.index(self.app.input_notebook.select())
                prompt = "Please generate Identity XML file"
                self.app.input_tabs[current_tab].text.delete("1.0", tk.END)
                self.app.input_tabs[current_tab].text.insert("1.0", prompt)
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error switching to AI Tools for XML generation: {e}")
    
    def _find_next_empty_tab(self):
        """Find the next empty input tab."""
        try:
            for i, tab in enumerate(self.app.input_tabs):
                content = tab.text.get("1.0", tk.END).strip()
                if not content:
                    return i
            return None
        except:
            return None
    
    def on_operation_change(self):
        """Handle operation selection change."""
        operation = self.operation_var.get()
        
        # Show/hide query frame based on operation
        if operation in ["jsonpath_query", "xpath_query"]:
            self.query_frame.pack(fill=tk.X, pady=(0, 10))
        else:
            self.query_frame.pack_forget()
    
    def process_data(self):
        """Process the data based on selected operation."""
        try:
            # Get input text from current active input tab
            current_input_tab = self.app.input_notebook.index(self.app.input_notebook.select())
            input_text = self.app.input_tabs[current_input_tab].text.get("1.0", tk.END).strip()
            if not input_text:
                self.status_label.config(text="Error: No input text", foreground="red")
                return
            
            operation = self.operation_var.get()
            result = ""
            
            if operation == "json_to_xml":
                result = self.json_to_xml(input_text)
            elif operation == "xml_to_json":
                result = self.xml_to_json(input_text)
            elif operation == "json_prettify":
                result = self.json_prettify(input_text)
            elif operation == "xml_prettify":
                result = self.xml_prettify(input_text)
            elif operation == "json_validate":
                result = self.json_validate(input_text)
            elif operation == "xml_validate":
                result = self.xml_validate(input_text)
            elif operation == "json_minify":
                result = self.json_minify(input_text)
            elif operation == "xml_minify":
                result = self.xml_minify(input_text)
            elif operation == "jsonpath_query":
                result = self.jsonpath_query(input_text)
            elif operation == "xpath_query":
                result = self.xpath_query(input_text)
            
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
                self.logger.error(f"JSON/XML Tool error: {e}")
    
    def json_to_xml(self, json_text):
        """Convert JSON to XML."""
        try:
            data = json.loads(json_text)
            root_name = self.root_element_var.get() or "root"
            
            root = ET.Element(root_name)
            self._dict_to_xml(data, root)
            
            # Pretty print
            rough_string = ET.tostring(root, encoding='unicode')
            reparsed = xml.dom.minidom.parseString(rough_string)
            indent = " " * int(self.xml_indent_var.get())
            return reparsed.toprettyxml(indent=indent).split('\n', 1)[1]  # Remove XML declaration
            
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON: {e}")
        except Exception as e:
            raise Exception(f"JSON to XML conversion failed: {e}")
    
    def _dict_to_xml(self, data, parent):
        """Recursively convert dictionary to XML elements."""
        if isinstance(data, dict):
            for key, value in data.items():
                if key.startswith('@') and self.preserve_attributes_var.get():
                    # Handle attributes
                    parent.set(key[1:], str(value))
                else:
                    element = ET.SubElement(parent, self._sanitize_xml_name(key))
                    self._dict_to_xml(value, element)
        elif isinstance(data, list):
            array_name = self.array_wrapper_var.get() or "item"
            for item in data:
                element = ET.SubElement(parent, array_name)
                self._dict_to_xml(item, element)
        else:
            parent.text = str(data)
    
    def _sanitize_xml_name(self, name):
        """Sanitize name for XML element."""
        # Replace invalid characters with underscores
        name = re.sub(r'[^a-zA-Z0-9_-]', '_', str(name))
        # Ensure it starts with a letter or underscore
        if name and not name[0].isalpha() and name[0] != '_':
            name = '_' + name
        return name or 'element'
    
    def xml_to_json(self, xml_text):
        """Convert XML to JSON."""
        try:
            root = ET.fromstring(xml_text)
            data = self._xml_to_dict(root)
            
            indent = int(self.json_indent_var.get()) if self.json_indent_var.get() != "0" else None
            sort_keys = self.sort_keys_var.get()
            
            return json.dumps(data, indent=indent, sort_keys=sort_keys, ensure_ascii=False)
            
        except ET.ParseError as e:
            raise Exception(f"Invalid XML: {e}")
        except Exception as e:
            raise Exception(f"XML to JSON conversion failed: {e}")
    
    def _xml_to_dict(self, element):
        """Recursively convert XML element to dictionary."""
        result = {}
        
        # Add attributes with @ prefix if preserving attributes
        if element.attrib and self.preserve_attributes_var.get():
            for key, value in element.attrib.items():
                result[f'@{key}'] = value
        
        # Handle child elements
        children = list(element)
        if children:
            child_dict = {}
            for child in children:
                child_data = self._xml_to_dict(child)
                if child.tag in child_dict:
                    # Convert to array if multiple elements with same tag
                    if not isinstance(child_dict[child.tag], list):
                        child_dict[child.tag] = [child_dict[child.tag]]
                    child_dict[child.tag].append(child_data)
                else:
                    child_dict[child.tag] = child_data
            result.update(child_dict)
        
        # Handle text content
        if element.text and element.text.strip():
            if result:  # If we have attributes or children, use special key for text
                result['#text'] = element.text.strip()
            else:  # If no attributes or children, return text directly
                return element.text.strip()
        
        return result if result else None
    
    def json_prettify(self, json_text):
        """Prettify JSON."""
        try:
            data = json.loads(json_text)
            indent = int(self.json_indent_var.get()) if self.json_indent_var.get() != "0" else None
            sort_keys = self.sort_keys_var.get()
            
            return json.dumps(data, indent=indent, sort_keys=sort_keys, ensure_ascii=False)
            
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON: {e}")
    
    def xml_prettify(self, xml_text):
        """Prettify XML."""
        try:
            root = ET.fromstring(xml_text)
            rough_string = ET.tostring(root, encoding='unicode')
            reparsed = xml.dom.minidom.parseString(rough_string)
            indent = " " * int(self.xml_indent_var.get())
            
            pretty = reparsed.toprettyxml(indent=indent)
            # Remove empty lines and clean up
            lines = [line for line in pretty.split('\n') if line.strip()]
            return '\n'.join(lines)
            
        except ET.ParseError as e:
            raise Exception(f"Invalid XML: {e}")
    
    def json_validate(self, json_text):
        """Validate JSON and return detailed results."""
        try:
            data = json.loads(json_text)
            
            # Basic validation info
            result = "✅ JSON is valid!\n\n"
            result += f"Type: {type(data).__name__}\n"
            
            if isinstance(data, dict):
                result += f"Keys: {len(data)}\n"
                result += f"Top-level keys: {list(data.keys())[:10]}"  # Show first 10 keys
                if len(data) > 10:
                    result += f" ... and {len(data) - 10} more"
            elif isinstance(data, list):
                result += f"Items: {len(data)}\n"
                if data:
                    result += f"First item type: {type(data[0]).__name__}"
            
            result += f"\n\nFormatted JSON:\n{json.dumps(data, indent=2, ensure_ascii=False)}"
            
            return result
            
        except json.JSONDecodeError as e:
            return f"❌ Invalid JSON!\n\nError: {e}\n\nLine {e.lineno}, Column {e.colno}\n\nTip: Check for missing quotes, commas, or brackets around the error location."
    
    def xml_validate(self, xml_text):
        """Validate XML and return detailed results."""
        try:
            root = ET.fromstring(xml_text)
            
            result = "✅ XML is valid!\n\n"
            result += f"Root element: <{root.tag}>\n"
            result += f"Attributes: {len(root.attrib)}\n"
            result += f"Child elements: {len(list(root))}\n"
            
            # Count all elements
            all_elements = root.findall('.//*')
            result += f"Total elements: {len(all_elements) + 1}\n"  # +1 for root
            
            # Show element types
            element_types = {}
            for elem in [root] + all_elements:
                element_types[elem.tag] = element_types.get(elem.tag, 0) + 1
            
            result += f"\nElement types:\n"
            for tag, count in sorted(element_types.items()):
                result += f"  <{tag}>: {count}\n"
            
            return result
            
        except ET.ParseError as e:
            return f"❌ Invalid XML!\n\nError: {e}\n\nSuggestions:\n- Check for unclosed tags\n- Ensure proper nesting\n- Verify attribute quotes\n- Check for invalid characters in element names"
    
    def json_minify(self, json_text):
        """Minify JSON by removing whitespace."""
        try:
            data = json.loads(json_text)
            return json.dumps(data, separators=(',', ':'), ensure_ascii=False)
            
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON: {e}")
    
    def xml_minify(self, xml_text):
        """Minify XML by removing whitespace."""
        try:
            root = ET.fromstring(xml_text)
            
            # Remove whitespace from all elements
            for elem in root.iter():
                if elem.text:
                    elem.text = elem.text.strip() or None
                if elem.tail:
                    elem.tail = elem.tail.strip() or None
            
            return ET.tostring(root, encoding='unicode')
            
        except ET.ParseError as e:
            raise Exception(f"Invalid XML: {e}")
    
    def jsonpath_query(self, json_text):
        """Execute JSONPath query."""
        if not JSONPATH_AVAILABLE:
            return "❌ JSONPath not available. Install with: pip install jsonpath-ng"
        
        try:
            data = json.loads(json_text)
            query = self.jsonpath_var.get() or "$"
            
            from jsonpath_ng import parse
            jsonpath_expr = parse(query)
            matches = jsonpath_expr.find(data)
            
            result = f"JSONPath Query: {query}\n"
            result += f"Matches found: {len(matches)}\n\n"
            
            if matches:
                for i, match in enumerate(matches):
                    result += f"Match {i + 1}:\n"
                    result += f"  Path: {match.full_path}\n"
                    result += f"  Value: {json.dumps(match.value, indent=2, ensure_ascii=False)}\n\n"
            else:
                result += "No matches found."
            
            return result
            
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON: {e}")
        except Exception as e:
            raise Exception(f"JSONPath query failed: {e}")
    
    def xpath_query(self, xml_text):
        """Execute XPath query."""
        try:
            if LXML_AVAILABLE:
                # Use lxml for better XPath support
                root = lxml_ET.fromstring(xml_text.encode())
                query = self.xpath_var.get() or "//*"
                matches = root.xpath(query)
            else:
                # Fallback to basic ElementTree (limited XPath support)
                root = ET.fromstring(xml_text)
                query = self.xpath_var.get() or ".//*"
                matches = root.findall(query)
            
            result = f"XPath Query: {query}\n"
            result += f"Matches found: {len(matches)}\n\n"
            
            if matches:
                for i, match in enumerate(matches):
                    result += f"Match {i + 1}:\n"
                    if hasattr(match, 'tag'):
                        result += f"  Element: <{match.tag}>\n"
                        if match.attrib:
                            result += f"  Attributes: {match.attrib}\n"
                        if match.text and match.text.strip():
                            result += f"  Text: {match.text.strip()}\n"
                    else:
                        result += f"  Value: {match}\n"
                    result += "\n"
            else:
                result += "No matches found."
            
            if not LXML_AVAILABLE:
                result += "\n\nNote: Using basic XPath support. Install lxml for advanced XPath features: pip install lxml"
            
            return result
            
        except ET.ParseError as e:
            raise Exception(f"Invalid XML: {e}")
        except Exception as e:
            raise Exception(f"XPath query failed: {e}")
    
    def get_settings(self):
        """Get current settings."""
        return {
            "operation": self.operation_var.get(),
            "json_indent": self.json_indent_var.get(),
            "xml_indent": self.xml_indent_var.get(),
            "preserve_attributes": self.preserve_attributes_var.get(),
            "sort_keys": self.sort_keys_var.get(),
            "array_wrapper": self.array_wrapper_var.get(),
            "root_element": self.root_element_var.get(),
            "jsonpath_query": self.jsonpath_var.get(),
            "xpath_query": self.xpath_var.get()
        }


# Static utility functions for BaseTool
def _json_prettify_static(text, indent=2):
    """Prettify JSON without UI dependencies."""
    try:
        data = json.loads(text)
        return json.dumps(data, indent=indent, ensure_ascii=False)
    except json.JSONDecodeError as e:
        return f"Invalid JSON: {e}"

def _json_minify_static(text):
    """Minify JSON without UI dependencies."""
    try:
        data = json.loads(text)
        return json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    except json.JSONDecodeError as e:
        return f"Invalid JSON: {e}"

def _json_validate_static(text):
    """Validate JSON without UI dependencies."""
    try:
        json.loads(text)
        return "✓ Valid JSON"
    except json.JSONDecodeError as e:
        return f"✗ Invalid JSON: {e}"

def _xml_prettify_static(text, indent=2):
    """Prettify XML without UI dependencies."""
    try:
        root = ET.fromstring(text)
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = xml.dom.minidom.parseString(rough_string)
        pretty = reparsed.toprettyxml(indent=" " * indent)
        lines = [line for line in pretty.split('\n') if line.strip()]
        return '\n'.join(lines)
    except ET.ParseError as e:
        return f"Invalid XML: {e}"

def _xml_minify_static(text):
    """Minify XML without UI dependencies."""
    try:
        root = ET.fromstring(text)
        return ET.tostring(root, encoding='unicode')
    except ET.ParseError as e:
        return f"Invalid XML: {e}"

def _xml_validate_static(text):
    """Validate XML without UI dependencies."""
    try:
        ET.fromstring(text)
        return "✓ Valid XML"
    except ET.ParseError as e:
        return f"✗ Invalid XML: {e}"


# BaseTool-compatible wrapper
try:
    from tools.base_tool import ToolWithOptions
    from typing import Dict, Any
    
    class JSONXMLToolV2(ToolWithOptions):
        """
        BaseTool-compatible version of JSONXMLTool.
        """
        
        TOOL_NAME = "JSON/XML Tool"
        TOOL_DESCRIPTION = "Convert, prettify, minify, and validate JSON/XML"
        TOOL_VERSION = "2.0.0"
        
        OPTIONS = [
            ("JSON Prettify", "json_prettify"),
            ("JSON Minify", "json_minify"),
            ("JSON Validate", "json_validate"),
            ("XML Prettify", "xml_prettify"),
            ("XML Minify", "xml_minify"),
            ("XML Validate", "xml_validate"),
        ]
        OPTIONS_LABEL = "Operation"
        USE_DROPDOWN = True
        DEFAULT_OPTION = "json_prettify"
        
        def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
            """Process text using the specified JSON/XML operation."""
            mode = settings.get("mode", "json_prettify")
            indent = settings.get("indent", 2)
            
            if mode == "json_prettify":
                return _json_prettify_static(input_text, indent)
            elif mode == "json_minify":
                return _json_minify_static(input_text)
            elif mode == "json_validate":
                return _json_validate_static(input_text)
            elif mode == "xml_prettify":
                return _xml_prettify_static(input_text, indent)
            elif mode == "xml_minify":
                return _xml_minify_static(input_text)
            elif mode == "xml_validate":
                return _xml_validate_static(input_text)
            else:
                return input_text

except ImportError:
    pass