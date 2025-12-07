"""
Translator Tools Module - Binary and Morse code translation utilities

This module provides comprehensive translation functionality with a tabbed UI interface
for the Promera AI Commander application.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import base64
import threading
import time

# Try to import NumPy for Morse code audio generation
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# Try to import PyAudio for Morse code audio
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False


class TranslatorToolsProcessor:
    """Translator tools processor with binary and Morse code translation capabilities."""
    
    # Morse code dictionary
    MORSE_CODE_DICT = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
        'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
        'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
        'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
        '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----', ' ': '/',
        ',': '--..--', '.': '.-.-.-', '?': '..--..', '/': '-..-.', '-': '-....-', '(': '-.--.', ')': '-.--.-'
    }
    
    REVERSED_MORSE_DICT = {v: k for k, v in MORSE_CODE_DICT.items()}
    
    # Audio constants
    MORSE_DOT_DURATION = 0.080
    MORSE_DASH_DURATION = 0.080 * 3
    SAMPLE_RATE = 44100
    TONE_FREQUENCY = 700

    @staticmethod
    def morse_translator(text, mode):
        """Translates text to or from Morse code."""
        if mode == "morse":
            return ' '.join(TranslatorToolsProcessor.MORSE_CODE_DICT.get(char.upper(), '') for char in text)
        else:  # mode == "text"
            return ''.join(TranslatorToolsProcessor.REVERSED_MORSE_DICT.get(code, '') for code in text.split(' '))

    @staticmethod
    def binary_translator(text):
        """Translates text to or from binary."""
        # Detect if input is binary or text
        if all(c in ' 01' for c in text):  # Binary to Text
            try:
                return ''.join(chr(int(b, 2)) for b in text.split())
            except (ValueError, TypeError):
                return "Error: Invalid binary sequence."
        else:  # Text to Binary
            return ' '.join(format(ord(char), '08b') for char in text)

    @staticmethod
    def process_text(input_text, tool_type, settings):
        """Process text using the specified translator tool and settings."""
        if tool_type == "Morse Code Translator":
            return TranslatorToolsProcessor.morse_translator(
                input_text, 
                settings.get("mode", "morse")
            )
        elif tool_type == "Binary Code Translator":
            return TranslatorToolsProcessor.binary_translator(input_text)
        else:
            return f"Unknown translator tool: {tool_type}"


class TranslatorToolsWidget(ttk.Frame):
    """Tabbed interface widget for translator tools, similar to Sorter Tools."""
    
    def __init__(self, parent, app, dialog_manager=None):
        super().__init__(parent)
        self.app = app
        self.dialog_manager = dialog_manager
        self.processor = TranslatorToolsProcessor()
        
        # Initialize UI variables for Morse Code Translator
        self.morse_mode = tk.StringVar(value="morse")
        
        # Audio-related variables
        self.morse_thread = None
        self.stop_morse_playback = threading.Event()
        self.audio_stream = None
        self.pyaudio_instance = None
        
        # Initialize PyAudio if available
        self.setup_audio()
        
        self.create_widgets()
        self.load_settings()
    
    def _show_error(self, title, message):
        """Show error dialog using DialogManager if available, otherwise use messagebox."""
        if self.dialog_manager:
            return self.dialog_manager.show_error(title, message, parent=self.winfo_toplevel())
        else:
            from tkinter import messagebox
            messagebox.showerror(title, message, parent=self.winfo_toplevel())
            return True
    
    def _show_audio_setup_instructions(self, missing_library):
        """Show detailed instructions for setting up audio features."""
        title = "Audio Feature Setup Required"
        
        if missing_library == "NumPy":
            message = """Morse Code Audio is not available in this optimized build.

To enable audio features, you have two options:

OPTION 1: Run from Source (Recommended)
1. Download Python 3.8+ from python.org
2. Install required libraries:
   pip install numpy pyaudio
3. Download source code from GitHub
4. Run: python pomera.py

OPTION 2: Use Text-Only Mode
• Morse code text translation works perfectly
• Copy the Morse code and use external audio tools
• This keeps the executable small (40MB vs 400MB+)

The current executable was optimized for size by excluding
audio libraries. Text-based Morse code works fully!"""
        
        else:  # PyAudio
            message = """Audio playback is not available.

To enable Morse code audio:

