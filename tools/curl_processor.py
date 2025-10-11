"""
Core HTTP processing module for the cURL GUI Tool.

This module provides the CurlProcessor class that handles HTTP requests,
response processing, and basic error handling for the cURL GUI Tool.
"""

import requests
import time
import re
import shlex
import json
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, Union, List, Tuple
from datetime import datetime


@dataclass
class ResponseData:
    """HTTP response data structure."""
    status_code: int
    headers: Dict[str, str]
    body: str
    timing: Dict[str, float]
    size: int
    encoding: str
    content_type: str
    url: str
    
    def is_json(self) -> bool:
        """Check if response is JSON."""
        return 'application/json' in self.content_type.lower()
    
    def format_body(self, format_type: str = 'auto') -> str:
        """Format response body for display."""
        if format_type == 'auto':
            if self.is_json():
                try:
                    import json
                    parsed = json.loads(self.body)
                    return json.dumps(parsed, indent=2)
                except (json.JSONDecodeError, ValueError):
                    return self.body
        return self.body


class CurlToolError(Exception):
    """Base exception for cURL tool errors."""
    pass


class RequestError(CurlToolError):
    """HTTP request execution errors."""
    def __init__(self, message: str, suggestion: Optional[str] = None, error_code: Optional[str] = None):
        self.message = message
        self.suggestion = suggestion
        self.error_code = error_code
        super().__init__(message)


class ParseError(CurlToolError):
    """cURL command parsing errors with helpful suggestions."""
    
    def __init__(self, message: str, suggestion: Optional[str] = None, position: Optional[int] = None):
        self.message = message
        self.suggestion = suggestion
        self.position = position
        
        # Auto-generate suggestions for common errors
        if not suggestion:
            self.suggestion = self._generate_suggestion(message)
        
        super().__init__(message)
    
    def _generate_suggestion(self, message: str) -> str:
        """Generate helpful suggestions based on error message."""
        message_lower = message.lower()
        
        if "empty" in message_lower or "missing" in message_lower:
            return "Make sure your cURL command includes a URL. Example: curl https://api.example.com"
        elif "quote" in message_lower or "unterminated" in message_lower:
            return "Check that all quotes are properly closed. Use matching single or double quotes."
        elif "method" in message_lower:
            return "Valid HTTP methods: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS"
        elif "header" in message_lower:
            return "Headers should be in format: -H \"Key: Value\""
        elif "start with" in message_lower:
            return "Command must begin with 'curl'. Example: curl -X GET https://api.example.com"
        else:
            return "Check the cURL command syntax. Use the Help button for examples."
    
    def __str__(self):
        """Format error message with suggestion."""
        msg = self.message
        if self.position is not None:
            msg += f" (at position {self.position})"
        return msg


@dataclass
class RequestConfig:
    """Configuration for HTTP requests."""
    method: str = "GET"
    url: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[str] = None
    body_type: str = "none"  # none, json, form, multipart, raw
    auth_type: str = "none"  # none, bearer, basic, apikey
    auth_data: Dict[str, str] = field(default_factory=dict)
    follow_redirects: bool = True
    verify_ssl: bool = True
    timeout: int = 30
    verbose: bool = False  # -v flag
    junk_session_cookies: bool = False  # -j flag
    save_to_file: bool = False  # -O flag
    use_remote_name: bool = False  # -O flag (same as save_to_file for our purposes)
    download_path: str = ""  # Directory for downloads
    complex_options: str = ""  # Additional cURL options not handled by UI
    
    def to_curl_command(self, processor=None) -> str:
        """Generate cURL command from configuration."""
        if processor is None:
            # Create a temporary processor instance
            from tools.curl_processor import CurlProcessor
            processor = CurlProcessor()
        return processor.generate_curl_command(self)
    
    @classmethod
    def from_curl_command(cls, curl_command: str, processor=None) -> 'RequestConfig':
        """Parse cURL command into configuration."""
        if processor is None:
            # Create a temporary processor instance
            from tools.curl_processor import CurlProcessor
            processor = CurlProcessor()
        return processor.parse_curl_command(curl_command)


