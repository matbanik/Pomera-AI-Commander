import tkinter as tk
from tkinter import ttk, messagebox
import json
import logging
import requests
import threading
import time
import random
import webbrowser
import hashlib
import hmac
import urllib.parse
import os
import base64
from datetime import datetime

try:
    from huggingface_hub import InferenceClient
    from huggingface_hub.utils import HfHubHTTPError
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False

def get_system_encryption_key():
    """Generate encryption key based on system characteristics"""
    if not ENCRYPTION_AVAILABLE:
        return None
    
    try:
        # Use machine-specific data as salt
        machine_id = os.environ.get('COMPUTERNAME', '') + os.environ.get('USERNAME', '')
        if not machine_id:
            machine_id = os.environ.get('HOSTNAME', '') + os.environ.get('USER', '')
        
        salt = machine_id.encode()[:16].ljust(16, b'0')
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(b"pomera_ai_tool_encryption"))
        return Fernet(key)
    except Exception:
        return None

def encrypt_api_key(api_key):
    """Encrypt API key for storage"""
    if not api_key or api_key == "putinyourkey" or not ENCRYPTION_AVAILABLE:
        return api_key
    
    # Check if already encrypted (starts with our prefix)
    if api_key.startswith("ENC:"):
        return api_key
    
    try:
        fernet = get_system_encryption_key()
        if not fernet:
            return api_key
        
        encrypted = fernet.encrypt(api_key.encode())
        return "ENC:" + base64.urlsafe_b64encode(encrypted).decode()
    except Exception:
        return api_key  # Fallback to unencrypted if encryption fails

def decrypt_api_key(encrypted_key):
    """Decrypt API key for use"""
    if not encrypted_key or encrypted_key == "putinyourkey" or not ENCRYPTION_AVAILABLE:
        return encrypted_key
    
    # Check if encrypted (starts with our prefix)
    if not encrypted_key.startswith("ENC:"):
        return encrypted_key  # Not encrypted, return as-is
    
    try:
        fernet = get_system_encryption_key()
        if not fernet:
            return encrypted_key
        
        # Remove prefix and decrypt
        encrypted_data = encrypted_key[4:]  # Remove "ENC:" prefix
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = fernet.decrypt(encrypted_bytes)
        return decrypted.decode()
    except Exception:
        return encrypted_key  # Fallback to encrypted value if decryption fails