OPTION 1: Install Audio Libraries
1. Install Python 3.8+ from python.org
2. Install audio libraries:
   pip install pyaudio numpy
3. Run from source: python pomera.py

OPTION 2: Use Text-Only Mode
• All Morse code translation features work
• Copy output to external audio tools if needed

Note: Audio libraries were excluded to keep the
executable small and portable."""
        
        if self.dialog_manager:
            return self.dialog_manager.show_info(title, message, parent=self.winfo_toplevel())
        else:
            from tkinter import messagebox
            messagebox.showinfo(title, message, parent=self.winfo_toplevel())
            return True

    def setup_audio(self):
        """Initialize PyAudio for Morse code audio playback."""
        if not PYAUDIO_AVAILABLE:
            return
            
        try:
            self.pyaudio_instance = pyaudio.PyAudio()
            self.audio_stream = self.pyaudio_instance.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=TranslatorToolsProcessor.SAMPLE_RATE,
                output=True
            )
        except Exception as e:
            print(f"Failed to initialize PyAudio: {e}")
            self.pyaudio_instance = None
            self.audio_stream = None

    def create_widgets(self):
        """Creates the tabbed interface for translator tools."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create Morse Code Translator tab
        self.morse_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.morse_frame, text="Morse Code Translator")
        self.create_morse_translator_widgets()
        
        # Create Binary Code Translator tab
        self.binary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.binary_frame, text="Binary Code Translator")
        self.create_binary_translator_widgets()

    def create_morse_translator_widgets(self):
        """Creates widgets for the Morse Code Translator tab."""
        # Mode selection
        mode_frame = ttk.LabelFrame(self.morse_frame, text="Translation Mode", padding=10)
        mode_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Radiobutton(
            mode_frame, 
            text="Text to Morse", 
            variable=self.morse_mode, 
            value="morse", 
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            mode_frame, 
            text="Morse to Text", 
            variable=self.morse_mode, 
            value="text", 
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(self.morse_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            button_frame, 
            text="Translate", 
            command=self._apply_morse_translator
        ).pack(side=tk.LEFT, padx=5)
        
        # Audio button (only if PyAudio is available)
        if PYAUDIO_AVAILABLE and self.audio_stream:
            self.play_morse_button = ttk.Button(
                button_frame, 
                text="Play Morse Audio", 
                command=self._play_morse_audio
            )
            self.play_morse_button.pack(side=tk.LEFT, padx=5)

    def create_binary_translator_widgets(self):
        """Creates widgets for the Binary Code Translator tab."""
        # Info label
        info_frame = ttk.LabelFrame(self.binary_frame, text="Information", padding=10)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        info_label = ttk.Label(
            info_frame, 
            text="Automatically detects input type:\n• Text → Binary (8-bit per character)\n• Binary → Text (space-separated binary)"
        )
        info_label.pack()
        
        # Button
        button_frame = ttk.Frame(self.binary_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            button_frame, 
            text="Translate", 
            command=self._apply_binary_translator
        ).pack(side=tk.LEFT, padx=5)

    def _on_setting_change(self):
        """Handle setting changes."""
        self.save_settings()
        if hasattr(self.app, 'on_tool_setting_change'):
            self.app.on_tool_setting_change()

    def _apply_morse_translator(self):
        """Apply the Morse Code Translator tool."""
        self._apply_tool("Morse Code Translator")

    def _apply_binary_translator(self):
        """Apply the Binary Code Translator tool."""
        self._apply_tool("Binary Code Translator")

    def _apply_tool(self, tool_type):
        """Apply the specified translator tool."""
        try:
            # Get input text from the active input tab
            active_input_tab = self.app.input_tabs[self.app.input_notebook.index(self.app.input_notebook.select())]
            input_text = active_input_tab.text.get("1.0", tk.END).strip()
            
            if not input_text:
                # Show a message if no input text
                active_output_tab = self.app.output_tabs[self.app.output_notebook.index(self.app.output_notebook.select())]
                active_output_tab.text.config(state="normal")
                active_output_tab.text.delete("1.0", tk.END)
                active_output_tab.text.insert("1.0", f"Please enter text to translate in the input area.\n\nFor {tool_type}:\n" + 
                    ("- Enter text to convert to Morse code, or Morse code to convert to text" if tool_type == "Morse Code Translator" 
                     else "- Enter text to convert to binary, or binary code to convert to text"))
                active_output_tab.text.config(state="disabled")
                return
            
            # Get settings for the tool
            settings = self.get_tool_settings(tool_type)
            
            # Process the text
            result = self.processor.process_text(input_text, tool_type, settings)
            
            # Update output
            active_output_tab = self.app.output_tabs[self.app.output_notebook.index(self.app.output_notebook.select())]
            active_output_tab.text.config(state="normal")
            active_output_tab.text.delete("1.0", tk.END)
            active_output_tab.text.insert("1.0", result)
            active_output_tab.text.config(state="disabled")
            
            # Update statistics
            if hasattr(self.app, 'update_all_stats'):
                self.app.after(10, self.app.update_all_stats)
                
        except Exception as e:
            # Show error in output if something goes wrong
            try:
                active_output_tab = self.app.output_tabs[self.app.output_notebook.index(self.app.output_notebook.select())]
                active_output_tab.text.config(state="normal")
                active_output_tab.text.delete("1.0", tk.END)
                active_output_tab.text.insert("1.0", f"Error: {str(e)}")
                active_output_tab.text.config(state="disabled")
            except:
                print(f"Translator Tools Error: {str(e)}")  # Fallback to console

    def _play_morse_audio(self):
        """Play Morse code audio from the output area."""
        if self.morse_thread and self.morse_thread.is_alive():
            print("Morse playback is already in progress.")
            return
            
        if not PYAUDIO_AVAILABLE or not self.audio_stream:
            self._show_audio_setup_instructions("PyAudio")
            return
            
        if not NUMPY_AVAILABLE:
            self._show_audio_setup_instructions("NumPy")
            return

        active_output_tab = self.app.output_tabs[self.app.output_notebook.index(self.app.output_notebook.select())]
        morse_code = active_output_tab.text.get("1.0", tk.END).strip()
        if not morse_code:
            print("No Morse code to play.")
            return
            
        self.stop_morse_playback.clear()
        self.morse_thread = threading.Thread(target=self._play_morse_thread, args=(morse_code,), daemon=True)
        self.morse_thread.start()

    def _stop_morse_audio(self):
        """Stop the currently playing Morse code audio."""
        self.stop_morse_playback.set()

    def _play_morse_thread(self, morse_code):
        """The actual playback logic that runs in a thread."""
        if hasattr(self, 'play_morse_button'):
            self.play_morse_button.config(text="Stop Playing", command=self._stop_morse_audio)
        print("Starting Morse code playback.")

        try:
            for char in morse_code:
                if self.stop_morse_playback.is_set():
                    print("Morse playback stopped by user.")
                    break
                if char == '.':
                    tone = self._generate_morse_tone(TranslatorToolsProcessor.MORSE_DOT_DURATION)
                    self.audio_stream.write(tone.tobytes())
                    time.sleep(TranslatorToolsProcessor.MORSE_DOT_DURATION)
                elif char == '-':
                    tone = self._generate_morse_tone(TranslatorToolsProcessor.MORSE_DASH_DURATION)
                    self.audio_stream.write(tone.tobytes())
                    time.sleep(TranslatorToolsProcessor.MORSE_DOT_DURATION)
                elif char == ' ':
                    time.sleep(TranslatorToolsProcessor.MORSE_DOT_DURATION * 3 - TranslatorToolsProcessor.MORSE_DOT_DURATION)
                elif char == '/':
                    time.sleep(TranslatorToolsProcessor.MORSE_DOT_DURATION * 7 - TranslatorToolsProcessor.MORSE_DOT_DURATION)
        except Exception as e:
            print(f"Error during morse playback: {e}")
        finally:
            if hasattr(self, 'play_morse_button'):
                self.play_morse_button.config(text="Play Morse Audio", command=self._play_morse_audio)
            print("Morse code playback finished.")
            self.stop_morse_playback.clear()

    def _generate_morse_tone(self, duration):
        """Generate a sine wave for a given duration for Morse code."""
        if not NUMPY_AVAILABLE:
            # Return silence if numpy is not available
            import array
            sample_count = int(TranslatorToolsProcessor.SAMPLE_RATE * duration)
            return array.array('f', [0.0] * sample_count)
        
        tone_freq = TranslatorToolsProcessor.TONE_FREQUENCY
        t = np.linspace(0, duration, int(TranslatorToolsProcessor.SAMPLE_RATE * duration), False)
        tone = np.sin(tone_freq * t * 2 * np.pi)
        return (0.5 * tone).astype(np.float32)

    def get_tool_settings(self, tool_type):
        """Get settings for the specified tool."""
        if tool_type == "Morse Code Translator":
            return {
                "mode": self.morse_mode.get()
            }
        elif tool_type == "Binary Code Translator":
            return {}  # Binary translator doesn't have settings
        return {}

    def get_all_settings(self):
        """Get all settings for both translator tools."""
        return {
            "Morse Code Translator": self.get_tool_settings("Morse Code Translator"),
            "Binary Code Translator": self.get_tool_settings("Binary Code Translator")
        }

    def load_settings(self):
        """Load settings from the main application."""
        if not hasattr(self.app, 'settings'):
            return
            
        # Load Morse Code Translator settings
        morse_settings = self.app.settings.get("tool_settings", {}).get("Morse Code Translator", {})
        self.morse_mode.set(morse_settings.get("mode", "morse"))

    def save_settings(self):
        """Save settings to the main application."""
        if not hasattr(self.app, 'settings'):
            return
            
        # Save Morse Code Translator settings
        if "Morse Code Translator" not in self.app.settings["tool_settings"]:
            self.app.settings["tool_settings"]["Morse Code Translator"] = {}
        self.app.settings["tool_settings"]["Morse Code Translator"]["mode"] = self.morse_mode.get()

    def __del__(self):
        """Cleanup audio resources when widget is destroyed."""
        if self.audio_stream:
            try:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
            except:
                pass
        if self.pyaudio_instance:
            try:
                self.pyaudio_instance.terminate()
            except:
                pass


class TranslatorTools:
    """Main Translator Tools class that provides the interface for the main application."""
    
    def __init__(self):
        self.processor = TranslatorToolsProcessor()
        self.widget = None
        
    def create_widget(self, parent, app, dialog_manager=None):
        """Create and return the tabbed widget component."""
        self.widget = TranslatorToolsWidget(parent, app, dialog_manager)
        return self.widget
        
    def process_text(self, input_text, tool_type, settings):
        """Process text using the specified translator tool and settings."""
        return self.processor.process_text(input_text, tool_type, settings)
        
    def get_default_settings(self):
        """Get default settings for both translator tools."""
        return {
            "Morse Code Translator": {"mode": "morse", "tone": TranslatorToolsProcessor.TONE_FREQUENCY},
            "Binary Code Translator": {}
        }


# Convenience functions for backward compatibility
def morse_translator(text, mode, morse_dict=None, reversed_morse_dict=None):
    """Translate text to/from Morse code."""
    return TranslatorToolsProcessor.morse_translator(text, mode)


def binary_translator(text):
    """Translate text to/from binary code."""
    return TranslatorToolsProcessor.binary_translator(text)


# BaseTool-compatible wrapper
try:
    from tools.base_tool import ToolWithOptions
    from typing import Dict, Any
    
    class TranslatorToolsV2(ToolWithOptions):
        """
        BaseTool-compatible version of TranslatorTools.
        """
        
        TOOL_NAME = "Translator Tools"
        TOOL_DESCRIPTION = "Translate text to/from Morse code and binary"
        TOOL_VERSION = "2.0.0"
        
        OPTIONS = [
            ("Text to Morse", "to_morse"),
            ("Morse to Text", "from_morse"),
            ("Text to Binary", "to_binary"),
            ("Binary to Text", "from_binary"),
        ]
        OPTIONS_LABEL = "Translation"
        USE_DROPDOWN = True
        DEFAULT_OPTION = "to_morse"
        
        def __init__(self):
            super().__init__()
            self._processor = TranslatorToolsProcessor()
        
        def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
            """Process text using the specified translation mode."""
            mode = settings.get("mode", "to_morse")
            
            if mode == "to_morse":
                return TranslatorToolsProcessor.morse_translator(input_text, "morse")
            elif mode == "from_morse":
                return TranslatorToolsProcessor.morse_translator(input_text, "text")
            elif mode in ("to_binary", "from_binary"):
                return TranslatorToolsProcessor.binary_translator(input_text)
            else:
                return input_text

except ImportError:
    pass