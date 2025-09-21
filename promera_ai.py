import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox, font
import re
import json
import os
import logging
import base64
import csv
import io
import platform
import subprocess
import requests
import threading
import time
import string
import random
import difflib
import urllib.parse
import webbrowser
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from docx import Document
try:
    import pyaudio
    import numpy as np
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
try:
    from metaphone import doublemetaphone
    from lemminflect import getLemma, getInflection
    METAPHONE_AVAILABLE = True
except ImportError:
    METAPHONE_AVAILABLE = False
try:
    from huggingface_hub import InferenceClient
    from huggingface_hub.utils import HfHubHTTPError
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False

class AppConfig:
    """Configuration constants for the application."""
    DEFAULT_WINDOW_SIZE = "1200x900"
    TAB_COUNT = 7
    DEBOUNCE_DELAY = 300  # milliseconds
    MORSE_DOT_DURATION = 0.080
    MORSE_DASH_DURATION = 0.080 * 3
    SAMPLE_RATE = 44100
    TONE_FREQUENCY = 700
    MAX_RETRIES = 5
    BASE_DELAY = 1

class TextProcessor:
    """Separate class for text processing logic to improve maintainability."""

    @staticmethod
    def sentence_case(text):
        """Converts text to sentence case, capitalizing the first letter of each sentence and each new line."""
        def capitalize_match(match):
            return match.group(1) + match.group(2).upper()
        
        # Capitalize the first letter of the string, and any letter following a newline or sentence-ending punctuation.
        return re.sub(r'([.!?\n]\s*|^)([a-z])', capitalize_match, text)

    @staticmethod
    def title_case(text, exclusions):
        """Converts text to title case, excluding specified words."""
        exclusion_list = {word.lower() for word in exclusions.splitlines()}
        words = text.split(' ')
        title_cased_words = []
        for i, word in enumerate(words):
            if i == 0 or word.lower() not in exclusion_list:
                title_cased_words.append(word.capitalize())
            else:
                title_cased_words.append(word.lower())
        return ' '.join(title_cased_words)

    @staticmethod
    def morse_translator(text, mode, morse_dict, reversed_morse_dict):
        """Translates text to or from Morse code."""
        if mode == "morse":
            return ' '.join(morse_dict.get(char.upper(), '') for char in text)
        else: # mode == "text"
            return ''.join(reversed_morse_dict.get(code, '') for code in text.split(' '))

    @staticmethod
    def binary_translator(text):
        """Translates text to or from binary."""
        # Detect if input is binary or text
        if all(c in ' 01' for c in text): # Binary to Text
            try:
                return ''.join(chr(int(b, 2)) for b in text.split())
            except (ValueError, TypeError):
                return "Error: Invalid binary sequence."
        else: # Text to Binary
            return ' '.join(format(ord(char), '08b') for char in text)

    @staticmethod
    def base64_processor(text, mode):
        """Encodes or decodes text using Base64."""
        try:
            if mode == "encode":
                return base64.b64encode(text.encode('utf-8')).decode('ascii')
            else: # mode == "decode"
                return base64.b64decode(text.encode('ascii')).decode('utf-8')
        except Exception as e:
            return f"Base64 Error: {e}"

    @staticmethod
    def number_sorter(text, order):
        """Sorts a list of numbers numerically."""
        try:
            numbers = [float(line.strip()) for line in text.splitlines() if line.strip()]
            numbers.sort(reverse=(order == "descending"))
            return '\n'.join(map(lambda n: '%g' % n, numbers))
        except ValueError:
            return "Error: Input contains non-numeric values."

    @staticmethod
    def extract_emails(text):
        """Extracts all email addresses from the text."""
        emails = re.findall(r'[\w\.-]+@[\w\.-]+', text)
        return '\n'.join(emails)

    @staticmethod
    def repeating_text(text, times, separator):
        """Repeats the input text a specified number of times."""
        if not isinstance(times, int) or times < 0:
            return "Error: 'Times' must be a non-negative number."
        return separator.join([text] * times)
    
    @staticmethod
    def alphabetical_sorter(text, order, unique_only=False, trim=False):
        """Sorts a list of lines alphabetically, with options for unique values and trimming."""
        lines = text.splitlines()
        if trim:
            lines = [line.strip() for line in lines]
        if unique_only:
            # Using dict.fromkeys to get unique lines while preserving order before sorting
            lines = list(dict.fromkeys(lines))
        lines.sort(key=str.lower, reverse=(order == "descending"))
        return '\n'.join(lines)
    
    @staticmethod
    def word_frequency(text):
        """Counts the frequency of each word in the text."""
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return "No words found."
        
        from collections import Counter
        word_counts = Counter(words)
        total_words = len(words)
        
        report = []
        for word, count in word_counts.most_common():
            percentage = (count / total_words) * 100
            report.append(f"{word} ({count} / {percentage:.2f}%)")
        return '\n'.join(report)
    
    @staticmethod
    def strong_password(length, numbers="", symbols=""):
        """Generates a strong, random password."""
        if not isinstance(length, int) or length <= 0:
            return "Error: Password length must be a positive number."

        chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(chars) for _ in range(length))
        
        # Ensure included numbers and symbols are present
        must_include = numbers + symbols
        if must_include:
            password_list = list(password)
            for i, char in enumerate(must_include):
                if i < len(password_list):
                    password_list[i] = char
            random.shuffle(password_list)
            password = "".join(password_list)

        return password

class TextWithLineNumbers(tk.Frame):
    """A custom widget that combines a Text widget with a line number sidebar."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=15, width=50)
        self.linenumbers = tk.Canvas(self, width=40, bg='#f0f0f0', highlightthickness=0)
        
        self.linenumbers.pack(side=tk.LEFT, fill=tk.Y)
        self.text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # The vbar is the vertical scrollbar of the ScrolledText widget
        self.text.vbar.config(command=self._on_text_scroll)
        self.linenumbers.bind("<MouseWheel>", self._on_mousewheel) # For Windows/macOS
        self.linenumbers.bind("<Button-4>", self._on_mousewheel)   # For Linux scroll up
        self.linenumbers.bind("<Button-5>", self._on_mousewheel)   # For Linux scroll down

        self.text.bind("<<Modified>>", self._on_text_modified)
        self.text.bind("<Configure>", self._on_text_modified)

        self._on_text_modified()

    def _on_text_scroll(self, *args):
        """Handles scrolling of the text widget to sync line numbers."""
        self.text.yview(*args)
        self._on_text_modified()

    def _on_mousewheel(self, event):
        """Handles mouse wheel scrolling over the line number canvas."""
        if platform.system() == "Windows":
            self.text.yview_scroll(int(-1*(event.delta/120)), "units")
        elif platform.system() == "Darwin": # macOS
             self.text.yview_scroll(int(-1 * event.delta), "units")
        else: # Linux
            if event.num == 4:
                self.text.yview_scroll(-1, "units")
            elif event.num == 5:
                self.text.yview_scroll(1, "units")
        self._on_text_modified()
        return "break"

    def _on_text_modified(self, event=None):
        """Redraws the line numbers when the text widget's content or view changes."""
        self.linenumbers.delete("all")
        
        # Cache the line info to avoid repeated calls
        line_info_cache = []
        i = self.text.index("@0,0")
        while True:
            dline = self.text.dlineinfo(i)
            if dline is None: 
                break
            line_info_cache.append((i, dline[1]))
            i = self.text.index("%s+1line" % i)
        
        # Batch render all line numbers
        for i, y in line_info_cache:
            linenum = str(i).split(".")[0]
            self.linenumbers.create_text(20, y, anchor="n", text=linenum, fill="gray")
        
        self.after(10, self.linenumbers.yview_moveto, self.text.yview()[0])
        if event and event.widget.edit_modified():
            event.widget.edit_modified(False) # Reset the modified flag

