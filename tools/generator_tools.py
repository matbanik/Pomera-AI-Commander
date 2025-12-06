"""
Generator Tools Module for Promera AI Commander

This module provides various text generation tools including:
- Strong Password Generator
- Repeating Text Generator
- Lorem Ipsum Generator
- UUID/GUID Generator

Author: Promera AI Commander
"""

import tkinter as tk
from tkinter import ttk
import string
import random
import json
import uuid
import base64
import hashlib


class GeneratorTools:
    """A class containing various text generation tools."""
    
    def __init__(self):
        """Initialize the GeneratorTools class."""
        self.tools = {
            "Strong Password Generator": self.strong_password,
            "Repeating Text Generator": self.repeating_text,
            "Lorem Ipsum Generator": self.lorem_ipsum,
            "UUID/GUID Generator": self.uuid_generator,
            "Random Email Generator": self.random_email_generator
        }
    
    def get_available_tools(self):
        """Returns a list of available generator tools."""
        return list(self.tools.keys())
    
    def get_default_settings(self):
        """Returns default settings for all generator tools."""
        return {
            "Strong Password Generator": {"length": 20, "numbers": "", "symbols": "", "letters_percent": 70, "numbers_percent": 20, "symbols_percent": 10},
            "Repeating Text Generator": {"times": 5, "separator": "+"},
            "Lorem Ipsum Generator": {"count": 5, "type": "paragraphs", "format": "plain", "ordered": False},
            "UUID/GUID Generator": {"version": 4, "format": "standard", "case": "lowercase", "count": 1, "namespace": "dns", "name": ""},
            "Random Email Generator": {"count": 5, "separator_type": "list", "separator": ",", "domain_type": "random", "domain": "example.com"},
            "ASCII Art Generator": {"font": "standard", "width": 80},
            "Hash Generator": {"algorithms": ["md5", "sha256"], "uppercase": False},
            "Slug Generator": {"separator": "-", "lowercase": True, "transliterate": True, "max_length": 0, "remove_stopwords": False}
        }
    
    def process_text(self, input_text, tool_name, settings):
        """Process text using the specified generator tool."""
        if tool_name not in self.tools:
            return f"Error: Unknown tool '{tool_name}'"
        
        return self.tools[tool_name](input_text, settings)
    
    @staticmethod
    def strong_password(input_text, settings):
        """Generates a strong, random password with specified character distribution."""
        length = settings.get("length", 20)
        numbers = settings.get("numbers", "")
        symbols = settings.get("symbols", "")
        letters_percent = settings.get("letters_percent", 70)
        numbers_percent = settings.get("numbers_percent", 20)
        symbols_percent = settings.get("symbols_percent", 10)
        
        if not isinstance(length, int) or length <= 0:
            return "Error: Password length must be a positive number."
        
        # Validate percentages
        total_percent = letters_percent + numbers_percent + symbols_percent
        if total_percent != 100:
            return "Error: Percentages must add up to 100%."
        
        # Character sets
        letters = string.ascii_letters
        digits = string.digits
        special_chars = string.punctuation
        
        # Calculate character counts with ±5% approximation
        def calculate_count(percent, total_length):
            base_count = int((percent / 100) * total_length)
            # Allow ±5% variation (rounded to nearest integer)
            variation = max(1, int(0.05 * total_length))
            min_count = max(0, base_count - variation)
            max_count = min(total_length, base_count + variation)
            return random.randint(min_count, max_count)
        
        letters_count = calculate_count(letters_percent, length)
        numbers_count = calculate_count(numbers_percent, length)
        symbols_count = length - letters_count - numbers_count
        
        # Ensure we don't exceed total length
        if symbols_count < 0:
            # Adjust if we went over
            excess = abs(symbols_count)
            if letters_count >= excess:
                letters_count -= excess
                symbols_count = 0
            else:
                numbers_count -= (excess - letters_count)
                letters_count = 0
                symbols_count = 0
        
        # Generate password parts
        password_chars = []
        
        # Add letters
        password_chars.extend(random.choices(letters, k=letters_count))
        
        # Add numbers
        password_chars.extend(random.choices(digits, k=numbers_count))
        
        # Add symbols
        password_chars.extend(random.choices(special_chars, k=symbols_count))
        
        # Ensure we have the exact length
        while len(password_chars) < length:
            password_chars.append(random.choice(letters + digits + special_chars))
        
        # Shuffle the password
        random.shuffle(password_chars)
        password = ''.join(password_chars)
        
        # Ensure included numbers and symbols are present
        must_include = numbers + symbols
        if must_include and len(must_include) <= length:
            password_list = list(password)
            for i, char in enumerate(must_include):
                if i < len(password_list):
                    password_list[i] = char
            random.shuffle(password_list)
            password = "".join(password_list)

        return password
    
    @staticmethod
    def repeating_text(input_text, settings):
        """Repeats the input text a specified number of times."""
        times = settings.get("times", 5)
        separator = settings.get("separator", "+")
        
        if not isinstance(times, int) or times < 0:
            return "Error: 'Times' must be a non-negative number."
        return separator.join([input_text] * times)
    
    @staticmethod
    def lorem_ipsum(input_text, settings):
        """Generates Lorem Ipsum text in various formats."""
        count = settings.get("count", 5)
        text_type = settings.get("type", "paragraphs")
        format_type = settings.get("format", "plain")
        ordered = settings.get("ordered", False)
        
        # Validation
        if not isinstance(count, int) or count <= 0:
            return "Error: Count must be a positive integer."
        
        if format_type not in ['plain', 'html', 'markdown', 'json']:
            return "Error: Format must be one of: 'plain', 'html', 'markdown', 'json'."
        
        # Lorem ipsum word bank
        lorem_words = [
            "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit",
            "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore",
            "magna", "aliqua", "enim", "ad", "minim", "veniam", "quis", "nostrud",
            "exercitation", "ullamco", "laboris", "nisi", "aliquip", "ex", "ea", "commodo",
            "consequat", "duis", "aute", "irure", "in", "reprehenderit", "voluptate",
            "velit", "esse", "cillum", "fugiat", "nulla", "pariatur", "excepteur", "sint",
            "occaecat", "cupidatat", "non", "proident", "sunt", "culpa", "qui", "officia",
            "deserunt", "mollit", "anim", "id", "est", "laborum", "at", "vero", "eos",
            "accusamus", "accusantium", "doloremque", "laudantium", "totam", "rem",
            "aperiam", "eaque", "ipsa", "quae", "ab", "illo", "inventore", "veritatis"
        ]
        
        def generate_sentence():
            """Generate a single sentence."""
            length = random.randint(8, 20)
            words = random.choices(lorem_words, k=length)
            words[0] = words[0].capitalize()
            return " ".join(words) + "."
        
        def generate_paragraph():
            """Generate a single paragraph."""
            sentences = [generate_sentence() for _ in range(random.randint(3, 8))]
            return " ".join(sentences)
        
        # Generate content based on type
        if text_type == "words":
            content = random.choices(lorem_words, k=count)
        elif text_type == "sentences":
            content = [generate_sentence() for _ in range(count)]
        elif text_type == "paragraphs":
            content = [generate_paragraph() for _ in range(count)]
        elif text_type == "bytes":
            # Generate text up to specified byte count
            text = ""
            while len(text.encode('utf-8')) < count:
                text += generate_sentence() + " "
            content = [text[:count]]
        else:
            return "Error: Invalid text type."
        
        # Format output
        if format_type == "plain":
            if text_type == "words":
                return " ".join(content)
            elif text_type == "sentences":
                return " ".join(content)
            elif text_type == "paragraphs":
                return "\n\n".join(content)
            else:  # bytes
                return content[0]
        
        elif format_type == "html":
            if text_type == "words":
                return "<span>" + " ".join(content) + "</span>"
            elif text_type == "sentences":
                if ordered:
                    items = "".join([f"<li>{sentence}</li>" for sentence in content])
                    return f"<ol>{items}</ol>"
                else:
                    items = "".join([f"<li>{sentence}</li>" for sentence in content])
                    return f"<ul>{items}</ul>"
            elif text_type == "paragraphs":
                paragraphs = "".join([f"<p>{para}</p>" for para in content])
                return paragraphs
            else:  # bytes
                return f"<div>{content[0]}</div>"
        
        elif format_type == "markdown":
            if text_type == "words":
                return " ".join(content)
            elif text_type == "sentences":
                if ordered:
                    items = "\n".join([f"{i+1}. {sentence}" for i, sentence in enumerate(content)])
                else:
                    items = "\n".join([f"- {sentence}" for sentence in content])
                return items
            elif text_type == "paragraphs":
                return "\n\n".join(content)
            else:  # bytes
                return content[0]
        
        elif format_type == "json":
            return json.dumps({
                "type": text_type,
                "count": len(content),
                "content": content
            }, indent=2)
        
        return "Error: Unknown format type."
    
    @staticmethod
    def uuid_generator(input_text, settings):
        """Generates UUID/GUID in various formats and versions."""
        version = settings.get("version", 4)
        format_type = settings.get("format", "standard")
        case = settings.get("case", "lowercase")
        count = settings.get("count", 1)
        namespace_name = settings.get("namespace", "dns")
        name = settings.get("name", "")
        
        # Validation
        if not isinstance(count, int) or count <= 0:
            return "Error: Count must be a positive integer."
        
        if version not in [1, 3, 4, 5]:
            return "Error: UUID version must be 1, 3, 4, or 5."
        
        if version in [3, 5] and not name:
            return "Error: Name is required for UUID versions 3 and 5."
        
        # Predefined namespaces
        namespaces = {
            "dns": uuid.NAMESPACE_DNS,
            "url": uuid.NAMESPACE_URL,
            "oid": uuid.NAMESPACE_OID,
            "x500": uuid.NAMESPACE_X500
        }
        
        def generate_single_uuid():
            """Generate a single UUID based on version."""
            if version == 1:
                return uuid.uuid1()
            elif version == 3:
                if namespace_name not in namespaces:
                    return None
                return uuid.uuid3(namespaces[namespace_name], name)
            elif version == 4:
                return uuid.uuid4()
            elif version == 5:
                if namespace_name not in namespaces:
                    return None
                return uuid.uuid5(namespaces[namespace_name], name)
        
        def format_uuid(uuid_obj):
            """Format UUID according to specified format and case."""
            if uuid_obj is None:
                return "Error: Invalid namespace."
            
            uuid_str = str(uuid_obj)
            
            # Apply case formatting
            if case == "uppercase":
                uuid_str = uuid_str.upper()
            elif case == "lowercase":
                uuid_str = uuid_str.lower()
            
            # Apply format
            if format_type == "standard":
                return uuid_str
            elif format_type == "hex":
                return uuid_str.replace("-", "")
            elif format_type == "microsoft":
                return "{" + uuid_str + "}"
            elif format_type == "urn":
                return "urn:uuid:" + uuid_str
            elif format_type == "base64":
                return base64.b64encode(uuid_obj.bytes).decode('ascii')
            elif format_type == "c_array":
                bytes_list = list(uuid_obj.bytes)
                hex_values = [f"0x{b:02x}" for b in bytes_list]
                # Format as C array with proper line breaks
                formatted = "{ " + ", ".join(hex_values[:8]) + ",\n  " + ", ".join(hex_values[8:]) + " }"
                return formatted
            elif format_type == "nil":
                return "00000000-0000-0000-0000-000000000000"
            else:
                return uuid_str
        
        # Generate UUIDs
        results = []
        for _ in range(count):
            if format_type == "nil":
                # Special case for nil UUID
                nil_uuid = uuid.UUID('00000000-0000-0000-0000-000000000000')
                results.append(format_uuid(nil_uuid))
            else:
                uuid_obj = generate_single_uuid()
                if uuid_obj is None:
                    return "Error: Invalid namespace for name-based UUID."
                results.append(format_uuid(uuid_obj))
        
        # Return results
        if count == 1:
            return results[0]
        else:
            return "\n".join(results)
    
    @staticmethod
    def random_email_generator(input_text, settings):
        """Generates random email addresses."""
        count = settings.get("count", 5)
        separator_type = settings.get("separator_type", "list")
        separator = settings.get("separator", ",")
        domain_type = settings.get("domain_type", "random")
        domain = settings.get("domain", "example.com")
        
        # Validation
        if not isinstance(count, int) or count <= 0:
            return "Error: Count must be a positive integer."
        
        # Common first names and last names for generating realistic emails
        first_names = [
            "john", "jane", "mike", "sarah", "david", "lisa", "chris", "anna", "james", "mary",
            "robert", "jennifer", "michael", "linda", "william", "elizabeth", "richard", "barbara",
            "joseph", "susan", "thomas", "jessica", "charles", "karen", "daniel", "nancy",
            "matthew", "betty", "anthony", "helen", "mark", "sandra", "donald", "donna",
            "steven", "carol", "paul", "ruth", "andrew", "sharon", "joshua", "michelle",
            "kenneth", "laura", "kevin", "sarah", "brian", "kimberly", "george", "deborah",
            "edward", "dorothy", "ronald", "lisa", "timothy", "nancy", "jason", "karen"
        ]
        
        last_names = [
            "smith", "johnson", "williams", "brown", "jones", "garcia", "miller", "davis",
            "rodriguez", "martinez", "hernandez", "lopez", "gonzalez", "wilson", "anderson",
            "thomas", "taylor", "moore", "jackson", "martin", "lee", "perez", "thompson",
            "white", "harris", "sanchez", "clark", "ramirez", "lewis", "robinson", "walker",
            "young", "allen", "king", "wright", "scott", "torres", "nguyen", "hill",
            "flores", "green", "adams", "nelson", "baker", "hall", "rivera", "campbell",
            "mitchell", "carter", "roberts", "gomez", "phillips", "evans", "turner", "diaz"
        ]
        
        # Common domain names for random domain generation
        random_domains = [
            "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com",
            "icloud.com", "protonmail.com", "mail.com", "zoho.com", "fastmail.com",
            "example.com", "test.com", "demo.org", "sample.net", "placeholder.io"
        ]
        
        def generate_single_email():
            """Generate a single random email address."""
            # Generate username part
            first = random.choice(first_names)
            last = random.choice(last_names)
            
            # Various username patterns
            patterns = [
                f"{first}.{last}",
                f"{first}{last}",
                f"{first}_{last}",
                f"{first}{random.randint(1, 999)}",
                f"{first}.{last}{random.randint(1, 99)}",
                f"{first[0]}{last}",
                f"{first}{last[0]}",
                f"{first}.{last[0]}",
                f"{first[0]}.{last}"
            ]
            
            username = random.choice(patterns)
            
            # Generate domain part
            if domain_type == "random":
                email_domain = random.choice(random_domains)
            else:
                email_domain = domain
            
            return f"{username}@{email_domain}"
        
        # Generate emails
        emails = []
        for _ in range(count):
            emails.append(generate_single_email())
        
        # Format output based on separator type
        if separator_type == "list":
            return "\n".join(emails)
        else:
            return separator.join(emails)


