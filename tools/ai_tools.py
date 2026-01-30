import tkinter as tk
from tkinter import ttk, messagebox, filedialog
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
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False

try:
    from huggingface_hub import InferenceClient
    from huggingface_hub.utils import HfHubHTTPError
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False

try:
    from tools.huggingface_helper import process_huggingface_request
    HUGGINGFACE_HELPER_AVAILABLE = True
except ImportError:
    HUGGINGFACE_HELPER_AVAILABLE = False

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False

try:
    from core.streaming_text_handler import (
        StreamingTextHandler,
        StreamingTextManager,
        StreamConfig,
        StreamMetrics
    )
    STREAMING_AVAILABLE = True
except ImportError:
    STREAMING_AVAILABLE = False

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
            "Vertex AI": {
                "url_template": "https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model}:generateContent",
                "headers_template": {'Content-Type': 'application/json', 'Authorization': 'Bearer {access_token}'},
                "api_url": "https://cloud.google.com/vertex-ai/docs/authentication"
            },
            "Azure AI": {
                "url_template": "{endpoint}/models/chat/completions?api-version={api_version}",  # Used for Foundry; Azure OpenAI uses /openai/deployments/{model}/...
                "headers_template": {'Content-Type': 'application/json', 'api-key': '{api_key}'},
                "api_url": "https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-models/how-to/quickstart-ai-project"
            },
            "Anthropic AI": {
                "url": "https://api.anthropic.com/v1/messages",
                "headers_template": {"x-api-key": "{api_key}", "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
                "api_url": "https://console.anthropic.com/settings/keys"
            },
            "OpenAI": {
                "url": "https://api.openai.com/v1/chat/completions",
                "url_responses": "https://api.openai.com/v1/responses",  # For GPT-5.2 models
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
                "headers_template": {
                    "Authorization": "Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/matbanik/Pomera-AI-Commander",
                    "X-Title": "Pomera AI Commander"
                },
                "api_url": "https://openrouter.ai/settings/keys"
            },
            "LM Studio": {
                "url_template": "{base_url}/v1/chat/completions",
                "headers_template": {"Content-Type": "application/json"},
                "api_url": "http://lmstudio.ai/",
                "local_service": True
            },
            "AWS Bedrock": {
                # Using Converse API (recommended) - provides unified interface across all models
                "url": "https://bedrock-runtime.{region}.amazonaws.com/model/{model}/converse",
                "url_invoke": "https://bedrock-runtime.{region}.amazonaws.com/model/{model}/invoke",  # Fallback for legacy
                "headers_template": {"Content-Type": "application/json", "Accept": "application/json"},
                "api_url": "https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html",
                "aws_service": True
            }
        }
        
        self.current_provider = "Google AI"
        self.ai_widgets = {}
        self._ai_thread = None
        
        # Streaming support - enabled by default when available
        self._streaming_enabled = STREAMING_AVAILABLE
        self._streaming_handler = None
        self._streaming_manager = None
        
        self.create_widgets()
        
        # Show encryption status in logs
        if ENCRYPTION_AVAILABLE:
            self.logger.info("API Key encryption is ENABLED - keys will be encrypted at rest")
        else:
            self.logger.warning("API Key encryption is DISABLED - cryptography library not found. Install with: pip install cryptography")
        
        # Show streaming status in logs
        if STREAMING_AVAILABLE:
            self.logger.info("Streaming text handler is ENABLED - AI responses will be streamed progressively")
        else:
            self.logger.warning("Streaming text handler is NOT AVAILABLE - AI responses will be displayed at once")
    
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
    
    def upload_vertex_ai_json(self, provider_name):
        """Upload and parse Vertex AI service account JSON file."""
        try:
            file_path = filedialog.askopenfilename(
                title="Select Vertex AI Service Account JSON File",
                filetypes=[
                    ("JSON files", "*.json"),
                    ("All files", "*.*")
                ]
            )
            
            if not file_path:
                return
            
            # Read and parse JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Validate required fields
            required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 
                             'client_email', 'client_id', 'auth_uri', 'token_uri']
            missing_fields = [field for field in required_fields if field not in json_data]
            
            if missing_fields:
                self._show_error("Invalid JSON File", 
                               f"Missing required fields: {', '.join(missing_fields)}")
                return
            
            # Encrypt private_key
            encrypted_private_key = encrypt_api_key(json_data['private_key'])
            
            # Store in database
            if hasattr(self.app, 'db_settings_manager') and self.app.db_settings_manager:
                conn_manager = self.app.db_settings_manager.connection_manager
                with conn_manager.transaction() as conn:
                    # Delete existing record (singleton pattern)
                    conn.execute("DELETE FROM vertex_ai_json")
                    
                    # Insert new record
                    conn.execute("""
                        INSERT INTO vertex_ai_json (
                            type, project_id, private_key_id, private_key,
                            client_email, client_id, auth_uri, token_uri,
                            auth_provider_x509_cert_url, client_x509_cert_url, universe_domain
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        json_data.get('type', ''),
                        json_data.get('project_id', ''),
                        json_data.get('private_key_id', ''),
                        encrypted_private_key,
                        json_data.get('client_email', ''),
                        json_data.get('client_id', ''),
                        json_data.get('auth_uri', ''),
                        json_data.get('token_uri', ''),
                        json_data.get('auth_provider_x509_cert_url'),
                        json_data.get('client_x509_cert_url'),
                        json_data.get('universe_domain')
                    ))
                
                # Update location setting if not already set (default to us-central1)
                settings = self.get_current_settings()
                if not settings.get("LOCATION"):
                    self.app.db_settings_manager.set_tool_setting(provider_name, "LOCATION", "us-central1")
                
                # Update project_id in tool_settings if not already set
                if not settings.get("PROJECT_ID"):
                    self.app.db_settings_manager.set_tool_setting(provider_name, "PROJECT_ID", json_data.get('project_id', ''))
                
                self._show_info("Success", "Vertex AI service account JSON uploaded and stored successfully.")
                self.logger.info(f"Vertex AI JSON uploaded: project_id={json_data.get('project_id')}")
                
                # Update status label if widget exists
                if provider_name in self.ai_widgets and "JSON_STATUS" in self.ai_widgets[provider_name]:
                    status_label = self.ai_widgets[provider_name]["JSON_STATUS"]
                    status_label.config(text=f"✓ Loaded: {json_data.get('project_id', 'Unknown')}", foreground="green")
            else:
                self._show_error("Error", "Database settings manager not available")
                
        except json.JSONDecodeError as e:
            self._show_error("Invalid JSON", f"The file is not valid JSON: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error uploading Vertex AI JSON: {e}", exc_info=True)
            self._show_error("Error", f"Failed to upload JSON file: {str(e)}")
    
    def get_vertex_ai_credentials(self):
        """Get Vertex AI service account credentials from database."""
        try:
            if not hasattr(self.app, 'db_settings_manager') or not self.app.db_settings_manager:
                return None
            
            conn_manager = self.app.db_settings_manager.connection_manager
            with conn_manager.transaction() as conn:
                cursor = conn.execute("""
                    SELECT type, project_id, private_key_id, private_key,
                           client_email, client_id, auth_uri, token_uri,
                           auth_provider_x509_cert_url, client_x509_cert_url, universe_domain
                    FROM vertex_ai_json
                    ORDER BY updated_at DESC
                    LIMIT 1
                """)
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                # Decrypt private_key
                decrypted_private_key = decrypt_api_key(row[3])
                
                # Reconstruct JSON structure
                credentials_dict = {
                    'type': row[0],
                    'project_id': row[1],
                    'private_key_id': row[2],
                    'private_key': decrypted_private_key,
                    'client_email': row[4],
                    'client_id': row[5],
                    'auth_uri': row[6],
                    'token_uri': row[7],
                    'auth_provider_x509_cert_url': row[8],
                    'client_x509_cert_url': row[9],
                    'universe_domain': row[10]
                }
                
                return credentials_dict
                
        except Exception as e:
            self.logger.error(f"Error getting Vertex AI credentials: {e}", exc_info=True)
            return None
    
    def get_vertex_ai_access_token(self):
        """Get OAuth2 access token for Vertex AI using service account credentials."""
        if not GOOGLE_AUTH_AVAILABLE:
            self.logger.error("google-auth library not available")
            return None
        
        try:
            credentials_dict = self.get_vertex_ai_credentials()
            if not credentials_dict:
                self.logger.warning("No Vertex AI credentials found in database")
                return None
            
            # Create credentials from service account info
            credentials = service_account.Credentials.from_service_account_info(
                credentials_dict,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            
            # Refresh token if needed
            if not credentials.valid:
                request = Request()
                credentials.refresh(request)
            
            # Get access token
            access_token = credentials.token
            self.logger.debug("Vertex AI access token obtained successfully")
            
            return access_token
            
        except Exception as e:
            self.logger.error(f"Error getting Vertex AI access token: {e}", exc_info=True)
            return None
    
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
            
            # Ensure AWS Bedrock fields are properly visible when switching to that tab
            if self.current_provider == "AWS Bedrock":
                self.after_idle(lambda: self.update_aws_credentials_fields(self.current_provider))
            
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
            
            auth_method_var = tk.StringVar(value=settings.get("AUTH_METHOD", "api_key"))
            auth_combo = ttk.Combobox(aws_frame, textvariable=auth_method_var, 
                                    values=[
                                        "API Key (Bearer Token)",
                                        "IAM (Explicit Credentials)", 
                                        "Session Token (Temporary Credentials)",
                                        "IAM (Implied Credentials)"
                                    ], 
                                    state="readonly", width=30)
            
            # Set the display value based on stored value
            stored_auth = settings.get("AUTH_METHOD", "api_key")  # Default to api_key for consistency
            
            # Ensure the AUTH_METHOD is saved in settings if not present
            if "AUTH_METHOD" not in settings:
                if provider_name not in self.app.settings["tool_settings"]:
                    self.app.settings["tool_settings"][provider_name] = {}
                self.app.settings["tool_settings"][provider_name]["AUTH_METHOD"] = stored_auth
                self.app.save_settings()
                self.logger.debug(f"Initialized AWS Bedrock AUTH_METHOD to: {stored_auth}")
            
            if stored_auth == "api_key":
                auth_combo.set("API Key (Bearer Token)")
            elif stored_auth == "iam":
                auth_combo.set("IAM (Explicit Credentials)")
            elif stored_auth == "sessionToken":
                auth_combo.set("Session Token (Temporary Credentials)")
            elif stored_auth == "iam_role":
                auth_combo.set("IAM (Implied Credentials)")
            else:
                # Fallback for any unknown values
                auth_combo.set("API Key (Bearer Token)")
                stored_auth = "api_key"
                # Update settings with corrected value
                self.app.settings["tool_settings"][provider_name]["AUTH_METHOD"] = stored_auth
                self.app.save_settings()
            
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
        elif provider_name == "Vertex AI":
            # Vertex AI Configuration section with JSON upload
            encryption_status = "🔒" if ENCRYPTION_AVAILABLE else "⚠️"
            api_frame = ttk.LabelFrame(top_frame, text=f"API Configuration {encryption_status}")
            api_frame.pack(side=tk.LEFT, padx=(0, 10), fill=tk.Y)
            
            ttk.Label(api_frame, text="Service Account:").pack(side=tk.LEFT, padx=(5, 5))
            
            # Upload JSON button for Vertex AI
            ttk.Button(api_frame, text="Upload JSON", 
                      command=lambda: self.upload_vertex_ai_json(provider_name)).pack(side=tk.LEFT, padx=(5, 5))
            
            # Status label to show if JSON is loaded
            status_label = ttk.Label(api_frame, text="", foreground="gray")
            status_label.pack(side=tk.LEFT, padx=(5, 5))
            self.ai_widgets[provider_name]["JSON_STATUS"] = status_label
            
            # Check if credentials exist and update status
            credentials = self.get_vertex_ai_credentials()
            if credentials:
                status_label.config(text=f"✓ Loaded: {credentials.get('project_id', 'Unknown')}", foreground="green")
            else:
                status_label.config(text="No JSON loaded", foreground="red")
            
            # API key link button (docs)
            ttk.Button(api_frame, text="Get API Key", 
                      command=lambda: webbrowser.open(self.ai_providers[provider_name]["api_url"])).pack(side=tk.LEFT, padx=(5, 5))
        elif provider_name == "Azure AI":
            # Azure AI Configuration section
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
            
            # Resource Endpoint field
            endpoint_frame = ttk.LabelFrame(top_frame, text="Endpoint")
            endpoint_frame.pack(side=tk.LEFT, padx=(0, 10), fill=tk.Y)
            
            ttk.Label(endpoint_frame, text="Resource Endpoint:").pack(side=tk.LEFT, padx=(5, 5))
            
            endpoint_var = tk.StringVar(value=settings.get("ENDPOINT", ""))
            endpoint_entry = ttk.Entry(endpoint_frame, textvariable=endpoint_var, width=30)
            endpoint_entry.pack(side=tk.LEFT, padx=(0, 5))
            endpoint_var.trace_add("write", lambda *args: self.on_setting_change(provider_name))
            
            self.ai_widgets[provider_name]["ENDPOINT"] = endpoint_var
            
            # API Version field
            api_version_frame = ttk.LabelFrame(top_frame, text="API Version")
            api_version_frame.pack(side=tk.LEFT, padx=(0, 10), fill=tk.Y)
            
            ttk.Label(api_version_frame, text="API Version:").pack(side=tk.LEFT, padx=(5, 5))
            
            api_version_var = tk.StringVar(value=settings.get("API_VERSION", "2024-10-21"))
            api_version_entry = ttk.Entry(api_version_frame, textvariable=api_version_var, width=15)
            api_version_entry.pack(side=tk.LEFT, padx=(0, 5))
            api_version_var.trace_add("write", lambda *args: self.on_setting_change(provider_name))
            
            self.ai_widgets[provider_name]["API_VERSION"] = api_version_var
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
        
        # Vertex AI Location field (similar to AWS Region)
        if provider_name == "Vertex AI":
            location_frame = ttk.LabelFrame(top_frame, text="Location")
            location_frame.pack(side=tk.LEFT, padx=(0, 10), fill=tk.Y)
            
            ttk.Label(location_frame, text="Location:").pack(side=tk.LEFT, padx=(5, 5))
            
            location_var = tk.StringVar(value=settings.get("LOCATION", "us-central1"))
            vertex_locations = [
                "us-central1", "us-east1", "us-east4", "us-west1", "us-west4",
                "europe-west1", "europe-west4", "europe-west6", "asia-east1",
                "asia-northeast1", "asia-southeast1", "asia-south1"
            ]
            location_combo = ttk.Combobox(location_frame, textvariable=location_var,
                                       values=vertex_locations, state="readonly", width=15)
            location_combo.pack(side=tk.LEFT, padx=(0, 5))
            location_var.trace_add("write", lambda *args: self.on_setting_change(provider_name))
            
            self.ai_widgets[provider_name]["LOCATION"] = location_var
        
        # Model Configuration section
        model_frame = ttk.LabelFrame(top_frame, text="Model Configuration")
        model_frame.pack(side=tk.LEFT, padx=(0, 10), fill=tk.Y)
        
        if provider_name == "Azure AI":
            ttk.Label(model_frame, text="Model (Deployment Name):").pack(side=tk.LEFT, padx=(5, 5))
        else:
            ttk.Label(model_frame, text="Model:").pack(side=tk.LEFT, padx=(5, 5))
        
        # Set default models for Vertex AI if not present
        if provider_name == "Vertex AI":
            models_list = settings.get("MODELS_LIST", [])
            if not models_list:
                models_list = ["gemini-2.5-flash", "gemini-2.5-pro"]
                if hasattr(self.app, 'db_settings_manager') and self.app.db_settings_manager:
                    self.app.db_settings_manager.set_tool_setting(provider_name, "MODELS_LIST", models_list)
                else:
                    if provider_name not in self.app.settings["tool_settings"]:
                        self.app.settings["tool_settings"][provider_name] = {}
                    self.app.settings["tool_settings"][provider_name]["MODELS_LIST"] = models_list
                    self.app.save_settings()
            
            # Set default model if not present
            if not settings.get("MODEL"):
                default_model = "gemini-2.5-flash"
                if hasattr(self.app, 'db_settings_manager') and self.app.db_settings_manager:
                    self.app.db_settings_manager.set_tool_setting(provider_name, "MODEL", default_model)
                else:
                    if provider_name not in self.app.settings["tool_settings"]:
                        self.app.settings["tool_settings"][provider_name] = {}
                    self.app.settings["tool_settings"][provider_name]["MODEL"] = default_model
                    self.app.save_settings()
                settings["MODEL"] = default_model
                settings["MODELS_LIST"] = models_list
        
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
        elif provider_name == "Google AI":
            # Refresh Models button for Google AI (fetches from API)
            ttk.Button(model_frame, text="Refresh", 
                      command=lambda: self.refresh_google_ai_models(provider_name)).pack(side=tk.LEFT, padx=(0, 5))
            # Model edit button
            ttk.Button(model_frame, text="\u270E", 
                      command=lambda: self.open_model_editor(provider_name), width=3).pack(side=tk.LEFT, padx=(0, 5))
        elif provider_name == "OpenRouterAI":
            # Refresh Models button for OpenRouter (fetches from API)
            ttk.Button(model_frame, text="Refresh", 
                      command=lambda: self.refresh_openrouter_models(provider_name)).pack(side=tk.LEFT, padx=(0, 5))
            # Model edit button
            ttk.Button(model_frame, text="\u270E", 
                      command=lambda: self.open_model_editor(provider_name), width=3).pack(side=tk.LEFT, padx=(0, 5))
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
            # Use after_idle to ensure all widgets are created before updating visibility
            self.after_idle(lambda: self.update_aws_credentials_fields(provider_name))
        
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
        
        # Parameters notebook with minimal height to reduce empty space (skip for AWS Bedrock, LM Studio, and Azure AI)
        # Note: Azure AI will use parameters, but we include it here since it uses standard OpenAI-style params
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
            
        elif config["type"] == "checkbox":
            # Convert string values to boolean for checkbox
            if isinstance(current_value, str):
                checkbox_value = current_value.lower() in ('true', '1', 'yes', 'on')
            else:
                checkbox_value = bool(current_value)
            
            var = tk.BooleanVar(value=checkbox_value)
            checkbox = ttk.Checkbutton(parent, variable=var)
            checkbox.grid(row=row, column=1, sticky="w", padx=(0, 10), pady=2)
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
        try:
            # Update settings in parent app
            if provider_name not in self.app.settings["tool_settings"]:
                self.app.settings["tool_settings"][provider_name] = {}
            
            # Collect all widget values first
            updated_settings = {}
            for param, widget in self.ai_widgets[provider_name].items():
                if isinstance(widget, tk.Text):
                    value = widget.get("1.0", tk.END).strip()
                else:
                    value = widget.get()
                
                # Encrypt sensitive credentials before saving (except for LM Studio)
                if provider_name != "LM Studio" and param in ["API_KEY", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"]:
                    if value and value != "putinyourkey":
                        value = encrypt_api_key(value)
                
                updated_settings[param] = value
            
            # Update settings using database manager directly for better reliability
            if hasattr(self.app, 'db_settings_manager') and self.app.db_settings_manager:
                # Use database manager's tool setting method for atomic updates
                for param, value in updated_settings.items():
                    self.app.db_settings_manager.set_tool_setting(provider_name, param, value)
                
                self.logger.info(f"Saved {len(updated_settings)} settings for {provider_name} via database manager")
            else:
                # Fallback to proxy method
                for param, value in updated_settings.items():
                    self.app.settings["tool_settings"][provider_name][param] = value
                
                # Force save
                self.app.save_settings()
                self.logger.info(f"Saved {len(updated_settings)} settings for {provider_name} via proxy")
                
        except Exception as e:
            self.logger.error(f"Failed to save settings for {provider_name}: {e}", exc_info=True)
            # Show user-friendly error
            self._show_info("Error", f"Failed to save {provider_name} settings: {str(e)}", "error")
    
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
    
    def refresh_google_ai_models(self, provider_name):
        """Refresh the model list from Google AI (Gemini) API."""
        if provider_name != "Google AI":
            return
        
        settings = self.get_current_settings()
        api_key = self.get_api_key_for_provider(provider_name, settings)
        
        if not api_key or api_key == "putinyourkey":
            self._show_error("Error", "Please enter a valid Google AI API key first")
            return
        
        try:
            # Google AI models endpoint
            models_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            
            response = requests.get(models_url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            models = []
            
            # Filter for generative models (not embedding models)
            for model in data.get("models", []):
                model_name = model.get("name", "")
                # Remove "models/" prefix
                if model_name.startswith("models/"):
                    model_name = model_name[7:]
                
                # Filter for text generation models (gemini models)
                supported_methods = model.get("supportedGenerationMethods", [])
                if "generateContent" in supported_methods:
                    models.append(model_name)
            
            if models:
                # Sort models (prefer newer versions)
                models.sort(reverse=True)
                
                # Update the model combobox
                if provider_name in self.ai_widgets and "MODEL" in self.ai_widgets[provider_name]:
                    # Find and update the combobox in the tab
                    for provider, tab_frame in self.tabs.items():
                        if provider == provider_name:
                            # Update the model variable and refresh the UI
                            self.ai_widgets[provider_name]["MODEL"].set(models[0] if models else "")
                            for widget in tab_frame.winfo_children():
                                widget.destroy()
                            self.create_provider_widgets(tab_frame, provider_name)
                            break
                
                # Update settings
                self.app.settings["tool_settings"][provider_name]["MODELS_LIST"] = models
                self.app.settings["tool_settings"][provider_name]["MODEL"] = models[0] if models else ""
                self.app.save_settings()
                
                self._show_info("Success", f"Found {len(models)} generative models from Google AI")
            else:
                self._show_warning("Warning", "No generative models found. Check your API key permissions.")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Could not connect to Google AI API\n\nError: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg += f"\n\nDetails: {json.dumps(error_detail, indent=2)}"
                except:
                    error_msg += f"\n\nResponse: {e.response.text}"
            self._show_error("Connection Error", error_msg)
        except Exception as e:
            self._show_error("Error", f"Error refreshing Google AI models: {e}")
    
    def refresh_openrouter_models(self, provider_name):
        """Refresh the model list from OpenRouter API."""
        if provider_name != "OpenRouterAI":
            return
        
        settings = self.get_current_settings()
        api_key = self.get_api_key_for_provider(provider_name, settings)
        
        # OpenRouter models endpoint is public, but API key is recommended
        try:
            headers = {"Content-Type": "application/json"}
            if api_key and api_key != "putinyourkey":
                headers["Authorization"] = f"Bearer {api_key}"
            
            # OpenRouter models endpoint
            models_url = "https://openrouter.ai/api/v1/models"
            
            response = requests.get(models_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            models = []
            
            # Extract model IDs from the response
            for model in data.get("data", []):
                model_id = model.get("id", "")
                if model_id:
                    models.append(model_id)
            
            if models:
                # Sort models alphabetically
                models.sort()
                
                # Update the model combobox
                if provider_name in self.ai_widgets and "MODEL" in self.ai_widgets[provider_name]:
                    # Find and update the combobox in the tab
                    for provider, tab_frame in self.tabs.items():
                        if provider == provider_name:
                            # Update the model variable and refresh the UI
                            current_model = self.ai_widgets[provider_name]["MODEL"].get()
                            if not current_model or current_model not in models:
                                self.ai_widgets[provider_name]["MODEL"].set(models[0] if models else "")
                            for widget in tab_frame.winfo_children():
                                widget.destroy()
                            self.create_provider_widgets(tab_frame, provider_name)
                            break
                
                # Update settings
                self.app.settings["tool_settings"][provider_name]["MODELS_LIST"] = models
                if not self.app.settings["tool_settings"].get(provider_name, {}).get("MODEL"):
                    self.app.settings["tool_settings"][provider_name]["MODEL"] = models[0] if models else ""
                self.app.save_settings()
                
                self._show_info("Success", f"Found {len(models)} models from OpenRouter")
            else:
                self._show_warning("Warning", "No models found from OpenRouter.")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Could not connect to OpenRouter API\n\nError: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg += f"\n\nDetails: {json.dumps(error_detail, indent=2)}"
                except:
                    error_msg += f"\n\nResponse: {e.response.text}"
            self._show_error("Connection Error", error_msg)
        except Exception as e:
            self._show_error("Error", f"Error refreshing OpenRouter models: {e}")
    
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
                # Add inference profile versions for models that require them
                enhanced_models = []
                inference_profile_mapping = {
                    # Claude 4.5 models (newest)
                    "anthropic.claude-haiku-4-5-20251001-v1:0": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    "anthropic.claude-sonnet-4-5-20250929-v1:0": "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
                    
                    # Claude 4.1 models  
                    "anthropic.claude-opus-4-1-20250805-v1:0": "us.anthropic.claude-opus-4-1-20250805-v1:0",
                    
                    # Claude 3.7 models
                    "anthropic.claude-3-7-sonnet-20250219-v1:0": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
                    
                    # Claude 3.5 models (v2)
                    "anthropic.claude-3-5-haiku-20241022-v1:0": "us.anthropic.claude-3-5-haiku-20241022-v1:0",
                    "anthropic.claude-3-5-sonnet-20241022-v2:0": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
                    
                    # Claude 3.5 models (v1)
                    "anthropic.claude-3-5-sonnet-20240620-v1:0": "us.anthropic.claude-3-5-sonnet-20240620-v1:0",
                    
                    # Claude 3 models (original)
                    "anthropic.claude-3-opus-20240229-v1:0": "us.anthropic.claude-3-opus-20240229-v1:0",
                    "anthropic.claude-3-sonnet-20240229-v1:0": "us.anthropic.claude-3-sonnet-20240229-v1:0",
                    "anthropic.claude-3-haiku-20240307-v1:0": "us.anthropic.claude-3-haiku-20240307-v1:0"
                }
                
                for model_id in models:
                    enhanced_models.append(model_id)
                    # If this model has an inference profile, add it as an option too
                    if model_id in inference_profile_mapping:
                        profile_id = inference_profile_mapping[model_id]
                        enhanced_models.append(f"{profile_id} (Inference Profile)")
                
                # Update the model combobox
                model_combo = self.ai_widgets[provider_name].get("MODEL_COMBO")
                if model_combo:
                    model_combo.configure(values=enhanced_models)
                    # Set first model as default if no model is currently selected
                    if enhanced_models and not self.ai_widgets[provider_name]["MODEL"].get():
                        self.ai_widgets[provider_name]["MODEL"].set(enhanced_models[0])
                
                # Update settings (store the enhanced list)
                self.app.settings["tool_settings"][provider_name]["MODELS_LIST"] = enhanced_models
                self.app.save_settings()
                
                profile_count = len([m for m in enhanced_models if "Inference Profile" in m])
                self._show_info("Success", f"Found {len(models)} models from AWS Bedrock ({profile_count} with inference profiles)")
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
            self.logger.debug(f"Skipping AWS credentials field update: provider={provider_name}, has_frame={hasattr(self, 'aws_creds_frame')}")
            return
        
        # Get the stored value from settings
        stored_auth = self.app.settings["tool_settings"].get(provider_name, {}).get("AUTH_METHOD", "api_key")
        self.logger.debug(f"AWS Bedrock auth method: {stored_auth}")
        
        # Hide all credential fields first
        fields_to_hide = ['api_key_row', 'access_key_row', 'secret_key_row', 'session_token_row', 'iam_role_info_frame']
        for field_name in fields_to_hide:
            if hasattr(self, field_name):
                try:
                    getattr(self, field_name).pack_forget()
                except Exception as e:
                    self.logger.debug(f"Error hiding {field_name}: {e}")
        
        # Show fields based on authentication method
        try:
            if stored_auth == "api_key":  # API Key (Bearer Token)
                if hasattr(self, 'api_key_row'):
                    self.api_key_row.pack(fill=tk.X, padx=5, pady=2)
                    self.logger.debug("Showing API key field")
                else:
                    self.logger.warning("API key row not found!")
            elif stored_auth == "iam":  # IAM (Explicit Credentials)
                if hasattr(self, 'access_key_row') and hasattr(self, 'secret_key_row'):
                    self.access_key_row.pack(fill=tk.X, padx=5, pady=2)
                    self.secret_key_row.pack(fill=tk.X, padx=5, pady=2)
                    self.logger.debug("Showing IAM credential fields")
            elif stored_auth == "sessionToken":  # Session Token (Temporary Credentials)
                if hasattr(self, 'access_key_row') and hasattr(self, 'secret_key_row') and hasattr(self, 'session_token_row'):
                    self.access_key_row.pack(fill=tk.X, padx=5, pady=2)
                    self.secret_key_row.pack(fill=tk.X, padx=5, pady=2)
                    self.session_token_row.pack(fill=tk.X, padx=5, pady=2)
                    self.logger.debug("Showing session token credential fields")
            elif stored_auth == "iam_role":  # IAM (Implied Credentials)
                if hasattr(self, 'iam_role_info_frame'):
                    self.iam_role_info_frame.pack(fill=tk.X, padx=5, pady=5)
                    self.logger.debug("Showing IAM role info")
            else:
                self.logger.warning(f"Unknown auth method: {stored_auth}, defaulting to API key")
                if hasattr(self, 'api_key_row'):
                    self.api_key_row.pack(fill=tk.X, padx=5, pady=2)
        except Exception as e:
            self.logger.error(f"Error updating AWS credentials fields: {e}", exc_info=True)
    
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
        
        # Validate Vertex AI credentials
        if provider_name == "Vertex AI":
            credentials = self.get_vertex_ai_credentials()
            if not credentials:
                self.app.after(0, self.app.update_output_text, "Error: Vertex AI requires service account JSON file. Please upload it using the 'Upload JSON' button.")
                return
            project_id = settings.get("PROJECT_ID")
            if not project_id:
                self.app.after(0, self.app.update_output_text, "Error: Project ID not found. Please upload the service account JSON file.")
                return
        
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
        elif provider_name == "Azure AI":
            # Validate Azure AI credentials
            endpoint = settings.get("ENDPOINT", "").strip()
            if not endpoint:
                self.app.after(0, self.app.update_output_text, "Error: Azure AI requires a Resource Endpoint. Please enter your endpoint URL.")
                return
            if not api_key or api_key == "putinyourkey":
                self.app.after(0, self.app.update_output_text, "Error: Azure AI requires an API Key. Please enter your API key.")
                return
        elif provider_name not in ["LM Studio", "Vertex AI"] and (not api_key or api_key == "putinyourkey"):
            self.app.after(0, self.app.update_output_text, f"Error: Please enter a valid {provider_name} API Key in the settings.")
            return
        if not prompt:
            self.app.after(0, self.app.update_output_text, "Error: Input text cannot be empty.")
            return
        
        self.logger.info(f"Submitting prompt to {provider_name} with model {settings.get('MODEL')}")
        
        # Handle HuggingFace separately (uses different client)
        if provider_name == "HuggingFace AI":
            if not api_key or api_key == "putinyourkey":
                error_msg = "Please configure your HuggingFace API key in the settings."
                self.logger.warning(error_msg)
                self.app.after(0, self.app.update_output_text, error_msg)
                return
                
            if HUGGINGFACE_HELPER_AVAILABLE:
                try:
                    # Use the huggingface_helper module for proper task detection
                    def update_callback(response):
                        # Use unified display method (handles streaming automatically)
                        self.display_ai_response(response)
                    
                    self.logger.debug(f"Calling HuggingFace helper with model: {settings.get('MODEL', 'unknown')}")
                    process_huggingface_request(api_key, prompt, settings, update_callback, self.logger)
                    
                except Exception as e:
                    error_msg = f"HuggingFace processing failed: {str(e)}"
                    self.logger.error(error_msg, exc_info=True)
                    self.app.after(0, self.app.update_output_text, error_msg)
            else:
                error_msg = "HuggingFace helper module not available. Please check your installation."
                self.logger.error(error_msg)
                self.app.after(0, self.app.update_output_text, error_msg)
            return

        # All other providers via REST helper
        try:
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
            
            # Log request details for Vertex AI (without sensitive token)
            if provider_name == "Vertex AI":
                self.logger.debug(f"Vertex AI Request URL: {url}")
                safe_headers = {k: ('***REDACTED***' if k == 'Authorization' else v) for k, v in headers.items()}
                self.logger.debug(f"Vertex AI Headers: {json.dumps(safe_headers, indent=2)}")

            # Check if provider supports streaming and streaming is enabled
            streaming_providers = ["OpenAI", "Groq AI", "OpenRouterAI", "Azure AI", "Anthropic AI"]
            use_streaming = (
                self.is_streaming_enabled() and 
                provider_name in streaming_providers
            )
            
            # Retry logic with exponential backoff
            max_retries = 5
            base_delay = 1

            for i in range(max_retries):
                try:
                    if use_streaming:
                        # Use streaming API call
                        self.logger.info(f"Using streaming mode for {provider_name}")
                        streaming_payload = payload.copy()
                        streaming_payload["stream"] = True
                        
                        self._call_streaming_api(url, streaming_payload, headers, provider_name)
                        return
                    else:
                        # Non-streaming API call
                        response = requests.post(url, json=payload, headers=headers, timeout=60)
                        response.raise_for_status()

                        data = response.json()
                        self.logger.debug(f"{provider_name} Response: {data}")

                        result_text = self._extract_response_text(provider_name, data)
                        self.logger.debug(f"FINAL: About to display result_text: {str(result_text)[:100]}...")
                        
                        # Use unified display method (handles streaming automatically)
                        self.display_ai_response(result_text)
                        return

                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429 and i < max_retries - 1:
                        delay = base_delay * (2 ** i) + random.uniform(0, 1)
                        self.logger.warning(f"Rate limit exceeded. Retrying in {delay:.2f} seconds...")
                        time.sleep(delay)
                    else:
                        # Get full error response
                        try:
                            error_response = e.response.text if hasattr(e, 'response') and e.response else str(e)
                            error_json = e.response.json() if hasattr(e, 'response') and e.response and e.response.headers.get('content-type', '').startswith('application/json') else None
                        except:
                            error_response = str(e)
                            error_json = None
                        
                        # Log detailed error for Vertex AI
                        if provider_name == "Vertex AI":
                            self.logger.error(f"Vertex AI API Error - Status: {e.response.status_code if hasattr(e, 'response') and e.response else 'N/A'}")
                            self.logger.error(f"Vertex AI Error Response: {error_response}")
                            if error_json:
                                self.logger.error(f"Vertex AI Error JSON: {json.dumps(error_json, indent=2)}")
                            self.logger.error(f"Vertex AI Request URL: {url}")
                            self.logger.debug(f"Vertex AI Headers (token redacted): {[(k, '***REDACTED***' if k == 'Authorization' else v) for k, v in headers.items()]}")
                            
                            # Provide helpful error message
                            if e.response.status_code == 403:
                                error_msg = f"Vertex AI 403 Forbidden Error\n\n"
                                error_msg += f"URL: {url}\n\n"
                                if error_json:
                                    error_msg += f"Error Details: {json.dumps(error_json, indent=2)}\n\n"
                                else:
                                    error_msg += f"Error Response: {error_response}\n\n"
                                error_msg += "Common causes:\n"
                                error_msg += "1. Service account doesn't have 'Vertex AI User' role\n"
                                error_msg += "2. Vertex AI API not enabled for the project\n"
                                error_msg += "3. Project ID format incorrect (check for encoding issues)\n"
                                error_msg += "4. Model name not available in the selected region\n"
                                error_msg += "5. Billing not enabled for the project\n\n"
                                error_msg += "Solutions:\n"
                                error_msg += "1. Enable Vertex AI API in Google Cloud Console\n"
                                error_msg += "2. Grant 'Vertex AI User' role to service account\n"
                                error_msg += "3. Ensure billing is enabled\n"
                                error_msg += "4. Verify model name is correct (try gemini-1.5-flash or gemini-1.5-pro)\n"
                                
                                self.app.after(0, self.app.update_output_text, error_msg)
                                return
                        
                        # Check for AWS Bedrock specific errors
                        if provider_name == "AWS Bedrock":
                            model_id = settings.get("MODEL", "unknown")
                            auth_method = settings.get("AUTH_METHOD", "api_key")
                            
                            if e.response.status_code == 403:
                                error_msg = f"AWS Bedrock 403 Forbidden Error\n\n"
                                error_msg += f"Model: {model_id}\n"
                                error_msg += f"Auth Method: {auth_method}\n\n"
                                error_msg += "This error typically means:\n"
                                error_msg += "1. Your credentials don't have permission to access this model\n"
                                error_msg += "2. The model is not enabled in your AWS account\n"
                                error_msg += "3. The model is not available in your selected region\n"
                                error_msg += "4. Your API key may be invalid or expired\n\n"
                                error_msg += "Solutions:\n"
                                error_msg += "1. Go to AWS Bedrock Console and enable model access\n"
                                error_msg += "2. Verify your IAM permissions include 'bedrock:InvokeModel'\n"
                                error_msg += "3. Try a different model (e.g., amazon.nova-lite-v1:0)\n"
                                error_msg += "4. Try a different region (us-east-1, us-west-2)\n"
                                error_msg += "5. If using API Key auth, try IAM credentials instead\n\n"
                                error_msg += f"Original error: {error_response}"
                                
                                self.logger.error(error_msg)
                                self.app.after(0, self.app.update_output_text, error_msg)
                                return
                            
                            if "on-demand throughput isn't supported" in error_response:
                                error_msg = f"AWS Bedrock Model Error: {model_id}\n\n"
                                error_msg += "This model requires an inference profile instead of direct model ID.\n\n"
                                error_msg += "Solutions:\n"
                                error_msg += "1. Use 'Refresh Models' button to get updated model list with inference profiles\n"
                                error_msg += "2. Manually update model ID with regional prefix:\n"
                                error_msg += f"   • US: us.{model_id}\n"
                                error_msg += f"   • EU: eu.{model_id}\n"
                                error_msg += f"   • APAC: apac.{model_id}\n"
                                error_msg += "3. For Claude Sonnet 4.5, use global profile: global.anthropic.claude-sonnet-4-5-20250929-v1:0\n\n"
                                error_msg += f"Original error: {error_response}"
                                
                                self.logger.error(error_msg)
                                self.app.after(0, self.app.update_output_text, error_msg)
                            elif e.response.status_code == 400 and any(provider in model_id for provider in ["openai.", "qwen.", "twelvelabs."]):
                                error_msg = f"AWS Bedrock Model Error: {model_id}\n\n"
                                error_msg += "This third-party model may not be properly configured or available in your region.\n\n"
                                error_msg += "Common issues:\n"
                                error_msg += "1. Model may not be available in your selected region\n"
                                error_msg += "2. Model may require special access or subscription\n"
                                error_msg += "3. Model may have been deprecated or renamed\n"
                                error_msg += "4. Payload format may not be compatible\n\n"
                                error_msg += "Solutions:\n"
                                error_msg += "1. Try a different region (us-east-1, us-west-2, eu-west-1)\n"
                                error_msg += "2. Use 'Refresh Models' to get current available models\n"
                                error_msg += "3. Try a similar model from Amazon, Anthropic, or Meta instead\n\n"
                                error_msg += f"Original error: {error_response}"
                                
                                self.logger.error(error_msg)
                                self.app.after(0, self.app.update_output_text, error_msg)
                            elif e.response.status_code == 404:
                                error_msg = f"AWS Bedrock Model Not Found: {model_id}\n\n"
                                error_msg += "This model is not available or the model ID is incorrect.\n\n"
                                error_msg += "Solutions:\n"
                                error_msg += "1. Use 'Refresh Models' button to get current available models\n"
                                error_msg += "2. Check if model ID has suffixes that need to be removed\n"
                                error_msg += "3. Verify the model is available in your selected region\n"
                                error_msg += "4. Try a similar model that's confirmed to be available\n\n"
                                error_msg += f"Original error: {error_response}"
                                
                                self.logger.error(error_msg)
                                self.app.after(0, self.app.update_output_text, error_msg)
                            else:
                                self.logger.error(f"AWS Bedrock API Request Error: {e}\nResponse: {error_response}")
                                self.app.after(0, self.app.update_output_text, f"AWS Bedrock API Request Error: {e}\nResponse: {error_response}")
                        else:
                            self.logger.error(f"API Request Error: {e}\nResponse: {error_response}")
                            self.app.after(0, self.app.update_output_text, f"API Request Error: {e}\nResponse: {error_response}")
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
        if provider_name == "Vertex AI":
            # Get project_id and location from settings
            project_id = settings.get("PROJECT_ID", "")
            location = settings.get("LOCATION", "us-central1")
            model = settings.get("MODEL", "")
            
            # Note: Project IDs in Google Cloud REST API URLs should be used as-is
            # If project_id contains colons (like project numbers), they're part of the format
            url = provider_config["url_template"].format(
                location=location,
                project_id=project_id,
                model=model
            )
            
            self.logger.debug(f"Vertex AI URL components - project_id: {project_id}, location: {location}, model: {model}")
        elif provider_name == "Azure AI":
            endpoint = settings.get("ENDPOINT", "").strip().rstrip('/')
            model = settings.get("MODEL", "gpt-4.1")
            api_version = settings.get("API_VERSION", "2024-10-21")
            
            # Auto-detect endpoint type and build URL accordingly
            # Azure AI Foundry: https://[resource].services.ai.azure.com
            # Azure OpenAI: https://[resource].openai.azure.com or https://[resource].cognitiveservices.azure.com
            
            if ".services.ai.azure.com" in endpoint:
                # Azure AI Foundry - use /models/chat/completions format (model goes in request body, not URL)
                # Check if endpoint already includes /api/projects/[project-name]
                import re
                if "/api/projects/" in endpoint:
                    # Project endpoint format - extract base resource endpoint
                    match = re.search(r'https://([^.]+)\.services\.ai\.azure\.com', endpoint)
                    if match:
                        resource_name = match.group(1)
                        endpoint = f"https://{resource_name}.services.ai.azure.com"
                # Use Foundry models endpoint format: /models/chat/completions
                url = f"{endpoint}/models/chat/completions?api-version={api_version}"
            elif ".openai.azure.com" in endpoint or ".cognitiveservices.azure.com" in endpoint:
                # Azure OpenAI - use /openai/deployments/[model]/chat/completions format
                # Both *.openai.azure.com and *.cognitiveservices.azure.com are Azure OpenAI endpoints
                url = f"{endpoint}/openai/deployments/{model}/chat/completions?api-version={api_version}"
            else:
                # Unknown format - assume Azure AI Foundry format by default
                # Most likely it's a Foundry endpoint if it's not explicitly OpenAI
                url = f"{endpoint}/models/chat/completions?api-version={api_version}"
        elif provider_name == "LM Studio":
            base_url = settings.get("BASE_URL", "http://127.0.0.1:1234").rstrip('/')
            url = provider_config["url_template"].format(base_url=base_url)
        elif provider_name == "AWS Bedrock":
            region = settings.get("AWS_REGION", "us-west-2")
            model_id = settings.get("MODEL", "meta.llama3-1-70b-instruct-v1:0")
            
            # Handle inference profile selection from dropdown
            if " (Inference Profile)" in model_id:
                model_id = model_id.replace(" (Inference Profile)", "")
                self.logger.debug(f"Using inference profile directly: {model_id}")
            
            # Clean up model ID suffixes that are metadata but not part of the actual model ID for API calls
            # These suffixes are used in the model list for information but need to be removed for API calls
            original_model_id = model_id
            if ":mm" in model_id:  # Multimodal capability indicator
                model_id = model_id.replace(":mm", "")
                self.logger.debug(f"Removed multimodal suffix: {original_model_id} -> {model_id}")
            elif ":8k" in model_id:  # Context length indicator  
                model_id = model_id.replace(":8k", "")
                self.logger.debug(f"Removed context length suffix: {original_model_id} -> {model_id}")
            elif model_id.count(":") > 2:  # Other suffixes (model should have max 2 colons: provider.model-name-version:number)
                # Keep only the first two parts (provider.model:version)
                parts = model_id.split(":")
                if len(parts) > 2:
                    model_id = ":".join(parts[:2])
                    self.logger.debug(f"Cleaned model ID: {original_model_id} -> {model_id}")
            
            # Check if model_id is already an inference profile (has regional prefix)
            # If so, don't apply the mapping - use it as-is
            already_has_prefix = any(model_id.startswith(prefix) for prefix in ['us.', 'eu.', 'apac.', 'global.'])
            
            if already_has_prefix:
                # Model already has inference profile prefix, use as-is
                final_model_id = model_id
                self.logger.debug(f"AWS Bedrock: Model '{model_id}' already has inference profile prefix")
            else:
                # AWS Bedrock requires inference profiles for newer Claude models
                # Based on AWS documentation and current model availability
                # Note: Only map base model IDs to inference profiles
                inference_profile_mapping = {
                    # Claude 3.5 models (v2) - these require inference profiles
                    "anthropic.claude-3-5-haiku-20241022-v1:0": "us.anthropic.claude-3-5-haiku-20241022-v1:0",
                    "anthropic.claude-3-5-sonnet-20241022-v2:0": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
                    
                    # Claude 3.5 models (v1)
                    "anthropic.claude-3-5-sonnet-20240620-v1:0": "us.anthropic.claude-3-5-sonnet-20240620-v1:0",
                    
                    # Claude 3 models (original) - some may work without profiles
                    "anthropic.claude-3-opus-20240229-v1:0": "us.anthropic.claude-3-opus-20240229-v1:0",
                    "anthropic.claude-3-sonnet-20240229-v1:0": "us.anthropic.claude-3-sonnet-20240229-v1:0",
                    "anthropic.claude-3-haiku-20240307-v1:0": "us.anthropic.claude-3-haiku-20240307-v1:0"
                }
                
                # Use inference profile if available, otherwise use direct model ID
                final_model_id = inference_profile_mapping.get(model_id, model_id)
            
            # If we're using an inference profile, log the conversion for debugging
            if final_model_id != model_id:
                self.logger.info(f"AWS Bedrock: Converting model ID '{model_id}' to inference profile '{final_model_id}'")
            
            # Handle regional preferences for inference profiles
            # If user is in EU region and model supports EU profiles, use EU prefix
            if region.startswith('eu-') and final_model_id.startswith('us.anthropic.'):
                eu_model_id = final_model_id.replace('us.anthropic.', 'eu.anthropic.')
                self.logger.info(f"AWS Bedrock: Using EU inference profile '{eu_model_id}' for region '{region}'")
                final_model_id = eu_model_id
            elif region.startswith('ap-') and final_model_id.startswith('us.anthropic.'):
                apac_model_id = final_model_id.replace('us.anthropic.', 'apac.anthropic.')
                self.logger.info(f"AWS Bedrock: Using APAC inference profile '{apac_model_id}' for region '{region}'")
                final_model_id = apac_model_id
            
            # Always use InvokeModel API - it's more reliable and works with both
            # inference profiles and base model IDs
            # The Converse API has compatibility issues with some authentication methods
            url = provider_config["url_invoke"].format(region=region, model=final_model_id)
            self.logger.info(f"AWS Bedrock: Using InvokeModel API for model '{final_model_id}'")
        elif "url_template" in provider_config:
            url = provider_config["url_template"].format(model=settings.get("MODEL"), api_key=api_key)
        else:
            # Check if using GPT-5.2 (needs Responses API)
            if provider_name == "OpenAI" and self._is_gpt52_model(settings.get("MODEL", "")):
                url = provider_config["url_responses"]
            else:
                url = provider_config["url"]
        
        # Build payload first (needed for AWS signing)
        payload = self._build_payload(provider_name, prompt, settings)
        
        # Build headers
        headers = {}
        for key, value in provider_config["headers_template"].items():
            if provider_name == "Vertex AI":
                # Vertex AI uses OAuth2 access token
                if "{access_token}" in value:
                    access_token = self.get_vertex_ai_access_token()
                    if not access_token:
                        raise ValueError("Failed to obtain Vertex AI access token. Please check your service account JSON.")
                    headers[key] = value.format(access_token=access_token)
                else:
                    headers[key] = value
            elif provider_name == "Azure AI":
                # Azure AI uses api-key header (not Authorization Bearer)
                headers[key] = value.format(api_key=api_key)
            elif provider_name in ["LM Studio", "AWS Bedrock"]:
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
        
        if provider_name in ["Google AI", "Vertex AI"]:
            system_prompt = settings.get("system_prompt", "").strip()
            
            # Use proper systemInstruction field instead of prepending to prompt
            # This is the recommended way to set system prompts for Gemini models
            payload = {"contents": [{"parts": [{"text": prompt}], "role": "user"}]}
            
            # Add systemInstruction as a separate field (proper Gemini API format)
            if system_prompt:
                payload["systemInstruction"] = {
                    "parts": [{"text": system_prompt}]
                }
            
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
        
        elif provider_name == "Azure AI":
            # Azure AI uses OpenAI-compatible format
            # For Azure OpenAI: model is in URL, so don't include in payload (recommended)
            # For Azure AI Foundry: model must be in payload
            endpoint = settings.get("ENDPOINT", "").strip().rstrip('/')
            payload = {"messages": []}
            
            # Only include model in payload for Azure AI Foundry
            # Azure OpenAI has model in URL path, so omit from payload for better compatibility
            if ".services.ai.azure.com" in endpoint:
                # Azure AI Foundry - model MUST be in payload
                payload["model"] = settings.get("MODEL")
            # For Azure OpenAI (openai.azure.com or cognitiveservices.azure.com), model is in URL
            # Some API versions accept model in payload too, but it's better to omit it
            
            system_prompt = settings.get("system_prompt", "").strip()
            if system_prompt:
                payload["messages"].append({"role": "system", "content": system_prompt})
            payload["messages"].append({"role": "user", "content": prompt})
            
            # Universal parameters supported by Azure AI Foundry
            self._add_param_if_valid(payload, settings, 'temperature', float)
            self._add_param_if_valid(payload, settings, 'top_p', float)
            self._add_param_if_valid(payload, settings, 'max_tokens', int)
            self._add_param_if_valid(payload, settings, 'frequency_penalty', float)
            self._add_param_if_valid(payload, settings, 'presence_penalty', float)
            self._add_param_if_valid(payload, settings, 'seed', int)
            
            stop_str = str(settings.get('stop', '')).strip()
            if stop_str:
                payload['stop'] = [s.strip() for s in stop_str.split(',')]
        elif provider_name in ["OpenAI", "Groq AI", "OpenRouterAI", "LM Studio"]:
            model = settings.get("MODEL", "")
            
            # GPT-5.2 uses Responses API with different format
            if provider_name == "OpenAI" and self._is_gpt52_model(model):
                payload = {"model": model, "input": prompt}
                
                # Optional parameters for Responses API (limited support)
                self._add_param_if_valid(payload, settings, 'temperature', float)
                self._add_param_if_valid(payload, settings, 'top_p', float)
                
                # Note: Responses API doesn't support max_tokens, frequency_penalty, presence_penalty, or seed
            else:
                # Standard Chat Completions API
                payload = {"model": model, "messages": []}
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
            # AWS Bedrock InvokeModel API - model-specific payload formats
            # Using InvokeModel API for better compatibility with API Key authentication
            model_id = settings.get("MODEL", "")
            system_prompt = settings.get("system_prompt", "").strip()
            
            max_tokens = settings.get("MAX_OUTPUT_TOKENS", "4096")
            try:
                max_tokens_int = int(max_tokens)
            except ValueError:
                max_tokens_int = 4096
            
            self.logger.debug(f"Building InvokeModel payload for model: {model_id}")
            
            if "anthropic.claude" in model_id:
                # Anthropic Claude models
                payload = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens_int,
                    "messages": [{"role": "user", "content": prompt}]
                }
                if system_prompt:
                    payload["system"] = system_prompt
            elif "amazon.nova" in model_id:
                # Amazon Nova models
                payload = {
                    "messages": [{"role": "user", "content": [{"text": prompt}]}],
                    "inferenceConfig": {"maxTokens": max_tokens_int}
                }
                if system_prompt:
                    payload["system"] = [{"text": system_prompt}]
            elif "amazon.titan" in model_id:
                # Amazon Titan models
                payload = {
                    "inputText": f"{system_prompt}\n\n{prompt}" if system_prompt else prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": max_tokens_int,
                        "temperature": 0.7,
                        "topP": 0.9
                    }
                }
            elif "meta.llama" in model_id:
                # Meta Llama models
                full_prompt = f"{system_prompt}\n\nHuman: {prompt}\n\nAssistant:" if system_prompt else f"Human: {prompt}\n\nAssistant:"
                payload = {
                    "prompt": full_prompt,
                    "max_gen_len": max_tokens_int,
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            elif "mistral." in model_id or "mixtral." in model_id:
                # Mistral models
                payload = {
                    "prompt": f"<s>[INST] {system_prompt}\n\n{prompt} [/INST]" if system_prompt else f"<s>[INST] {prompt} [/INST]",
                    "max_tokens": max_tokens_int,
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            elif "cohere.command" in model_id:
                # Cohere Command models
                payload = {
                    "message": prompt,
                    "max_tokens": max_tokens_int,
                    "temperature": 0.7,
                    "p": 0.9
                }
                if system_prompt:
                    payload["preamble"] = system_prompt
            elif "ai21." in model_id:
                # AI21 models
                payload = {
                    "prompt": f"{system_prompt}\n\n{prompt}" if system_prompt else prompt,
                    "maxTokens": max_tokens_int,
                    "temperature": 0.7,
                    "topP": 0.9
                }
            else:
                # Default format - try messages format first (works for many models)
                payload = {
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens_int,
                    "temperature": 0.7
                }
                payload["messages"].insert(0, {"role": "system", "content": system_prompt})
        
        return payload
    
    def _is_gpt52_model(self, model: str) -> bool:
        """Check if model is GPT-5.2 which requires Responses API."""
        if not model:
            return False
        model_lower = model.lower()
        return 'gpt-5.2' in model_lower or 'gpt5.2' in model_lower or model_lower.startswith('gpt-52')
    
    def _add_param_if_valid(self, param_dict, settings, key, param_type):
        """Add parameter to dict if it's valid."""
        val = settings.get(key)
        if val is not None and val != "":
            try:
                converted_val = param_type(val)
                # Only add if not an empty string, 0, or 0.0 (unless 0 or 0.0 is a valid setting)
                # For now, assuming 0/0.0 are valid if type is int/float
                if converted_val is not None and (converted_val != "" or param_type == str):
                    param_dict[key] = converted_val
            except (ValueError, TypeError):
                self.logger.warning(f"Could not convert {key} value '{val}' to {param_type}")
    
    def _extract_response_text(self, provider_name, data):
        """Extract response text from API response."""
        result_text = f"Error: Could not parse response from {provider_name}."
        
        if provider_name in ["Google AI", "Vertex AI"]:
            result_text = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', result_text)
        elif provider_name == "Anthropic AI":
            result_text = data.get('content', [{}])[0].get('text', result_text)
        elif provider_name in ["OpenAI", "Groq AI", "OpenRouterAI", "LM Studio", "Azure AI"]:
            # Check for Responses API format (GPT-5.2)
            if 'item' in data and isinstance(data['item'], dict):
                # Responses API format
                result_text = data['item'].get('content', result_text)
            else:
                # Standard Chat Completions format
                result_text = data.get('choices', [{}])[0].get('message', {}).get('content', result_text)
        elif provider_name == "Cohere AI":
            result_text = data.get('text', result_text)
        elif provider_name == "AWS Bedrock":
            # Extract response from AWS Bedrock Converse API
            # Converse API response format: {'output': {'message': {'content': [{'text': '...'}], 'role': 'assistant'}}}
            self.logger.debug(f"AWS Bedrock response data: {data}")
            
            try:
                # Primary: Converse API format (recommended)
                if 'output' in data and 'message' in data['output']:
                    message_data = data['output']['message']
                    self.logger.debug("Using Converse API response format")
                    
                    if 'content' in message_data and isinstance(message_data['content'], list):
                        # Extract text from content array
                        text_parts = []
                        for content_item in message_data['content']:
                            if isinstance(content_item, dict) and 'text' in content_item:
                                text_parts.append(content_item['text'])
                        
                        if text_parts:
                            result_text = ''.join(text_parts)
                            self.logger.debug(f"Successfully extracted Converse API text: {result_text[:100]}...")
                        else:
                            self.logger.warning("Converse API response had no text content")
                            result_text = str(message_data.get('content', ''))
                    else:
                        result_text = str(message_data)
                
                # Fallback: Legacy InvokeModel API formats
                elif 'content' in data and isinstance(data['content'], list) and len(data['content']) > 0:
                    # Anthropic Claude format (InvokeModel)
                    self.logger.debug("Using legacy Claude content format")
                    result_text = data['content'][0].get('text', result_text)
                elif 'generation' in data:
                    # Meta Llama format (InvokeModel)
                    self.logger.debug("Using legacy Llama generation format")
                    result_text = data['generation']
                elif 'results' in data and len(data['results']) > 0:
                    # Amazon Titan format (InvokeModel)
                    self.logger.debug("Using legacy Titan results format")
                    result_text = data['results'][0].get('outputText', result_text)
                elif 'text' in data:
                    # Direct text format
                    self.logger.debug("Using direct text format")
                    result_text = data['text']
                elif 'response' in data:
                    # Some models use 'response' field
                    self.logger.debug("Using response field format")
                    result_text = data['response']
                elif 'choices' in data and len(data['choices']) > 0:
                    # OpenAI-style format
                    self.logger.debug("Using OpenAI-style choices format")
                    choice = data['choices'][0]
                    if 'message' in choice and 'content' in choice['message']:
                        result_text = choice['message']['content']
                    elif 'text' in choice:
                        result_text = choice['text']
                else:
                    # Fallback - try to find text in common locations
                    self.logger.debug("Using fallback format - no recognized structure")
                    result_text = data.get('text', data.get('output', data.get('response', str(data))))
            except Exception as e:
                self.logger.error(f"Error extracting AWS Bedrock response: {e}")
                result_text = str(data)
        
        return result_text
    
    def _call_streaming_api(self, url, payload, headers, provider_name):
        """
        Make a streaming API call and progressively display the response.
        
        Supports OpenAI-compatible streaming format (SSE with data: prefix).
        Works with OpenAI, Groq, OpenRouter, Azure AI, and Anthropic.
        
        Args:
            url: API endpoint URL
            payload: Request payload (should include "stream": True)
            headers: Request headers
            provider_name: Name of the AI provider
        """
        try:
            # Start streaming display
            if not self.start_streaming_response():
                self.logger.warning("Failed to start streaming display, falling back to non-streaming")
                # Fall back to non-streaming
                payload_copy = payload.copy()
                payload_copy.pop("stream", None)
                response = requests.post(url, json=payload_copy, headers=headers, timeout=60)
                response.raise_for_status()
                data = response.json()
                result_text = self._extract_response_text(provider_name, data)
                self.display_ai_response(result_text)
                return
            
            
            # Debug logging for GPT-5.2 troubleshooting
            self.logger.info(f"Making API request to: {url}")
            self.logger.info(f"Payload: {json.dumps(payload, indent=2)}")
            
            # Make streaming request
            response = requests.post(url, json=payload, headers=headers, timeout=120, stream=True)
            response.raise_for_status()
            
            accumulated_text = ""
            
            for line in response.iter_lines():
                if not line:
                    continue
                    
                line_text = line.decode('utf-8')
                
                # Handle SSE format (data: prefix)
                if line_text.startswith('data: '):
                    data_str = line_text[6:]  # Remove 'data: ' prefix
                    
                    # Check for stream end marker
                    if data_str.strip() == '[DONE]':
                        break
                    
                    try:
                        chunk_data = json.loads(data_str)
                        
                        # Extract content based on provider format
                        content = self._extract_streaming_chunk(chunk_data, provider_name)
                        
                        if content:
                            accumulated_text += content
                            self.add_streaming_chunk(content)
                            
                    except json.JSONDecodeError as e:
                        self.logger.debug(f"Skipping non-JSON line: {data_str[:50]}...")
                        continue
                        
                # Handle Anthropic's event-based format
                elif line_text.startswith('event: '):
                    # Anthropic uses event: content_block_delta, etc.
                    continue
            
            # End streaming
            self.end_streaming_response()
            
            if not accumulated_text:
                self.logger.warning("No content received from streaming response")
                self.app.after(0, self.app.update_output_text, "Error: No content received from streaming response.")
                
        except requests.exceptions.HTTPError as e:
            self.cancel_streaming()
            # Log the detailed error response
            error_detail = "No details available"
            if e.response is not None:
                try:
                    error_detail = e.response.text
                    self.logger.error(f"API Error Response: {error_detail}")
                except:
                    pass
            self.logger.error(f"Streaming API request failed: {e}")
            self.app.after(0, self.app.update_output_text, f"Streaming API Error: {e}\\n\\nDetails: {error_detail}")
        except requests.exceptions.RequestException as e:
            self.cancel_streaming()
            self.logger.error(f"Streaming API request failed: {e}")
            self.app.after(0, self.app.update_output_text, f"Streaming API Error: {e}")
        except Exception as e:
            self.cancel_streaming()
            self.logger.error(f"Streaming error: {e}", exc_info=True)
            self.app.after(0, self.app.update_output_text, f"Streaming Error: {e}")
    
    def _extract_streaming_chunk(self, chunk_data, provider_name):
        """
        Extract text content from a streaming chunk based on provider format.
        
        Args:
            chunk_data: Parsed JSON chunk data
            provider_name: Name of the AI provider
            
        Returns:
            Extracted text content or empty string
        """
        try:
            if provider_name == "Anthropic AI":
                # Anthropic format: {"type": "content_block_delta", "delta": {"text": "..."}}
                if chunk_data.get("type") == "content_block_delta":
                    return chunk_data.get("delta", {}).get("text", "")
                return ""
            else:
                # Check for Responses API format first (GPT-5.2)
                chunk_type = chunk_data.get("type", "")
                if chunk_type == "response.output_text.delta":
                    # Responses API format: {"type": "response.output_text.delta", "delta": "..."}
                    return chunk_data.get("delta", "")
                
                # OpenAI Chat Completions format (OpenAI, Groq, OpenRouter, Azure AI)
                # Format: {"choices": [{"delta": {"content": "..."}}]}
                choices = chunk_data.get("choices", [])
                if choices and len(choices) > 0:
                    delta = choices[0].get("delta", {})
                    return delta.get("content", "")
                return ""
        except Exception as e:
            self.logger.debug(f"Error extracting streaming chunk: {e}")
            return ""
    
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
            "Vertex AI": {
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
            },
            "Azure AI": {
                "max_tokens": {"tab": "content", "type": "entry", "tip": "Maximum number of tokens to generate."},
                "temperature": {"tab": "sampling", "type": "scale", "range": (0.0, 2.0), "res": 0.1, "tip": "Controls randomness. Higher is more creative."},
                "top_p": {"tab": "sampling", "type": "scale", "range": (0.0, 1.0), "res": 0.05, "tip": "Nucleus sampling threshold."},
                "frequency_penalty": {"tab": "sampling", "type": "scale", "range": (-2.0, 2.0), "res": 0.1, "tip": "Penalizes frequent tokens."},
                "presence_penalty": {"tab": "sampling", "type": "scale", "range": (-2.0, 2.0), "res": 0.1, "tip": "Penalizes tokens that have appeared."},
                "seed": {"tab": "content", "type": "entry", "tip": "Random seed for reproducible outputs."},
                "stop": {"tab": "content", "type": "entry", "tip": "Comma-separated list of strings to stop generation."}
            }
        }
        
        return configs.get(provider_name, {})
    
    # ==================== Streaming Support Methods ====================
    
    def enable_streaming(self, enabled: bool = True) -> bool:
        """
        Enable or disable streaming mode for AI responses.
        
        Args:
            enabled: Whether to enable streaming
            
        Returns:
            True if streaming was enabled/disabled successfully
        """
        if not STREAMING_AVAILABLE:
            self.logger.warning("Streaming is not available - module not loaded")
            return False
        
        self._streaming_enabled = enabled
        self.logger.info(f"Streaming mode {'enabled' if enabled else 'disabled'}")
        return True
    
    def is_streaming_enabled(self) -> bool:
        """Check if streaming mode is enabled."""
        return self._streaming_enabled and STREAMING_AVAILABLE
    
    def _get_output_text_widget(self):
        """Get the current output text widget from the app."""
        try:
            current_tab_index = self.app.output_notebook.index(self.app.output_notebook.select())
            active_output_tab = self.app.output_tabs[current_tab_index]
            return active_output_tab.text
        except Exception as e:
            self.logger.error(f"Failed to get output text widget: {e}")
            return None
    
    def _init_streaming_handler(self, text_widget):
        """Initialize the streaming handler for a text widget."""
        if not STREAMING_AVAILABLE:
            return None
        
        try:
            config = StreamConfig(
                chunk_delay_ms=10,
                batch_size=3,
                auto_scroll=True,
                highlight_new_text=False,
                use_threading=True
            )
            
            self._streaming_manager = StreamingTextManager(
                text_widget,
                stream_config=config
            )
            
            return self._streaming_manager
        except Exception as e:
            self.logger.error(f"Failed to initialize streaming handler: {e}")
            return None
    
    def start_streaming_response(self, clear_existing: bool = True) -> bool:
        """
        Start streaming an AI response to the output widget.
        
        Args:
            clear_existing: Whether to clear existing content
            
        Returns:
            True if streaming started successfully
        """
        if not self.is_streaming_enabled():
            return False
        
        text_widget = self._get_output_text_widget()
        if not text_widget:
            return False
        
        # Enable the text widget for editing
        text_widget.config(state="normal")
        
        manager = self._init_streaming_handler(text_widget)
        if not manager:
            return False
        
        def on_progress(chars_received, total):
            self.logger.debug(f"Streaming progress: {chars_received} chars received")
        
        def on_complete(metrics):
            self.logger.info(
                f"Streaming complete: {metrics.total_characters} chars "
                f"in {metrics.duration:.2f}s ({metrics.chars_per_second:.0f} chars/s)"
            )
            # Disable the text widget after streaming
            self.app.after(0, lambda: text_widget.config(state="disabled"))
            # Update stats
            self.app.after(10, self.app.update_all_stats)
        
        return manager.start_streaming(
            clear_existing=clear_existing,
            on_progress=on_progress,
            on_complete=on_complete
        )
    
    def add_streaming_chunk(self, chunk: str) -> bool:
        """
        Add a chunk of text to the streaming response.
        
        Args:
            chunk: Text chunk to add
            
        Returns:
            True if chunk was added successfully
        """
        if not self._streaming_manager:
            return False
        
        return self._streaming_manager.add_stream_chunk(chunk)
    
    def end_streaming_response(self):
        """End the streaming response and finalize."""
        if not self._streaming_manager:
            return None
        
        metrics = self._streaming_manager.end_streaming()
        
        # Save settings after streaming completes
        self.app.save_settings()
        
        return metrics
    
    def cancel_streaming(self):
        """Cancel the current streaming operation."""
        if self._streaming_manager:
            self._streaming_manager.cancel()
            self._streaming_manager = None
    
    def process_streaming_response(self, response_iterator):
        """
        Process a streaming response from an API.
        
        This method handles the full streaming lifecycle:
        1. Start streaming
        2. Process each chunk from the iterator
        3. End streaming
        
        Args:
            response_iterator: Iterator yielding response chunks
            
        Returns:
            The complete accumulated text, or None if streaming failed
        """
        if not self.start_streaming_response():
            self.logger.warning("Failed to start streaming, falling back to non-streaming")
            return None
        
        try:
            for chunk in response_iterator:
                if not self.add_streaming_chunk(chunk):
                    self.logger.warning("Failed to add chunk, stopping stream")
                    break
            
            self.end_streaming_response()
            return self._streaming_manager.get_accumulated_text() if self._streaming_manager else None
            
        except Exception as e:
            self.logger.error(f"Error during streaming: {e}")
            self.cancel_streaming()
            return None
    
    def display_text_with_streaming(self, text: str, chunk_size: int = 50):
        """
        Display text progressively using streaming, simulating a streaming response.
        
        Useful for displaying large text content progressively.
        
        Args:
            text: The text to display
            chunk_size: Size of each chunk to display
        """
        if not self.is_streaming_enabled():
            # Fall back to regular display
            self.app.after(0, self.app.update_output_text, text)
            return
        
        def chunk_generator():
            for i in range(0, len(text), chunk_size):
                yield text[i:i + chunk_size]
        
        # Run in background thread
        def stream_text():
            self.process_streaming_response(chunk_generator())
        
        thread = threading.Thread(target=stream_text, daemon=True)
        thread.start()
    
    def display_ai_response(self, text: str, min_streaming_length: int = 500):
        """
        Unified method to display AI response with automatic streaming for large responses.
        
        This method should be used by all AI providers to display their responses.
        It automatically decides whether to use streaming based on response length.
        
        Args:
            text: The AI response text to display
            min_streaming_length: Minimum text length to trigger streaming (default 500)
        """
        if self.is_streaming_enabled() and len(text) > min_streaming_length:
            self.logger.debug(f"Using streaming display for response ({len(text)} chars)")
            self.app.after(0, lambda t=text: self.display_text_with_streaming(t))
        else:
            self.app.after(0, self.app.update_output_text, text)