class AIToolsWidget(ttk.Frame):
    """A tabbed interface for all AI tools."""
    
    def __init__(self, parent, app_instance, dialog_manager=None):
        super().__init__(parent)
        self.app = app_instance
        self.logger = app_instance.logger
        self.dialog_manager = dialog_manager
        
        # AI provider configurations
        self.ai_providers = {
            "Google AI": {
                "url_template": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
                "headers_template": {'Content-Type': 'application/json'},
                "api_url": "https://aistudio.google.com/apikey"
            },
            "Anthropic AI": {
                "url": "https://api.anthropic.com/v1/messages",
                "headers_template": {"x-api-key": "{api_key}", "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
                "api_url": "https://console.anthropic.com/settings/keys"
            },
            "OpenAI": {
                "url": "https://api.openai.com/v1/chat/completions",
                "headers_template": {"Authorization": "Bearer {api_key}", "Content-Type": "application/json"},
                "api_url": "https://platform.openai.com/settings/organization/api-keys"
            },
            "Cohere AI": {
                "url": "https://api.cohere.com/v1/chat",
                "headers_template": {"Authorization": "Bearer {api_key}", "Content-Type": "application/json"},
                "api_url": "https://dashboard.cohere.com/api-keys"
            },
            "HuggingFace AI": {
                "api_url": "https://huggingface.co/settings/tokens"
            },
            "Groq AI": {
                "url": "https://api.groq.com/openai/v1/chat/completions",
                "headers_template": {"Authorization": "Bearer {api_key}", "Content-Type": "application/json"},
                "api_url": "https://console.groq.com/keys"
            },
            "OpenRouterAI": {
                "url": "https://openrouter.ai/api/v1/chat/completions",
                "headers_template": {"Authorization": "Bearer {api_key}", "Content-Type": "application/json"},
                "api_url": "https://openrouter.ai/settings/keys"
            },
            "LM Studio": {
                "url_template": "{base_url}/v1/chat/completions",
                "headers_template": {"Content-Type": "application/json"},
                "api_url": "http://lmstudio.ai/",
                "local_service": True
            },
            "AWS Bedrock": {
                "url": "https://bedrock-runtime.{region}.amazonaws.com/model/{model}/invoke",
                "headers_template": {"Content-Type": "application/json"},
                "api_url": "https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html",
                "aws_service": True
            }
        }
        
        self.current_provider = "Google AI"
        self.ai_widgets = {}
        self._ai_thread = None
        
        self.create_widgets()
        
        # Show encryption status in logs
        if ENCRYPTION_AVAILABLE:
            self.logger.info("API Key encryption is ENABLED - keys will be encrypted at rest")
        else:
            self.logger.warning("API Key encryption is DISABLED - cryptography library not found. Install with: pip install cryptography")
    
    def apply_font_to_widgets(self, font_tuple):
        """Apply font to all text widgets in AI Tools."""
        try:
            for provider_name, widgets in self.ai_widgets.items():
                for widget_name, widget in widgets.items():
                    # Apply to Text widgets (like system prompts)
                    if isinstance(widget, tk.Text):
                        widget.configure(font=font_tuple)
            
            self.logger.debug(f"Applied font {font_tuple} to AI Tools widgets")
        except Exception as e:
            self.logger.debug(f"Error applying font to AI Tools widgets: {e}")
    
    def get_api_key_for_provider(self, provider_name, settings):
        """Get decrypted API key for a provider"""
        if provider_name == "LM Studio":
            return ""  # LM Studio doesn't use API keys
        
        encrypted_key = settings.get("API_KEY", "")
        return decrypt_api_key(encrypted_key)
    
    def get_aws_credential(self, settings, credential_name):
        """Get decrypted AWS credential"""
        encrypted_credential = settings.get(credential_name, "")
        return decrypt_api_key(encrypted_credential)
    
    def save_encrypted_api_key(self, provider_name, api_key):
        """Save encrypted API key for a provider"""
        if provider_name == "LM Studio":
            return  # LM Studio doesn't use API keys
        
        if not api_key or api_key == "putinyourkey":
            # Don't encrypt empty or placeholder keys
            self.app.settings["tool_settings"][provider_name]["API_KEY"] = api_key
        else:
            encrypted_key = encrypt_api_key(api_key)
            self.app.settings["tool_settings"][provider_name]["API_KEY"] = encrypted_key
        
        self.app.save_settings()
    
    def _show_info(self, title, message, category="success"):
        """Show info dialog using DialogManager if available, otherwise use messagebox."""
        if self.dialog_manager:
            return self.dialog_manager.show_info(title, message, category)
        else:
            from tkinter import messagebox
            messagebox.showinfo(title, message)
            return True
    
    def _show_warning(self, title, message, category="warning"):
        """Show warning dialog using DialogManager if available, otherwise use messagebox."""
        if self.dialog_manager:
            return self.dialog_manager.show_warning(title, message, category)
        else:
            from tkinter import messagebox
            messagebox.showwarning(title, message)
            return True
    
    def _show_error(self, title, message):
        """Show error dialog using DialogManager if available, otherwise use messagebox."""
        if self.dialog_manager:
            return self.dialog_manager.show_error(title, message)
        else:
            from tkinter import messagebox
            messagebox.showerror(title, message)
            return True
    
    def create_widgets(self):
        """Create the tabbed interface for AI tools."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs for each AI provider
        self.tabs = {}
        for provider in self.ai_providers.keys():
            tab_frame = ttk.Frame(self.notebook)
            self.notebook.add(tab_frame, text=provider)
            self.tabs[provider] = tab_frame
            self.create_provider_widgets(tab_frame, provider)
        
        # Bind tab selection event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Set initial tab
        self.notebook.select(0)
        self.current_provider = list(self.ai_providers.keys())[0]
    
    def on_tab_changed(self, event=None):
        """Handle tab change event."""
        try:
            selected_tab = self.notebook.select()
            tab_index = self.notebook.index(selected_tab)
            self.current_provider = list(self.ai_providers.keys())[tab_index]
            self.app.on_tool_setting_change()  # Notify parent app of change
        except tk.TclError:
            pass
    
    def create_provider_widgets(self, parent, provider_name):
        """Create widgets for a specific AI provider."""
        # Get settings for this provider
        settings = self.app.settings["tool_settings"].get(provider_name, {})
        
        # Create main container with reduced padding - don't expand vertically
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.X, padx=5, pady=5, anchor="n")
        
        # Top frame with API key, model, and process button all on same line
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Store reference for later access
        if provider_name not in self.ai_widgets:
            self.ai_widgets[provider_name] = {}
        
        # API Configuration section (different for LM Studio and AWS Bedrock)
        if provider_name == "LM Studio":
            # LM Studio Configuration section
            lm_frame = ttk.LabelFrame(top_frame, text="LM Studio Configuration")
            lm_frame.pack(side=tk.LEFT, padx=(0, 10), fill=tk.Y)
            
            ttk.Label(lm_frame, text="Base URL:").pack(side=tk.LEFT, padx=(5, 5))
            
            base_url_var = tk.StringVar(value=settings.get("BASE_URL", "http://127.0.0.1:1234"))
            base_url_entry = ttk.Entry(lm_frame, textvariable=base_url_var, width=20)
            base_url_entry.pack(side=tk.LEFT, padx=(0, 5))
            base_url_var.trace_add("write", lambda *args: self.on_setting_change(provider_name))
            
            self.ai_widgets[provider_name]["BASE_URL"] = base_url_var
            
            # Refresh models button
            ttk.Button(lm_frame, text="Refresh Models", 
                      command=lambda: self.refresh_lm_studio_models(provider_name)).pack(side=tk.LEFT, padx=(5, 5))
        elif provider_name == "AWS Bedrock":
            # AWS Bedrock Configuration section
            aws_frame = ttk.LabelFrame(top_frame, text="AWS Bedrock Configuration")
            aws_frame.pack(side=tk.LEFT, padx=(0, 10), fill=tk.Y)
            
            # Authentication Method
            ttk.Label(aws_frame, text="Auth Method:").pack(side=tk.LEFT, padx=(5, 5))
            
            auth_method_var = tk.StringVar(value=settings.get("AUTH_METHOD", "iam"))
            auth_combo = ttk.Combobox(aws_frame, textvariable=auth_method_var, 
                                    values=[
                                        "API Key (Bearer Token)",
                                        "IAM (Explicit Credentials)", 
                                        "Session Token (Temporary Credentials)",
                                        "IAM (Implied Credentials)"
                                    ], 
                                    state="readonly", width=30)
            
            # Set the display value based on stored value
            stored_auth = settings.get("AUTH_METHOD", "api_key")
            if stored_auth == "api_key":
                auth_combo.set("API Key (Bearer Token)")
            elif stored_auth == "iam":
                auth_combo.set("IAM (Explicit Credentials)")
            elif stored_auth == "sessionToken":
                auth_combo.set("Session Token (Temporary Credentials)")
            elif stored_auth == "iam_role":
                auth_combo.set("IAM (Implied Credentials)")
            auth_combo.pack(side=tk.LEFT, padx=(0, 5))
            auth_method_var.trace_add("write", lambda *args: [self.on_aws_auth_change(provider_name), self.update_aws_credentials_fields(provider_name)])
            
            self.ai_widgets[provider_name]["AUTH_METHOD"] = auth_method_var
            
            # AWS Region
            ttk.Label(aws_frame, text="Region:").pack(side=tk.LEFT, padx=(10, 5))
            
            region_var = tk.StringVar(value=settings.get("AWS_REGION", "us-west-2"))
            aws_regions = [
                "us-east-1", "us-east-2", "us-west-1", "us-west-2",
                "ca-central-1", "eu-north-1", "eu-west-1", "eu-west-2", 
                "eu-west-3", "eu-central-1", "eu-south-1", "af-south-1",
                "ap-northeast-1", "ap-northeast-2", "ap-northeast-3",
                "ap-southeast-1", "ap-southeast-2", "ap-southeast-3",
                "ap-east-1", "ap-south-1", "sa-east-1", "me-south-1"
            ]
            region_combo = ttk.Combobox(aws_frame, textvariable=region_var, 
                                      values=aws_regions, state="readonly", width=15)
            region_combo.pack(side=tk.LEFT, padx=(0, 5))
            region_var.trace_add("write", lambda *args: self.on_setting_change(provider_name))
            
            self.ai_widgets[provider_name]["AWS_REGION"] = region_var
        else:
            # Standard API Configuration section
            encryption_status = "🔒" if ENCRYPTION_AVAILABLE else "⚠️"
            api_frame = ttk.LabelFrame(top_frame, text=f"API Configuration {encryption_status}")
            api_frame.pack(side=tk.LEFT, padx=(0, 10), fill=tk.Y)
            
            ttk.Label(api_frame, text="API Key:").pack(side=tk.LEFT, padx=(5, 5))
            
            # Get decrypted API key for display
            decrypted_key = self.get_api_key_for_provider(provider_name, settings)
            api_key_var = tk.StringVar(value=decrypted_key if decrypted_key else "putinyourkey")
            api_key_entry = ttk.Entry(api_frame, textvariable=api_key_var, show="*", width=20)
            api_key_entry.pack(side=tk.LEFT, padx=(0, 5))
            api_key_var.trace_add("write", lambda *args: self.on_setting_change(provider_name))
            
            self.ai_widgets[provider_name]["API_KEY"] = api_key_var
            
            # API key link button
            ttk.Button(api_frame, text="Get API Key", 
                      command=lambda: webbrowser.open(self.ai_providers[provider_name]["api_url"])).pack(side=tk.LEFT, padx=(5, 5))
        
        # Model Configuration section
        model_frame = ttk.LabelFrame(top_frame, text="Model Configuration")
        model_frame.pack(side=tk.LEFT, padx=(0, 10), fill=tk.Y)
        
        ttk.Label(model_frame, text="Model:").pack(side=tk.LEFT, padx=(5, 5))
        
        model_var = tk.StringVar(value=settings.get("MODEL", ""))
        models_list = settings.get("MODELS_LIST", [])
        
        model_combo = ttk.Combobox(model_frame, textvariable=model_var, values=models_list, width=30)
        model_combo.pack(side=tk.LEFT, padx=(0, 5))
        model_combo.bind("<<ComboboxSelected>>", lambda e: self.on_setting_change(provider_name))
        model_combo.bind("<KeyRelease>", lambda e: self.on_setting_change(provider_name))
        
        # Model buttons
        if provider_name == "AWS Bedrock":
            # Refresh Models button for AWS Bedrock
            ttk.Button(model_frame, text="Refresh Models", 
                      command=lambda: self.refresh_bedrock_models(provider_name)).pack(side=tk.LEFT, padx=(0, 5))
        elif provider_name == "LM Studio":
            # Store model combobox reference for LM Studio
            pass  # LM Studio refresh button is in the configuration section
        else:
            # Model edit button for other providers
            ttk.Button(model_frame, text="\u270E", 
                      command=lambda: self.open_model_editor(provider_name), width=3).pack(side=tk.LEFT, padx=(0, 5))
        
        self.ai_widgets[provider_name]["MODEL"] = model_var
        
        # Store model combobox reference for LM Studio and AWS Bedrock
        if provider_name in ["LM Studio", "AWS Bedrock"]:
            self.ai_widgets[provider_name]["MODEL_COMBO"] = model_combo
        
        # Max Tokens for LM Studio
        if provider_name == "LM Studio":
            ttk.Label(model_frame, text="Max Tokens:").pack(side=tk.LEFT, padx=(10, 5))
            
            max_tokens_var = tk.StringVar(value=settings.get("MAX_TOKENS", "2048"))
            max_tokens_entry = ttk.Entry(model_frame, textvariable=max_tokens_var, width=10)
            max_tokens_entry.pack(side=tk.LEFT, padx=(0, 5))
            max_tokens_var.trace_add("write", lambda *args: self.on_setting_change(provider_name))
            
            self.ai_widgets[provider_name]["MAX_TOKENS"] = max_tokens_var
        
        # AWS Bedrock specific fields
        if provider_name == "AWS Bedrock":
            # AWS Credentials section
            self.aws_creds_frame = ttk.LabelFrame(main_frame, text="AWS Credentials")
            self.aws_creds_frame.pack(fill=tk.X, pady=(5, 0))
            
            # Add note about AWS Bedrock authentication
            note_frame = ttk.Frame(self.aws_creds_frame)
            note_frame.pack(fill=tk.X, padx=5, pady=2)
            
            auth_note = "AWS Bedrock supports both API Key (Bearer Token) and IAM authentication.\nAPI Key is simpler, IAM provides more granular control."
            if ENCRYPTION_AVAILABLE:
                auth_note += "\n🔒 API keys are encrypted at rest for security."
            else:
                auth_note += "\n⚠️ API keys are stored in plain text. Install 'cryptography' for encryption."
            
            note_label = ttk.Label(note_frame, text=auth_note, foreground="blue", font=('TkDefaultFont', 8))
            note_label.pack(side=tk.LEFT)
            
            # API Key row
            self.api_key_row = ttk.Frame(self.aws_creds_frame)
            self.api_key_row.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(self.api_key_row, text="AWS Bedrock API Key:").pack(side=tk.LEFT)
            # Get decrypted API key for display
            decrypted_key = self.get_api_key_for_provider(provider_name, settings)
            api_key_var = tk.StringVar(value=decrypted_key if decrypted_key else "")
            api_key_entry = ttk.Entry(self.api_key_row, textvariable=api_key_var, show="*", width=40)
            api_key_entry.pack(side=tk.LEFT, padx=(5, 0))
            api_key_var.trace_add("write", lambda *args: self.on_setting_change(provider_name))
            self.ai_widgets[provider_name]["API_KEY"] = api_key_var
            
            # Get API Key link
            get_key_link = ttk.Label(self.api_key_row, text="Get API Key", foreground="blue", cursor="hand2")
            get_key_link.pack(side=tk.LEFT, padx=(10, 0))
            get_key_link.bind("<Button-1>", lambda e: webbrowser.open("https://console.aws.amazon.com/bedrock/home"))
            
            # Access Key ID row
            self.access_key_row = ttk.Frame(self.aws_creds_frame)
            self.access_key_row.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(self.access_key_row, text="AWS Bedrock IAM Access ID:").pack(side=tk.LEFT)
            # Get decrypted AWS Access Key for display
            decrypted_access_key = self.get_aws_credential(settings, "AWS_ACCESS_KEY_ID")
            access_key_var = tk.StringVar(value=decrypted_access_key)
            access_key_entry = ttk.Entry(self.access_key_row, textvariable=access_key_var, show="*", width=30)
            access_key_entry.pack(side=tk.LEFT, padx=(5, 0))
            access_key_var.trace_add("write", lambda *args: self.on_setting_change(provider_name))
            self.ai_widgets[provider_name]["AWS_ACCESS_KEY_ID"] = access_key_var
            
            # Secret Access Key row
            self.secret_key_row = ttk.Frame(self.aws_creds_frame)
            self.secret_key_row.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(self.secret_key_row, text="AWS Bedrock IAM Access Key:").pack(side=tk.LEFT)
            # Get decrypted AWS Secret Key for display
            decrypted_secret_key = self.get_aws_credential(settings, "AWS_SECRET_ACCESS_KEY")
            secret_key_var = tk.StringVar(value=decrypted_secret_key)
            secret_key_entry = ttk.Entry(self.secret_key_row, textvariable=secret_key_var, show="*", width=30)
            secret_key_entry.pack(side=tk.LEFT, padx=(5, 0))
            secret_key_var.trace_add("write", lambda *args: self.on_setting_change(provider_name))
            self.ai_widgets[provider_name]["AWS_SECRET_ACCESS_KEY"] = secret_key_var
            
            # Session Token row
            self.session_token_row = ttk.Frame(self.aws_creds_frame)
            self.session_token_row.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(self.session_token_row, text="AWS Bedrock Session Token:").pack(side=tk.LEFT)
            # Get decrypted AWS Session Token for display
            decrypted_session_token = self.get_aws_credential(settings, "AWS_SESSION_TOKEN")
            session_token_var = tk.StringVar(value=decrypted_session_token)
            session_token_entry = ttk.Entry(self.session_token_row, textvariable=session_token_var, show="*", width=30)
            session_token_entry.pack(side=tk.LEFT, padx=(5, 0))
            session_token_var.trace_add("write", lambda *args: self.on_setting_change(provider_name))
            self.ai_widgets[provider_name]["AWS_SESSION_TOKEN"] = session_token_var
            
            # Content section (renamed from Model Configuration)
            content_frame = ttk.LabelFrame(main_frame, text="Content")
            content_frame.pack(fill=tk.X, pady=(5, 0))
            
            content_row = ttk.Frame(content_frame)
            content_row.pack(fill=tk.X, padx=5, pady=5)
            
            # Context Window
            ttk.Label(content_row, text="Model context window:").pack(side=tk.LEFT)
            context_window_var = tk.StringVar(value=settings.get("CONTEXT_WINDOW", "8192"))
            context_window_entry = ttk.Entry(content_row, textvariable=context_window_var, width=10)
            context_window_entry.pack(side=tk.LEFT, padx=(5, 20))
            context_window_var.trace_add("write", lambda *args: self.on_setting_change(provider_name))
            self.ai_widgets[provider_name]["CONTEXT_WINDOW"] = context_window_var
            
            # Max Output Tokens
            ttk.Label(content_row, text="Model max output tokens:").pack(side=tk.LEFT)
            max_output_tokens_var = tk.StringVar(value=settings.get("MAX_OUTPUT_TOKENS", "4096"))
            max_output_tokens_entry = ttk.Entry(content_row, textvariable=max_output_tokens_var, width=10)
            max_output_tokens_entry.pack(side=tk.LEFT, padx=(5, 0))
            max_output_tokens_var.trace_add("write", lambda *args: self.on_setting_change(provider_name))
            self.ai_widgets[provider_name]["MAX_OUTPUT_TOKENS"] = max_output_tokens_var
            
            # Add IAM role info frame
            self.iam_role_info_frame = ttk.Frame(self.aws_creds_frame)
            self.iam_role_info_frame.pack(fill=tk.X, padx=5, pady=5)
            
            info_label = ttk.Label(self.iam_role_info_frame, 
                                 text="IAM Role authentication uses the AWS credentials configured on this system.\nEnsure your AWS CLI is configured or EC2 instance has proper IAM role.",
                                 foreground="gray")
            info_label.pack(side=tk.LEFT)
            
            # Initialize field visibility based on current auth method
            self.update_aws_credentials_fields(provider_name)
        
        # Process button section
        process_frame = ttk.Frame(top_frame)
        process_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        ttk.Button(process_frame, text="Process", 
                  command=self.run_ai_in_thread).pack(padx=5, pady=10)
        
        # System prompt
        system_frame = ttk.LabelFrame(main_frame, text="System Prompt")
        system_frame.pack(fill=tk.X, pady=(0, 5))
        
        system_prompt_key = "system_prompt"
        if provider_name == "Anthropic AI":
            system_prompt_key = "system"
        elif provider_name == "Cohere AI":
            system_prompt_key = "preamble"
        
        system_text = tk.Text(system_frame, height=2, wrap=tk.WORD)
        
        # Apply current font settings from main app
        try:
            if hasattr(self.app, 'get_best_font'):
                text_font_family, text_font_size = self.app.get_best_font("text")
                system_text.configure(font=(text_font_family, text_font_size))
        except:
            pass  # Use default font if font settings not available
        
        system_text.pack(fill=tk.X, padx=5, pady=3)
        system_text.insert("1.0", settings.get(system_prompt_key, "You are a helpful assistant."))
        
        self.ai_widgets[provider_name][system_prompt_key] = system_text
        
        # Parameters notebook with minimal height to reduce empty space (skip for AWS Bedrock and LM Studio)
        if provider_name not in ["AWS Bedrock", "LM Studio"]:
            params_notebook = ttk.Notebook(main_frame)
            # Much smaller height to eliminate wasted space - users can scroll if needed
            params_notebook.pack(fill=tk.X, pady=(5, 0))
            params_notebook.configure(height=120)  # Significantly reduced height
            
            # Create parameter tabs
            self.create_parameter_tabs(params_notebook, provider_name, settings)
        
        # Bind change events
        model_var.trace_add("write", lambda *args: self.on_setting_change(provider_name))
        system_text.bind("<KeyRelease>", lambda *args: self.on_setting_change(provider_name))
    
    def create_parameter_tabs(self, notebook, provider_name, settings):
        """Create parameter configuration tabs."""
        # Get parameter configuration for this provider
        params_config = self._get_ai_params_config(provider_name)
        
        # Group parameters by tab
        tabs_data = {}
        for param, config in params_config.items():
            tab_name = config.get("tab", "general")
            if tab_name not in tabs_data:
                tabs_data[tab_name] = {}
            tabs_data[tab_name][param] = config
        
        # Create tabs
        for tab_name, params in tabs_data.items():
            tab_frame = ttk.Frame(notebook)
            notebook.add(tab_frame, text=tab_name.title())
            
            # Create scrollable frame with improved scrolling
            canvas = tk.Canvas(tab_frame, highlightthickness=0)
            scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            def configure_scroll_region(event=None):
                canvas.configure(scrollregion=canvas.bbox("all"))
            
            def on_mousewheel(event):
                # Handle cross-platform mouse wheel events
                if event.delta:
                    # Windows
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                else:
                    # Linux
                    if event.num == 4:
                        canvas.yview_scroll(-1, "units")
                    elif event.num == 5:
                        canvas.yview_scroll(1, "units")
            
            scrollable_frame.bind("<Configure>", configure_scroll_region)
            
            # Bind mouse wheel to canvas and scrollable frame (cross-platform)
            canvas.bind("<MouseWheel>", on_mousewheel)  # Windows
            canvas.bind("<Button-4>", on_mousewheel)    # Linux scroll up
            canvas.bind("<Button-5>", on_mousewheel)    # Linux scroll down
            scrollable_frame.bind("<MouseWheel>", on_mousewheel)
            scrollable_frame.bind("<Button-4>", on_mousewheel)
            scrollable_frame.bind("<Button-5>", on_mousewheel)
            
            # Make sure mouse wheel works when hovering over child widgets
            def bind_mousewheel_to_children(widget):
                widget.bind("<MouseWheel>", on_mousewheel)
                widget.bind("<Button-4>", on_mousewheel)
                widget.bind("<Button-5>", on_mousewheel)
                for child in widget.winfo_children():
                    bind_mousewheel_to_children(child)
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Store references for later mouse wheel binding
            canvas._scrollable_frame = scrollable_frame
            canvas._bind_mousewheel_to_children = bind_mousewheel_to_children
            
            # Add parameters to scrollable frame
            row = 0
            for param, config in params.items():
                self.create_parameter_widget(scrollable_frame, provider_name, param, config, settings, row)
                row += 1
            
            # Bind mouse wheel to all child widgets after they're created
            canvas._bind_mousewheel_to_children(scrollable_frame)
    
    def create_parameter_widget(self, parent, provider_name, param, config, settings, row):
        """Create a widget for a specific parameter."""
        # Label
        ttk.Label(parent, text=param.replace("_", " ").title() + ":").grid(row=row, column=0, sticky="w", padx=(5, 10), pady=2)
        
        # Get current value
        current_value = settings.get(param, "")
        
        # Create appropriate widget based on type
        if config["type"] == "scale":
            var = tk.DoubleVar(value=float(current_value) if current_value else config["range"][0])
            scale = ttk.Scale(parent, from_=config["range"][0], to=config["range"][1], 
                            variable=var, orient=tk.HORIZONTAL, length=200)
            scale.grid(row=row, column=1, sticky="ew", padx=(0, 10), pady=2)
            
            # Value label
            value_label = ttk.Label(parent, text=f"{var.get():.2f}")
            value_label.grid(row=row, column=2, padx=(0, 5), pady=2)
            
            # Update label when scale changes
            def update_label(*args):
                value_label.config(text=f"{var.get():.2f}")
                self.on_setting_change(provider_name)
            
            var.trace_add("write", update_label)
            
        elif config["type"] == "combo":
            var = tk.StringVar(value=current_value)
            combo = ttk.Combobox(parent, textvariable=var, values=config["values"], width=20)
            combo.grid(row=row, column=1, sticky="ew", padx=(0, 10), pady=2)
            var.trace_add("write", lambda *args: self.on_setting_change(provider_name))
            
        else:  # entry
            var = tk.StringVar(value=current_value)
            entry = ttk.Entry(parent, textvariable=var, width=30)
            entry.grid(row=row, column=1, sticky="ew", padx=(0, 10), pady=2)
            var.trace_add("write", lambda *args: self.on_setting_change(provider_name))
        
        # Store widget reference
        self.ai_widgets[provider_name][param] = var
        
        # Tooltip
        if "tip" in config:
            self.create_tooltip(parent.grid_slaves(row=row, column=1)[0], config["tip"])
        
        # Configure column weights
        parent.columnconfigure(1, weight=1)
    
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget with proper delay."""
        tooltip_window = None
        tooltip_timer = None
        
        def show_tooltip_delayed():
            nonlocal tooltip_window
            if tooltip_window is None:
                x, y = widget.winfo_rootx() + 25, widget.winfo_rooty() + 25
                tooltip_window = tk.Toplevel()
                tooltip_window.wm_overrideredirect(True)
                tooltip_window.wm_geometry(f"+{x}+{y}")
                
                label = ttk.Label(tooltip_window, text=text, background="#ffffe0", 
                                relief="solid", borderwidth=1, wraplength=250)
                label.pack()
        
        def on_enter(event):
            nonlocal tooltip_timer
            # Cancel any existing timer
            if tooltip_timer:
                widget.after_cancel(tooltip_timer)
            # Start new timer with 750ms delay (standard for most applications)
            tooltip_timer = widget.after(750, show_tooltip_delayed)
        
        def on_leave(event):
            nonlocal tooltip_window, tooltip_timer
            # Cancel the timer if we leave before tooltip shows
            if tooltip_timer:
                widget.after_cancel(tooltip_timer)
                tooltip_timer = None
            # Hide tooltip if it's showing
            if tooltip_window:
                tooltip_window.destroy()
                tooltip_window = None
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def on_setting_change(self, provider_name):
        """Handle setting changes for a provider."""
        # Update settings in parent app
        if provider_name not in self.app.settings["tool_settings"]:
            self.app.settings["tool_settings"][provider_name] = {}
        
        # Update all widget values
        for param, widget in self.ai_widgets[provider_name].items():
            if isinstance(widget, tk.Text):
                value = widget.get("1.0", tk.END).strip()
            else:
                value = widget.get()
            
            # Encrypt sensitive credentials before saving (except for LM Studio)
            if provider_name != "LM Studio" and param in ["API_KEY", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"]:
                if value and value != "putinyourkey":
                    value = encrypt_api_key(value)
            
            self.app.settings["tool_settings"][provider_name][param] = value
        
        # Save settings
        self.app.save_settings()
    
    def refresh_lm_studio_models(self, provider_name):
        """Refresh the model list from LM Studio server."""
        if provider_name != "LM Studio":
            return
        
        base_url = self.ai_widgets[provider_name]["BASE_URL"].get().strip()
        if not base_url:
            self._show_error("Error", "Please enter a valid Base URL")
            return
        
        try:
            # Remove trailing slash if present
            base_url = base_url.rstrip('/')
            models_url = f"{base_url}/v1/models"
            
            response = requests.get(models_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            models = [model["id"] for model in data.get("data", [])]
            
            if models:
                # Update the model combobox using stored reference
                model_combo = self.ai_widgets[provider_name].get("MODEL_COMBO")
                if model_combo:
                    model_combo.configure(values=models)
                    # Set first model as default if no model is currently selected
                    if models and not self.ai_widgets[provider_name]["MODEL"].get():
                        self.ai_widgets[provider_name]["MODEL"].set(models[0])
                
                # Update settings
                self.app.settings["tool_settings"][provider_name]["MODELS_LIST"] = models
                self.app.save_settings()
                
                self._show_info("Success", f"Found {len(models)} models from LM Studio")
            else:
                self._show_warning("Warning", "No models found. Make sure LM Studio is running and has models loaded.")
                
        except requests.exceptions.RequestException as e:
            self._show_error("Connection Error", f"Could not connect to LM Studio at {base_url}\n\nError: {e}\n\nMake sure LM Studio is running and the Base URL is correct.")
        except Exception as e:
            self._show_error("Error", f"Error refreshing models: {e}")
    
    def refresh_bedrock_models(self, provider_name):
        """Refresh the model list from AWS Bedrock ListFoundationModels API."""
        if provider_name != "AWS Bedrock":
            return
        
        settings = self.app.settings["tool_settings"].get(provider_name, {})
        auth_method = settings.get("AUTH_METHOD", "api_key")
        region = settings.get("AWS_REGION", "us-west-2")
        
        # AWS Bedrock ListFoundationModels API requires AWS IAM credentials
        access_key = self.get_aws_credential(settings, "AWS_ACCESS_KEY_ID")
        secret_key = self.get_aws_credential(settings, "AWS_SECRET_ACCESS_KEY")
        
        if not access_key or not secret_key:
            self._show_error("Error", "Please enter your AWS IAM credentials (Access Key ID and Secret Access Key) first")
            return
        
        try:
            # Build ListFoundationModels API URL
            list_models_url = f"https://bedrock.{region}.amazonaws.com/foundation-models"
            
            # Always use AWS SigV4 signing for ListFoundationModels API
            session_token = self.get_aws_credential(settings, "AWS_SESSION_TOKEN") if auth_method == "sessionToken" else None
            
            # Sign the request (GET method, empty payload)
            signed_headers = self.sign_aws_request(
                "GET", list_models_url, "", access_key, secret_key,
                session_token, region, "bedrock"
            )
            
            # Make the API request with signed headers
            response = requests.get(list_models_url, headers=signed_headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            models = []
            
            # Extract model IDs from the response, filtering out embedding and image models
            models = []
            if "modelSummaries" in data:
                for model in data["modelSummaries"]:
                    model_id = model.get("modelId", "")
                    model_name = model.get("modelName", "")
                    
                    # Filter out embedding models and image generation models
                    # Embedding models: contain "embed" in ID or name
                    # Image models: contain "image", "stable-diffusion", "titan-image", "nova-canvas", "nova-reel"
                    if model_id and not any(keyword in model_id.lower() for keyword in [
                        "embed", "embedding", "image", "stable-diffusion", 
                        "titan-image", "nova-canvas", "nova-reel", "nova-sonic"
                    ]):
                        # Also check model name for additional filtering
                        if not any(keyword in model_name.lower() for keyword in [
                            "embed", "embedding", "image", "vision"
                        ]):
                            models.append(model_id)
            
            if models:
                # Update the model combobox
                model_combo = self.ai_widgets[provider_name].get("MODEL_COMBO")
                if model_combo:
                    model_combo.configure(values=models)
                    # Set first model as default if no model is currently selected
                    if models and not self.ai_widgets[provider_name]["MODEL"].get():
                        self.ai_widgets[provider_name]["MODEL"].set(models[0])
                
                # Update settings
                self.app.settings["tool_settings"][provider_name]["MODELS_LIST"] = models
                self.app.save_settings()
                
                self._show_info("Success", f"Found {len(models)} models from AWS Bedrock")
            else:
                self._show_warning("Warning", "No models found. Please check your credentials and region.")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Could not connect to AWS Bedrock API\n\nError: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    if "message" in error_data:
                        error_msg += f"\n\nAWS Error: {error_data['message']}"
                except:
                    error_msg += f"\n\nHTTP {e.response.status_code}: {e.response.text}"
            self._show_error("Connection Error", error_msg)
        except Exception as e:
            self._show_error("Error", f"Error refreshing models: {e}")
    
    def update_aws_credentials_fields(self, provider_name):
        """Update AWS credentials field visibility based on authentication method."""
        if provider_name != "AWS Bedrock" or not hasattr(self, 'aws_creds_frame'):
            return
        
        # Get the stored value from settings
        stored_auth = self.app.settings["tool_settings"].get(provider_name, {}).get("AUTH_METHOD", "iam")
        
        # Hide all credential fields first
        if hasattr(self, 'api_key_row'):
            self.api_key_row.pack_forget()
        if hasattr(self, 'access_key_row'):
            self.access_key_row.pack_forget()
        if hasattr(self, 'secret_key_row'):
            self.secret_key_row.pack_forget()
        if hasattr(self, 'session_token_row'):
            self.session_token_row.pack_forget()
        if hasattr(self, 'iam_role_info_frame'):
            self.iam_role_info_frame.pack_forget()
        
        # Show fields based on authentication method
        if stored_auth == "api_key":  # API Key (Bearer Token)
            self.api_key_row.pack(fill=tk.X, padx=5, pady=2)
        elif stored_auth == "iam":  # IAM (Explicit Credentials)
            self.access_key_row.pack(fill=tk.X, padx=5, pady=2)
            self.secret_key_row.pack(fill=tk.X, padx=5, pady=2)
        elif stored_auth == "sessionToken":  # Session Token (Temporary Credentials)
            self.access_key_row.pack(fill=tk.X, padx=5, pady=2)
            self.secret_key_row.pack(fill=tk.X, padx=5, pady=2)
            self.session_token_row.pack(fill=tk.X, padx=5, pady=2)
        elif stored_auth == "iam_role":  # IAM (Implied Credentials)
            self.iam_role_info_frame.pack(fill=tk.X, padx=5, pady=5)
    
    def on_aws_auth_change(self, provider_name):
        """Handle AWS authentication method change and convert display name to stored value."""
        if provider_name != "AWS Bedrock":
            return
        
        display_value = self.ai_widgets[provider_name]["AUTH_METHOD"].get()
        
        # Convert display name to stored value
        if display_value == "API Key (Bearer Token)":
            stored_value = "api_key"
        elif display_value == "IAM (Explicit Credentials)":
            stored_value = "iam"
        elif display_value == "Session Token (Temporary Credentials)":
            stored_value = "sessionToken"
        elif display_value == "IAM (Implied Credentials)":
            stored_value = "iam_role"
        else:
            stored_value = "api_key"  # default
        
        # Update settings with the stored value
        if provider_name not in self.app.settings["tool_settings"]:
            self.app.settings["tool_settings"][provider_name] = {}
        
        self.app.settings["tool_settings"][provider_name]["AUTH_METHOD"] = stored_value
        self.app.save_settings()
    
    def sign_aws_request(self, method, url, payload, access_key, secret_key, session_token=None, region="us-west-2", service="bedrock"):
        """Sign AWS request using Signature Version 4."""
        try:
            # Parse URL
            parsed_url = urllib.parse.urlparse(url)
            host = parsed_url.netloc
            path = parsed_url.path
            
            # Create timestamp
            t = datetime.utcnow()
            amz_date = t.strftime('%Y%m%dT%H%M%SZ')
            date_stamp = t.strftime('%Y%m%d')
            
            # Create canonical request
            canonical_uri = path
            canonical_querystring = ''
            canonical_headers = f'host:{host}\nx-amz-date:{amz_date}\n'
            signed_headers = 'host;x-amz-date'
            
            if session_token:
                canonical_headers += f'x-amz-security-token:{session_token}\n'
                signed_headers += ';x-amz-security-token'
            
            payload_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
            canonical_request = f'{method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}'
            
            # Create string to sign
            algorithm = 'AWS4-HMAC-SHA256'
            credential_scope = f'{date_stamp}/{region}/{service}/aws4_request'
            string_to_sign = f'{algorithm}\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()}'
            
            # Calculate signature
            def sign(key, msg):
                return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
            
            def get_signature_key(key, date_stamp, region_name, service_name):
                k_date = sign(('AWS4' + key).encode('utf-8'), date_stamp)
                k_region = sign(k_date, region_name)
                k_service = sign(k_region, service_name)
                k_signing = sign(k_service, 'aws4_request')
                return k_signing
            
            signing_key = get_signature_key(secret_key, date_stamp, region, service)
            signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
            
            # Create authorization header
            authorization_header = f'{algorithm} Credential={access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}'
            
            # Build headers
            headers = {
                'Content-Type': 'application/json',
                'X-Amz-Date': amz_date,
                'Authorization': authorization_header,
                'X-Amz-Content-Sha256': payload_hash
            }
            
            if session_token:
                headers['X-Amz-Security-Token'] = session_token
            
            return headers
            
        except Exception as e:
            self.logger.error(f"Error signing AWS request: {e}")
            return {}
    
    def get_current_provider(self):
        """Get the currently selected provider."""
        return self.current_provider
    
    def get_current_settings(self):
        """Get settings for the current provider."""
        return self.app.settings["tool_settings"].get(self.current_provider, {})
    
    def run_ai_in_thread(self):
        """Start AI processing in a separate thread."""
        if hasattr(self, '_ai_thread') and self._ai_thread and self._ai_thread.is_alive():
            return
        
        self.app.update_output_text("Generating response from AI...")
        self._ai_thread = threading.Thread(target=self.process_ai_request, daemon=True)
        self._ai_thread.start()
    
    def process_ai_request(self):
        """Process the AI request."""
        provider_name = self.current_provider
        settings = self.get_current_settings()
        api_key = self.get_api_key_for_provider(provider_name, settings)
        
        # Get input text from parent app
        active_input_tab = self.app.input_tabs[self.app.input_notebook.index(self.app.input_notebook.select())]
        prompt = active_input_tab.text.get("1.0", tk.END).strip()
        
        # LM Studio doesn't require API key, AWS Bedrock has multiple auth methods
        if provider_name == "AWS Bedrock":
            # Validate AWS Bedrock credentials
            auth_method = settings.get("AUTH_METHOD", "api_key")
            
            # Handle both display names and internal values for backward compatibility
            is_api_key_auth = auth_method in ["api_key", "API Key (Bearer Token)"]
            is_iam_auth = auth_method in ["iam", "IAM (Explicit Credentials)"]
            is_session_token_auth = auth_method in ["sessionToken", "Session Token (Temporary Credentials)"]
            
            if is_api_key_auth:
                api_key = self.get_api_key_for_provider(provider_name, settings)
                if not api_key or api_key == "putinyourkey":
                    self.app.after(0, self.app.update_output_text, "Error: AWS Bedrock requires an API Key. Please enter your AWS Bedrock API Key.")
                    return
            elif is_iam_auth or is_session_token_auth:
                access_key = self.get_aws_credential(settings, "AWS_ACCESS_KEY_ID")
                secret_key = self.get_aws_credential(settings, "AWS_SECRET_ACCESS_KEY")
                if not access_key or not secret_key:
                    self.app.after(0, self.app.update_output_text, "Error: AWS Bedrock requires Access Key ID and Secret Access Key.")
                    return
                if is_session_token_auth:
                    session_token = self.get_aws_credential(settings, "AWS_SESSION_TOKEN")
                    if not session_token:
                        self.app.after(0, self.app.update_output_text, "Error: AWS Bedrock requires Session Token for temporary credentials.")
                        return
        elif provider_name != "LM Studio" and (not api_key or api_key == "putinyourkey"):
            self.app.after(0, self.app.update_output_text, f"Error: Please enter a valid {provider_name} API Key in the settings.")
            return
        if not prompt:
            self.app.after(0, self.app.update_output_text, "Error: Input text cannot be empty.")
            return
        
        self.logger.info(f"Submitting prompt to {provider_name} with model {settings.get('MODEL')}")
        
        # Handle HuggingFace separately (uses different client)
        if provider_name == "HuggingFace AI":
            self._process_huggingface_request(api_key, prompt, settings)
        else:
            self._process_rest_api_request(provider_name, api_key, prompt, settings)
    
    def _process_huggingface_request(self, api_key, prompt, settings):
        """Process HuggingFace AI request."""
        if not HUGGINGFACE_AVAILABLE:
            self.app.after(0, self.app.update_output_text, "Error: huggingface_hub library not found. Please install it.")
            return
        
        try:
            client = InferenceClient(token=api_key)
            messages = []
            system_prompt = settings.get("system_prompt", "").strip()
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            params = {"messages": messages, "model": settings.get("MODEL")}
            
            # Add supported parameters
            self._add_param_if_valid(params, settings, "max_tokens", int)
            self._add_param_if_valid(params, settings, "seed", int)
            self._add_param_if_valid(params, settings, "temperature", float)
            self._add_param_if_valid(params, settings, "top_p", float)
            
            stop_seq_str = str(settings.get("stop_sequences", '')).strip()
            if stop_seq_str:
                params["stop"] = [s.strip() for s in stop_seq_str.split(',')]
            
            self.logger.debug(f"HuggingFace payload: {json.dumps(params, indent=2, default=str)}")
            response_obj = client.chat_completion(**params)
            self.app.after(0, self.app.update_output_text, response_obj.choices[0].message.content)
            
        except HfHubHTTPError as e:
            error_msg = f"HuggingFace API Error: {e.response.status_code} - {e.response.reason}\n\n{e.response.text}"
            if e.response.status_code == 401:
                error_msg += "\n\nThis means your API token is invalid or expired."
            elif e.response.status_code == 403:
                error_msg += f"\n\nThis is a 'gated model'. You MUST accept the terms on the model page:\nhttps://huggingface.co/{settings.get('MODEL')}"
            self.logger.error(error_msg, exc_info=True)
            self.app.after(0, self.app.update_output_text, error_msg)
        except Exception as e:
            self.logger.error(f"HuggingFace Client Error: {e}", exc_info=True)
            self.app.after(0, self.app.update_output_text, f"HuggingFace Client Error: {e}")
    
    def _process_rest_api_request(self, provider_name, api_key, prompt, settings):
        """Process REST API request for other providers."""
        try:
            # Validate model selection for AWS Bedrock
            if provider_name == "AWS Bedrock":
                model_id = settings.get("MODEL", "")
                # Check if it's an embedding or image model
                if any(keyword in model_id.lower() for keyword in [
                    "embed", "embedding", "image", "stable-diffusion", 
                    "titan-image", "nova-canvas", "nova-reel", "nova-sonic"
                ]):
                    error_msg = (
                        f"Error: '{model_id}' is not a text generation model.\n\n"
                        "You've selected an embedding or image model which cannot generate text.\n\n"
                        "Please select a text generation model such as:\n"
                        "• amazon.nova-pro-v1:0\n"
                        "• anthropic.claude-3-5-sonnet-20241022-v2:0\n"
                        "• meta.llama3-1-70b-instruct-v1:0\n"
                        "• mistral.mistral-large-2402-v1:0\n\n"
                        "Use the 'Refresh Models' button to get an updated list of text generation models."
                    )
                    self.logger.error(error_msg)
                    self.app.after(0, self.app.update_output_text, error_msg)
                    return
            
            url, payload, headers = self._build_api_request(provider_name, api_key, prompt, settings)
            
            self.logger.debug(f"{provider_name} payload: {json.dumps(payload, indent=2)}")
            
            # Retry logic with exponential backoff
            max_retries = 5
            base_delay = 1
            
            for i in range(max_retries):
                try:
                    response = requests.post(url, json=payload, headers=headers, timeout=60)
                    response.raise_for_status()
                    
                    data = response.json()
                    self.logger.debug(f"{provider_name} Response: {data}")
                    
                    result_text = self._extract_response_text(provider_name, data)
                    self.logger.debug(f"FINAL: About to display result_text: {str(result_text)[:100]}...")
                    self.app.after(0, self.app.update_output_text, result_text)
                    return
                    
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429 and i < max_retries - 1:
                        delay = base_delay * (2 ** i) + random.uniform(0, 1)
                        self.logger.warning(f"Rate limit exceeded. Retrying in {delay:.2f} seconds...")
                        time.sleep(delay)
                    else:
                        self.logger.error(f"API Request Error: {e}\nResponse: {e.response.text}")
                        self.app.after(0, self.app.update_output_text, f"API Request Error: {e}\nResponse: {e.response.text}")
                        return
                except requests.exceptions.RequestException as e:
                    self.logger.error(f"Network Error: {e}")
                    self.app.after(0, self.app.update_output_text, f"Network Error: {e}")
                    return
                except (KeyError, IndexError, json.JSONDecodeError) as e:
                    self.logger.error(f"Error parsing AI response: {e}\n\nResponse:\n{response.text if 'response' in locals() else 'N/A'}")
                    self.app.after(0, self.app.update_output_text, f"Error parsing AI response: {e}\n\nResponse:\n{response.text if 'response' in locals() else 'N/A'}")
                    return
            
            self.app.after(0, self.app.update_output_text, "Error: Max retries exceeded. The API is still busy.")
            
        except Exception as e:
            self.logger.error(f"Error configuring API for {provider_name}: {e}")
            self.app.after(0, self.app.update_output_text, f"Error configuring API request: {e}")
    
    def _build_api_request(self, provider_name, api_key, prompt, settings):
        """Build API request URL, payload, and headers."""
        provider_config = self.ai_providers[provider_name]
        
        # Build URL
        if provider_name == "LM Studio":
            base_url = settings.get("BASE_URL", "http://127.0.0.1:1234").rstrip('/')
            url = provider_config["url_template"].format(base_url=base_url)
        elif provider_name == "AWS Bedrock":
            region = settings.get("AWS_REGION", "us-west-2")
            model_id = settings.get("MODEL", "meta.llama3-1-70b-instruct-v1:0")
            
            # Some models require inference profiles instead of direct model IDs
            inference_profile_mapping = {
                "anthropic.claude-3-5-haiku-20241022-v1:0": "us.anthropic.claude-3-5-haiku-20241022-v1:0",
                "anthropic.claude-3-5-sonnet-20241022-v2:0": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
                "anthropic.claude-3-opus-20240229-v1:0": "us.anthropic.claude-3-opus-20240229-v1:0",
                "anthropic.claude-3-sonnet-20240229-v1:0": "us.anthropic.claude-3-sonnet-20240229-v1:0",
                "anthropic.claude-3-haiku-20240307-v1:0": "us.anthropic.claude-3-haiku-20240307-v1:0"
            }
            
            # Use inference profile if available, otherwise use direct model ID
            final_model_id = inference_profile_mapping.get(model_id, model_id)
            url = provider_config["url"].format(region=region, model=final_model_id)
        elif "url_template" in provider_config:
            url = provider_config["url_template"].format(model=settings.get("MODEL"), api_key=api_key)
        else:
            url = provider_config["url"]
        
        # Build payload first (needed for AWS signing)
        payload = self._build_payload(provider_name, prompt, settings)
        
        # Build headers
        headers = {}
        for key, value in provider_config["headers_template"].items():
            if provider_name in ["LM Studio", "AWS Bedrock"]:
                # LM Studio and AWS Bedrock don't need API key in headers
                headers[key] = value
            else:
                headers[key] = value.format(api_key=api_key)
        
        # AWS Bedrock authentication - following Roo Code's approach
        if provider_name == "AWS Bedrock":
            auth_method = settings.get("AUTH_METHOD", "api_key")
            region = settings.get("AWS_REGION", "us-west-2")
            
            # Handle both display names and internal values for backward compatibility
            is_api_key_auth = auth_method in ["api_key", "API Key (Bearer Token)"]
            is_iam_auth = auth_method in ["iam", "IAM (Explicit Credentials)"]
            is_session_token_auth = auth_method in ["sessionToken", "Session Token (Temporary Credentials)"]
            is_iam_role_auth = auth_method in ["iam_role", "IAM (Implied Credentials)"]
            
            # Based on Roo Code's implementation, they support API key authentication
            # Let's add that back and use Bearer token format like they do
            if is_api_key_auth:
                # Use API key/token-based authentication (Roo Code style)
                api_key_value = self.get_api_key_for_provider(provider_name, settings)
                self.logger.debug(f"AWS Bedrock API Key auth: key length = {len(api_key_value) if api_key_value else 0}")
                headers.update({
                    "Authorization": f"Bearer {api_key_value}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                })
            elif is_iam_auth or is_session_token_auth:
                # Use AWS SigV4 authentication
                access_key = self.get_aws_credential(settings, "AWS_ACCESS_KEY_ID")
                secret_key = self.get_aws_credential(settings, "AWS_SECRET_ACCESS_KEY")
                session_token = self.get_aws_credential(settings, "AWS_SESSION_TOKEN") if is_session_token_auth else None
                
                if access_key and secret_key:
                    payload_str = json.dumps(payload)
                    signed_headers = self.sign_aws_request(
                        "POST", url, payload_str, access_key, secret_key, 
                        session_token, region, "bedrock-runtime"
                    )
                    headers.update(signed_headers)
            elif is_iam_role_auth:
                # For IAM role, we would need to use boto3 or assume role
                # For now, add basic headers (this won't work without proper IAM role setup)
                headers.update({
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                })
        
        return url, payload, headers
    
    def _build_payload(self, provider_name, prompt, settings):
        """Build API payload for the specific provider."""
        payload = {}
        
        if provider_name == "Google AI":
            system_prompt = settings.get("system_prompt", "").strip()
            full_prompt = f"{system_prompt}\n\n{prompt}".strip() if system_prompt else prompt
            payload = {"contents": [{"parts": [{"text": full_prompt}], "role": "user"}]}
            
            gen_config = {}
            self._add_param_if_valid(gen_config, settings, 'temperature', float)
            self._add_param_if_valid(gen_config, settings, 'topP', float)
            self._add_param_if_valid(gen_config, settings, 'topK', int)
            self._add_param_if_valid(gen_config, settings, 'maxOutputTokens', int)
            self._add_param_if_valid(gen_config, settings, 'candidateCount', int)
            
            stop_seq_str = str(settings.get('stopSequences', '')).strip()
            if stop_seq_str:
                gen_config['stopSequences'] = [s.strip() for s in stop_seq_str.split(',')]
            
            if gen_config:
                payload['generationConfig'] = gen_config
        
        elif provider_name == "Anthropic AI":
            payload = {"model": settings.get("MODEL"), "messages": [{"role": "user", "content": prompt}]}
            if settings.get("system"):
                payload["system"] = settings.get("system")
            
            self._add_param_if_valid(payload, settings, 'max_tokens', int)
            self._add_param_if_valid(payload, settings, 'temperature', float)
            self._add_param_if_valid(payload, settings, 'top_p', float)
            self._add_param_if_valid(payload, settings, 'top_k', int)
            
            stop_seq_str = str(settings.get('stop_sequences', '')).strip()
            if stop_seq_str:
                payload['stop_sequences'] = [s.strip() for s in stop_seq_str.split(',')]
        
        elif provider_name == "Cohere AI":
            payload = {"model": settings.get("MODEL"), "message": prompt}
            if settings.get("preamble"):
                payload["preamble"] = settings.get("preamble")
            
            self._add_param_if_valid(payload, settings, 'temperature', float)
            self._add_param_if_valid(payload, settings, 'p', float)
            self._add_param_if_valid(payload, settings, 'k', int)
            self._add_param_if_valid(payload, settings, 'max_tokens', int)
            self._add_param_if_valid(payload, settings, 'frequency_penalty', float)
            self._add_param_if_valid(payload, settings, 'presence_penalty', float)
            
            if settings.get('citation_quality'):
                payload['citation_quality'] = settings['citation_quality']
            
            stop_seq_str = str(settings.get('stop_sequences', '')).strip()
            if stop_seq_str:
                payload['stop_sequences'] = [s.strip() for s in stop_seq_str.split(',')]
        
        elif provider_name in ["OpenAI", "Groq AI", "OpenRouterAI", "LM Studio"]:
            payload = {"model": settings.get("MODEL"), "messages": []}
            system_prompt = settings.get("system_prompt", "").strip()
            if system_prompt:
                payload["messages"].append({"role": "system", "content": system_prompt})
            payload["messages"].append({"role": "user", "content": prompt})
            
            # LM Studio specific parameters
            if provider_name == "LM Studio":
                max_tokens = settings.get("MAX_TOKENS", "2048")
                if max_tokens:
                    try:
                        payload["max_tokens"] = int(max_tokens)
                    except ValueError:
                        pass
            else:
                # Standard OpenAI-compatible parameters
                self._add_param_if_valid(payload, settings, 'temperature', float)
                self._add_param_if_valid(payload, settings, 'top_p', float)
                self._add_param_if_valid(payload, settings, 'max_tokens', int)
                self._add_param_if_valid(payload, settings, 'frequency_penalty', float)
                self._add_param_if_valid(payload, settings, 'presence_penalty', float)
                self._add_param_if_valid(payload, settings, 'seed', int)
                
                stop_str = str(settings.get('stop', '')).strip()
                if stop_str:
                    payload['stop'] = [s.strip() for s in stop_str.split(',')]
                
                if settings.get("response_format") == "json_object":
                    payload["response_format"] = {"type": "json_object"}
                
                # OpenRouter specific parameters
                if provider_name == "OpenRouterAI":
                    self._add_param_if_valid(payload, settings, 'top_k', int)
                    self._add_param_if_valid(payload, settings, 'repetition_penalty', float)
        
        elif provider_name == "AWS Bedrock":
            # AWS Bedrock payload structure varies by model
            model_id = settings.get("MODEL", "meta.llama3-1-70b-instruct-v1:0")
            system_prompt = settings.get("system_prompt", "").strip()
            
            if "anthropic.claude" in model_id:
                # Anthropic Claude models
                payload = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "messages": [{"role": "user", "content": prompt}]
                }
                if system_prompt:
                    payload["system"] = system_prompt
                
                max_tokens = settings.get("MAX_OUTPUT_TOKENS", "4096")
                try:
                    payload["max_tokens"] = int(max_tokens)
                except ValueError:
                    payload["max_tokens"] = 4096
                    
            elif "amazon.nova" in model_id:
                # Amazon Nova models (use messages format but different parameter structure)
                payload = {
                    "messages": [{"role": "user", "content": [{"text": prompt}]}]
                }
                if system_prompt:
                    # Nova models expect system as an array of objects, not a string
                    payload["system"] = [{"text": system_prompt}]
                
                # Nova models use inferenceConfig instead of max_tokens
                max_tokens = settings.get("MAX_OUTPUT_TOKENS", "4096")
                try:
                    payload["inferenceConfig"] = {
                        "maxTokens": int(max_tokens)
                    }
                except ValueError:
                    payload["inferenceConfig"] = {
                        "maxTokens": 4096
                    }
                    
            elif "meta.llama" in model_id:
                # Meta Llama models
                full_prompt = f"{system_prompt}\n\nHuman: {prompt}\n\nAssistant:" if system_prompt else f"Human: {prompt}\n\nAssistant:"
                payload = {
                    "prompt": full_prompt,
                    "max_gen_len": int(settings.get("MAX_OUTPUT_TOKENS", "4096")),
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            elif "amazon.titan" in model_id:
                # Amazon Titan models
                payload = {
                    "inputText": f"{system_prompt}\n\n{prompt}" if system_prompt else prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": int(settings.get("MAX_OUTPUT_TOKENS", "4096")),
                        "temperature": 0.7,
                        "topP": 0.9
                    }
                }
            else:
                # Default structure for other models
                payload = {
                    "prompt": f"{system_prompt}\n\n{prompt}" if system_prompt else prompt,
                    "max_tokens": int(settings.get("MAX_OUTPUT_TOKENS", "4096"))
                }
        
        return payload
    
    def _add_param_if_valid(self, param_dict, settings, key, param_type):
        """Add parameter to dict if it's valid."""
        val_str = str(settings.get(key, '')).strip()
        if val_str:
            try:
                converted_val = param_type(val_str)
                if converted_val:  # Excludes empty strings, 0, and 0.0
                    param_dict[key] = converted_val
            except (ValueError, TypeError):
                self.logger.warning(f"Could not convert {key} value '{val_str}' to {param_type}")
    
    def _extract_response_text(self, provider_name, data):
        """Extract response text from API response."""
        result_text = f"Error: Could not parse response from {provider_name}."
        
        if provider_name == "Google AI":
            result_text = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', result_text)
        elif provider_name == "Anthropic AI":
            result_text = data.get('content', [{}])[0].get('text', result_text)
        elif provider_name in ["OpenAI", "Groq AI", "OpenRouterAI", "LM Studio"]:
            result_text = data.get('choices', [{}])[0].get('message', {}).get('content', result_text)
        elif provider_name == "Cohere AI":
            result_text = data.get('text', result_text)
        elif provider_name == "AWS Bedrock":
            # Extract response based on model type
            self.logger.debug(f"AWS Bedrock response data: {data}")
            
            try:
                # Handle Nova format with output wrapper
                if 'output' in data and 'message' in data['output'] and 'content' in data['output']['message']:
                    # Amazon Nova format with output wrapper: {'output': {'message': {'content': [{'text': '...'}], 'role': 'assistant'}}}
                    self.logger.debug("Found Nova message format with output wrapper")
                    message_data = data['output']['message']
                    self.logger.debug(f"Message content type: {type(message_data['content'])}")
                    self.logger.debug(f"Message content: {message_data['content']}")
                    
                    if isinstance(message_data['content'], list) and len(message_data['content']) > 0:
                        first_content = message_data['content'][0]
                        self.logger.debug(f"First content item: {first_content}")
                        self.logger.debug(f"First content type: {type(first_content)}")
                        
                        if isinstance(first_content, dict) and 'text' in first_content:
                            extracted_text = first_content['text']
                            self.logger.debug(f"Extracted text: '{extracted_text}'")
                            if extracted_text:
                                result_text = extracted_text
                                self.logger.debug(f"SUCCESS: Set result_text to Nova response")
                            else:
                                self.logger.debug("Text field was empty")
                                result_text = "Error: Nova response text field was empty"
                        else:
                            self.logger.debug(f"First content item doesn't have text field: {first_content}")
                            result_text = str(first_content)
                    else:
                        self.logger.debug(f"Content is not a list or is empty: {message_data['content']}")
                        result_text = str(message_data['content'])
                elif 'message' in data and 'content' in data['message']:
                    # Amazon Nova format: {'message': {'content': [{'text': '...'}], 'role': 'assistant'}}
                    self.logger.debug("Found Nova message format")
                    if isinstance(data['message']['content'], list) and len(data['message']['content']) > 0:
                        extracted_text = data['message']['content'][0].get('text', '')
                        if extracted_text:
                            result_text = extracted_text
                            self.logger.debug(f"Successfully extracted Nova text: {result_text[:100]}...")
                        else:
                            self.logger.debug("Nova text field was empty")
                    else:
                        result_text = str(data['message']['content'])
                        self.logger.debug(f"Nova content as string: {result_text}")
                elif 'content' in data and isinstance(data['content'], list) and len(data['content']) > 0:
                    # Anthropic Claude format
                    self.logger.debug("Using Claude content format")
                    result_text = data['content'][0].get('text', result_text)
                elif 'generation' in data:
                    # Meta Llama format
                    result_text = data['generation']
                elif 'results' in data and len(data['results']) > 0:
                    # Amazon Titan format
                    result_text = data['results'][0].get('outputText', result_text)
                elif 'completions' in data and len(data['completions']) > 0:
                    # Other model formats
                    result_text = data['completions'][0].get('data', {}).get('text', result_text)
                else:
                    # Fallback - try to find text in common locations
                    self.logger.debug("Using fallback format - no recognized structure")
                    result_text = data.get('text', data.get('output', str(data)))
            except Exception as e:
                self.logger.error(f"Error extracting AWS Bedrock response: {e}")
                result_text = str(data)
        
        return result_text
    
    def open_model_editor(self, provider_name):
        """Opens a Toplevel window to edit the model list for an AI provider."""
        dialog = tk.Toplevel(self.app)
        dialog.title(f"Edit {provider_name} Models")
        
        self.app.update_idletasks()
        dialog_width = 400
        dialog_height = 200
        main_x, main_y, main_width, main_height = self.app.winfo_x(), self.app.winfo_y(), self.app.winfo_width(), self.app.winfo_height()
        pos_x = main_x + (main_width // 2) - (dialog_width // 2)
        pos_y = main_y + (main_height // 2) - (dialog_height // 2)
        dialog.geometry(f"{dialog_width}x{dialog_height}+{pos_x}+{pos_y}")
        dialog.transient(self.app)
        dialog.grab_set()

        ttk.Label(dialog, text="One model per line. The first line is the default.").pack(pady=(10, 2))
        
        text_area = tk.Text(dialog, height=7, width=45, undo=True)
        text_area.pack(pady=5, padx=10)
        
        current_models = self.app.settings["tool_settings"].get(provider_name, {}).get("MODELS_LIST", [])
        text_area.insert("1.0", "\n".join(current_models))
        
        save_button = ttk.Button(dialog, text="Save Changes", 
                               command=lambda: self.save_model_list(provider_name, text_area, dialog))
        save_button.pack(pady=5)

    def save_model_list(self, provider_name, text_area, dialog):
        """Saves the edited model list back to settings."""
        content = text_area.get("1.0", tk.END)
        new_list = [line.strip() for line in content.splitlines() if line.strip()]
        
        if not new_list:
            self._show_warning("No Models", "Model list cannot be empty.")
            return
            
        self.app.settings["tool_settings"][provider_name]["MODELS_LIST"] = new_list
        self.app.settings["tool_settings"][provider_name]["MODEL"] = new_list[0]
        
        # Update the combobox values
        if provider_name in self.ai_widgets and "MODEL" in self.ai_widgets[provider_name]:
            # Find the combobox widget and update its values
            for provider, tab_frame in self.tabs.items():
                if provider == provider_name:
                    # Update the model variable and refresh the UI
                    self.ai_widgets[provider_name]["MODEL"].set(new_list[0])
                    # We need to recreate the provider widgets to update the combobox values
                    for widget in tab_frame.winfo_children():
                        widget.destroy()
                    self.create_provider_widgets(tab_frame, provider_name)
                    break
        
        self.app.save_settings()
        dialog.destroy()

    def _get_ai_params_config(self, provider_name):
        """Get parameter configuration for AI provider."""
        configs = {
            "Google AI": {
                "temperature": {"tab": "sampling", "type": "scale", "range": (0.0, 2.0), "res": 0.1, "tip": "Controls randomness. Higher is more creative."},
                "topP": {"tab": "sampling", "type": "scale", "range": (0.0, 1.0), "res": 0.05, "tip": "Cumulative probability threshold for token selection."},
                "topK": {"tab": "sampling", "type": "scale", "range": (1, 100), "res": 1, "tip": "Limits token selection to top K candidates."},
                "maxOutputTokens": {"tab": "content", "type": "entry", "tip": "Maximum number of tokens to generate."},
                "candidateCount": {"tab": "content", "type": "scale", "range": (1, 8), "res": 1, "tip": "Number of response candidates to generate."},
                "stopSequences": {"tab": "content", "type": "entry", "tip": "Comma-separated list of strings to stop generation."}
            },
            "Anthropic AI": {
                "max_tokens": {"tab": "content", "type": "entry", "tip": "Maximum number of tokens to generate."},
                "temperature": {"tab": "sampling", "type": "scale", "range": (0.0, 1.0), "res": 0.1, "tip": "Controls randomness. Higher is more creative."},
                "top_p": {"tab": "sampling", "type": "scale", "range": (0.0, 1.0), "res": 0.05, "tip": "Cumulative probability threshold for token selection."},
                "top_k": {"tab": "sampling", "type": "scale", "range": (1, 200), "res": 1, "tip": "Limits token selection to top K candidates."},
                "stop_sequences": {"tab": "content", "type": "entry", "tip": "Comma-separated list of strings to stop generation."}
            },
            "OpenAI": {
                "max_tokens": {"tab": "content", "type": "entry", "tip": "Maximum number of tokens to generate."},
                "temperature": {"tab": "sampling", "type": "scale", "range": (0.0, 2.0), "res": 0.1, "tip": "Controls randomness. Higher is more creative."},
                "top_p": {"tab": "sampling", "type": "scale", "range": (0.0, 1.0), "res": 0.05, "tip": "Nucleus sampling threshold."},
                "frequency_penalty": {"tab": "sampling", "type": "scale", "range": (-2.0, 2.0), "res": 0.1, "tip": "Penalizes frequent tokens."},
                "presence_penalty": {"tab": "sampling", "type": "scale", "range": (-2.0, 2.0), "res": 0.1, "tip": "Penalizes tokens that have appeared."},
                "seed": {"tab": "content", "type": "entry", "tip": "Random seed for reproducible outputs."},
                "stop": {"tab": "content", "type": "entry", "tip": "Comma-separated list of strings to stop generation."},
                "response_format": {"tab": "content", "type": "combo", "values": ["text", "json_object"], "tip": "Force JSON output."}
            },
            "Cohere AI": {
                "max_tokens": {"tab": "content", "type": "entry", "tip": "Maximum number of tokens to generate."},
                "temperature": {"tab": "sampling", "type": "scale", "range": (0.0, 1.0), "res": 0.1, "tip": "Controls randomness. Higher is more creative."},
                "p": {"tab": "sampling", "type": "scale", "range": (0.0, 1.0), "res": 0.05, "tip": "Top-p/nucleus sampling threshold."},
                "k": {"tab": "sampling", "type": "scale", "range": (1, 500), "res": 1, "tip": "Top-k sampling threshold."},
                "frequency_penalty": {"tab": "sampling", "type": "scale", "range": (0.0, 1.0), "res": 0.1, "tip": "Penalizes frequent tokens."},
                "presence_penalty": {"tab": "sampling", "type": "scale", "range": (0.0, 1.0), "res": 0.1, "tip": "Penalizes tokens that have appeared."},
                "stop_sequences": {"tab": "content", "type": "entry", "tip": "Comma-separated list of strings to stop generation."},
                "citation_quality": {"tab": "content", "type": "combo", "values": ["accurate", "fast"], "tip": "Citation quality vs. speed."}
            },
            "HuggingFace AI": {
                "max_tokens": {"tab": "content", "type": "entry", "tip": "Maximum number of tokens to generate."},
                "temperature": {"tab": "sampling", "type": "scale", "range": (0.0, 2.0), "res": 0.1, "tip": "Controls randomness. Higher is more creative."},
                "top_p": {"tab": "sampling", "type": "scale", "range": (0.0, 1.0), "res": 0.05, "tip": "Nucleus sampling threshold."},
                "seed": {"tab": "content", "type": "entry", "tip": "Random seed for reproducible outputs."},
                "stop_sequences": {"tab": "content", "type": "entry", "tip": "Comma-separated list of strings to stop generation."}
            },
            "Groq AI": {
                "max_tokens": {"tab": "content", "type": "entry", "tip": "Maximum number of tokens to generate."},
                "temperature": {"tab": "sampling", "type": "scale", "range": (0.0, 2.0), "res": 0.1, "tip": "Controls randomness. Higher is more creative."},
                "top_p": {"tab": "sampling", "type": "scale", "range": (0.0, 1.0), "res": 0.05, "tip": "Nucleus sampling threshold."},
                "frequency_penalty": {"tab": "sampling", "type": "scale", "range": (-2.0, 2.0), "res": 0.1, "tip": "Penalizes frequent tokens."},
                "presence_penalty": {"tab": "sampling", "type": "scale", "range": (-2.0, 2.0), "res": 0.1, "tip": "Penalizes tokens that have appeared."},
                "seed": {"tab": "content", "type": "entry", "tip": "Random seed for reproducible outputs."},
                "stop": {"tab": "content", "type": "entry", "tip": "Comma-separated list of strings to stop generation."},
                "response_format": {"tab": "content", "type": "combo", "values": ["text", "json_object"], "tip": "Force JSON output."}
            },
            "OpenRouterAI": {
                "max_tokens": {"tab": "content", "type": "entry", "tip": "Maximum number of tokens to generate."},
                "temperature": {"tab": "sampling", "type": "scale", "range": (0.0, 2.0), "res": 0.1, "tip": "Controls randomness. Higher is more creative."},
                "top_p": {"tab": "sampling", "type": "scale", "range": (0.0, 1.0), "res": 0.05, "tip": "Nucleus sampling threshold."},
                "top_k": {"tab": "sampling", "type": "scale", "range": (1, 100), "res": 1, "tip": "Limits token selection to top K candidates."},
                "frequency_penalty": {"tab": "sampling", "type": "scale", "range": (-2.0, 2.0), "res": 0.1, "tip": "Penalizes frequent tokens."},
                "presence_penalty": {"tab": "sampling", "type": "scale", "range": (-2.0, 2.0), "res": 0.1, "tip": "Penalizes tokens that have appeared."},
                "repetition_penalty": {"tab": "sampling", "type": "scale", "range": (0.0, 2.0), "res": 0.1, "tip": "Penalizes repetitive text."},
                "seed": {"tab": "content", "type": "entry", "tip": "Random seed for reproducible outputs."},
                "stop": {"tab": "content", "type": "entry", "tip": "Comma-separated list of strings to stop generation."}
            }
        }
        
        return configs.get(provider_name, {})