class GeneratorToolsWidget:
    """Widget for the Generator Tools tabbed interface."""
    
    def __init__(self, generator_tools):
        """Initialize the GeneratorToolsWidget."""
        self.generator_tools = generator_tools
        self.main_app = None
        
        # Variables for Strong Password Generator
        self.pw_len_var = None
        self.pw_num_var = None
        self.pw_sym_var = None
        self.pw_letters_percent_var = None
        self.pw_numbers_percent_var = None
        self.pw_symbols_percent_var = None
        
        # Variables for Repeating Text Generator
        self.repeat_times_var = None
        self.repeat_sep_var = None
        
        # Variables for Lorem Ipsum Generator
        self.lorem_count_var = None
        self.lorem_type_var = None
        self.lorem_format_var = None
        self.lorem_ordered_var = None
        
        # Variables for UUID/GUID Generator
        self.uuid_version_var = None
        self.uuid_format_var = None
        self.uuid_case_var = None
        self.uuid_count_var = None
        self.uuid_namespace_var = None
        self.uuid_name_var = None
        
        # Variables for Random Email Generator
        self.email_count_var = None
        self.email_separator_type_var = None
        self.email_separator_var = None
        self.email_domain_type_var = None
        self.email_domain_var = None
    
    def create_widget(self, parent, main_app):
        """Create and return the main widget."""
        self.main_app = main_app
        
        # Create main frame
        main_frame = ttk.Frame(parent)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.create_password_generator_tab()
        self.create_repeating_text_tab()
        self.create_lorem_ipsum_tab()
        self.create_uuid_generator_tab()
        self.create_email_generator_tab()
        self.create_ascii_art_generator_tab()
        self.create_hash_generator_tab()
        self.create_slug_generator_tab()
        
        return main_frame
    
    def create_password_generator_tab(self):
        """Create the Strong Password Generator tab."""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="Strong Password Generator")
        
        # Get current settings
        settings = self.main_app.settings["tool_settings"].get("Generator Tools", {}).get("Strong Password Generator", {})
        
        # Length setting
        length_frame = ttk.Frame(tab_frame)
        length_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(length_frame, text="Password Length:").pack(side=tk.LEFT)
        self.pw_len_var = tk.StringVar(value=str(settings.get("length", 20)))
        length_entry = ttk.Entry(length_frame, textvariable=self.pw_len_var, width=10)
        length_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Character distribution sliders
        distribution_frame = ttk.LabelFrame(tab_frame, text="Character Distribution (%)")
        distribution_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Letters percentage slider
        letters_frame = ttk.Frame(distribution_frame)
        letters_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(letters_frame, text="Letters:", width=12).pack(side=tk.LEFT)
        self.pw_letters_percent_var = tk.IntVar(value=settings.get("letters_percent", 70))
        letters_slider = ttk.Scale(letters_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                                 variable=self.pw_letters_percent_var, command=self.update_percentages)
        letters_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        letters_label = ttk.Label(letters_frame, text="70%", width=5)
        letters_label.pack(side=tk.RIGHT)
        self.pw_letters_label = letters_label
        
        # Numbers percentage slider
        numbers_frame = ttk.Frame(distribution_frame)
        numbers_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(numbers_frame, text="Numbers:", width=12).pack(side=tk.LEFT)
        self.pw_numbers_percent_var = tk.IntVar(value=settings.get("numbers_percent", 20))
        numbers_slider = ttk.Scale(numbers_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                                 variable=self.pw_numbers_percent_var, command=self.update_percentages)
        numbers_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        numbers_label = ttk.Label(numbers_frame, text="20%", width=5)
        numbers_label.pack(side=tk.RIGHT)
        self.pw_numbers_label = numbers_label
        
        # Symbols percentage slider
        symbols_frame = ttk.Frame(distribution_frame)
        symbols_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(symbols_frame, text="Symbols:", width=12).pack(side=tk.LEFT)
        self.pw_symbols_percent_var = tk.IntVar(value=settings.get("symbols_percent", 10))
        symbols_slider = ttk.Scale(symbols_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                                 variable=self.pw_symbols_percent_var, command=self.update_percentages)
        symbols_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        symbols_label = ttk.Label(symbols_frame, text="10%", width=5)
        symbols_label.pack(side=tk.RIGHT)
        self.pw_symbols_label = symbols_label
        
        # Total percentage display
        total_frame = ttk.Frame(distribution_frame)
        total_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(total_frame, text="Total:", width=12, font=('TkDefaultFont', 9, 'bold')).pack(side=tk.LEFT)
        self.pw_total_label = ttk.Label(total_frame, text="100%", width=5, font=('TkDefaultFont', 9, 'bold'))
        self.pw_total_label.pack(side=tk.RIGHT)
        
        # Numbers setting
        numbers_include_frame = ttk.Frame(tab_frame)
        numbers_include_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(numbers_include_frame, text="Must Include Numbers:").pack(side=tk.LEFT)
        self.pw_num_var = tk.StringVar(value=settings.get("numbers", ""))
        numbers_entry = ttk.Entry(numbers_include_frame, textvariable=self.pw_num_var, width=20)
        numbers_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Symbols setting
        symbols_include_frame = ttk.Frame(tab_frame)
        symbols_include_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(symbols_include_frame, text="Must Include Symbols:").pack(side=tk.LEFT)
        self.pw_sym_var = tk.StringVar(value=settings.get("symbols", ""))
        symbols_entry = ttk.Entry(symbols_include_frame, textvariable=self.pw_sym_var, width=20)
        symbols_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Generate button
        button_frame = ttk.Frame(tab_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        generate_btn = ttk.Button(button_frame, text="Generate Password", 
                                command=lambda: self.generate_password())
        generate_btn.pack(side=tk.LEFT)
        
        # Initialize percentage display
        self.update_percentages()
    
    def create_repeating_text_tab(self):
        """Create the Repeating Text Generator tab."""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="Repeating Text Generator")
        
        # Get current settings
        settings = self.main_app.settings["tool_settings"].get("Generator Tools", {}).get("Repeating Text Generator", {})
        
        # Times setting
        times_frame = ttk.Frame(tab_frame)
        times_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(times_frame, text="Repeat Times:").pack(side=tk.LEFT)
        self.repeat_times_var = tk.StringVar(value=str(settings.get("times", 5)))
        times_entry = ttk.Entry(times_frame, textvariable=self.repeat_times_var, width=10)
        times_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Separator setting
        separator_frame = ttk.Frame(tab_frame)
        separator_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(separator_frame, text="Separator:").pack(side=tk.LEFT)
        self.repeat_sep_var = tk.StringVar(value=settings.get("separator", "+"))
        separator_entry = ttk.Entry(separator_frame, textvariable=self.repeat_sep_var, width=20)
        separator_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Generate button
        button_frame = ttk.Frame(tab_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        repeat_btn = ttk.Button(button_frame, text="Generate Repeated Text", 
                              command=lambda: self.generate_repeated_text())
        repeat_btn.pack(side=tk.LEFT)
    
    def create_lorem_ipsum_tab(self):
        """Create the Lorem Ipsum Generator tab."""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="Lorem Ipsum Generator")
        
        # Get current settings
        settings = self.main_app.settings["tool_settings"].get("Generator Tools", {}).get("Lorem Ipsum Generator", {})
        
        # Count setting
        count_frame = ttk.Frame(tab_frame)
        count_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(count_frame, text="Count:").pack(side=tk.LEFT)
        self.lorem_count_var = tk.StringVar(value=str(settings.get("count", 5)))
        count_entry = ttk.Entry(count_frame, textvariable=self.lorem_count_var, width=10)
        count_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Type selection (radio buttons)
        type_frame = ttk.LabelFrame(tab_frame, text="Type")
        type_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.lorem_type_var = tk.StringVar(value=settings.get("type", "paragraphs"))
        
        type_options = [
            ("Words", "words"),
            ("Sentences", "sentences"),
            ("Paragraphs", "paragraphs"),
            ("Bytes", "bytes")
        ]
        
        for text, value in type_options:
            ttk.Radiobutton(type_frame, text=text, variable=self.lorem_type_var, 
                          value=value).pack(side=tk.LEFT, padx=5)
        
        # Format selection (radio buttons)
        format_frame = ttk.LabelFrame(tab_frame, text="Format")
        format_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.lorem_format_var = tk.StringVar(value=settings.get("format", "plain"))
        
        format_options = [
            ("Plain", "plain"),
            ("HTML", "html"),
            ("Markdown", "markdown"),
            ("JSON", "json")
        ]
        
        for text, value in format_options:
            ttk.Radiobutton(format_frame, text=text, variable=self.lorem_format_var, 
                          value=value).pack(side=tk.LEFT, padx=5)
        
        # Ordered checkbox (for lists)
        ordered_frame = ttk.Frame(tab_frame)
        ordered_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.lorem_ordered_var = tk.BooleanVar(value=settings.get("ordered", False))
        ordered_check = ttk.Checkbutton(ordered_frame, text="Ordered (for lists)", 
                                      variable=self.lorem_ordered_var)
        ordered_check.pack(side=tk.LEFT)
        
        # Generate button
        button_frame = ttk.Frame(tab_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        lorem_btn = ttk.Button(button_frame, text="Generate", 
                             command=lambda: self.generate_lorem_ipsum())
        lorem_btn.pack(side=tk.LEFT)
    
    def create_uuid_generator_tab(self):
        """Create the UUID/GUID Generator tab."""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="UUID/GUID Generator")
        
        # Get current settings
        settings = self.main_app.settings["tool_settings"].get("Generator Tools", {}).get("UUID/GUID Generator", {})
        
        # Create top row frame for UUID Version and Name-based settings
        top_row_frame = ttk.Frame(tab_frame)
        top_row_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # UUID Version selection (left side)
        version_frame = ttk.LabelFrame(top_row_frame, text="UUID Version")
        version_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.uuid_version_var = tk.IntVar(value=settings.get("version", 4))
        
        version_options = [
            ("Version 1 (Time-based)", 1),
            ("Version 3 (MD5 Name-based)", 3),
            ("Version 4 (Random)", 4),
            ("Version 5 (SHA-1 Name-based)", 5)
        ]
        
        for text, value in version_options:
            ttk.Radiobutton(version_frame, text=text, variable=self.uuid_version_var, 
                          value=value, command=self.update_uuid_fields).pack(anchor=tk.W, padx=5, pady=2)
        
        # Name-based UUID settings (right side, for versions 3 and 5)
        self.uuid_namebased_frame = ttk.LabelFrame(top_row_frame, text="Name-based Settings")
        self.uuid_namebased_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Namespace selection
        namespace_frame = ttk.Frame(self.uuid_namebased_frame)
        namespace_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(namespace_frame, text="Namespace:").pack(side=tk.LEFT)
        self.uuid_namespace_var = tk.StringVar(value=settings.get("namespace", "dns"))
        namespace_combo = ttk.Combobox(namespace_frame, textvariable=self.uuid_namespace_var, 
                                     values=["dns", "url", "oid", "x500"], state="readonly", width=15)
        namespace_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Name input
        name_frame = ttk.Frame(self.uuid_namebased_frame)
        name_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(name_frame, text="Name:").pack(side=tk.LEFT)
        self.uuid_name_var = tk.StringVar(value=settings.get("name", ""))
        name_entry = ttk.Entry(name_frame, textvariable=self.uuid_name_var, width=25)
        name_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # Output Format selection
        format_frame = ttk.LabelFrame(tab_frame, text="Output Format")
        format_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.uuid_format_var = tk.StringVar(value=settings.get("format", "standard"))
        
        format_options = [
            ("Standard (8-4-4-4-12)", "standard"),
            ("Hex (32 chars)", "hex"),
            ("Microsoft GUID {}", "microsoft"),
            ("URN format", "urn"),
            ("Base64", "base64"),
            ("C Array", "c_array"),
            ("Nil UUID", "nil")
        ]
        
        # Create two columns for format options
        format_left = ttk.Frame(format_frame)
        format_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        format_right = ttk.Frame(format_frame)
        format_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        for i, (text, value) in enumerate(format_options):
            parent = format_left if i < 4 else format_right
            ttk.Radiobutton(parent, text=text, variable=self.uuid_format_var, 
                          value=value).pack(anchor=tk.W, padx=5, pady=1)
        
        # Case selection
        case_frame = ttk.LabelFrame(tab_frame, text="Case")
        case_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.uuid_case_var = tk.StringVar(value=settings.get("case", "lowercase"))
        
        case_options = [
            ("Lowercase", "lowercase"),
            ("Uppercase", "uppercase")
        ]
        
        for text, value in case_options:
            ttk.Radiobutton(case_frame, text=text, variable=self.uuid_case_var, 
                          value=value).pack(side=tk.LEFT, padx=5)
        
        # Count setting
        count_frame = ttk.Frame(tab_frame)
        count_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(count_frame, text="Count:").pack(side=tk.LEFT)
        self.uuid_count_var = tk.StringVar(value=str(settings.get("count", 1)))
        count_entry = ttk.Entry(count_frame, textvariable=self.uuid_count_var, width=10)
        count_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Generate button
        button_frame = ttk.Frame(tab_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        uuid_btn = ttk.Button(button_frame, text="Generate", 
                            command=lambda: self.generate_uuid())
        uuid_btn.pack(side=tk.LEFT)
        
        # Initialize field visibility
        self.update_uuid_fields()
    
    def create_email_generator_tab(self):
        """Create the Random Email Generator tab."""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="Random Email Generator")
        
        # Get current settings
        settings = self.main_app.settings["tool_settings"].get("Generator Tools", {}).get("Random Email Generator", {})
        
        # Count setting
        count_frame = ttk.Frame(tab_frame)
        count_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(count_frame, text="Count:").pack(side=tk.LEFT)
        self.email_count_var = tk.StringVar(value=str(settings.get("count", 5)))
        count_entry = ttk.Entry(count_frame, textvariable=self.email_count_var, width=10)
        count_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Separator type selection (radio buttons)
        separator_type_frame = ttk.LabelFrame(tab_frame, text="Output Format")
        separator_type_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.email_separator_type_var = tk.StringVar(value=settings.get("separator_type", "list"))
        
        separator_type_options = [
            ("List (\\n separator)", "list"),
            ("Custom Separator", "custom")
        ]
        
        for text, value in separator_type_options:
            ttk.Radiobutton(separator_type_frame, text=text, variable=self.email_separator_type_var, 
                          value=value, command=self.update_email_separator_field).pack(side=tk.LEFT, padx=5)
        
        # Custom separator field
        self.email_separator_frame = ttk.Frame(tab_frame)
        self.email_separator_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(self.email_separator_frame, text="Separator:").pack(side=tk.LEFT)
        self.email_separator_var = tk.StringVar(value=settings.get("separator", ","))
        separator_entry = ttk.Entry(self.email_separator_frame, textvariable=self.email_separator_var, width=10)
        separator_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Domain type selection (radio buttons)
        domain_type_frame = ttk.LabelFrame(tab_frame, text="Domain")
        domain_type_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.email_domain_type_var = tk.StringVar(value=settings.get("domain_type", "random"))
        
        domain_type_options = [
            ("Random", "random"),
            ("Custom Domain", "custom")
        ]
        
        for text, value in domain_type_options:
            ttk.Radiobutton(domain_type_frame, text=text, variable=self.email_domain_type_var, 
                          value=value, command=self.update_email_domain_field).pack(side=tk.LEFT, padx=5)
        
        # Custom domain field
        self.email_domain_frame = ttk.Frame(tab_frame)
        self.email_domain_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(self.email_domain_frame, text="Domain:").pack(side=tk.LEFT)
        self.email_domain_var = tk.StringVar(value=settings.get("domain", "example.com"))
        domain_entry = ttk.Entry(self.email_domain_frame, textvariable=self.email_domain_var, width=30)
        domain_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Generate button
        button_frame = ttk.Frame(tab_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        email_btn = ttk.Button(button_frame, text="Generate", 
                             command=lambda: self.generate_emails())
        email_btn.pack(side=tk.LEFT)
        
        # Initialize field visibility
        self.update_email_separator_field()
        self.update_email_domain_field()
    
    def update_uuid_fields(self):
        """Update UUID field visibility based on selected version."""
        if hasattr(self, 'uuid_version_var') and hasattr(self, 'uuid_namebased_frame'):
            version = self.uuid_version_var.get()
            if version in [3, 5]:
                # Show name-based settings for versions 3 and 5
                self.uuid_namebased_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
            else:
                # Hide name-based settings for versions 1 and 4
                self.uuid_namebased_frame.pack_forget()
    
    def update_email_separator_field(self):
        """Update email separator field visibility based on selected type."""
        if hasattr(self, 'email_separator_type_var') and hasattr(self, 'email_separator_frame'):
            separator_type = self.email_separator_type_var.get()
            if separator_type == "custom":
                # Show separator field for custom separator
                self.email_separator_frame.pack(fill=tk.X, padx=10, pady=5)
            else:
                # Hide separator field for list format
                self.email_separator_frame.pack_forget()
    
    def update_email_domain_field(self):
        """Update email domain field visibility based on selected type."""
        if hasattr(self, 'email_domain_type_var') and hasattr(self, 'email_domain_frame'):
            domain_type = self.email_domain_type_var.get()
            if domain_type == "custom":
                # Show domain field for custom domain
                self.email_domain_frame.pack(fill=tk.X, padx=10, pady=5)
            else:
                # Hide domain field for random domain
                self.email_domain_frame.pack_forget()
    
    def update_percentages(self, *args):
        """Update percentage labels and ensure they add up to 100%."""
        if hasattr(self, 'pw_letters_percent_var'):
            letters_percent = self.pw_letters_percent_var.get()
            numbers_percent = self.pw_numbers_percent_var.get()
            symbols_percent = self.pw_symbols_percent_var.get()
            
            total = letters_percent + numbers_percent + symbols_percent
            
            # Update labels
            self.pw_letters_label.config(text=f"{letters_percent}%")
            self.pw_numbers_label.config(text=f"{numbers_percent}%")
            self.pw_symbols_label.config(text=f"{symbols_percent}%")
            
            # Update total label with color coding
            if total == 100:
                self.pw_total_label.config(text=f"{total}%", foreground="green")
            else:
                self.pw_total_label.config(text=f"{total}%", foreground="red")
    
    def generate_password(self):
        """Generate a password and update the output."""
        try:
            length = int(self.pw_len_var.get())
            numbers = self.pw_num_var.get()
            symbols = self.pw_sym_var.get()
            letters_percent = self.pw_letters_percent_var.get()
            numbers_percent = self.pw_numbers_percent_var.get()
            symbols_percent = self.pw_symbols_percent_var.get()
            
            settings = {
                "length": length,
                "numbers": numbers,
                "symbols": symbols,
                "letters_percent": letters_percent,
                "numbers_percent": numbers_percent,
                "symbols_percent": symbols_percent
            }
            
            result = self.generator_tools.strong_password("", settings)
            self.main_app.update_output_text(result)
            
            # Save settings
            self.save_settings()
            
        except ValueError:
            self.main_app.update_output_text("Error: Invalid password length")
    
    def generate_repeated_text(self):
        """Generate repeated text and update the output."""
        try:
            # Get input text
            active_input_tab = self.main_app.input_tabs[self.main_app.input_notebook.index(self.main_app.input_notebook.select())]
            input_text = active_input_tab.text.get("1.0", tk.END).strip()
            
            if not input_text:
                self.main_app.update_output_text("Error: No input text provided")
                return
            
            times = int(self.repeat_times_var.get())
            separator = self.repeat_sep_var.get()
            
            settings = {
                "times": times,
                "separator": separator
            }
            
            result = self.generator_tools.repeating_text(input_text, settings)
            self.main_app.update_output_text(result)
            
            # Save settings
            self.save_settings()
            
        except ValueError:
            self.main_app.update_output_text("Error: Invalid repeat times value")
    
    def generate_lorem_ipsum(self):
        """Generate Lorem Ipsum text and update the output."""
        try:
            count = int(self.lorem_count_var.get())
            text_type = self.lorem_type_var.get()
            format_type = self.lorem_format_var.get()
            ordered = self.lorem_ordered_var.get()
            
            settings = {
                "count": count,
                "type": text_type,
                "format": format_type,
                "ordered": ordered
            }
            
            result = self.generator_tools.lorem_ipsum("", settings)
            self.main_app.update_output_text(result)
            
            # Save settings
            self.save_settings()
            
        except ValueError:
            self.main_app.update_output_text("Error: Invalid count value")
    
    def generate_uuid(self):
        """Generate UUID/GUID and update the output."""
        try:
            version = self.uuid_version_var.get()
            format_type = self.uuid_format_var.get()
            case = self.uuid_case_var.get()
            count = int(self.uuid_count_var.get())
            namespace = self.uuid_namespace_var.get()
            name = self.uuid_name_var.get()
            
            settings = {
                "version": version,
                "format": format_type,
                "case": case,
                "count": count,
                "namespace": namespace,
                "name": name
            }
            
            result = self.generator_tools.uuid_generator("", settings)
            self.main_app.update_output_text(result)
            
            # Save settings
            self.save_settings()
            
        except ValueError:
            self.main_app.update_output_text("Error: Invalid count value")
    
    def generate_emails(self):
        """Generate random emails and update the output."""
        try:
            count = int(self.email_count_var.get())
            separator_type = self.email_separator_type_var.get()
            separator = self.email_separator_var.get()
            domain_type = self.email_domain_type_var.get()
            domain = self.email_domain_var.get()
            
            settings = {
                "count": count,
                "separator_type": separator_type,
                "separator": separator,
                "domain_type": domain_type,
                "domain": domain
            }
            
            result = self.generator_tools.random_email_generator("", settings)
            self.main_app.update_output_text(result)
            
            # Save settings
            self.save_settings()
            
        except ValueError:
            self.main_app.update_output_text("Error: Invalid count value")
    
    def save_settings(self):
        """Save current settings to the main app."""
        if not self.main_app:
            return
        
        # Ensure the Generator Tools settings exist
        if "Generator Tools" not in self.main_app.settings["tool_settings"]:
            self.main_app.settings["tool_settings"]["Generator Tools"] = {}
        
        # Save Strong Password Generator settings
        try:
            self.main_app.settings["tool_settings"]["Generator Tools"]["Strong Password Generator"] = {
                "length": int(self.pw_len_var.get()),
                "numbers": self.pw_num_var.get(),
                "symbols": self.pw_sym_var.get(),
                "letters_percent": self.pw_letters_percent_var.get(),
                "numbers_percent": self.pw_numbers_percent_var.get(),
                "symbols_percent": self.pw_symbols_percent_var.get()
            }
        except (ValueError, AttributeError):
            pass
        
        # Save Repeating Text Generator settings
        try:
            self.main_app.settings["tool_settings"]["Generator Tools"]["Repeating Text Generator"] = {
                "times": int(self.repeat_times_var.get()),
                "separator": self.repeat_sep_var.get()
            }
        except (ValueError, AttributeError):
            pass
        
        # Save Lorem Ipsum Generator settings
        try:
            self.main_app.settings["tool_settings"]["Generator Tools"]["Lorem Ipsum Generator"] = {
                "count": int(self.lorem_count_var.get()),
                "type": self.lorem_type_var.get(),
                "format": self.lorem_format_var.get(),
                "ordered": self.lorem_ordered_var.get()
            }
        except (ValueError, AttributeError):
            pass
        
        # Save UUID/GUID Generator settings
        try:
            self.main_app.settings["tool_settings"]["Generator Tools"]["UUID/GUID Generator"] = {
                "version": self.uuid_version_var.get(),
                "format": self.uuid_format_var.get(),
                "case": self.uuid_case_var.get(),
                "count": int(self.uuid_count_var.get()),
                "namespace": self.uuid_namespace_var.get(),
                "name": self.uuid_name_var.get()
            }
        except (ValueError, AttributeError):
            pass
        
        # Save Random Email Generator settings
        try:
            self.main_app.settings["tool_settings"]["Generator Tools"]["Random Email Generator"] = {
                "count": int(self.email_count_var.get()),
                "separator_type": self.email_separator_type_var.get(),
                "separator": self.email_separator_var.get(),
                "domain_type": self.email_domain_type_var.get(),
                "domain": self.email_domain_var.get()
            }
        except (ValueError, AttributeError):
            pass
        
        # Save ASCII Art Generator settings
        try:
            if hasattr(self.main_app, 'ascii_art_generator') and self.main_app.ascii_art_generator:
                if "ASCII Art Generator" not in self.main_app.settings["tool_settings"]:
                    self.main_app.settings["tool_settings"]["ASCII Art Generator"] = {}
                # Settings are saved by the widget itself
        except (ValueError, AttributeError):
            pass
        
        # Save Hash Generator settings
        try:
            if hasattr(self.main_app, 'hash_generator') and self.main_app.hash_generator:
                if "Hash Generator" not in self.main_app.settings["tool_settings"]:
                    self.main_app.settings["tool_settings"]["Hash Generator"] = {}
                # Settings are saved by the widget itself
        except (ValueError, AttributeError):
            pass
        
        # Save Slug Generator settings
        try:
            if hasattr(self.main_app, 'slug_generator') and self.main_app.slug_generator:
                if "Slug Generator" not in self.main_app.settings["tool_settings"]:
                    self.main_app.settings["tool_settings"]["Slug Generator"] = {}
                # Settings are saved by the widget itself
        except (ValueError, AttributeError):
            pass
        
        # Save settings to file
        self.main_app.save_settings()
    
    def create_ascii_art_generator_tab(self):
        """Create the ASCII Art Generator tab."""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="ASCII Art Generator")
        
        try:
            from tools.ascii_art_generator import ASCIIArtGenerator
            if hasattr(self.main_app, 'ascii_art_generator') and self.main_app.ascii_art_generator:
                widget = self.main_app.ascii_art_generator.create_widget(tab_frame, self.main_app)
                widget.pack(fill=tk.BOTH, expand=True)
            else:
                ttk.Label(tab_frame, text="ASCII Art Generator module not available").pack(padx=10, pady=10)
        except ImportError:
            ttk.Label(tab_frame, text="ASCII Art Generator module not available").pack(padx=10, pady=10)
    
    def create_hash_generator_tab(self):
        """Create the Hash Generator tab."""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="Hash Generator")
        
        try:
            from tools.hash_generator import HashGenerator
            if hasattr(self.main_app, 'hash_generator') and self.main_app.hash_generator:
                widget = self.main_app.hash_generator.create_widget(tab_frame, self.main_app)
                widget.pack(fill=tk.BOTH, expand=True)
            else:
                ttk.Label(tab_frame, text="Hash Generator module not available").pack(padx=10, pady=10)
        except ImportError:
            ttk.Label(tab_frame, text="Hash Generator module not available").pack(padx=10, pady=10)
    
    def create_slug_generator_tab(self):
        """Create the Slug Generator tab."""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="Slug Generator")
        
        try:
            from tools.slug_generator import SlugGenerator
            if hasattr(self.main_app, 'slug_generator') and self.main_app.slug_generator:
                widget = self.main_app.slug_generator.create_widget(tab_frame, self.main_app)
                widget.pack(fill=tk.BOTH, expand=True)
            else:
                ttk.Label(tab_frame, text="Slug Generator module not available").pack(padx=10, pady=10)
        except ImportError:
            ttk.Label(tab_frame, text="Slug Generator module not available").pack(padx=10, pady=10)