class AuthenticationManager:
    """Handles authentication for HTTP requests."""
    
    @staticmethod
    def apply_auth(auth_type: str, auth_data: Dict[str, str], request_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply authentication to request parameters.
        
        Args:
            auth_type: Type of authentication (bearer, basic, apikey, none)
            auth_data: Authentication data dictionary
            request_params: Request parameters dictionary to modify
            
        Returns:
            Modified request parameters with authentication applied
            
        Raises:
            RequestError: If authentication configuration is invalid
        """
        if auth_type == "none" or not auth_data:
            return request_params
        
        if auth_type == "bearer":
            token = auth_data.get('token', '').strip()
            if not token:
                raise RequestError("Bearer token is required", "Please enter a valid bearer token")
            
            # Add Authorization header
            if 'headers' not in request_params:
                request_params['headers'] = {}
            request_params['headers']['Authorization'] = f"Bearer {token}"
            
        elif auth_type == "basic":
            username = auth_data.get('username', '').strip()
            password = auth_data.get('password', '')
            
            if not username:
                raise RequestError("Username is required for Basic Auth", "Please enter a username")
            
            # Use requests built-in basic auth
            from requests.auth import HTTPBasicAuth
            request_params['auth'] = HTTPBasicAuth(username, password)
            
        elif auth_type == "apikey":
            key_name = auth_data.get('key_name', '').strip()
            key_value = auth_data.get('key_value', '').strip()
            location = auth_data.get('location', 'header')
            
            if not key_name or not key_value:
                raise RequestError("API key name and value are required", "Please enter both key name and value")
            
            if location == 'header':
                # Add as header
                if 'headers' not in request_params:
                    request_params['headers'] = {}
                request_params['headers'][key_name] = key_value
            elif location == 'query_parameter':
                # Add as query parameter
                if 'params' not in request_params:
                    request_params['params'] = {}
                request_params['params'][key_name] = key_value
        
        return request_params
    
    @staticmethod
    def get_auth_error_suggestion(auth_type: str, error: Exception) -> str:
        """
        Get authentication-specific error suggestions.
        
        Args:
            auth_type: Type of authentication that failed
            error: The exception that occurred
            
        Returns:
            Helpful suggestion for fixing the authentication error
        """
        error_str = str(error).lower()
        
        if auth_type == "bearer":
            if "401" in error_str or "unauthorized" in error_str:
                return "Bearer token may be invalid or expired. Please check your token and try again."
            elif "403" in error_str or "forbidden" in error_str:
                return "Bearer token is valid but doesn't have permission for this resource."
        
        elif auth_type == "basic":
            if "401" in error_str or "unauthorized" in error_str:
                return "Username or password may be incorrect. Please verify your credentials."
            elif "403" in error_str or "forbidden" in error_str:
                return "Credentials are valid but don't have permission for this resource."
        
        elif auth_type == "apikey":
            if "401" in error_str or "unauthorized" in error_str:
                return "API key may be invalid or missing. Please check your key and location settings."
            elif "403" in error_str or "forbidden" in error_str:
                return "API key is valid but doesn't have permission for this resource."
        
        return "Authentication failed. Please check your credentials and try again."


class CurlProcessor:
    """Core HTTP request processing and cURL command handling."""
    
    def __init__(self):
        """Initialize the CurlProcessor with a requests session."""
        self.session = requests.Session()
        self.history = []
        self.current_request = None
        self.current_response = None
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'Pomera-cURL-Tool/1.0'
        })
    
    def execute_request(self, method: str, url: str, headers: Optional[Dict[str, str]] = None, 
                       body: Optional[Union[str, Dict]] = None, auth: Optional[Any] = None,
                       auth_type: str = "none", auth_data: Optional[Dict[str, str]] = None,
                       **kwargs) -> ResponseData:
        """
        Execute HTTP request with the specified parameters.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            url: Target URL
            headers: Optional headers dictionary
            body: Optional request body (string or dict for JSON)
            auth: Optional authentication object (legacy)
            auth_type: Authentication type (bearer, basic, apikey, none)
            auth_data: Authentication data dictionary
            **kwargs: Additional requests parameters
            
        Returns:
            ResponseData object containing response information
            
        Raises:
            RequestError: If the request fails
        """
        if not url:
            raise RequestError("URL is required", "Please enter a valid URL")
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        method = method.upper()
        if method not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
            raise RequestError(f"Unsupported HTTP method: {method}", 
                             "Supported methods: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS")
        
        # Prepare request parameters
        request_params = {
            'method': method,
            'url': url,
            'timeout': kwargs.get('timeout', 30),
            'allow_redirects': kwargs.get('follow_redirects', True),
            'verify': kwargs.get('verify_ssl', True)
        }
        
        # Add headers if provided
        if headers:
            request_params['headers'] = headers.copy()
        
        # Apply authentication using the authentication manager
        try:
            request_params = AuthenticationManager.apply_auth(
                auth_type or "none", 
                auth_data or {}, 
                request_params
            )
        except RequestError:
            raise  # Re-raise authentication errors
        
        # Add legacy authentication if provided (for backward compatibility)
        if auth and not auth_type:
            request_params['auth'] = auth
        
        # Handle files and data for multipart form data
        if 'files' in kwargs and kwargs['files']:
            request_params['files'] = kwargs['files']
            # Also add form data if provided
            if 'data' in kwargs and kwargs['data']:
                request_params['data'] = kwargs['data']
        # Add body for methods that support it
        elif body and method in ['POST', 'PUT', 'PATCH']:
            if isinstance(body, dict):
                request_params['json'] = body
            else:
                request_params['data'] = body
        
        try:
            # Record detailed timing information
            timing_info = {}
            start_time = time.time()
            
            # Execute the request with detailed timing
            response = self.session.request(**request_params)
            
            # Calculate timing
            total_time = time.time() - start_time
            
            # Extract detailed timing from response if available
            timing_info = self._extract_detailed_timing(response, total_time)
            
            # Create response data
            response_data = ResponseData(
                status_code=response.status_code,
                headers=dict(response.headers),
                body=response.text,
                timing=timing_info,
                size=len(response.content),
                encoding=response.encoding or 'utf-8',
                content_type=response.headers.get('content-type', ''),
                url=response.url
            )
            
            # Store current request and response
            self.current_request = request_params
            self.current_response = response_data
            
            # Add to history
            self._add_to_history(method, url, response_data)
            
            return response_data
            
        except requests.exceptions.ConnectionError as e:
            diagnostic_info = self._get_connection_diagnostic(url, str(e))
            raise RequestError(
                f"Connection failed: {str(e)}", 
                diagnostic_info
            )
        except requests.exceptions.Timeout as e:
            diagnostic_info = self._get_timeout_diagnostic(request_params.get('timeout', 30))
            raise RequestError(
                f"Request timed out after {request_params.get('timeout', 30)}s: {str(e)}", 
                diagnostic_info
            )
        except requests.exceptions.SSLError as e:
            diagnostic_info = self._get_ssl_diagnostic(url, str(e))
            raise RequestError(
                f"SSL verification failed: {str(e)}", 
                diagnostic_info
            )
        except requests.exceptions.HTTPError as e:
            # Check for authentication-related HTTP errors
            if response.status_code in [401, 403]:
                auth_suggestion = AuthenticationManager.get_auth_error_suggestion(
                    auth_type or "none", e
                )
                diagnostic_info = self._get_http_diagnostic(response.status_code, response.headers)
                raise RequestError(
                    f"HTTP {response.status_code}: {str(e)}", 
                    f"{auth_suggestion}\n\nDiagnostic Info:\n{diagnostic_info}"
                )
            else:
                diagnostic_info = self._get_http_diagnostic(response.status_code, response.headers)
                raise RequestError(
                    f"HTTP {response.status_code}: {str(e)}", 
                    f"Check the request parameters and try again.\n\nDiagnostic Info:\n{diagnostic_info}"
                )
        except requests.exceptions.RequestException as e:
            # Check if it's an authentication error based on response
            if hasattr(e, 'response') and e.response and e.response.status_code in [401, 403]:
                auth_suggestion = AuthenticationManager.get_auth_error_suggestion(
                    auth_type or "none", e
                )
                diagnostic_info = self._get_http_diagnostic(e.response.status_code, e.response.headers)
                raise RequestError(
                    f"Authentication failed: {str(e)}", 
                    f"{auth_suggestion}\n\nDiagnostic Info:\n{diagnostic_info}"
                )
            else:
                diagnostic_info = self._get_general_diagnostic(str(e))
                raise RequestError(
                    f"Request failed: {str(e)}", 
                    f"Check the URL and request parameters.\n\nDiagnostic Info:\n{diagnostic_info}"
                )
        except Exception as e:
            diagnostic_info = self._get_general_diagnostic(str(e))
            raise RequestError(
                f"Unexpected error: {str(e)}", 
                f"Please try again or contact support.\n\nDiagnostic Info:\n{diagnostic_info}"
            )
    
    def _extract_detailed_timing(self, response, total_time):
        """Extract detailed timing information from response."""
        timing = {
            'total': total_time,
            'dns': 0.0,
            'connect': 0.0,
            'tls': 0.0,
            'ttfb': total_time,
            'download': 0.0
        }
        
        # Try to extract timing from response object if available
        if hasattr(response, 'elapsed'):
            # requests library provides elapsed time
            timing['ttfb'] = response.elapsed.total_seconds()
            timing['download'] = max(0, total_time - timing['ttfb'])
        
        # Estimate timing breakdown (basic approximation)
        if total_time > 0:
            # Very rough estimates for timing breakdown
            timing['dns'] = min(0.1, total_time * 0.1)  # DNS usually quick
            timing['connect'] = min(0.2, total_time * 0.15)  # TCP connect
            timing['tls'] = min(0.3, total_time * 0.2) if response.url.startswith('https://') else 0.0
            timing['ttfb'] = max(0, total_time - timing['dns'] - timing['connect'] - timing['tls'] - timing['download'])
        
        return timing
    
    def _add_to_history(self, method: str, url: str, response_data: ResponseData):
        """Add request to history."""
        history_item = {
            'timestamp': datetime.now(),
            'method': method,
            'url': url,
            'status_code': response_data.status_code,
            'response_time': response_data.timing['total'],
            'success': 200 <= response_data.status_code < 400,
            'response_preview': response_data.body[:200] if response_data.body else ''
        }
        
        self.history.append(history_item)
        
        # Keep only last 100 requests
        if len(self.history) > 100:
            self.history.pop(0)
    
    def get_history(self):
        """Get request history."""
        return self.history.copy()
    
    def clear_history(self):
        """Clear request history."""
        self.history.clear()
    
    def download_file(self, url: str, filepath: str = None, use_remote_name: bool = False, 
                     resume: bool = False, progress_callback=None, **kwargs) -> Dict[str, Any]:
        """
        Download a file from URL with progress indication and resume support.
        
        Args:
            url: URL to download from
            filepath: Local file path to save to (optional if use_remote_name=True)
            use_remote_name: Use the remote filename from URL or Content-Disposition header
            resume: Attempt to resume interrupted download
            progress_callback: Callback function for progress updates (bytes_downloaded, total_bytes, speed)
            **kwargs: Additional request parameters (headers, auth, etc.)
            
        Returns:
            Dictionary with download information (filepath, size, time, success)
            
        Raises:
            RequestError: If download fails
        """
        import os
        from urllib.parse import urlparse, unquote
        
        if not url:
            raise RequestError("URL is required for download", "Please enter a valid URL")
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Determine filename if use_remote_name is True
        if use_remote_name:
            parsed_url = urlparse(url)
            filename = os.path.basename(unquote(parsed_url.path))
            if not filename or '.' not in filename:
                filename = 'downloaded_file'
            
            if filepath:
                # If filepath is provided and it's a directory, append filename
                if os.path.isdir(filepath):
                    filepath = os.path.join(filepath, filename)
                # If filepath is provided and it's not a directory, use it as-is
            else:
                # No filepath provided, use current directory with remote filename
                filepath = filename
        elif not filepath:
            raise RequestError("Filepath is required when not using remote name", 
                             "Please specify a file path or enable 'Use Remote Name'")
        
        # Prepare request parameters
        request_params = {
            'timeout': kwargs.get('timeout', 30),
            'allow_redirects': kwargs.get('follow_redirects', True),
            'verify': kwargs.get('verify_ssl', True),
            'stream': True  # Important for large file downloads
        }
        
        # Add headers if provided
        if 'headers' in kwargs:
            request_params['headers'] = kwargs['headers'].copy()
        else:
            request_params['headers'] = {}
        
        # Apply authentication
        auth_type = kwargs.get('auth_type', 'none')
        auth_data = kwargs.get('auth_data', {})
        try:
            request_params = AuthenticationManager.apply_auth(auth_type, auth_data, request_params)
        except RequestError:
            raise
        
        # Handle resume functionality
        start_byte = 0
        if resume and os.path.exists(filepath):
            start_byte = os.path.getsize(filepath)
            request_params['headers']['Range'] = f'bytes={start_byte}-'
        
        try:
            start_time = time.time()
            
            # Make initial request to get headers and file info
            response = self.session.get(url, **request_params)
            response.raise_for_status()
            
            # Get total file size
            total_size = None
            if 'content-length' in response.headers:
                total_size = int(response.headers['content-length'])
                if resume and start_byte > 0:
                    total_size += start_byte  # Add existing bytes to total
            
            # Check if server supports resume
            if resume and start_byte > 0:
                if response.status_code != 206:  # Partial Content
                    # Server doesn't support resume, start over
                    start_byte = 0
                    response.close()
                    # Remove Range header and try again
                    if 'Range' in request_params['headers']:
                        del request_params['headers']['Range']
                    response = self.session.get(url, **request_params)
                    response.raise_for_status()
                    if 'content-length' in response.headers:
                        total_size = int(response.headers['content-length'])
            
            # Update filename from Content-Disposition header if use_remote_name
            if use_remote_name:
                content_disposition = response.headers.get('content-disposition', '')
                if 'filename=' in content_disposition:
                    # Extract filename from Content-Disposition header
                    import re
                    filename_match = re.search(r'filename[*]?=([^;]+)', content_disposition)
                    if filename_match:
                        remote_filename = filename_match.group(1).strip('"\'')
                        if remote_filename:
                            # Update filepath with the remote filename
                            directory = os.path.dirname(filepath) if os.path.dirname(filepath) else '.'
                            filepath = os.path.join(directory, remote_filename)
            
            # Open file for writing (append mode if resuming)
            mode = 'ab' if (resume and start_byte > 0) else 'wb'
            
            with open(filepath, mode) as f:
                downloaded_bytes = start_byte
                last_progress_time = time.time()
                last_downloaded_bytes = downloaded_bytes
                
                # Download in chunks
                chunk_size = 8192  # 8KB chunks
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:  # Filter out keep-alive chunks
                        f.write(chunk)
                        downloaded_bytes += len(chunk)
                        
                        # Call progress callback if provided
                        if progress_callback:
                            current_time = time.time()
                            # Calculate speed (bytes per second)
                            time_diff = current_time - last_progress_time
                            if time_diff >= 0.1:  # Update every 100ms
                                bytes_diff = downloaded_bytes - last_downloaded_bytes
                                speed = bytes_diff / time_diff if time_diff > 0 else 0
                                
                                progress_callback(downloaded_bytes, total_size, speed)
                                
                                last_progress_time = current_time
                                last_downloaded_bytes = downloaded_bytes
            
            # Final progress callback
            if progress_callback:
                total_time = time.time() - start_time
                avg_speed = downloaded_bytes / total_time if total_time > 0 else 0
                progress_callback(downloaded_bytes, total_size or downloaded_bytes, avg_speed)
            
            download_info = {
                'filepath': os.path.abspath(filepath),
                'size': downloaded_bytes,
                'total_size': total_size,
                'time': time.time() - start_time,
                'success': True,
                'resumed': resume and start_byte > 0,
                'url': url
            }
            
            return download_info
            
        except requests.exceptions.ConnectionError as e:
            diagnostic_info = self._get_connection_diagnostic(url, str(e))
            raise RequestError(
                f"Download failed - Connection error: {str(e)}", 
                diagnostic_info
            )
        except requests.exceptions.Timeout as e:
            diagnostic_info = self._get_timeout_diagnostic(request_params.get('timeout', 30))
            raise RequestError(
                f"Download failed - Request timed out after {request_params.get('timeout', 30)}s: {str(e)}", 
                diagnostic_info
            )
        except requests.exceptions.HTTPError as e:
            if response.status_code == 416:  # Range Not Satisfiable
                raise RequestError(
                    "Resume failed - file may be complete or server doesn't support resume",
                    "Try downloading without resume option"
                )
            else:
                diagnostic_info = self._get_http_diagnostic(response.status_code, response.headers)
                raise RequestError(
                    f"Download failed - HTTP {response.status_code}: {str(e)}", 
                    diagnostic_info
                )
        except OSError as e:
            raise RequestError(
                f"Download failed - File system error: {str(e)}",
                "Check file path permissions and available disk space"
            )
        except Exception as e:
            raise RequestError(
                f"Download failed - Unexpected error: {str(e)}",
                "Please try again or check the URL and file path"
            )
    
    def validate_json(self, text: str) -> tuple[bool, Optional[str]]:
        """
        Validate JSON text.
        
        Args:
            text: JSON text to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            json.loads(text)
            return True, None
        except json.JSONDecodeError as e:
            return False, f"JSON error at line {e.lineno}, column {e.colno}: {e.msg}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def parse_curl_command(self, curl_command: str) -> RequestConfig:
        """
        Parse a cURL command string into a RequestConfig object.
        
        Args:
            curl_command: The cURL command string to parse
            
        Returns:
            RequestConfig object with parsed parameters
            
        Raises:
            ParseError: If the cURL command cannot be parsed
        """
        if not curl_command.strip():
            raise ParseError("Empty cURL command")
        
        # Clean up the command - remove line breaks and extra whitespace
        curl_command = self._clean_curl_command(curl_command)
        
        try:
            # Split the command into tokens using shlex for proper quote handling
            tokens = shlex.split(curl_command)
        except ValueError as e:
            raise ParseError(f"Failed to parse cURL command: {str(e)}")
        
        if not tokens or tokens[0] != 'curl':
            raise ParseError("Command must start with 'curl'")
        
        config = RequestConfig()
        i = 1  # Skip 'curl'
        
        while i < len(tokens):
            token = tokens[i]
            
            if token in ['-X', '--request']:
                # HTTP method
                if i + 1 >= len(tokens):
                    raise ParseError(f"Missing value for {token}")
                config.method = tokens[i + 1].upper()
                i += 2
                
            elif token in ['-H', '--header']:
                # Headers
                if i + 1 >= len(tokens):
                    raise ParseError(f"Missing value for {token}")
                header_str = tokens[i + 1]
                self._parse_header(header_str, config)
                i += 2
                
            elif token in ['-d', '--data', '--data-raw']:
                # Request body
                if i + 1 >= len(tokens):
                    raise ParseError(f"Missing value for {token}")
                config.body = tokens[i + 1]
                config.body_type = "raw"
                # If method not explicitly set and we have data, assume POST
                if config.method == "GET":
                    config.method = "POST"
                i += 2
                
            elif token == '--data-urlencode':
                # URL encoded data
                if i + 1 >= len(tokens):
                    raise ParseError(f"Missing value for {token}")
                config.body = tokens[i + 1]
                config.body_type = "form"
                if config.method == "GET":
                    config.method = "POST"
                i += 2
                
            elif token in ['-u', '--user']:
                # Basic authentication
                if i + 1 >= len(tokens):
                    raise ParseError(f"Missing value for {token}")
                auth_str = tokens[i + 1]
                self._parse_basic_auth(auth_str, config)
                i += 2
                
            elif token in ['-k', '--insecure']:
                # Disable SSL verification
                config.verify_ssl = False
                i += 1
                
            elif token in ['-L', '--location']:
                # Follow redirects
                config.follow_redirects = True
                i += 1
                
            elif token in ['-v', '--verbose']:
                # Verbose mode
                config.verbose = True
                i += 1
                
            elif token in ['-j', '--junk-session-cookies']:
                # Junk session cookies
                config.junk_session_cookies = True
                i += 1
                
            elif token in ['-J', '--remote-header-name']:
                # Use remote header name for downloads - not directly supported in UI
                i += 1
                
            elif token in ['-O', '--remote-name']:
                # Use remote name for downloads
                config.save_to_file = True
                config.use_remote_name = True
                i += 1
                
            elif token in ['--max-time', '-m']:
                # Timeout
                if i + 1 >= len(tokens):
                    raise ParseError(f"Missing value for {token}")
                try:
                    config.timeout = int(tokens[i + 1])
                except ValueError:
                    raise ParseError(f"Invalid timeout value: {tokens[i + 1]}")
                i += 2
                
            elif token.startswith('-') and len(token) > 2 and not token.startswith('--'):
                # Handle combined short flags like -vLJO
                for flag_char in token[1:]:  # Skip the initial '-'
                    if flag_char == 'v':
                        # Verbose mode
                        config.verbose = True
                    elif flag_char == 'L':
                        # Follow redirects
                        config.follow_redirects = True
                    elif flag_char == 'j':
                        # Junk session cookies
                        config.junk_session_cookies = True
                    elif flag_char == 'J':
                        # Use remote header name - not directly supported in UI
                        pass
                    elif flag_char == 'O':
                        # Use remote name for downloads
                        config.save_to_file = True
                        config.use_remote_name = True
                    elif flag_char == 'k':
                        # Insecure SSL
                        config.verify_ssl = False
                    # Add more single-character flags as needed
                i += 1
                
            elif token.startswith('-'):
                # Collect unknown flags into complex_options
                complex_parts = [token]
                i += 1
                
                # Check if this flag has a value (next token doesn't start with -)
                if i < len(tokens) and not tokens[i].startswith('-'):
                    complex_parts.append(tokens[i])
                    i += 1
                
                # Add to complex_options
                if config.complex_options:
                    config.complex_options += " " + " ".join(complex_parts)
                else:
                    config.complex_options = " ".join(complex_parts)
                    
            else:
                # Assume it's the URL if we haven't found one yet
                if not config.url:
                    config.url = token
                i += 1
        
        if not config.url:
            raise ParseError("No URL found in cURL command")
        
        # Auto-detect JSON content type
        if config.body and config.body_type == "raw":
            try:
                json.loads(config.body)
                config.body_type = "json"
                if 'content-type' not in [h.lower() for h in config.headers.keys()]:
                    config.headers['Content-Type'] = 'application/json'
            except (json.JSONDecodeError, ValueError):
                pass
        
        return config
    
    def _clean_curl_command(self, curl_command: str) -> str:
        """Clean up cURL command by removing line breaks and normalizing whitespace."""
        # Remove line continuation characters and normalize whitespace
        cleaned = re.sub(r'\\\s*\n\s*', ' ', curl_command)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned.strip()
    
    def _parse_header(self, header_str: str, config: RequestConfig):
        """Parse a header string and add it to the config."""
        if ':' not in header_str:
            raise ParseError(f"Invalid header format: {header_str}")
        
        key, value = header_str.split(':', 1)
        key = key.strip()
        value = value.strip()
        
        # Handle authorization headers specially
        if key.lower() == 'authorization':
            if value.lower().startswith('bearer '):
                config.auth_type = "bearer"
                config.auth_data['token'] = value[7:]  # Remove 'Bearer '
                config.auth_data['format'] = 'Bearer'  # Store original format
            elif value.lower().startswith('token '):
                # GitHub-style token authentication
                config.auth_type = "bearer"
                config.auth_data['token'] = value[6:]  # Remove 'token '
                config.auth_data['format'] = 'token'  # Store original format
            elif value.lower().startswith('basic '):
                config.auth_type = "basic"
                # Basic auth is already encoded, we'll store it as-is
                config.auth_data['encoded'] = value[6:]  # Remove 'Basic '
        
        config.headers[key] = value
    
    def _parse_basic_auth(self, auth_str: str, config: RequestConfig):
        """Parse basic authentication string."""
        if ':' in auth_str:
            username, password = auth_str.split(':', 1)
            config.auth_type = "basic"
            config.auth_data['username'] = username
            config.auth_data['password'] = password
        else:
            # Username only, password will be prompted
            config.auth_type = "basic"
            config.auth_data['username'] = auth_str
            config.auth_data['password'] = ""
    
    def generate_curl_command(self, config: RequestConfig) -> str:
        """
        Generate a cURL command string from a RequestConfig object.
        
        Args:
            config: RequestConfig object with request parameters
            
        Returns:
            Formatted cURL command string
            
        Raises:
            ValueError: If required parameters are missing
        """
        if not config.url:
            raise ValueError("URL is required to generate cURL command")
        
        parts = ['curl']
        
        # Add method if not GET
        if config.method and config.method.upper() != 'GET':
            parts.extend(['-X', config.method.upper()])
        
        # Add URL (always quote it to handle special characters)
        parts.append(self._quote_if_needed(config.url))
        
        # Add headers
        for key, value in config.headers.items():
            # Skip auto-generated headers that we'll handle separately
            if key.lower() == 'authorization' and config.auth_type != "none":
                continue
            header_str = f"{key}: {value}"
            parts.extend(['-H', self._quote_if_needed(header_str)])
        
        # Add authentication
        if config.auth_type == "bearer" and config.auth_data.get('token'):
            # Use the original format if stored, otherwise default to 'Bearer'
            auth_format = config.auth_data.get('format', 'Bearer')
            auth_header = f"Authorization: {auth_format} {config.auth_data['token']}"
            parts.extend(['-H', self._quote_if_needed(auth_header)])
        elif config.auth_type == "basic":
            if config.auth_data.get('username') and config.auth_data.get('password'):
                auth_str = f"{config.auth_data['username']}:{config.auth_data['password']}"
                parts.extend(['-u', self._quote_if_needed(auth_str)])
            elif config.auth_data.get('username'):
                parts.extend(['-u', self._quote_if_needed(config.auth_data['username'])])
        elif config.auth_type == "apikey":
            # API key authentication - add as header or query param
            key_name = config.auth_data.get('key_name', 'X-API-Key')
            key_value = config.auth_data.get('key_value', '')
            location = config.auth_data.get('location', 'header')
            
            if location == 'header':
                api_header = f"{key_name}: {key_value}"
                parts.extend(['-H', self._quote_if_needed(api_header)])
            # Query param handling would need URL modification, skip for now
        
        # Add request body
        if config.body:
            if config.body_type == "form":
                parts.extend(['--data-urlencode', self._quote_if_needed(config.body)])
            else:
                parts.extend(['-d', self._quote_if_needed(config.body)])
        
        # Add SSL verification flag
        if not config.verify_ssl:
            parts.append('-k')
        
        # Add redirect following
        if config.follow_redirects:
            parts.append('-L')
        
        # Add verbose flag
        if config.verbose:
            parts.append('-v')
        
        # Add download flags
        if config.save_to_file and config.use_remote_name:
            parts.append('-O')
        
        # Add timeout if not default
        if config.timeout != 30:
            parts.extend(['--max-time', str(config.timeout)])
        
        # Add junk session cookies flag
        if config.junk_session_cookies:
            parts.append('-j')
        
        # Add complex options (additional flags not handled by UI)
        if config.complex_options and config.complex_options.strip():
            # Split complex options by lines and filter out comments and empty lines
            complex_lines = config.complex_options.strip().split('\n')
            for line in complex_lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Split the line into individual options and add them
                    import shlex
                    try:
                        complex_parts = shlex.split(line)
                        parts.extend(complex_parts)
                    except ValueError:
                        # If shlex fails, just add the line as-is
                        parts.append(line)
        
        return ' '.join(parts)
    
    def _quote_if_needed(self, value: str) -> str:
        """Quote a string if it contains special characters."""
        # Characters that require quoting in shell commands
        special_chars = [' ', '"', "'", '\\', '&', '|', ';', '(', ')', '<', '>', 
                        '`', '$', '!', '*', '?', '[', ']', '{', '}', '~']
        
        if any(char in value for char in special_chars):
            # Escape existing quotes and wrap in quotes
            escaped = value.replace('\\', '\\\\').replace('"', '\\"')
            return f'"{escaped}"'
        
        return value
    
    def _get_connection_diagnostic(self, url: str, error_msg: str) -> str:
        """Get diagnostic information for connection errors."""
        diagnostics = []
        
        # Parse URL for diagnostics
        from urllib.parse import urlparse
        parsed = urlparse(url)
        
        diagnostics.append("Connection Error Diagnostics:")
        diagnostics.append(f"• Host: {parsed.hostname}")
        diagnostics.append(f"• Port: {parsed.port or (443 if parsed.scheme == 'https' else 80)}")
        diagnostics.append(f"• Protocol: {parsed.scheme}")
        
        # Common connection issues
        if "name or service not known" in error_msg.lower() or "nodename nor servname provided" in error_msg.lower():
            diagnostics.append("• Issue: DNS resolution failed")
            diagnostics.append("• Suggestion: Check if the hostname is correct and accessible")
        elif "connection refused" in error_msg.lower():
            diagnostics.append("• Issue: Server refused connection")
            diagnostics.append("• Suggestion: Check if the server is running and port is correct")
        elif "timeout" in error_msg.lower():
            diagnostics.append("• Issue: Connection timed out")
            diagnostics.append("• Suggestion: Server may be slow or unreachable")
        elif "network is unreachable" in error_msg.lower():
            diagnostics.append("• Issue: Network routing problem")
            diagnostics.append("• Suggestion: Check your internet connection")
        
        return "\n".join(diagnostics)
    
    def _get_timeout_diagnostic(self, timeout_value: int) -> str:
        """Get diagnostic information for timeout errors."""
        diagnostics = []
        
        diagnostics.append("Timeout Error Diagnostics:")
        diagnostics.append(f"• Configured timeout: {timeout_value} seconds")
        
        if timeout_value < 10:
            diagnostics.append("• Issue: Timeout may be too short")
            diagnostics.append("• Suggestion: Try increasing timeout to 30+ seconds")
        elif timeout_value < 30:
            diagnostics.append("• Issue: Server is responding slowly")
            diagnostics.append("• Suggestion: Try increasing timeout or check server status")
        else:
            diagnostics.append("• Issue: Server is not responding within reasonable time")
            diagnostics.append("• Suggestion: Check server status or network connectivity")
        
        diagnostics.append("• Troubleshooting: Try the request in a browser or with curl command line")
        
        return "\n".join(diagnostics)
    
    def _get_ssl_diagnostic(self, url: str, error_msg: str) -> str:
        """Get diagnostic information for SSL errors."""
        diagnostics = []
        
        diagnostics.append("SSL Error Diagnostics:")
        diagnostics.append(f"• URL: {url}")
        
        if "certificate verify failed" in error_msg.lower():
            diagnostics.append("• Issue: SSL certificate verification failed")
            diagnostics.append("• Suggestion: Certificate may be expired, self-signed, or invalid")
            diagnostics.append("• Workaround: Disable SSL verification (not recommended for production)")
        elif "ssl: wrong_version_number" in error_msg.lower():
            diagnostics.append("• Issue: SSL version mismatch")
            diagnostics.append("• Suggestion: Server may not support HTTPS on this port")
        elif "ssl: handshake_failure" in error_msg.lower():
            diagnostics.append("• Issue: SSL handshake failed")
            diagnostics.append("• Suggestion: Server and client SSL/TLS versions may be incompatible")
        
        diagnostics.append("• Troubleshooting: Check certificate validity with browser or openssl")
        
        return "\n".join(diagnostics)
    
    def _get_http_diagnostic(self, status_code: int, headers: dict) -> str:
        """Get diagnostic information for HTTP errors."""
        diagnostics = []
        
        diagnostics.append(f"HTTP {status_code} Error Diagnostics:")
        
        # Status code specific diagnostics
        if status_code == 400:
            diagnostics.append("• Issue: Bad Request - malformed request syntax")
            diagnostics.append("• Suggestion: Check request body format, headers, and parameters")
        elif status_code == 401:
            diagnostics.append("• Issue: Unauthorized - authentication required")
            diagnostics.append("• Suggestion: Check authentication credentials")
        elif status_code == 403:
            diagnostics.append("• Issue: Forbidden - insufficient permissions")
            diagnostics.append("• Suggestion: Check if your credentials have required permissions")
        elif status_code == 404:
            diagnostics.append("• Issue: Not Found - resource doesn't exist")
            diagnostics.append("• Suggestion: Verify the URL path and endpoint")
        elif status_code == 405:
            diagnostics.append("• Issue: Method Not Allowed")
            diagnostics.append("• Suggestion: Check if the HTTP method is supported by this endpoint")
        elif status_code == 429:
            diagnostics.append("• Issue: Too Many Requests - rate limit exceeded")
            diagnostics.append("• Suggestion: Wait before retrying or check rate limit headers")
        elif status_code >= 500:
            diagnostics.append("• Issue: Server Error - problem on server side")
            diagnostics.append("• Suggestion: Try again later or contact server administrator")
        
        # Check for helpful response headers
        if 'retry-after' in headers:
            diagnostics.append(f"• Retry After: {headers['retry-after']} seconds")
        
        if 'www-authenticate' in headers:
            diagnostics.append(f"• Authentication Method: {headers['www-authenticate']}")
        
        return "\n".join(diagnostics)
    
    def _get_general_diagnostic(self, error_msg: str) -> str:
        """Get general diagnostic information for other errors."""
        diagnostics = []
        
        diagnostics.append("General Error Diagnostics:")
        diagnostics.append(f"• Error: {error_msg}")
        
        # Common issues
        if "json" in error_msg.lower():
            diagnostics.append("• Issue: JSON parsing or formatting error")
            diagnostics.append("• Suggestion: Check JSON syntax in request body")
        elif "encoding" in error_msg.lower():
            diagnostics.append("• Issue: Character encoding problem")
            diagnostics.append("• Suggestion: Check response encoding or content type")
        elif "memory" in error_msg.lower():
            diagnostics.append("• Issue: Memory or resource limitation")
            diagnostics.append("• Suggestion: Response may be too large")
        
        diagnostics.append("• Troubleshooting: Enable verbose logging for more details")
        
        return "\n".join(diagnostics)
    
    def generate_curl_from_request_data(self, method: str, url: str, 
                                      headers: Optional[Dict[str, str]] = None,
                                      body: Optional[str] = None,
                                      auth_type: str = "none",
                                      auth_data: Optional[Dict[str, str]] = None,
                                      **kwargs) -> str:
        """
        Generate cURL command from individual request parameters.
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Optional headers dictionary
            body: Optional request body
            auth_type: Authentication type
            auth_data: Authentication data
            **kwargs: Additional options
            
        Returns:
            Formatted cURL command string
        """
        config = RequestConfig(
            method=method,
            url=url,
            headers=headers or {},
            body=body,
            auth_type=auth_type,
            auth_data=auth_data or {},
            follow_redirects=kwargs.get('follow_redirects', True),
            verify_ssl=kwargs.get('verify_ssl', True),
            timeout=kwargs.get('timeout', 30)
        )
        
        # Auto-detect body type
        if body:
            try:
                json.loads(body)
                config.body_type = "json"
            except (json.JSONDecodeError, ValueError):
                config.body_type = "raw"
        
        return self.generate_curl_command(config)