class PromeraAIApp(tk.Tk):
    """
    A comprehensive Text Processing GUI application built with Tkinter.
    """
    class Tooltip:
        """Creates a tooltip for a given widget."""
        def __init__(self, widget, text):
            self.widget = widget
            self.text = text
            self.tooltip_window = None
            self.widget.bind("<Enter>", self.show_tip)
            self.widget.bind("<Leave>", self.hide_tip)

        def show_tip(self, event=None):
            x, y, _, _ = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 25

            self.tooltip_window = tk.Toplevel(self.widget)
            self.tooltip_window.wm_overrideredirect(True)
            self.tooltip_window.wm_geometry(f"+{x}+{y}")

            label = tk.Label(self.tooltip_window, text=self.text, justify='left',
                             background="#ffffe0", relief='solid', borderwidth=1,
                             wraplength=250, font=("sans-serif", 8))
            label.pack(ipadx=1)

        def hide_tip(self, event=None):
            if self.tooltip_window:
                self.tooltip_window.destroy()
            self.tooltip_window = None

    def __init__(self):
        """Initializes the main application window and its components."""
        super().__init__()
        self.title("Promera AI Commander")
        self.geometry(AppConfig.DEFAULT_WINDOW_SIZE)

        self._after_id = None 
        self._regex_cache = {}
        self.ai_widgets = {}
        self.ai_provider_urls = {
            "Google AI": "https://aistudio.google.com/apikey",
            "Cohere AI": "https://dashboard.cohere.com/api-keys",
            "HuggingFace AI": "https://huggingface.co/settings/tokens",
            "Groq AI": "https://console.groq.com/keys",
            "OpenRouterAI": "https://openrouter.ai/settings/keys",
            "Anthropic AI": "https://console.anthropic.com/settings/keys",
            "OpenAI": "https://platform.openai.com/settings/organization/api-keys"
        }

        self.manual_process_tools = [
            "Case Tool", "Find & Replace Text", "Google AI", "Anthropic AI", 
            "OpenAI", "Cohere AI", "HuggingFace AI", "Groq AI", "OpenRouterAI",
            "Extract Emails", "Strong Password Generator", "Alphabetical Sorter",
            "Word Frequency Counter", "URL Parser", "Repeating Text Generator",
            "Number Sorter", "Base64 Encoder/Decoder", "Binary Code Translator",
            "Morse Code Translator", "Diff Viewer"
        ]

        # CORRECTED ORDER: Load settings BEFORE setting up logging
        self.settings = self.load_settings()
        self.setup_logging()
        self.setup_audio()
        self.create_widgets()
        self.load_last_state()
        
        if self.tool_var.get() not in self.manual_process_tools:
            self.apply_tool()
        elif self.tool_var.get() == "Diff Viewer":
            self.central_frame.grid_remove()
            self.diff_frame.grid(row=1, column=0, sticky="nsew", pady=5)
            self.update_tool_settings_ui()
            self.load_diff_viewer_content()
            self.run_diff_viewer()
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_settings(self):
        """Loads settings from the 'settings.json' file."""
        try:
            with open("settings.json", "r", encoding='utf-8') as f:
                settings = json.load(f)
                self._validate_settings(settings)
                return settings
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # self.logger is not available yet if this is the first run, so we can't log here
            print(f"Settings file error: {e}, using defaults")
            return self._get_default_settings()
    
    def _validate_settings(self, settings):
        """Validate and sanitize loaded settings."""
        default_settings = self._get_default_settings()
        
        for key in ["input_tabs", "output_tabs", "tool_settings"]:
            if key not in settings:
                settings[key] = default_settings[key]
        
        if len(settings.get("input_tabs", [])) != AppConfig.TAB_COUNT:
            settings["input_tabs"] = [""] * AppConfig.TAB_COUNT
        if len(settings.get("output_tabs", [])) != AppConfig.TAB_COUNT:
            settings["output_tabs"] = [""] * AppConfig.TAB_COUNT
        
        # Backward compatibility for model lists
        for tool_name, tool_data in default_settings["tool_settings"].items():
            if "MODELS_LIST" in tool_data:
                if tool_name not in settings["tool_settings"] or "MODELS_LIST" not in settings["tool_settings"][tool_name]:
                    if tool_name not in settings["tool_settings"]:
                         settings["tool_settings"][tool_name] = {}
                    settings["tool_settings"][tool_name]["MODELS_LIST"] = tool_data["MODELS_LIST"]
    
    def _get_default_settings(self):
        """Returns default settings when none exist or are invalid."""
        default_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        return {
            "export_path": default_path,
            "debug_level": "INFO",
            "selected_tool": "Case Tool",
            "input_tabs": [""] * AppConfig.TAB_COUNT,
            "output_tabs": [""] * AppConfig.TAB_COUNT,
            "active_input_tab": 0,
            "active_output_tab": 0,
            "tool_settings": {
                "Case Tool": {"mode": "Sentence", "exclusions": "a\nan\nand\nas\nat\nbut\nby\nen\nfor\nif\nin\nis\nof\non\nor\nthe\nto\nvia\nvs"},
                "Morse Code Translator": {"mode": "morse", "tone": AppConfig.TONE_FREQUENCY},
                "Base64 Encoder/Decoder": {"mode": "encode"},
                "Number Sorter": {"order": "ascending"},
                "Find & Replace Text": {"find": "", "replace": "", "mode": "Text", "option": "ignore_case"},
                "Repeating Text Generator": {"times": 5, "separator": "+"},
                "Alphabetical Sorter": {"order": "ascending", "unique_only": False, "trim": False},
                "Strong Password Generator": {"length": 20, "numbers": "", "symbols": ""},
                "URL Parser": {"ascii_decode": True},
                "Google AI": {
                    "API_KEY": "putinyourkey", "MODEL": "gemini-1.5-pro-latest", "MODELS_LIST": ["gemini-1.5-pro-latest", "gemini-1.5-flash-latest", "gemini-1.0-pro"],
                    "system_prompt": "You are a helpful assistant.",
                    "temperature": 0.7, "topK": 40, "topP": 0.95, "candidateCount": 1, "maxOutputTokens": 8192, "stopSequences": ""
                },
                "Anthropic AI": {
                    "API_KEY": "putinyourkey", "MODEL": "claude-3-5-sonnet-20240620", "MODELS_LIST": ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
                    "system": "You are a helpful assistant.", "max_tokens": 4096, "temperature": 0.7, "top_p": 0.9, "top_k": 40, "stop_sequences": ""
                },
                "OpenAI": {
                    "API_KEY": "putinyourkey", "MODEL": "gpt-4o", "MODELS_LIST": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o-mini"],
                    "system_prompt": "You are a helpful assistant.", "temperature": 0.7, "max_tokens": 4096, "top_p": 1.0, "frequency_penalty": 0.0,
                    "presence_penalty": 0.0, "seed": "", "response_format": "text", "stop": ""
                },
                "Cohere AI": {
                    "API_KEY": "putinyourkey", "MODEL": "command-r-plus", "MODELS_LIST": ["command-r-plus", "command-r", "command", "command-light"],
                    "preamble": "You are a helpful assistant.", "temperature": 0.7, "max_tokens": 4000, "k": 50, "p": 0.75, "frequency_penalty": 0.0,
                    "presence_penalty": 0.0, "stop_sequences": "", "citation_quality": "accurate"
                },
                "HuggingFace AI": {
                    "API_KEY": "putinyourkey", "MODEL": "meta-llama/Meta-Llama-3-8B-Instruct", "MODELS_LIST": ["meta-llama/Meta-Llama-3-8B-Instruct", "mistralai/Mistral-7B-Instruct-v0.2", "google/gemma-7b-it"],
                    "system_prompt": "You are a helpful assistant.", "max_tokens": 4096, "temperature": 0.7, "top_p": 0.95, "stop_sequences": "", "seed": ""
                },
                "Groq AI": {
                    "API_KEY": "putinyourkey", "MODEL": "llama3-70b-8192", "MODELS_LIST": ["llama3-70b-8192", "mixtral-8x7b-32768", "gemma2-9b-it"],
                    "system_prompt": "You are a helpful assistant.", "temperature": 0.7, "max_tokens": 8192, "top_p": 1.0, "frequency_penalty": 0.0,
                    "presence_penalty": 0.0, "stop": "", "seed": "", "response_format": "text"
                },
                "OpenRouterAI": {
                    "API_KEY": "putinyourkey", "MODEL": "anthropic/claude-3.5-sonnet", "MODELS_LIST": ["anthropic/claude-3.5-sonnet", "google/gemini-flash-1.5:free", "meta-llama/llama-3-8b-instruct:free", "openai/gpt-4o-mini"],
                    "system_prompt": "You are a helpful assistant.", "temperature": 0.7, "max_tokens": 4096, "top_p": 1.0, "top_k": 0, "frequency_penalty": 0.0,
                    "presence_penalty": 0.0, "repetition_penalty": 1.0, "seed": "", "stop": ""
                },
                "Diff Viewer": {"option": "ignore_case"}
            }
        }
        
    def save_settings(self):
        """Saves the current settings to 'settings.json'."""
        self.settings["input_tabs"] = [tab.text.get("1.0", tk.END).strip() for tab in self.input_tabs]
        self.settings["output_tabs"] = [tab.text.get("1.0", tk.END).strip() for tab in self.output_tabs]
        self.settings["active_input_tab"] = self.input_notebook.index(self.input_notebook.select())
        self.settings["active_output_tab"] = self.output_notebook.index(self.output_notebook.select())
        
        with open("settings.json", "w") as f:
            json.dump(self.settings, f, indent=4)
        self.logger.info("Settings saved.")

    def load_last_state(self):
        """Loads the last saved text and tab selections into the UI."""
        for i, content in enumerate(self.settings.get("input_tabs", [""]*AppConfig.TAB_COUNT)):
            self.input_tabs[i].text.insert("1.0", content)
        for i, content in enumerate(self.settings.get("output_tabs", [""]*AppConfig.TAB_COUNT)):
            self.output_tabs[i].text.config(state="normal")
            self.output_tabs[i].text.insert("1.0", content)
            self.output_tabs[i].text.config(state="disabled")
        
        self.input_notebook.select(self.settings.get("active_input_tab", 0))
        self.output_notebook.select(self.settings.get("active_output_tab", 0))
        
        self.update_all_stats()
        self.update_tab_labels()


    def setup_logging(self):
        """Configures the logging system for the application."""
        self.logger = logging.getLogger("PromeraAIApp")
        
        if not self.logger.handlers:
            self.log_level = tk.StringVar(value=self.settings.get("debug_level", "INFO"))
            self.logger.setLevel(self.log_level.get())
            
            self.log_handler = logging.StreamHandler()
            self.log_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            )
            self.logger.addHandler(self.log_handler)
        
    def setup_audio(self):
        """Initializes the PyAudio stream for Morse code playback."""
        global PYAUDIO_AVAILABLE
        self.audio_stream = None
        self.pyaudio_instance = None
        self.morse_thread = None
        
        self.morse_code_dict = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
            'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
            'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
            'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
            '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----', ' ': '/',
            ',': '--..--', '.': '.-.-.-', '?': '..--..', '/': '-..-.', '-': '-....-', '(': '-.--.', ')': '-.--.-'
        }
        self.reversed_morse_dict = {v: k for k, v in self.morse_code_dict.items()}
        
        if PYAUDIO_AVAILABLE:
            try:
                self.pyaudio_instance = pyaudio.PyAudio()
                self.audio_stream = self.pyaudio_instance.open(format=pyaudio.paFloat32,
                                                     channels=1,
                                                     rate=AppConfig.SAMPLE_RATE,
                                                     output=True)
                self.logger.info("PyAudio initialized successfully.")
            except Exception as e:
                self.logger.error(f"Failed to initialize PyAudio: {e}")
                PYAUDIO_AVAILABLE = False
        self.stop_morse_playback = threading.Event()

    def create_widgets(self):
        """Creates and arranges all the GUI widgets in the main window."""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)

        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.grid(row=0, column=0, sticky="ew", pady=5)
        self.create_settings_widgets(settings_frame)

        self.central_frame = ttk.Frame(main_frame, padding="10")
        self.central_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        self.central_frame.grid_columnconfigure(0, weight=1)
        self.central_frame.grid_columnconfigure(1, weight=1)
        self.central_frame.grid_rowconfigure(1, weight=1)

        self.create_input_widgets(self.central_frame)
        self.create_output_widgets(self.central_frame)

        self.create_diff_viewer(main_frame)

        tool_frame = ttk.LabelFrame(main_frame, text="Text Processing Tool", padding="10")
        tool_frame.grid(row=2, column=0, sticky="ew", pady=5)
        self.create_tool_widgets(tool_frame)

        console_frame = ttk.LabelFrame(main_frame, text="Console Log", padding="10")
        console_frame.grid(row=3, column=0, sticky="ew", pady=5)
        self.create_console_widgets(console_frame)

    def create_settings_widgets(self, parent):
        """Creates widgets for the settings section."""
        ttk.Label(parent, text="Export Path:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.export_path_var = tk.StringVar(value=self.settings.get("export_path", ""))
        ttk.Entry(parent, textvariable=self.export_path_var, width=50).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(parent, text="Browse...", command=self.browse_export_path).grid(row=0, column=2, padx=5, pady=5)

        ttk.Button(parent, text="Export As PDF", command=lambda: self.export_file("pdf")).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(parent, text="Export As TXT", command=lambda: self.export_file("txt")).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(parent, text="Export As DOCX", command=lambda: self.export_file("docx")).grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(parent, text="Debug Level:").grid(row=0, column=6, padx=5, pady=5, sticky="w")
        debug_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        self.log_level_combo = ttk.Combobox(parent, textvariable=self.log_level, values=debug_levels, state="readonly")
        self.log_level_combo.grid(row=0, column=7, padx=5, pady=5)
        self.log_level_combo.bind("<<ComboboxSelected>>", self.update_log_level)
        parent.grid_columnconfigure(1, weight=1)

    def create_input_widgets(self, parent):
        """Creates widgets for the input text section."""
        input_frame = ttk.Frame(parent)
        input_frame.grid(row=0, column=0, rowspan=2, padx=(0, 5), sticky="nsew")
        input_frame.grid_rowconfigure(1, weight=1)
        input_frame.grid_columnconfigure(0, weight=1)

        title_row = ttk.Frame(input_frame)
        title_row.grid(row=0, column=0, sticky="w")
        ttk.Label(title_row, text="Text Input", font=("Helvetica", 12, "bold")).pack(side=tk.LEFT)
        ttk.Button(title_row, text="Clear All Input Tabs", command=self.clear_all_input_tabs).pack(side=tk.LEFT, padx=(10, 0))
        
        self.input_notebook = ttk.Notebook(input_frame)
        self.input_notebook.grid(row=1, column=0, sticky="nsew")
        self.input_tabs = []
        for i in range(AppConfig.TAB_COUNT):
            tab = TextWithLineNumbers(self.input_notebook)
            tab.text.bind("<KeyRelease>", self.on_input_changed)
            tab.text.bind("<<Modified>>", self.on_tab_content_changed)
            tab.text.tag_configure("yellow_highlight", background="yellow")
            self.input_tabs.append(tab)
            self.input_notebook.add(tab, text=f"{i+1}:")
        self.input_notebook.bind("<<NotebookTabChanged>>", self.on_input_tab_change)

        self.input_status_bar = ttk.Label(input_frame, text="Char: 0 | Word: 0 | Sentence: 0 | Line: 0 | Tokens: 0")
        self.input_status_bar.grid(row=2, column=0, sticky="ew")

    def create_output_widgets(self, parent):
        """Creates widgets for the output text section."""
        output_frame = ttk.Frame(parent)
        output_frame.grid(row=0, column=1, rowspan=2, padx=(5, 0), sticky="nsew")
        output_frame.grid_rowconfigure(1, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)

        title_row = ttk.Frame(output_frame)
        title_row.grid(row=0, column=0, sticky="w")
        ttk.Button(title_row, text="Copy to Input Tab ?", command=self.prompt_copy_to_input_tab).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(title_row, text="Copy to Clipboard", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(title_row, text="Clear All Output Tabs", command=self.clear_all_output_tabs).pack(side=tk.LEFT)

        self.output_notebook = ttk.Notebook(output_frame)
        self.output_notebook.grid(row=1, column=0, sticky="nsew")
        self.output_tabs = []
        for i in range(AppConfig.TAB_COUNT):
            tab = TextWithLineNumbers(self.output_notebook)
            tab.text.config(state="disabled")
            tab.text.bind("<<Modified>>", self.on_tab_content_changed)
            tab.text.tag_configure("pink_highlight", background="pink")
            self.output_tabs.append(tab)
            self.output_notebook.add(tab, text=f"{i+1}:")
        self.output_notebook.bind("<<NotebookTabChanged>>", self.on_output_tab_change)

        self.output_status_bar = ttk.Label(output_frame, text="Char: 0 | Word: 0 | Sentence: 0 | Line: 0 | Tokens: 0")
        self.output_status_bar.grid(row=2, column=0, sticky="ew")

    def clear_all_input_tabs(self):
        """Asks for confirmation and clears all input tab contents."""
        if messagebox.askyesno("Confirm", "Clear all Input tabs? This cannot be undone."):
            for tab in self.input_tabs:
                tab.text.delete("1.0", tk.END)
            if hasattr(self, 'diff_input_tabs'):
                for tab in self.diff_input_tabs:
                    tab.text.delete("1.0", tk.END)
            self.update_tab_labels()
            self.save_settings()
            self.after(10, self.update_all_stats)

    def clear_all_output_tabs(self):
        """Asks for confirmation and clears all output tab contents."""
        if messagebox.askyesno("Confirm", "Clear all Output tabs? This cannot be undone."):
            for tab in self.output_tabs:
                tab.text.config(state="normal")
                tab.text.delete("1.0", tk.END)
                tab.text.config(state="disabled")
            if hasattr(self, 'diff_output_tabs'):
                for tab in self.diff_output_tabs:
                    tab.text.delete("1.0", tk.END)
            self.update_tab_labels()
            self.save_settings()
            self.after(10, self.update_all_stats)

    def create_tool_widgets(self, parent):
        """Creates widgets for the tool selection and settings section."""
        self.tool_var = tk.StringVar(value=self.settings.get("selected_tool", "Case Tool"))
        
        self.tool_options = [
            "Find & Replace Text", "Diff Viewer", "Case Tool", "Extract Emails",
            "Strong Password Generator", "Alphabetical Sorter", "Word Frequency Counter",
            "URL Parser", "Repeating Text Generator", "Number Sorter", "Google AI",
            "Cohere AI", "HuggingFace AI", "Groq AI", "OpenRouterAI", "Anthropic AI",
            "OpenAI", "Base64 Encoder/Decoder", "Binary Code Translator",
            "Morse Code Translator"
        ]
        self.filtered_tool_options = self.tool_options.copy()
        
        self.tool_menu = ttk.Combobox(parent, textvariable=self.tool_var, values=self.filtered_tool_options, state="normal", font=("Arial", 12))
        self.tool_menu.pack(side=tk.LEFT, padx=5)
        self.tool_menu.bind("<<ComboboxSelected>>", self.on_tool_selected)
        self.tool_menu.bind("<KeyRelease>", self.on_tool_search)
        self.tool_menu.bind("<FocusOut>", self.on_tool_focus_out)

        self.tool_settings_frame = ttk.Frame(parent)
        self.tool_settings_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.update_tool_settings_ui()

    def on_tool_search(self, event=None):
        """Filters tool options based on typed text."""
        current_text = self.tool_menu.get()
        search_text = current_text.lower()
        
        if not search_text:
            self.filtered_tool_options = self.tool_options.copy()
        else:
            self.filtered_tool_options = [
                tool for tool in self.tool_options
                if any(search_text in word.lower() for word in tool.split())
            ]
        self.tool_menu['values'] = self.filtered_tool_options

    def on_tool_focus_out(self, event=None):
        """Handles when the tool combobox loses focus."""
        current_value = self.tool_menu.get()
        if current_value and current_value not in self.tool_options:
            for tool in self.tool_options:
                if tool.lower() == current_value.lower():
                    self.tool_var.set(tool)
                    self.on_tool_selected()
                    return
            for tool in self.tool_options:
                if current_value.lower() in tool.lower():
                    self.tool_var.set(tool)
                    self.on_tool_selected()
                    return
            self.tool_var.set(self.settings.get("selected_tool", "Case Tool"))
        
        self.filtered_tool_options = self.tool_options.copy()
        self.tool_menu['values'] = self.filtered_tool_options

    def create_console_widgets(self, parent):
        """Creates the console log text widget."""
        self.console_log = scrolledtext.ScrolledText(parent, wrap=tk.WORD, state="disabled", height=5)
        self.console_log.pack(fill=tk.BOTH, expand=True)

        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                logging.Handler.__init__(self)
                self.text_widget = text_widget

            def emit(self, record):
                msg = self.format(record)
                def append():
                    self.text_widget.configure(state='normal')
                    self.text_widget.insert(tk.END, msg + '\n')
                    self.text_widget.configure(state='disabled')
                    self.text_widget.yview(tk.END)
                self.text_widget.after(0, append)

        text_handler = TextHandler(self.console_log)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(text_handler)

    def create_diff_viewer(self, parent):
        """Creates the diff viewer widgets, initially hidden."""
        self.diff_frame = ttk.Frame(parent, padding="10")
        self.diff_frame.grid_columnconfigure(0, weight=1)
        self.diff_frame.grid_columnconfigure(1, weight=1)
        self.diff_frame.grid_rowconfigure(1, weight=1)
        
        input_title_row = ttk.Frame(self.diff_frame)
        input_title_row.grid(row=0, column=0, sticky="w")
        ttk.Label(input_title_row, text="Input", font=("Helvetica", 12, "bold")).pack(side=tk.LEFT)
        ttk.Button(input_title_row, text="Clear All Input Tabs", command=self.clear_all_input_tabs).pack(side=tk.LEFT, padx=(10, 0))
        
        output_title_row = ttk.Frame(self.diff_frame)
        output_title_row.grid(row=0, column=1, sticky="w")
        ttk.Button(output_title_row, text="Copy to Input Tab ?", command=self.prompt_copy_to_input_tab).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(output_title_row, text="Copy to Clipboard", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(output_title_row, text="Clear All Output Tabs", command=self.clear_all_output_tabs).pack(side=tk.LEFT)

        self.diff_input_notebook = ttk.Notebook(self.diff_frame)
        self.diff_input_notebook.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        self.diff_input_tabs = []
        for i in range(AppConfig.TAB_COUNT):
            tab = TextWithLineNumbers(self.diff_input_notebook)
            tab.text.bind("<<Modified>>", self.on_tab_content_changed)
            self.diff_input_tabs.append(tab)
            self.diff_input_notebook.add(tab, text=f"Input {i+1}")
        
        self.diff_output_notebook = ttk.Notebook(self.diff_frame)
        self.diff_output_notebook.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        self.diff_output_tabs = []
        for i in range(AppConfig.TAB_COUNT):
            tab = TextWithLineNumbers(self.diff_output_notebook)
            tab.text.bind("<<Modified>>", self.on_tab_content_changed)
            self.diff_output_tabs.append(tab)
            self.diff_output_notebook.add(tab, text=f"Output {i+1}")

        for tab_list in [self.diff_input_tabs, self.diff_output_tabs]:
            for tab in tab_list:
                widget = tab.text
                widget.config(state="normal")
                widget.tag_configure("addition", background="#e6ffed")
                widget.tag_configure("deletion", background="#ffebe9")
                widget.tag_configure("modification", background="#e6f7ff")
                widget.tag_configure("inline_add", background="#a7f0ba")
                widget.tag_configure("inline_del", background="#ffc9c9")

        self.diff_input_notebook.bind("<<NotebookTabChanged>>", self._setup_diff_sync)
        self.diff_output_notebook.bind("<<NotebookTabChanged>>", self._setup_diff_sync)
        self._setup_diff_sync()

    def _setup_diff_sync(self, event=None):
        """Configures scroll and mousewheel syncing for the active diff tabs."""
        try:
            active_input_tab = self.diff_input_tabs[self.diff_input_notebook.index("current")]
            active_output_tab = self.diff_output_tabs[self.diff_output_notebook.index("current")]
        except (tk.TclError, IndexError):
            return

        active_input_tab.text.vbar.config(command=self._sync_diff_scroll)
        active_output_tab.text.vbar.config(command=self._sync_diff_scroll)

        for tab in [active_input_tab, active_output_tab]:
            tab.text.bind("<MouseWheel>", self._on_diff_mousewheel)
            tab.text.bind("<Button-4>", self._on_diff_mousewheel)
            tab.text.bind("<Button-5>", self._on_diff_mousewheel)

    def _sync_diff_scroll(self, *args):
        """Syncs both diff viewer text widgets when one's scrollbar is used."""
        active_input_tab = self.diff_input_tabs[self.diff_input_notebook.index("current")]
        active_output_tab = self.diff_output_tabs[self.diff_output_notebook.index("current")]
        
        active_input_tab.text.yview(*args)
        active_output_tab.text.yview(*args)
        
        active_input_tab._on_text_modified()
        active_output_tab._on_text_modified()

    def _on_diff_mousewheel(self, event):
        """Handles mouse wheel scrolling over either diff text widget."""
        if platform.system() == "Windows":
            delta = int(-1*(event.delta/120))
        elif platform.system() == "Darwin":
            delta = int(-1 * event.delta)
        else:
            delta = -1 if event.num == 4 else 1
        
        active_input_tab = self.diff_input_tabs[self.diff_input_notebook.index("current")]
        active_output_tab = self.diff_output_tabs[self.diff_output_notebook.index("current")]
        
        active_input_tab.text.yview_scroll(delta, "units")
        active_output_tab.text.yview_scroll(delta, "units")
        
        active_input_tab._on_text_modified()
        active_output_tab._on_text_modified()
        return "break"

    def on_tool_selected(self, event=None):
        """Handles the selection of a new tool from the dropdown."""
        self.stop_morse_audio()
        tool_name = self.tool_var.get()
        self.settings["selected_tool"] = tool_name
        self.logger.info(f"Tool selected: {tool_name}")

        if tool_name == "Diff Viewer":
            self.central_frame.grid_remove()
            self.diff_frame.grid(row=1, column=0, sticky="nsew", pady=5)
            self.update_tool_settings_ui()
            self.load_diff_viewer_content()
            self.run_diff_viewer()
        else:
            if hasattr(self, 'diff_frame') and self.diff_frame.winfo_viewable():
                self.sync_diff_viewer_to_main_tabs()
            
            self.diff_frame.grid_remove()
            self.central_frame.grid()
            
            self.update_tool_settings_ui()

            if tool_name not in self.manual_process_tools:
                self.apply_tool()
            
        self.save_settings()

    def update_tool_settings_ui(self):
        """Updates the UI to show settings for the currently selected tool."""
        for widget in self.tool_settings_frame.winfo_children():
            widget.destroy()

        tool_name = self.tool_var.get()
        tool_settings = self.settings["tool_settings"].get(tool_name, {})

        if tool_name in ["Google AI", "Anthropic AI", "OpenAI", "Cohere AI", "HuggingFace AI", "Groq AI", "OpenRouterAI"]:
            self.create_ai_provider_widgets(self.tool_settings_frame, tool_name)
        elif tool_name == "Case Tool":
            self.create_case_tool_widgets(self.tool_settings_frame, tool_settings)
        elif tool_name == "Morse Code Translator":
            self.morse_mode = tk.StringVar(value=tool_settings.get("mode", "morse"))
            ttk.Radiobutton(self.tool_settings_frame, text="Text to Morse", variable=self.morse_mode, value="morse", command=self.on_tool_setting_change).pack(side=tk.LEFT)
            ttk.Radiobutton(self.tool_settings_frame, text="Morse to Text", variable=self.morse_mode, value="text", command=self.on_tool_setting_change).pack(side=tk.LEFT)
            ttk.Button(self.tool_settings_frame, text="Process", command=self.apply_tool).pack(side=tk.LEFT, padx=10)
            self.play_morse_button = ttk.Button(self.tool_settings_frame, text="Play Morse Audio", command=self.play_morse_audio)
            self.play_morse_button.pack(side=tk.LEFT, padx=10)
        elif tool_name == "Base64 Encoder/Decoder":
            self.base64_mode = tk.StringVar(value=tool_settings.get("mode", "encode"))
            ttk.Radiobutton(self.tool_settings_frame, text="Encode", variable=self.base64_mode, value="encode", command=self.on_tool_setting_change).pack(side=tk.LEFT)
            ttk.Radiobutton(self.tool_settings_frame, text="Decode", variable=self.base64_mode, value="decode", command=self.on_tool_setting_change).pack(side=tk.LEFT)
            ttk.Button(self.tool_settings_frame, text="Process", command=self.apply_tool).pack(side=tk.LEFT, padx=10)
        elif tool_name == "Number Sorter":
            self.number_order = tk.StringVar(value=tool_settings.get("order", "ascending"))
            ttk.Radiobutton(self.tool_settings_frame, text="Ascending", variable=self.number_order, value="ascending", command=self.on_tool_setting_change).pack(side=tk.LEFT)
            ttk.Radiobutton(self.tool_settings_frame, text="Descending", variable=self.number_order, value="descending", command=self.on_tool_setting_change).pack(side=tk.LEFT)
            ttk.Button(self.tool_settings_frame, text="Sort", command=self.apply_tool).pack(side=tk.LEFT, padx=10)
        elif tool_name == "Find & Replace Text":
            self.create_find_replace_widgets(self.tool_settings_frame, tool_settings)
        elif tool_name == "Repeating Text Generator":
            ttk.Label(self.tool_settings_frame, text="Times:").pack(side=tk.LEFT, padx=(10, 2))
            self.repeat_times_var = tk.StringVar(value=str(tool_settings.get("times", 5)))
            ttk.Entry(self.tool_settings_frame, textvariable=self.repeat_times_var, width=5).pack(side=tk.LEFT)
            self.repeat_times_var.trace_add("write", self.on_tool_setting_change)
            ttk.Label(self.tool_settings_frame, text="Separator:").pack(side=tk.LEFT, padx=(10, 2))
            self.repeat_sep_var = tk.StringVar(value=tool_settings.get("separator", "+"))
            ttk.Entry(self.tool_settings_frame, textvariable=self.repeat_sep_var, width=5).pack(side=tk.LEFT)
            self.repeat_sep_var.trace_add("write", self.on_tool_setting_change)
            ttk.Button(self.tool_settings_frame, text="Repeat", command=self.apply_tool).pack(side=tk.LEFT, padx=10)
        elif tool_name == "Alphabetical Sorter":
            self.alpha_order = tk.StringVar(value=tool_settings.get("order", "ascending"))
            ttk.Radiobutton(self.tool_settings_frame, text="Ascending (A-Z)", variable=self.alpha_order, value="ascending", command=self.on_tool_setting_change).pack(side=tk.LEFT)
            ttk.Radiobutton(self.tool_settings_frame, text="Descending (Z-A)", variable=self.alpha_order, value="descending", command=self.on_tool_setting_change).pack(side=tk.LEFT)
            self.alpha_trim = tk.BooleanVar(value=tool_settings.get("trim", False))
            ttk.Checkbutton(self.tool_settings_frame, text="Trim", variable=self.alpha_trim, command=self.on_tool_setting_change).pack(side=tk.LEFT, padx=10)
            self.alpha_unique_only = tk.BooleanVar(value=tool_settings.get("unique_only", False))
            ttk.Checkbutton(self.tool_settings_frame, text="Only Unique Values", variable=self.alpha_unique_only, command=self.on_tool_setting_change).pack(side=tk.LEFT, padx=10)
            ttk.Button(self.tool_settings_frame, text="Sort", command=self.apply_tool).pack(side=tk.LEFT, padx=10)
        elif tool_name == "Strong Password Generator":
            ttk.Label(self.tool_settings_frame, text="Length:").pack(side=tk.LEFT, padx=(10, 2))
            self.pw_len_var = tk.StringVar(value=str(tool_settings.get("length", 20)))
            ttk.Entry(self.tool_settings_frame, textvariable=self.pw_len_var, width=5).pack(side=tk.LEFT)
            self.pw_len_var.trace_add("write", self.on_tool_setting_change)
            ttk.Label(self.tool_settings_frame, text="Include Numbers:").pack(side=tk.LEFT, padx=(10, 2))
            self.pw_num_var = tk.StringVar(value=tool_settings.get("numbers", ""))
            ttk.Entry(self.tool_settings_frame, textvariable=self.pw_num_var, width=10).pack(side=tk.LEFT)
            self.pw_num_var.trace_add("write", self.on_tool_setting_change)
            ttk.Label(self.tool_settings_frame, text="Include Symbols:").pack(side=tk.LEFT, padx=(10, 2))
            self.pw_sym_var = tk.StringVar(value=tool_settings.get("symbols", ""))
            ttk.Entry(self.tool_settings_frame, textvariable=self.pw_sym_var, width=10).pack(side=tk.LEFT)
            self.pw_sym_var.trace_add("write", self.on_tool_setting_change)
            ttk.Button(self.tool_settings_frame, text="Generate", command=self.apply_tool).pack(side=tk.LEFT, padx=10)
        elif tool_name == "URL Parser":
            default_decode = tool_settings.get("ascii_decode", True)
            self.url_parser_decode_var = tk.BooleanVar(value=default_decode)
            chk = ttk.Checkbutton(self.tool_settings_frame, text="ASCII Decoding", variable=self.url_parser_decode_var, command=self.on_tool_setting_change)
            chk.pack(side=tk.LEFT, padx=5)
            ttk.Button(self.tool_settings_frame, text="Parse", command=self.apply_tool).pack(side=tk.LEFT, padx=10)
        elif tool_name == "Diff Viewer":
            dv_settings = self.settings["tool_settings"].get("Diff Viewer", {})
            default_option = dv_settings.get("option", "ignore_case")
            self.diff_option_var = tk.StringVar(value=default_option)
            ttk.Radiobutton(self.tool_settings_frame, text="Ignore case", variable=self.diff_option_var, value="ignore_case", command=self.on_tool_setting_change).pack(side=tk.LEFT, padx=(0, 8))
            ttk.Radiobutton(self.tool_settings_frame, text="Match case", variable=self.diff_option_var, value="match_case", command=self.on_tool_setting_change).pack(side=tk.LEFT, padx=(0, 8))
            ttk.Radiobutton(self.tool_settings_frame, text="Ignore whitespace", variable=self.diff_option_var, value="ignore_whitespace", command=self.on_tool_setting_change).pack(side=tk.LEFT, padx=(0, 16))
            ttk.Button(self.tool_settings_frame, text="Compare Active Tabs", command=self.run_diff_viewer).pack(side=tk.LEFT, padx=5)
        elif tool_name == "Extract Emails":
            ttk.Button(self.tool_settings_frame, text="Extract", command=self.apply_tool).pack(side=tk.LEFT, padx=10)
        elif tool_name == "Word Frequency Counter":
            ttk.Button(self.tool_settings_frame, text="Count", command=self.apply_tool).pack(side=tk.LEFT, padx=10)
        elif tool_name == "Binary Code Translator":
            ttk.Button(self.tool_settings_frame, text="Process", command=self.apply_tool).pack(side=tk.LEFT, padx=10)

    def create_case_tool_widgets(self, parent, settings):
        """Creates the UI for the new consolidated Case Tool."""
        self.case_mode_var = tk.StringVar(value=settings.get("mode", "Sentence"))

        radio_frame = ttk.Frame(parent)
        radio_frame.pack(side=tk.LEFT, padx=5)

        modes = ["Sentence", "Lower", "Upper", "Capitalized", "Title"]
        for mode in modes:
            rb = ttk.Radiobutton(radio_frame, text=mode, variable=self.case_mode_var, value=mode, command=self.on_case_tool_mode_change)
            rb.pack(anchor="w")

        self.title_case_frame = ttk.Frame(parent)
        ttk.Label(self.title_case_frame, text="Exclusions (one per line):").pack(anchor="w")
        self.title_case_exclusions = tk.Text(self.title_case_frame, height=5, width=20)
        self.title_case_exclusions.insert(tk.END, settings.get("exclusions", ""))
        self.title_case_exclusions.pack(side=tk.LEFT, padx=5)
        self.title_case_exclusions.bind("<KeyRelease>", self.on_tool_setting_change)

        ttk.Button(parent, text="Process", command=self.apply_tool).pack(side=tk.LEFT, padx=10, pady=10)
        self.on_case_tool_mode_change()

    def on_case_tool_mode_change(self):
        """Shows or hides the Title Case exclusions widgets."""
        if self.case_mode_var.get() == "Title":
            self.title_case_frame.pack(side=tk.LEFT, padx=5)
        else:
            self.title_case_frame.pack_forget()
        self.on_tool_setting_change()

    def create_ai_provider_widgets(self, parent, provider_name):
        """Creates a standardized set of widgets for an AI provider."""
        self.ai_widgets = {} # Clear previous widgets
        settings = self.settings["tool_settings"].get(provider_name, {})
        model_list = settings.get("MODELS_LIST", [])
        
        # --- Top Frame for essential controls ---
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=tk.X, expand=True, pady=(0, 5))

        api_key_var = tk.StringVar(value=settings.get("API_KEY", "putinyourkey"))
        self.ai_widgets[f"{provider_name}_api_key_var"] = api_key_var
        ttk.Label(top_frame, text="API Key:").pack(side=tk.LEFT)
        entry = ttk.Entry(top_frame, textvariable=api_key_var, width=20, show="*")
        entry.pack(side=tk.LEFT, padx=(2, 5))
        api_key_var.trace_add("write", self.on_tool_setting_change)
        
        if provider_name in self.ai_provider_urls:
            url = self.ai_provider_urls[provider_name]
            link_font = font.Font(family="Helvetica", size=9, underline=True)
            link_label = ttk.Label(top_frame, text="Get API Key", foreground="blue", cursor="hand2", font=link_font)
            link_label.pack(side=tk.LEFT, padx=(0, 10))
            link_label.bind("<Button-1>", lambda e, link=url: webbrowser.open_new(link))
        
        model_var = tk.StringVar(value=settings.get("MODEL", model_list[0] if model_list else ""))
        self.ai_widgets[f"{provider_name}_model_var"] = model_var
        ttk.Label(top_frame, text="Model:").pack(side=tk.LEFT)
        model_menu = ttk.Combobox(top_frame, textvariable=model_var, values=model_list, state="normal", width=30)
        model_menu.pack(side=tk.LEFT, padx=2)
        model_menu.bind("<<ComboboxSelected>>", self.on_tool_setting_change)
        model_menu.bind("<KeyRelease>", self.on_tool_setting_change)

        ttk.Button(top_frame, text="\u270E", command=lambda: self.open_model_editor(provider_name), width=3).pack(side=tk.LEFT, padx=(0,10))
        ttk.Button(top_frame, text="Process", command=self.run_ai_in_thread).pack(side=tk.LEFT, padx=5)
        
        # --- System Prompt ---
        system_prompt_key = "system_prompt"
        if provider_name == "Anthropic AI": system_prompt_key = "system"
        elif provider_name == "Cohere AI": system_prompt_key = "preamble"
        
        system_frame = ttk.Frame(parent)
        system_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        ttk.Label(system_frame, text="System Message:").pack(side=tk.LEFT, anchor='n', padx=(0,5))
        system_prompt_text = scrolledtext.ScrolledText(system_frame, height=3, width=50, wrap=tk.WORD)
        system_prompt_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        system_prompt_text.insert("1.0", settings.get(system_prompt_key, "You are a helpful assistant."))
        system_prompt_text.bind("<KeyRelease>", self.on_tool_setting_change)
        self.ai_widgets[f"{provider_name}_system_prompt"] = system_prompt_text
        self.ai_widgets[f"{provider_name}_system_prompt_key"] = system_prompt_key

        # --- Parameters ---
        params_config = self._get_ai_params_config(provider_name)
        if not params_config: return
        
        params_notebook = ttk.Notebook(parent)
        params_notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        sampling_frame = ttk.Frame(params_notebook, padding=5)
        params_notebook.add(sampling_frame, text="Sampling")
        
        content_frame = ttk.Frame(params_notebook, padding=5)
        params_notebook.add(content_frame, text="Content Control")

        self.ai_widgets[f"{provider_name}_params"] = {}
        
        s_row, c_row = 0, 0
        for name, config in params_config.items():
            frame = sampling_frame if config['tab'] == 'sampling' else content_frame
            row = s_row if config['tab'] == 'sampling' else c_row
            
            var = self._create_parameter_widget(frame, name, config, settings.get(name), row)
            var.trace_add("write", self.on_tool_setting_change)
            self.ai_widgets[f"{provider_name}_params"][name] = var
            
            if config['tab'] == 'sampling': s_row += 1
            else: c_row += 1
    
    def _get_ai_params_config(self, provider_name):
        """Returns the parameter configuration for a given AI provider."""
        configs = {
            "Google AI": {
                "temperature": {"tab": "sampling", "type": "scale", "range": (0.0, 2.0), "res": 0.1, "tip": "Controls randomness. Higher is more creative."},
                "topP": {"tab": "sampling", "type": "scale", "range": (0.0, 1.0), "res": 0.05, "tip": "Cumulative probability threshold for token selection."},
                "topK": {"tab": "sampling", "type": "entry", "tip": "Number of top tokens to consider for sampling."},
                "maxOutputTokens": {"tab": "content", "type": "entry", "tip": "Maximum number of tokens in the response."},
                "candidateCount": {"tab": "content", "type": "entry", "tip": "Number of response variations to generate (1-8)."},
                "stopSequences": {"tab": "content", "type": "entry", "tip": "Comma-separated list of strings to stop generation."}
            },
            "Anthropic AI": {
                "temperature": {"tab": "sampling", "type": "scale", "range": (0.0, 1.0), "res": 0.1, "tip": "Controls randomness. Higher is more creative."},
                "top_p": {"tab": "sampling", "type": "scale", "range": (0.0, 1.0), "res": 0.05, "tip": "Cumulative probability threshold for token selection."},
                "top_k": {"tab": "sampling", "type": "entry", "tip": "Number of top tokens to consider for sampling."},
                "max_tokens": {"tab": "content", "type": "entry", "tip": "Maximum number of tokens in the response."},
                "stop_sequences": {"tab": "content", "type": "entry", "tip": "Comma-separated list of strings to stop generation."}
            },
            "OpenAI": {
                "temperature": {"tab": "sampling", "type": "scale", "range": (0.0, 2.0), "res": 0.1, "tip": "Controls randomness. Higher is more creative."},
                "top_p": {"tab": "sampling", "type": "scale", "range": (0.0, 1.0), "res": 0.05, "tip": "Nucleus sampling threshold."},
                "seed": {"tab": "sampling", "type": "entry", "tip": "Integer for reproducible outputs (Beta)."},
                "max_tokens": {"tab": "content", "type": "entry", "tip": "Maximum number of tokens in the response."},
                "frequency_penalty": {"tab": "content", "type": "scale", "range": (-2.0, 2.0), "res": 0.1, "tip": "Penalizes repeating tokens."},
                "presence_penalty": {"tab": "content", "type": "scale", "range": (-2.0, 2.0), "res": 0.1, "tip": "Penalizes introducing new tokens."},
                "stop": {"tab": "content", "type": "entry", "tip": "Comma-separated list of strings to stop generation."},
                "response_format": {"tab": "content", "type": "combo", "values": ["text", "json_object"], "tip": "Force JSON output."}
            },
            "Cohere AI": {
                "temperature": {"tab": "sampling", "type": "scale", "range": (0.0, 1.0), "res": 0.1, "tip": "Controls randomness. Higher is more creative."},
                "p": {"tab": "sampling", "type": "scale", "range": (0.0, 1.0), "res": 0.05, "tip": "Top-p/nucleus sampling threshold."},
                "k": {"tab": "sampling", "type": "entry", "tip": "Top-k sampling (0-500)."},
                "max_tokens": {"tab": "content", "type": "entry", "tip": "Maximum number of tokens in the response."},
                "frequency_penalty": {"tab": "content", "type": "scale", "range": (0.0, 1.0), "res": 0.1, "tip": "Reduces repetition."},
                "presence_penalty": {"tab": "content", "type": "scale", "range": (0.0, 1.0), "res": 0.1, "tip": "Encourages new topics."},
                "stop_sequences": {"tab": "content", "type": "entry", "tip": "Comma-separated list of strings to stop generation."},
                "citation_quality": {"tab": "content", "type": "combo", "values": ["accurate", "fast"], "tip": "Citation quality vs. speed."}
            },
            "HuggingFace AI": {
                "temperature": {"tab": "sampling", "type": "scale", "range": (0.0, 2.0), "res": 0.1, "tip": "Controls randomness. Higher is more creative."},
                "top_p": {"tab": "sampling", "type": "scale", "range": (0.0, 1.0), "res": 0.05, "tip": "Nucleus sampling threshold."},
                "seed": {"tab": "sampling", "type": "entry", "tip": "Integer for reproducible outputs."},
                "max_tokens": {"tab": "content", "type": "entry", "tip": "Maximum number of tokens in the response."},
                "stop_sequences": {"tab": "content", "type": "entry", "tip": "Comma-separated list of strings to stop generation."}
            },
            "Groq AI": {
                "temperature": {"tab": "sampling", "type": "scale", "range": (0.0, 2.0), "res": 0.1, "tip": "Controls randomness. Higher is more creative."},
                "top_p": {"tab": "sampling", "type": "scale", "range": (0.0, 1.0), "res": 0.05, "tip": "Nucleus sampling threshold."},
                "seed": {"tab": "sampling", "type": "entry", "tip": "Integer for reproducible outputs."},
                "max_tokens": {"tab": "content", "type": "entry", "tip": "Maximum number of tokens in the response."},
                "frequency_penalty": {"tab": "content", "type": "scale", "range": (-2.0, 2.0), "res": 0.1, "tip": "Penalizes repeating tokens."},
                "presence_penalty": {"tab": "content", "type": "scale", "range": (-2.0, 2.0), "res": 0.1, "tip": "Penalizes introducing new tokens."},
                "stop": {"tab": "content", "type": "entry", "tip": "Comma-separated list of strings to stop generation."},
                "response_format": {"tab": "content", "type": "combo", "values": ["text", "json_object"], "tip": "Force JSON output."}
            },
             "OpenRouterAI": {
                "temperature": {"tab": "sampling", "type": "scale", "range": (0.0, 2.0), "res": 0.1, "tip": "Controls randomness. Higher is more creative."},
                "top_p": {"tab": "sampling", "type": "scale", "range": (0.0, 1.0), "res": 0.05, "tip": "Nucleus sampling threshold."},
                "top_k": {"tab": "sampling", "type": "entry", "tip": "Top-k sampling (0=disabled)."},
                "seed": {"tab": "sampling", "type": "entry", "tip": "Integer for reproducible outputs."},
                "max_tokens": {"tab": "content", "type": "entry", "tip": "Maximum number of tokens in the response."},
                "frequency_penalty": {"tab": "content", "type": "scale", "range": (-2.0, 2.0), "res": 0.1, "tip": "Penalizes repeating tokens."},
                "presence_penalty": {"tab": "content", "type": "scale", "range": (-2.0, 2.0), "res": 0.1, "tip": "Penalizes introducing new tokens."},
                "repetition_penalty": {"tab": "content", "type": "scale", "range": (0.0, 2.0), "res": 0.1, "tip": "Penalizes repeating tokens (1.0 = none)."},
                "stop": {"tab": "content", "type": "entry", "tip": "Comma-separated list of strings to stop generation."}
            }
        }
        return configs.get(provider_name, {})

    def _create_parameter_widget(self, parent, name, config, current_value, row):
        """Creates a label and an appropriate widget for a given AI parameter."""
        var = tk.StringVar(value=str(current_value))
        
        lbl = ttk.Label(parent, text=f"{name}:")
        lbl.grid(row=row, column=0, sticky='w', padx=5, pady=2)
        self.Tooltip(lbl, config['tip'])
        
        widget_type = config['type']
        if widget_type == 'scale':
            start, end = config['range']
            widget = ttk.Scale(parent, from_=start, to=end, orient='horizontal', variable=var,
                               command=lambda v, v_var=var: v_var.set(f"{float(v):.2f}"))
            # Display value next to scale
            val_lbl = ttk.Label(parent, textvariable=var, width=5)
            val_lbl.grid(row=row, column=2, sticky='w', padx=5)
        elif widget_type == 'entry':
            widget = ttk.Entry(parent, textvariable=var)
        elif widget_type == 'combo':
            widget = ttk.Combobox(parent, textvariable=var, values=config['values'], state='readonly')
            if current_value not in config['values']: # Set a default if saved value is invalid
                var.set(config['values'][0])

        widget.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
        parent.grid_columnconfigure(1, weight=1)
        return var

    def open_model_editor(self, provider_name):
        """Opens a Toplevel window to edit the model list for an AI provider."""
        dialog = tk.Toplevel(self)
        dialog.title(f"Edit {provider_name} Models")
        
        self.update_idletasks()
        dialog_width = 400
        dialog_height = 200
        main_x, main_y, main_width, main_height = self.winfo_x(), self.winfo_y(), self.winfo_width(), self.winfo_height()
        pos_x = main_x + (main_width // 2) - (dialog_width // 2)
        pos_y = main_y + (main_height // 2) - (dialog_height // 2)
        dialog.geometry(f"{dialog_width}x{dialog_height}+{pos_x}+{pos_y}")
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(dialog, text="One model per line. The first line is the default.").pack(pady=(10, 2))
        
        text_area = tk.Text(dialog, height=7, width=45)
        text_area.pack(pady=5, padx=10)
        
        current_models = self.settings["tool_settings"].get(provider_name, {}).get("MODELS_LIST", [])
        text_area.insert("1.0", "\n".join(current_models))
        
        save_button = ttk.Button(dialog, text="Save Changes", command=lambda: self.save_model_list(provider_name, text_area, dialog))
        save_button.pack(pady=5)

    def save_model_list(self, provider_name, text_area, dialog):
        """Saves the edited model list back to settings."""
        content = text_area.get("1.0", tk.END)
        new_list = [line.strip() for line in content.splitlines() if line.strip()]
        
        if not new_list:
            messagebox.showwarning("No Models", "Model list cannot be empty.", parent=dialog)
            return
            
        self.settings["tool_settings"][provider_name]["MODELS_LIST"] = new_list
        self.settings["tool_settings"][provider_name]["MODEL"] = new_list[0]
        
        self.save_settings()
        self.update_tool_settings_ui()
        dialog.destroy()

    def create_find_replace_widgets(self, parent, settings):
        """Creates the complex UI for the Find & Replace tool."""
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        options_frame = ttk.Frame(parent)
        options_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        self.match_count_label = ttk.Label(controls_frame, text="Found matches: 0")
        self.match_count_label.pack(anchor="w")

        find_frame = ttk.Frame(controls_frame)
        find_frame.pack(fill=tk.X, pady=2)
        ttk.Label(find_frame, text="Find:").pack(side=tk.LEFT)
        self.find_text_area = tk.Text(find_frame, height=2, width=30)
        self.find_text_area.insert("1.0", settings.get("find", ""))
        self.find_text_area.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.find_mode_var = tk.StringVar(value=settings.get("mode", "Text"))
        find_mode_menu = ttk.Combobox(find_frame, textvariable=self.find_mode_var, values=["Text", "Regex"], state="readonly", width=5)
        find_mode_menu.pack(side=tk.LEFT)
        find_mode_menu.bind("<<ComboboxSelected>>", self.on_tool_setting_change)

        replace_frame = ttk.Frame(controls_frame)
        replace_frame.pack(fill=tk.X, pady=2)
        ttk.Label(replace_frame, text="Replace:").pack(side=tk.LEFT)
        self.replace_text_area = tk.Text(replace_frame, height=2, width=30)
        self.replace_text_area.insert("1.0", settings.get("replace", ""))
        self.replace_text_area.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(fill=tk.X, pady=5)
        ttk.Button(buttons_frame, text="Preview", command=self.preview_find_replace).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Process", command=self.apply_tool).pack(side=tk.LEFT, padx=5)

        self.fr_option_var = tk.StringVar(value=settings.get("option", "ignore_case"))
        options = {
            "ignore_case": "Ignore case", "match_case": "Match case", "whole_words": "Find whole words only", 
            "wildcards": "Use wildcards (*, ?)", "match_prefix": "Match prefix", "match_suffix": "Match suffix", 
            "sounds_like": "Sounds like (English)", "all_word_forms": "Find all word forms (English)", 
            "ignore_punctuation": "Ignore punctuation", "ignore_whitespace": "Ignore white-space"
        }
        
        col = 0
        row = 0
        for key, text in options.items():
            rb = ttk.Radiobutton(options_frame, text=text, variable=self.fr_option_var, value=key, command=self.on_tool_setting_change)
            rb.grid(row=row, column=col, sticky="w")
            row += 1
            if row > 4:
                row = 0
                col += 1

    def on_tool_setting_change(self, *args):
        """
        Handles changes in tool-specific settings.
        Also saves the new settings.
        """
        tool_name = self.tool_var.get()
        if tool_name not in self.settings["tool_settings"]:
            self.settings["tool_settings"][tool_name] = {}

        if tool_name in ["Google AI", "Anthropic AI", "OpenAI", "Cohere AI", "HuggingFace AI", "Groq AI", "OpenRouterAI"]:
            settings = self.settings["tool_settings"][tool_name]
            if f"{tool_name}_api_key_var" in self.ai_widgets:
                settings["API_KEY"] = self.ai_widgets[f"{tool_name}_api_key_var"].get()
            if f"{tool_name}_model_var" in self.ai_widgets:
                settings["MODEL"] = self.ai_widgets[f"{tool_name}_model_var"].get()
            
            system_prompt_widget = self.ai_widgets.get(f"{tool_name}_system_prompt")
            system_prompt_key = self.ai_widgets.get(f"{tool_name}_system_prompt_key")
            if system_prompt_widget and system_prompt_key:
                settings[system_prompt_key] = system_prompt_widget.get("1.0", tk.END).strip()
            
            param_vars = self.ai_widgets.get(f"{tool_name}_params", {})
            for key, var in param_vars.items():
                settings[key] = var.get()

        elif tool_name == "Case Tool":
            self.settings["tool_settings"][tool_name]["mode"] = self.case_mode_var.get()
            if hasattr(self, 'title_case_exclusions'):
                self.settings["tool_settings"][tool_name]["exclusions"] = self.title_case_exclusions.get("1.0", tk.END).strip()
        elif tool_name == "Morse Code Translator":
            self.settings["tool_settings"][tool_name]["mode"] = self.morse_mode.get()
        elif tool_name == "Base64 Encoder/Decoder":
            self.settings["tool_settings"][tool_name]["mode"] = self.base64_mode.get()
        elif tool_name == "Number Sorter":
            self.settings["tool_settings"][tool_name]["order"] = self.number_order.get()
        elif tool_name == "Find & Replace Text":
            settings = self.settings["tool_settings"][tool_name]
            settings["find"] = self.find_text_area.get("1.0", tk.END).strip()
            settings["replace"] = self.replace_text_area.get("1.0", tk.END).strip()
            settings["mode"] = self.find_mode_var.get()
            settings["option"] = self.fr_option_var.get()
        elif tool_name == "Repeating Text Generator":
            try:
                self.settings["tool_settings"][tool_name]["times"] = int(self.repeat_times_var.get())
            except ValueError: pass
            self.settings["tool_settings"][tool_name]["separator"] = self.repeat_sep_var.get()
        elif tool_name == "Alphabetical Sorter":
            self.settings["tool_settings"][tool_name]["order"] = self.alpha_order.get()
            self.settings["tool_settings"][tool_name]["unique_only"] = self.alpha_unique_only.get()
            self.settings["tool_settings"][tool_name]["trim"] = self.alpha_trim.get()
        elif tool_name == "Strong Password Generator":
            try:
                self.settings["tool_settings"][tool_name]["length"] = int(self.pw_len_var.get())
            except ValueError: pass
            self.settings["tool_settings"][tool_name]["numbers"] = self.pw_num_var.get()
            self.settings["tool_settings"][tool_name]["symbols"] = self.pw_sym_var.get()
        elif tool_name == "URL Parser":
            self.settings["tool_settings"][tool_name]["ascii_decode"] = self.url_parser_decode_var.get()
        elif tool_name == "Diff Viewer":
            if "Diff Viewer" not in self.settings["tool_settings"]:
                self.settings["tool_settings"]["Diff Viewer"] = {}
            self.settings["tool_settings"]["Diff Viewer"]["option"] = self.diff_option_var.get()

        if tool_name not in self.manual_process_tools:
            self.apply_tool()
        
        self.save_settings()
        self.after(10, self.update_all_stats)
        
    def browse_export_path(self):
        """Opens a dialog to choose an export directory."""
        path = filedialog.askdirectory(initialdir=self.export_path_var.get())
        if path:
            self.export_path_var.set(path)
            self.settings["export_path"] = path
            self.save_settings()
            self.logger.info(f"Export path set to: {path}")

    def update_log_level(self, event=None):
        """Updates the logger's level based on the dropdown selection."""
        level = self.log_level.get()
        self.logger.setLevel(level)
        self.settings["debug_level"] = level
        self.save_settings()
        self.logger.warning(f"Log level changed to {level}")

    def update_stats(self, text_widget, status_bar):
        """Calculates and updates the status bar for a given text widget."""
        text = text_widget.get("1.0", tk.END)
        char_count = len(text.strip())
        word_count = len(re.findall(r'\S+', text))
        sentence_count = len(re.findall(r'[.!?]+', text))
        line_count = text.count('\n')
        token_count = round(len(text) / 4)

        status_bar.config(text=f"Char: {char_count} | Word: {word_count} | Sentence: {sentence_count} | Line: {line_count} | Tokens: {token_count}")

    def update_tab_labels(self):
        """Updates tab labels to show first 7 non-whitespace characters of content."""
        for i, tab in enumerate(self.input_tabs):
            content = tab.text.get("1.0", tk.END).strip()
            first_chars = ''.join(char for char in content if char not in ' \t\n\r')[:7]
            self.input_notebook.tab(i, text=f"{i+1}: {first_chars}" if first_chars else f"{i+1}:")
        
        for i, tab in enumerate(self.output_tabs):
            content = tab.text.get("1.0", tk.END).strip()
            first_chars = ''.join(char for char in content if char not in ' \t\n\r')[:7]
            self.output_notebook.tab(i, text=f"{i+1}: {first_chars}" if first_chars else f"{i+1}:")
        
        if hasattr(self, 'diff_input_tabs'):
            for i, tab in enumerate(self.diff_input_tabs):
                content = tab.text.get("1.0", tk.END).strip()
                first_chars = ''.join(char for char in content if char not in ' \t\n\r')[:7]
                self.diff_input_notebook.tab(i, text=f"{i+1}: {first_chars}" if first_chars else f"{i+1}:")
            
            for i, tab in enumerate(self.diff_output_tabs):
                content = tab.text.get("1.0", tk.END).strip()
                first_chars = ''.join(char for char in content if char not in ' \t\n\r')[:7]
                self.diff_output_notebook.tab(i, text=f"{i+1}: {first_chars}" if first_chars else f"{i+1}:")

    def update_all_stats(self):
        """Updates the status bars for both input and output."""
        active_input_tab = self.input_tabs[self.input_notebook.index(self.input_notebook.select())]
        active_output_tab = self.output_tabs[self.output_notebook.index(self.output_notebook.select())]
        self.update_stats(active_input_tab.text, self.input_status_bar)
        self.update_stats(active_output_tab.text, self.output_status_bar)
        self.update_tab_labels()

    def on_input_changed(self, event=None):
        """Handles input changes with debouncing."""
        self.update_all_stats()
        
        if self.tool_var.get() in self.manual_process_tools:
            return

        if hasattr(self, '_after_id') and self._after_id:
            self.after_cancel(self._after_id)
        
        self._after_id = self.after(AppConfig.DEBOUNCE_DELAY, self.apply_tool)

    def prompt_copy_to_input_tab(self):
        """Opens a confirmation window to select which input tab to copy to."""
        dialog = tk.Toplevel(self)
        dialog.title("Select Destination Tab")
        
        self.update_idletasks()
        dialog_width, dialog_height = 650, 100
        main_x, main_y, main_width, main_height = self.winfo_x(), self.winfo_y(), self.winfo_width(), self.winfo_height()
        pos_x = main_x + (main_width // 2) - (dialog_width // 2)
        pos_y = main_y + (main_height // 2) - (dialog_height // 2)
        dialog.geometry(f"{dialog_width}x{dialog_height}+{pos_x}+{pos_y}")
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(dialog, text="Copy the current output to which input tab?").pack(pady=10)

        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=5)

        for i in range(AppConfig.TAB_COUNT):
            btn = ttk.Button(button_frame, text=f"Tab {i+1}", 
                             command=lambda target_tab=i: self.copy_to_specific_input_tab(target_tab, dialog))
            btn.grid(row=0, column=i, padx=5, pady=5)

    def copy_to_specific_input_tab(self, target_tab_index, dialog):
        """Copies output to a specific input tab and closes the dialog."""
        if hasattr(self, 'diff_frame') and self.diff_frame.winfo_viewable():
            active_output_tab = self.diff_output_tabs[self.diff_output_notebook.index("current")]
        else:
            active_output_tab = self.output_tabs[self.output_notebook.index("current")]
        
        output_text = active_output_tab.text.get("1.0", tk.END)
        
        destination_tab = self.input_tabs[target_tab_index]
        destination_tab.text.delete("1.0", tk.END)
        destination_tab.text.insert("1.0", output_text)

        self.logger.info(f"Output copied to Input Tab {target_tab_index + 1}.")
        dialog.destroy()
        
        self.after(10, self.update_all_stats)
        self.update_tab_labels()
        if self.input_notebook.index("current") == target_tab_index:
             self.apply_tool()

    def copy_to_clipboard(self):
        """Copies the content of the output text area to the system clipboard."""
        if hasattr(self, 'diff_frame') and self.diff_frame.winfo_viewable():
            active_output_tab = self.diff_output_tabs[self.diff_output_notebook.index(self.diff_output_notebook.select())]
        else:
            active_output_tab = self.output_tabs[self.output_notebook.index(self.output_notebook.select())]
        
        self.clipboard_clear()
        self.clipboard_append(active_output_tab.text.get("1.0", tk.END))
        self.update()
        self.logger.info("Output copied to clipboard.")
        messagebox.showinfo("Copied", "Output text has been copied to the clipboard.")
        self.after(10, self.update_all_stats)

    def on_input_tab_change(self, event):
        """Handles logic when the input tab is changed."""
        if self.tool_var.get() not in self.manual_process_tools:
            self.apply_tool()
        self.after(10, self.update_all_stats)

    def on_output_tab_change(self, event):
        """Handles logic when the output tab is changed."""
        active_output_tab = self.output_tabs[self.output_notebook.index(self.output_notebook.select())]
        if not active_output_tab.text.get("1.0", tk.END).strip():
            if self.tool_var.get() not in self.manual_process_tools:
                self.apply_tool()
        self.after(10, self.update_all_stats)

    def apply_tool(self):
        """Applies the selected text processing tool to the input text."""
        tool_name = self.tool_var.get()
        
        if tool_name in ["Google AI", "Anthropic AI", "OpenAI", "Cohere AI", "HuggingFace AI", "Groq AI", "OpenRouterAI", "Diff Viewer"]:
            return

        try:
            active_input_tab = self.input_tabs[self.input_notebook.index(self.input_notebook.select())]
            input_text = active_input_tab.text.get("1.0", tk.END).strip()
            
            if tool_name != "Strong Password Generator" and not input_text:
                self.update_output_text("")
                return
                
            output_text = self._process_text_with_tool(tool_name, input_text)
            self.update_output_text(output_text)
            
        except Exception as e:
            error_msg = f"Error processing text with {tool_name}: {e}"
            self.logger.error(error_msg, exc_info=True)
            self.update_output_text(f"Error: {error_msg}")
    
    def _process_text_with_tool(self, tool_name, input_text):
        """Processes text with the specified tool using the TextProcessor class."""
        try:
            if tool_name == "Case Tool":
                settings = self.settings["tool_settings"]["Case Tool"]
                mode = settings.get("mode", "Sentence")
                if mode == "Sentence": return TextProcessor.sentence_case(input_text)
                elif mode == "Lower": return input_text.lower()
                elif mode == "Upper": return input_text.upper()
                elif mode == "Capitalized": return input_text.title()
                elif mode == "Title": return TextProcessor.title_case(input_text, settings.get("exclusions", ""))
            elif tool_name == "Morse Code Translator": return TextProcessor.morse_translator(input_text, self.morse_mode.get(), self.morse_code_dict, self.reversed_morse_dict)
            elif tool_name == "Binary Code Translator": return TextProcessor.binary_translator(input_text)
            elif tool_name == "Base64 Encoder/Decoder": return TextProcessor.base64_processor(input_text, self.base64_mode.get())
            elif tool_name == "Number Sorter": return TextProcessor.number_sorter(input_text, self.number_order.get())
            elif tool_name == "Find & Replace Text": return self.tool_find_replace()
            elif tool_name == "Extract Emails": return TextProcessor.extract_emails(input_text)
            elif tool_name == "Repeating Text Generator":
                try:
                    times = int(self.repeat_times_var.get())
                    return TextProcessor.repeating_text(input_text, times, self.repeat_sep_var.get())
                except ValueError:
                    return "Error: 'Times' must be a valid integer."
            elif tool_name == "Alphabetical Sorter":
                settings = self.settings["tool_settings"]["Alphabetical Sorter"]
                return TextProcessor.alphabetical_sorter(input_text, settings.get("order", "ascending"), settings.get("unique_only", False), settings.get("trim", False))
            elif tool_name == "Word Frequency Counter": return TextProcessor.word_frequency(input_text)
            elif tool_name == "Strong Password Generator": return TextProcessor.strong_password(int(self.pw_len_var.get()), self.pw_num_var.get(), self.pw_sym_var.get())
            elif tool_name == "URL Parser": return self.tool_url_parser(input_text)
            else: return f"Unknown tool: {tool_name}"
        except Exception as e:
            self.logger.error(f"Error in _process_text_with_tool for {tool_name}: {e}")
            raise

    def update_output_text(self, text):
        """Thread-safe method to update the output text widget."""
        active_output_tab = self.output_tabs[self.output_notebook.index(self.output_notebook.select())]
        active_output_tab.text.config(state="normal")
        active_output_tab.text.delete("1.0", tk.END)
        active_output_tab.text.insert("1.0", text)
        active_output_tab.text.config(state="disabled")
        self.save_settings()
        self.after(10, self.update_all_stats)
        
        if self.tool_var.get() == "Find & Replace Text":
            self.highlight_processed_results()
        
        self.update_tab_labels()

    def _get_search_pattern(self):
        """Helper to build the regex pattern for Find & Replace."""
        settings = self.settings["tool_settings"]["Find & Replace Text"]
        find_str = settings.get("find", "")
        option = settings.get("option", "ignore_case")
        mode = settings.get("mode")
        
        cache_key = (find_str, option, mode)
        if cache_key in self._regex_cache:
            return self._regex_cache[cache_key]
        
        if mode == "Regex":
            pattern = find_str
        else:
            search_term = re.escape(find_str)
            if option == "wildcards": search_term = search_term.replace('\\*', '.*').replace('\\?', '.')
            if option == "whole_words": search_term = r'\b' + search_term + r'\b'
            elif option == "match_prefix": search_term = r'\b' + search_term
            elif option == "match_suffix": search_term = search_term + r'\b'
            pattern = search_term
        
        self._regex_cache[cache_key] = pattern
        return pattern

    def preview_find_replace(self):
        """Highlights matches in input and output without replacing."""
        self.on_tool_setting_change()
        active_input_tab = self.input_tabs[self.input_notebook.index(self.input_notebook.select())]
        active_output_tab = self.output_tabs[self.output_notebook.index(self.output_notebook.select())]

        active_input_tab.text.tag_remove("yellow_highlight", "1.0", tk.END)
        active_output_tab.text.config(state="normal")
        active_output_tab.text.tag_remove("pink_highlight", "1.0", tk.END)
        
        input_content = active_input_tab.text.get("1.0", tk.END)
        active_output_tab.text.delete("1.0", tk.END)
        active_output_tab.text.insert("1.0", input_content)

        find_str = self.settings["tool_settings"]["Find & Replace Text"].get("find", "")
        if not find_str:
            active_output_tab.text.config(state="disabled")
            self.match_count_label.config(text="Found matches: 0")
            return
            
        pattern = self._get_search_pattern()
        settings = self.settings["tool_settings"]["Find & Replace Text"]
        flags = re.IGNORECASE if settings.get("option") == "ignore_case" else 0

        match_count = 0
        try:
            for match in re.finditer(pattern, input_content, flags):
                start, end = match.span()
                active_input_tab.text.tag_add("yellow_highlight", f"1.0 + {start}c", f"1.0 + {end}c")
                match_count += 1

            for match in re.finditer(pattern, active_output_tab.text.get("1.0", tk.END), flags):
                start, end = match.span()
                active_output_tab.text.tag_add("pink_highlight", f"1.0 + {start}c", f"1.0 + {end}c")
        except re.error as e:
            self.logger.error(f"Regex error in preview: {e}")
            match_count = "Regex Error"


        self.match_count_label.config(text=f"Found matches: {match_count}")
        active_output_tab.text.config(state="disabled")
        self.after(10, self.update_all_stats)

    def highlight_processed_results(self):
        """Highlights input (found) and output (replaced) text after processing."""
        active_input_tab = self.input_tabs[self.input_notebook.index(self.input_notebook.select())]
        active_output_tab = self.output_tabs[self.output_notebook.index(self.output_notebook.select())]

        active_input_tab.text.tag_remove("yellow_highlight", "1.0", tk.END)
        active_output_tab.text.config(state="normal")
        active_output_tab.text.tag_remove("pink_highlight", "1.0", tk.END)

        find_str = self.settings["tool_settings"]["Find & Replace Text"].get("find", "")
        replace_str = self.settings["tool_settings"]["Find & Replace Text"].get("replace", "")
        if not find_str:
            active_output_tab.text.config(state="disabled")
            self.match_count_label.config(text="Found matches: 0")
            return

        pattern = self._get_search_pattern()
        settings = self.settings["tool_settings"]["Find & Replace Text"]
        flags = re.IGNORECASE if settings.get("option") == "ignore_case" else 0

        match_count = 0
        try:
            for match in re.finditer(pattern, active_input_tab.text.get("1.0", tk.END), flags):
                start, end = match.span()
                active_input_tab.text.tag_add("yellow_highlight", f"1.0 + {start}c", f"1.0 + {end}c")
                match_count += 1
                
            if replace_str:
                 for match in re.finditer(re.escape(replace_str), active_output_tab.text.get("1.0", tk.END), flags):
                    start, end = match.span()
                    active_output_tab.text.tag_add("pink_highlight", f"1.0 + {start}c", f"1.0 + {end}c")
        except re.error as e:
            self.logger.error(f"Regex error in highlight: {e}")
            match_count = "Regex Error"

        self.match_count_label.config(text=f"Found matches: {match_count}")
        active_output_tab.text.config(state="disabled")

    def tool_find_replace(self):
        """Performs find and replace with advanced options."""
        settings = self.settings["tool_settings"]["Find & Replace Text"]
        find_str = settings.get("find", "")
        replace_str = settings.get("replace", "")
        
        active_input_tab = self.input_tabs[self.input_notebook.index(self.input_notebook.select())]
        input_text = active_input_tab.text.get("1.0", tk.END)

        if not find_str:
            return input_text.strip()

        if settings.get("mode") == "Regex":
            try:
                flags = 0 if settings.get("option") == "match_case" else re.IGNORECASE
                return re.sub(find_str, replace_str, input_text, flags=flags).strip()
            except re.error as e:
                return f"Regex Error: {e}"

        option = settings.get("option", "ignore_case")
        if option in ["sounds_like", "all_word_forms", "ignore_punctuation", "ignore_whitespace"]:
            output_lines = []
            for line in input_text.splitlines():
                words = re.split(r'(\s+)', line)
                new_words = []
                for word in words:
                    if not word.strip():
                        new_words.append(word)
                        continue

                    original_word = word
                    compare_word = word
                    compare_find_str = find_str
                    
                    if option == "ignore_punctuation":
                        compare_word = word.translate(str.maketrans('', '', string.punctuation))
                        compare_find_str = find_str.translate(str.maketrans('', '', string.punctuation))
                    if option == "ignore_whitespace":
                        compare_word = "".join(compare_word.split())
                        compare_find_str = "".join(compare_find_str.split())

                    match = False
                    if option == "sounds_like" and METAPHONE_AVAILABLE:
                        if compare_word and compare_find_str and doublemetaphone(compare_word) == doublemetaphone(compare_find_str):
                            match = True
                    elif option == "all_word_forms" and METAPHONE_AVAILABLE:
                        if compare_word and compare_find_str:
                            lemmas_find = set(getLemma(compare_find_str.lower(), upos='VERB') + getLemma(compare_find_str.lower(), upos='NOUN'))
                            lemmas_word = set(getLemma(compare_word.lower(), upos='VERB') + getLemma(compare_word.lower(), upos='NOUN'))
                            if lemmas_find.intersection(lemmas_word):
                                match = True
                    else:
                        if compare_word.lower() == compare_find_str.lower():
                            match = True

                    new_words.append(replace_str if match else original_word)
                output_lines.append("".join(new_words))
            return "\n".join(output_lines)
        else:
            search_term = self._get_search_pattern()
            flags = re.IGNORECASE if option == "ignore_case" else 0
            return re.sub(search_term, replace_str, input_text, flags=flags).strip()


    def tool_url_parser(self, text):
        """Parses a URL into its components."""
        if not text.strip(): return "Please enter a URL to parse."
        try:
            parsed_url = urllib.parse.urlparse(text)
            output = []
            if parsed_url.scheme: output.append(f"protocol: {parsed_url.scheme}")
            if parsed_url.netloc:
                output.append(f"host: {parsed_url.netloc}")
                if parsed_url.hostname:
                    parts = parsed_url.hostname.split('.')
                    if len(parts) > 1:
                        domain = f"{parts[-2]}.{parts[-1]}"
                        output.append(f"domain: {domain}")
                        if len(parts) > 2:
                            output.append(f"subdomain: {'.'.join(parts[:-2])}")
                        output.append(f"tld: {parts[-1]}")
            if parsed_url.path: output.append(f"Path: {parsed_url.path}")
            if parsed_url.query:
                output.append("\nQuery String:")
                should_decode = self.settings["tool_settings"].get("URL Parser", {}).get("ascii_decode", True)
                if should_decode:
                    query_params = urllib.parse.parse_qs(parsed_url.query, keep_blank_values=True)
                    for key, values in query_params.items():
                        output.append(f"{key}= {', '.join(values)}")
                else:
                    for pair in parsed_url.query.split('&'):
                        output.append(pair.replace('=', '= ', 1) if '=' in pair else pair)
            if parsed_url.fragment: output.append(f"\nHash/Fragment: {parsed_url.fragment}")
            return '\n'.join(output)
        except Exception as e:
            self.logger.error(f"URL Parsing Error: {e}")
            return f"Error parsing URL: {e}"

    def generate_morse_tone(self, duration):
        """Generates a sine wave for a given duration for Morse code."""
        TONE_FREQ = self.settings["tool_settings"]["Morse Code Translator"].get("tone", AppConfig.TONE_FREQUENCY)
        t = np.linspace(0, duration, int(AppConfig.SAMPLE_RATE * duration), False)
        tone = np.sin(TONE_FREQ * t * 2 * np.pi)
        return (0.5 * tone).astype(np.float32)
        
    def play_morse_audio(self):
        """Plays the Morse code audio using PyAudio in a separate thread."""
        if self.morse_thread and self.morse_thread.is_alive():
            self.logger.warning("Morse playback is already in progress.")
            return
            
        if not PYAUDIO_AVAILABLE or not self.audio_stream:
            messagebox.showerror("Audio Error", "PyAudio is not available or failed to initialize. Cannot play audio.")
            return

        active_output_tab = self.output_tabs[self.output_notebook.index(self.output_notebook.select())]
        morse_code = active_output_tab.text.get("1.0", tk.END).strip()
        if not morse_code:
            self.logger.warning("No Morse code to play.")
            return
            
        self.stop_morse_playback.clear()
        self.morse_thread = threading.Thread(target=self._play_morse_thread, args=(morse_code,), daemon=True)
        self.morse_thread.start()

    def stop_morse_audio(self):
        """Stops the currently playing Morse code audio."""
        self.stop_morse_playback.set()

    def _play_morse_thread(self, morse_code):
        """The actual playback logic that runs in a thread."""
        self.play_morse_button.config(text="Stop Playing", command=self.stop_morse_audio)
        self.logger.info("Starting Morse code playback.")

        try:
            for char in morse_code:
                if self.stop_morse_playback.is_set():
                    self.logger.info("Morse playback stopped by user.")
                    break
                if char == '.':
                    self.audio_stream.write(self.generate_morse_tone(AppConfig.MORSE_DOT_DURATION).tobytes())
                    time.sleep(AppConfig.MORSE_DOT_DURATION)
                elif char == '-':
                    self.audio_stream.write(self.generate_morse_tone(AppConfig.MORSE_DASH_DURATION).tobytes())
                    time.sleep(AppConfig.MORSE_DOT_DURATION)
                elif char == ' ':
                    time.sleep(AppConfig.MORSE_DOT_DURATION * 3 - AppConfig.MORSE_DOT_DURATION)
                elif char == '/':
                    time.sleep(AppConfig.MORSE_DOT_DURATION * 7 - AppConfig.MORSE_DOT_DURATION)
        except Exception as e:
            self.logger.error(f"Error during morse playback: {e}")
        finally:
            self.play_morse_button.config(text="Play Morse Audio", command=self.play_morse_audio)
            self.logger.info("Morse code playback finished.")
            self.stop_morse_playback.clear()

    def run_ai_in_thread(self):
        """Starts a new thread to run the AI tool without freezing the GUI."""
        if hasattr(self, '_ai_thread') and self._ai_thread.is_alive():
            self.logger.warning("An AI process is already running.")
            return
            
        self.update_output_text("Generating response from AI...")
        self._ai_thread = threading.Thread(target=self.tool_ai_processing, daemon=True)
        self._ai_thread.start()

    def tool_ai_processing(self):
        """Submits the input text to the selected AI provider API with exponential backoff."""
        tool_name = self.tool_var.get()
        settings = self.settings["tool_settings"].get(tool_name, {})
        api_key = settings.get("API_KEY")
        
        active_input_tab = self.input_tabs[self.input_notebook.index(self.input_notebook.select())]
        prompt = active_input_tab.text.get("1.0", tk.END).strip()

        if not api_key or api_key == "putinyourkey":
            self.after(0, self.update_output_text, f"Error: Please enter a valid {tool_name} API Key in the settings.")
            return
        if not prompt:
            self.after(0, self.update_output_text, "Error: Input text cannot be empty.")
            return
        
        self.logger.info(f"Submitting prompt to {tool_name} with model {settings.get('MODEL')}")

        # --- HuggingFace (uses its own client) ---
        if tool_name == "HuggingFace AI":
            if not HUGGINGFACE_AVAILABLE:
                self.after(0, self.update_output_text, "Error: huggingface_hub library not found. Please install it.")
                return
            try:
                client = InferenceClient(token=api_key)
                messages = []
                system_prompt = settings.get("system_prompt", "").strip()
                if system_prompt: messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                params = {"messages": messages, "model": settings.get("MODEL")}
                
                # Helper function to safely add params
                def add_param_hf(key, p_type):
                    val_str = str(settings.get(key, '')).strip()
                    if val_str:
                        try:
                            converted_val = p_type(val_str)
                            if converted_val:  # Excludes empty strings, 0, and 0.0
                                params[key] = converted_val
                        except (ValueError, TypeError):
                            self.logger.warning(f"Could not convert {key} value '{val_str}' to {p_type}")

                # FIX: Only add parameters that are explicitly supported by chat_completion
                add_param_hf("max_tokens", int)
                add_param_hf("seed", int)
                add_param_hf("temperature", float)
                add_param_hf("top_p", float)
                
                # The parameters 'top_k' and 'repetition_penalty' are not direct arguments
                # for the chat_completion method and were causing TypeErrors.
                # They are removed from this call. For some models, these might be
                # available under a nested 'parameters' dictionary, but for now,
                # removing them ensures compatibility with the client's method signature.
                
                # The following lines were removed as they caused the error:
                # add_param_hf("top_k", int)
                # add_param_hf("repetition_penalty", float)

                stop_seq_str = str(settings.get("stop_sequences", '')).strip()
                if stop_seq_str:
                    # Note: The parameter is often 'stop', but we'll keep 'stop_sequences'
                    # if the client is expected to handle it. Given the other errors,
                    # sticking to a minimal set of confirmed parameters is safer.
                    params["stop"] = [s.strip() for s in stop_seq_str.split(',')]

                self.logger.debug(f"HuggingFace payload: {json.dumps(params, indent=2, default=str)}")
                response_obj = client.chat_completion(**params)
                self.after(0, self.update_output_text, response_obj.choices[0].message.content)
            except HfHubHTTPError as e:
                error_msg = f"HuggingFace API Error: {e.response.status_code} - {e.response.reason}\n\n{e.response.text}"
                if e.response.status_code == 401: error_msg += "\n\nThis means your API token is invalid or expired."
                elif e.response.status_code == 403: error_msg += f"\n\nThis is a 'gated model'. You MUST accept the terms on the model page:\nhttps://huggingface.co/{settings.get('MODEL')}"
                self.logger.error(error_msg, exc_info=True)
                self.after(0, self.update_output_text, error_msg)
            except Exception as e:
                self.logger.error(f"HuggingFace Client Error: {e}", exc_info=True)
                self.after(0, self.update_output_text, f"HuggingFace Client Error: {e}")
            return
            
        # --- Other Providers (REST API) ---
        url, payload, headers = "", {}, {}
        try:
            # --- Helper to safely add params ---
            def add_param(p_dict, key, p_type):
                val_str = str(settings.get(key, '')).strip()
                if val_str:
                    try:
                        converted_val = p_type(val_str)
                        if converted_val: # Excludes empty strings, 0, and 0.0
                            p_dict[key] = converted_val
                    except (ValueError, TypeError):
                        self.logger.warning(f"Could not convert {key} value '{val_str}' to {p_type}")
            
            # --- Get URL and Headers ---
            if tool_name == "Google AI":
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.get('MODEL')}:generateContent?key={api_key}"
                headers = {'Content-Type': 'application/json'}
            elif tool_name == "Anthropic AI":
                url = "https://api.anthropic.com/v1/messages"
                headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
            elif tool_name == "OpenAI":
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            elif tool_name == "Groq AI":
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            elif tool_name == "OpenRouterAI":
                url = "https://openrouter.ai/api/v1/chat/completions"
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            elif tool_name == "Cohere AI":
                url = "https://api.cohere.com/v1/chat"
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            
            # --- Build Payload ---
            if tool_name == "Google AI":
                system_prompt = settings.get("system_prompt", "").strip()
                full_prompt = f"{system_prompt}\n\n{prompt}".strip() if system_prompt else prompt
                payload = {"contents": [{"parts": [{"text": full_prompt}], "role": "user"}]}
                gen_config = {}
                add_param(gen_config, 'temperature', float)
                add_param(gen_config, 'topP', float)
                add_param(gen_config, 'topK', int)
                add_param(gen_config, 'maxOutputTokens', int)
                add_param(gen_config, 'candidateCount', int)
                stop_seq_str = str(settings.get('stopSequences', '')).strip()
                if stop_seq_str: gen_config['stopSequences'] = [s.strip() for s in stop_seq_str.split(',')]
                if gen_config: payload['generationConfig'] = gen_config
            
            elif tool_name == "Anthropic AI":
                payload = {"model": settings.get("MODEL"), "messages": [{"role": "user", "content": prompt}]}
                if settings.get("system"): payload["system"] = settings.get("system")
                add_param(payload, 'max_tokens', int)
                add_param(payload, 'temperature', float)
                add_param(payload, 'top_p', float)
                add_param(payload, 'top_k', int)
                stop_seq_str = str(settings.get('stop_sequences', '')).strip()
                if stop_seq_str: payload['stop_sequences'] = [s.strip() for s in stop_seq_str.split(',')]

            elif tool_name == "Cohere AI":
                payload = {"model": settings.get("MODEL"), "message": prompt}
                if settings.get("preamble"): payload["preamble"] = settings.get("preamble")
                add_param(payload, 'temperature', float)
                add_param(payload, 'p', float)
                add_param(payload, 'k', int)
                add_param(payload, 'max_tokens', int)
                add_param(payload, 'frequency_penalty', float)
                add_param(payload, 'presence_penalty', float)
                if settings.get('citation_quality'): payload['citation_quality'] = settings['citation_quality']
                stop_seq_str = str(settings.get('stop_sequences', '')).strip()
                if stop_seq_str: payload['stop_sequences'] = [s.strip() for s in stop_seq_str.split(',')]

            elif tool_name in ["OpenAI", "Groq AI", "OpenRouterAI"]:
                payload = {"model": settings.get("MODEL"), "messages": []}
                system_prompt = settings.get("system_prompt", "").strip()
                if system_prompt: payload["messages"].append({"role": "system", "content": system_prompt})
                payload["messages"].append({"role": "user", "content": prompt})

                add_param(payload, 'temperature', float)
                add_param(payload, 'top_p', float)
                add_param(payload, 'max_tokens', int)
                add_param(payload, 'frequency_penalty', float)
                add_param(payload, 'presence_penalty', float)
                add_param(payload, 'seed', int)
                
                stop_str = str(settings.get('stop', '')).strip()
                if stop_str: payload['stop'] = [s.strip() for s in stop_str.split(',')]
                
                if settings.get("response_format") == "json_object": payload["response_format"] = {"type": "json_object"}
                # OpenRouter specific
                add_param(payload, 'top_k', int)
                add_param(payload, 'repetition_penalty', float)

        except Exception as e: # Catch any potential errors during payload creation
            self.logger.error(f"Error configuring API for {tool_name}: {e}")
            self.after(0, self.update_output_text, f"Error configuring API request: {e}")
            return
        
        self.logger.debug(f"{tool_name} payload: {json.dumps(payload, indent=2)}")
        for i in range(AppConfig.MAX_RETRIES):
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=60)
                response.raise_for_status()
                
                data = response.json()
                self.logger.debug(f"{tool_name} Response: {data}")
                
                result_text = f"Error: Could not parse response from {tool_name}."
                if tool_name == "Google AI": result_text = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', result_text)
                elif tool_name == "Anthropic AI": result_text = data.get('content', [{}])[0].get('text', result_text)
                elif tool_name in ["OpenAI", "Groq AI", "OpenRouterAI"]: result_text = data.get('choices', [{}])[0].get('message', {}).get('content', result_text)
                elif tool_name == "Cohere AI": result_text = data.get('text', result_text)

                self.after(0, self.update_output_text, result_text)
                return
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429 and i < AppConfig.MAX_RETRIES -1:
                    delay = AppConfig.BASE_DELAY * (2 ** i) + (random.uniform(0, 1))
                    self.logger.warning(f"Rate limit exceeded. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                else:
                    self.logger.error(f"API Request Error: {e}\nResponse: {e.response.text}")
                    self.after(0, self.update_output_text, f"API Request Error: {e}\nResponse: {e.response.text}")
                    return
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Network Error: {e}")
                self.after(0, self.update_output_text, f"Network Error: {e}")
                return
            except (KeyError, IndexError, json.JSONDecodeError) as e:
                self.logger.error(f"Error parsing AI response: {e}\n\nResponse:\n{response.text if 'response' in locals() else 'N/A'}")
                self.after(0, self.update_output_text, f"Error parsing AI response: {e}\n\nResponse:\n{response.text if 'response' in locals() else 'N/A'}")
                return

        self.after(0, self.update_output_text, "Error: Max retries exceeded. The API is still busy.")
        
    def load_diff_viewer_content(self):
        """Copies content from the main input/output tabs to the diff viewer tabs."""
        self.logger.info("Loading content into Diff Viewer.")
        for i in range(AppConfig.TAB_COUNT):
            input_content = self.input_tabs[i].text.get("1.0", tk.END)
            self.diff_input_tabs[i].text.delete("1.0", tk.END)
            self.diff_input_tabs[i].text.insert("1.0", input_content)
            
            output_content = self.output_tabs[i].text.get("1.0", tk.END)
            self.diff_output_tabs[i].text.delete("1.0", tk.END)
            self.diff_output_tabs[i].text.insert("1.0", output_content)
            
        try:
            self.diff_input_notebook.select(self.input_notebook.index("current"))
            self.diff_output_notebook.select(self.output_notebook.index("current"))
        except tk.TclError:
            self.diff_input_notebook.select(0)
            self.diff_output_notebook.select(0)
        
        self.update_tab_labels()

    def sync_diff_viewer_to_main_tabs(self):
        """Copies content from the diff viewer tabs back to the main tabs."""
        self.logger.info("Syncing Diff Viewer content back to main tabs.")
        for i in range(AppConfig.TAB_COUNT):
            diff_input_content = self.diff_input_tabs[i].text.get("1.0", tk.END)
            self.input_tabs[i].text.delete("1.0", tk.END)
            self.input_tabs[i].text.insert("1.0", diff_input_content)
            
            diff_output_content = self.diff_output_tabs[i].text.get("1.0", tk.END)
            self.output_tabs[i].text.config(state="normal")
            self.output_tabs[i].text.delete("1.0", tk.END)
            self.output_tabs[i].text.insert("1.0", diff_output_content)
            self.output_tabs[i].text.config(state="disabled")
        
        self.update_tab_labels()
        self.save_settings()

    def _preprocess_for_diff(self, text, option):
        """Preprocess text into line dicts according to diff option."""
        lines = text.splitlines()
        processed = []
        for line in lines:
            cmp_line = line
            if option == "ignore_case": cmp_line = cmp_line.lower()
            elif option == "ignore_whitespace": cmp_line = re.sub(r"\s+", " ", cmp_line).strip()
            processed.append({"raw": line, "cmp": cmp_line})
        return processed

    def run_diff_viewer(self):
        """Compares the active tabs within the Diff Viewer and displays the diff."""
        self.logger.info("Running Diff Viewer comparison.")
        
        input_text = self.diff_input_tabs[self.diff_input_notebook.index("current")].text.get("1.0", tk.END)
        output_text = self.diff_output_tabs[self.diff_output_notebook.index("current")].text.get("1.0", tk.END)

        option = self.settings.get("tool_settings", {}).get("Diff Viewer", {}).get("option", "ignore_case")

        diff_input_widget = self.diff_input_tabs[self.diff_input_notebook.index("current")].text
        diff_output_widget = self.diff_output_tabs[self.diff_output_notebook.index("current")].text

        diff_input_widget.delete("1.0", tk.END)
        diff_output_widget.delete("1.0", tk.END)

        if not input_text.strip() and not output_text.strip(): return
        elif not input_text.strip():
            for line in output_text.splitlines():
                diff_input_widget.insert(tk.END, '\n')
                diff_output_widget.insert(tk.END, line + '\n', 'addition')
            return
        elif not output_text.strip():
            for line in input_text.splitlines():
                diff_input_widget.insert(tk.END, line + '\n', 'deletion')
                diff_output_widget.insert(tk.END, '\n')
            return

        left_lines = self._preprocess_for_diff(input_text, option)
        right_lines = self._preprocess_for_diff(output_text, option)
        left_cmp = [l["cmp"] for l in left_lines]
        right_cmp = [r["cmp"] for r in right_lines]
        
        try:
            matcher = difflib.SequenceMatcher(None, left_cmp, right_cmp, autojunk=False)
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == 'equal':
                    for i in range(i1, i2):
                        diff_input_widget.insert(tk.END, left_lines[i]["raw"] + '\n')
                        diff_output_widget.insert(tk.END, right_lines[j1 + (i - i1)]["raw"] + '\n')
                elif tag == 'delete':
                    for i in range(i1, i2):
                        diff_input_widget.insert(tk.END, left_lines[i]["raw"] + '\n', 'deletion')
                        diff_output_widget.insert(tk.END, '\n')
                elif tag == 'insert':
                    for j in range(j1, j2):
                        diff_input_widget.insert(tk.END, '\n')
                        diff_output_widget.insert(tk.END, right_lines[j]["raw"] + '\n', 'addition')
                elif tag == 'replace':
                    input_block = [l["raw"] for l in left_lines[i1:i2]]
                    output_block = [r["raw"] for r in right_lines[j1:j2]]
                    while len(input_block) < len(output_block): input_block.append("")
                    while len(output_block) < len(input_block): output_block.append("")
                    for line1, line2 in zip(input_block, output_block):
                        if line1 and line2: self._highlight_word_diffs(diff_input_widget, [line1], diff_output_widget, [line2])
                        elif line1:
                            diff_input_widget.insert(tk.END, line1 + '\n', 'deletion')
                            diff_output_widget.insert(tk.END, '\n')
                        elif line2:
                            diff_input_widget.insert(tk.END, '\n')
                            diff_output_widget.insert(tk.END, line2 + '\n', 'addition')
        except Exception as e:
            self.logger.error(f"Error in diff computation: {e}")
            diff_input_widget.insert(tk.END, input_text)
            diff_output_widget.insert(tk.END, output_text)
        
        diff_input_widget.yview_moveto(0)
        diff_output_widget.yview_moveto(0)
        self._setup_diff_sync()

    def _highlight_word_diffs(self, w1, lines1, w2, lines2):
        """Highlights word-level differences within a 'replace' block."""
        for line1, line2 in zip(lines1, lines2):
            w1.insert(tk.END, line1 + '\n', 'modification')
            w2.insert(tk.END, line2 + '\n', 'modification')

            line_start1 = w1.index(f"{w1.index(tk.INSERT)} -1 lines linestart")
            line_start2 = w2.index(f"{w2.index(tk.INSERT)} -1 lines linestart")

            words1 = re.split(r'(\s+)', line1)
            words2 = re.split(r'(\s+)', line2)
            matcher = difflib.SequenceMatcher(None, words1, words2)

            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == 'delete' or tag == 'replace':
                    start_char1 = len("".join(words1[:i1]))
                    end_char1 = len("".join(words1[:i2]))
                    w1.tag_add('inline_del', f"{line_start1}+{start_char1}c", f"{line_start1}+{end_char1}c")
                if tag == 'insert' or tag == 'replace':
                    start_char2 = len("".join(words2[:j1]))
                    end_char2 = len("".join(words2[:j2]))
                    w2.tag_add('inline_add', f"{line_start2}+{start_char2}c", f"{line_start2}+{end_char2}c")

    def export_file(self, file_format):
        """Exports the output text to the specified file format."""
        active_output_tab = self.output_tabs[self.output_notebook.index(self.output_notebook.select())]
        output_text = active_output_tab.text.get("1.0", tk.END)
        export_path = self.export_path_var.get()
        if not os.path.isdir(export_path):
            messagebox.showerror("Export Error", "Invalid export path specified in settings.")
            return

        filename = filedialog.asksaveasfilename(
            initialdir=export_path,
            title=f"Save as {file_format.upper()}",
            defaultextension=f".{file_format}",
            filetypes=[(f"{file_format.upper()} files", f"*.{file_format}"), ("All files", "*.*")]
        )
        if not filename: return

        try:
            if file_format == "txt":
                with open(filename, "w", encoding="utf-8") as f: f.write(output_text)
            elif file_format == "pdf": self.export_to_pdf(filename, output_text)
            elif file_format == "docx": self.export_to_docx(filename, output_text)

            self.logger.info(f"Successfully exported to {filename}")
            messagebox.showinfo("Export Successful", f"File saved as {filename}")

            if platform.system() == "Windows": os.startfile(filename)
            elif platform.system() == "Darwin": subprocess.Popen(["open", filename])
            else: subprocess.Popen(["xdg-open", filename])
        except Exception as e:
            self.logger.error(f"Failed to export to {filename}: {e}")
            messagebox.showerror("Export Error", f"An error occurred while exporting:\n{e}")

    def export_to_pdf(self, filename, text):
        """Helper function to create a PDF file."""
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        text_object = c.beginText(40, height - 40)
        text_object.setFont("Helvetica", 10)
        for line in text.splitlines():
            text_object.textLine(line)
        c.drawText(text_object)
        c.save()

    def export_to_docx(self, filename, text):
        """Helper function to create a DOCX file."""
        doc = Document()
        doc.add_paragraph(text)
        doc.save(filename)
        
    def clear_regex_cache(self):
        self._regex_cache.clear()
        self.logger.debug("Regex cache cleared")
        
    def on_closing(self):
        """Handles cleanup when the application window is closed."""
        self.save_settings()
        self.clear_regex_cache()
        if self.audio_stream:
            self.stop_morse_audio()
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()
        self.destroy()

    def on_tab_content_changed(self, event=None):
        """Handles changes in tab content to update labels and sync diff edits"""
        if hasattr(self, '_tab_label_after_id'): self.after_cancel(self._tab_label_after_id)
        self._tab_label_after_id = self.after(500, self.update_tab_labels)

        src_widget = getattr(event, 'widget', None)
        if not src_widget: return
        try:
            for i, tab in enumerate(getattr(self, 'diff_input_tabs', [])):
                if tab.text is src_widget:
                    content = tab.text.get("1.0", tk.END)
                    self.input_tabs[i].text.delete("1.0", tk.END)
                    self.input_tabs[i].text.insert("1.0", content)
                    self.save_settings()
                    self.after(10, self.update_all_stats)
                    return
            for i, tab in enumerate(getattr(self, 'diff_output_tabs', [])):
                if tab.text is src_widget:
                    content = tab.text.get("1.0", tk.END)
                    self.output_tabs[i].text.config(state="normal")
                    self.output_tabs[i].text.delete("1.0", tk.END)
                    self.output_tabs[i].text.insert("1.0", content)
                    self.output_tabs[i].text.config(state="disabled")
                    self.save_settings()
                    self.after(10, self.update_all_stats)
                    return
        except Exception: pass

if __name__ == "__main__":
    if not METAPHONE_AVAILABLE:
        print("Warning: 'Metaphone' and 'lemminflect' libraries not found. 'Sounds like' and 'Find all word forms' features will be disabled.")
        print("Please install them using: pip install Metaphone lemminflect")
    if not PYAUDIO_AVAILABLE:
        print("Warning: 'PyAudio' or 'numpy' not found. Morse audio playback will be disabled.")
        print("Please install them using: pip install pyaudio numpy")
    app = PromeraAIApp()
    app.mainloop()