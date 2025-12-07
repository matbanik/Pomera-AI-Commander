"""
MCP Manager Widget - UI for MCP Server Control

This module provides a graphical interface for managing the MCP server,
allowing users to start/stop the server and monitor its status.

Features:
- Start/Stop MCP server (as detached background process)
- Detect running server on startup
- View server status and connection info
- View available tools
- Server log display
- Dynamic path configuration for Claude Desktop/Cursor
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import sys
import os
import json
import logging
import subprocess
import signal
import atexit
from datetime import datetime
from typing import Optional, Callable

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# PID file for tracking server process
PID_FILE = os.path.join(PROJECT_ROOT, ".mcp_server.pid")


def get_pomera_executable_path() -> tuple:
    """
    Get the path to the Pomera executable/script for MCP server mode.
    
    Returns:
        Tuple of (command, args) for running the MCP server.
        For frozen exe: ("pomera.exe", ["--mcp-server"])
        For Python: ("python", ["pomera.py", "--mcp-server"])
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        exe_path = sys.executable
        return (exe_path, ["--mcp-server"])
    else:
        # Running as Python script
        pomera_script = os.path.join(PROJECT_ROOT, "pomera.py")
        return (sys.executable, [pomera_script, "--mcp-server"])


def get_mcp_config_json() -> str:
    """
    Generate MCP configuration JSON with dynamic path.
    
    Returns:
        JSON string for claude_desktop_config.json or .cursor/mcp.json
    """
    command, args = get_pomera_executable_path()
    
    # Format path for JSON (use forward slashes)
    command = command.replace("\\", "/")
    args = [arg.replace("\\", "/") for arg in args]
    
    config = {
        "mcpServers": {
            "pomera": {
                "command": command,
                "args": args
            }
        }
    }
    return json.dumps(config, indent=2)


def read_pid_file() -> Optional[int]:
    """Read the PID from the PID file if it exists."""
    try:
        if os.path.exists(PID_FILE):
            with open(PID_FILE, 'r') as f:
                return int(f.read().strip())
    except (ValueError, IOError):
        pass
    return None


def write_pid_file(pid: int):
    """Write the PID to the PID file."""
    try:
        with open(PID_FILE, 'w') as f:
            f.write(str(pid))
    except IOError as e:
        logging.getLogger(__name__).error(f"Failed to write PID file: {e}")


def remove_pid_file():
    """Remove the PID file."""
    try:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
    except IOError:
        pass


def is_process_running(pid: int) -> bool:
    """Check if a process with the given PID is running."""
    if pid is None:
        return False
    try:
        if sys.platform == "win32":
            # Windows: use tasklist
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True,
                text=True
            )
            return str(pid) in result.stdout
        else:
            # Unix: send signal 0 to check if process exists
            os.kill(pid, 0)
            return True
    except (OSError, subprocess.SubprocessError):
        return False


def find_running_mcp_server() -> Optional[int]:
    """
    Find a running MCP server process.
    
    Returns:
        PID of running server, or None if not found
    """
    # First check PID file
    pid = read_pid_file()
    if pid and is_process_running(pid):
        return pid
    
    # Clean up stale PID file
    remove_pid_file()
    return None


class MCPServerProcess:
    """Manages the MCP server as a detached subprocess that persists after app close."""
    
    def __init__(self, log_queue: queue.Queue, on_started: Callable, on_stopped: Callable):
        self.log_queue = log_queue
        self.on_started = on_started
        self.on_stopped = on_stopped
        self.process: Optional[subprocess.Popen] = None
        self.monitor_thread: Optional[threading.Thread] = None
        self._stopping = False
        self._external_pid: Optional[int] = None  # PID of externally started server
    
    def check_existing_server(self) -> bool:
        """
        Check if a server is already running.
        
        Returns:
            True if server is running, False otherwise
        """
        pid = find_running_mcp_server()
        if pid:
            self._external_pid = pid
            self.log_queue.put(("INFO", f"Found existing MCP server (PID: {pid})"))
            return True
        return False
    
    def start(self, detached: bool = False) -> bool:
        """
        Start the MCP server as a subprocess for testing.
        
        Args:
            detached: If True, server runs with minimal parent connection.
                     Note: stdio MCP servers are designed to be started by MCP clients
                     (Claude Desktop, Cursor). This test mode captures logs for debugging.
        """
        # Check if already running
        if self.is_running():
            self.log_queue.put(("WARNING", "Server is already running"))
            return False
        
        try:
            command, args = get_pomera_executable_path()
            full_args = [command] + args + ["--debug"]
            
            self.log_queue.put(("INFO", f"Starting MCP server: {' '.join(full_args)}"))
            
            # Platform-specific process creation
            # Note: We always capture stderr for logging, but stdin/stdout are for MCP protocol
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP
                if detached:
                    creation_flags |= subprocess.CREATE_NO_WINDOW
                
                self.process = subprocess.Popen(
                    full_args,
                    stdout=subprocess.PIPE,  # Capture MCP responses for logging
                    stderr=subprocess.PIPE,  # Capture debug logs
                    stdin=subprocess.PIPE,   # For sending MCP requests (testing)
                    creationflags=creation_flags,
                    text=True,
                    bufsize=1
                )
            else:
                # Unix
                self.process = subprocess.Popen(
                    full_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    start_new_session=detached
                )
            
            self._stopping = False
            self._external_pid = None
            
            # Write PID file for tracking
            write_pid_file(self.process.pid)
            
            # Start monitoring thread to capture stderr logs
            if self.process.stderr:
                self.monitor_thread = threading.Thread(target=self._monitor_process, daemon=True)
                self.monitor_thread.start()
            
            self.log_queue.put(("INFO", f"Server started (PID: {self.process.pid})"))
            self.log_queue.put(("INFO", "Server is running in test mode - logs will be captured"))
            self.log_queue.put(("INFO", "Note: For production use, configure your MCP client to start the server"))
            
            self.on_started()
            return True
            
        except Exception as e:
            self.log_queue.put(("ERROR", f"Failed to start server: {str(e)}"))
            return False
    
    def stop(self):
        """Stop the MCP server subprocess."""
        pid_to_stop = None
        
        if self.process and self.process.poll() is None:
            pid_to_stop = self.process.pid
        elif self._external_pid and is_process_running(self._external_pid):
            pid_to_stop = self._external_pid
        
        if not pid_to_stop:
            self.log_queue.put(("WARNING", "No server process to stop"))
            return
        
        self._stopping = True
        self.log_queue.put(("INFO", f"Stopping MCP server (PID: {pid_to_stop})..."))
        
        try:
            if sys.platform == "win32":
                # Windows: use taskkill
                subprocess.run(["taskkill", "/F", "/PID", str(pid_to_stop)], 
                             capture_output=True)
            else:
                # Unix: send SIGTERM then SIGKILL
                os.kill(pid_to_stop, signal.SIGTERM)
                # Give it a moment to terminate
                import time
                time.sleep(1)
                if is_process_running(pid_to_stop):
                    os.kill(pid_to_stop, signal.SIGKILL)
            
            self.log_queue.put(("INFO", "Server stopped"))
        except Exception as e:
            self.log_queue.put(("ERROR", f"Error stopping server: {str(e)}"))
        finally:
            self.process = None
            self._external_pid = None
            remove_pid_file()
            self.on_stopped()
    
    def _monitor_process(self):
        """Monitor the server process and capture output."""
        if not self.process or not self.process.stderr:
            return
        
        # Read stderr for log messages
        try:
            for line in self.process.stderr:
                if self._stopping:
                    break
                line = line.strip()
                if line:
                    # Parse log level from line if present
                    # Format: "2024-12-06 15:33:17,123 - module - LEVEL - message"
                    if " - CRITICAL - " in line:
                        self.log_queue.put(("CRITICAL", line))
                    elif " - ERROR - " in line:
                        self.log_queue.put(("ERROR", line))
                    elif " - WARNING - " in line:
                        self.log_queue.put(("WARNING", line))
                    elif " - DEBUG - " in line:
                        self.log_queue.put(("DEBUG", line))
                    elif " - INFO - " in line:
                        self.log_queue.put(("INFO", line))
                    else:
                        # Default to INFO for unrecognized format
                        self.log_queue.put(("INFO", line))
        except Exception as e:
            self.log_queue.put(("ERROR", f"Error reading server output: {e}"))
        
        # Check if process ended unexpectedly
        if self.process and not self._stopping:
            return_code = self.process.poll()
            if return_code is not None:
                self.log_queue.put(("WARNING", f"Server process ended (exit code: {return_code})"))
                remove_pid_file()
                self.on_stopped()
    
    def is_running(self) -> bool:
        """Check if the server is running (either our process or external)."""
        if self.process is not None and self.process.poll() is None:
            return True
        if self._external_pid and is_process_running(self._external_pid):
            return True
        # Also check PID file
        pid = find_running_mcp_server()
        if pid:
            self._external_pid = pid
            return True
        return False
    
    def get_pid(self) -> Optional[int]:
        """Get the PID of the running server."""
        if self.process and self.process.poll() is None:
            return self.process.pid
        if self._external_pid and is_process_running(self._external_pid):
            return self._external_pid
        return find_running_mcp_server()


class MCPManagerWidget(ttk.Frame):
    """
    MCP Manager Widget for controlling the MCP server.
    
    Provides UI for:
    - Starting/stopping the server
    - Viewing server status
    - Viewing available tools
    - Displaying server logs
    - Configuration help
    """
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.logger = app.logger if hasattr(app, 'logger') else logging.getLogger(__name__)
        
        # Server state
        self.server_process: Optional[MCPServerProcess] = None
        self.server_running = False
        self.log_queue = queue.Queue()
        
        # Tool registry for display
        self.registry = None
        self._load_registry()
        
        self.create_widgets()
        self.start_log_polling()
        
        # Check for existing server after UI is ready
        self.after(500, self.check_existing_server)
    
    def _load_registry(self):
        """Load tool registry for display purposes."""
        try:
            from core.mcp.tool_registry import ToolRegistry
            self.registry = ToolRegistry()
        except Exception as e:
            self.logger.error(f"Failed to load tool registry: {e}")
            self.registry = None
    
    def create_widgets(self):
        """Create the widget interface."""
        # Main container with notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Server Control Tab
        self.control_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.control_frame, text="Server Control")
        self.create_control_tab()
        
        # Tools Tab
        self.tools_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tools_frame, text="Available Tools")
        self.create_tools_tab()
        
        # Configuration Tab
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text="Configuration")
        self.create_config_tab()
        
        # Test Tool Tab
        self.test_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.test_frame, text="Test Tool")
        self.create_test_tab()
        
        # Log Tab
        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text="Server Log")
        self.create_log_tab()
    
    def create_control_tab(self):
        """Create the server control tab."""
        # Status frame
        status_frame = ttk.LabelFrame(self.control_frame, text="Server Status", padding=10)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Status indicator
        status_row = ttk.Frame(status_frame)
        status_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(status_row, text="Status:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.status_indicator = tk.Canvas(status_row, width=16, height=16, highlightthickness=0)
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 5))
        self._draw_status_indicator(False)
        
        self.status_label = ttk.Label(status_row, text="Stopped", font=("", 10, "bold"))
        self.status_label.pack(side=tk.LEFT)
        
        # Server info
        info_frame = ttk.Frame(status_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text="Server:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(info_frame, text="pomera-mcp-server v0.1.0").pack(side=tk.LEFT)
        
        tools_frame = ttk.Frame(status_frame)
        tools_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(tools_frame, text="Tools:").pack(side=tk.LEFT, padx=(0, 10))
        tool_count = len(self.registry) if self.registry else 0
        self.tools_count_label = ttk.Label(tools_frame, text=f"{tool_count} available")
        self.tools_count_label.pack(side=tk.LEFT)
        
        # PID display
        pid_frame = ttk.Frame(status_frame)
        pid_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(pid_frame, text="Process ID:").pack(side=tk.LEFT, padx=(0, 10))
        self.pid_label = ttk.Label(pid_frame, text="Not running")
        self.pid_label.pack(side=tk.LEFT)
        
        # Control buttons
        button_frame = ttk.LabelFrame(self.control_frame, text="Controls", padding=10)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        btn_row = ttk.Frame(button_frame)
        btn_row.pack(fill=tk.X)
        
        self.start_btn = ttk.Button(btn_row, text="▶ Start Server", command=self.start_server, width=15)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(btn_row, text="■ Stop Server", command=self.stop_server, width=15, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_row, text="🔄 Refresh Tools", command=self.refresh_tools, width=15).pack(side=tk.LEFT, padx=5)
        
        # Info note
        note_frame = ttk.LabelFrame(self.control_frame, text="How to Use", padding=10)
        note_frame.pack(fill=tk.X, padx=5, pady=5)
        
        note_text = (
            "The MCP server exposes Pomera's text tools via the Model Context Protocol.\n\n"
            "Option 1: Start from here (for testing/debugging)\n"
            "  • Click 'Start Server' to test the MCP server\n"
            "  • Server logs will be captured in the 'Server Log' tab\n"
            "  • Server will stop when Pomera closes (stdio transport limitation)\n\n"
            "Option 2: Configure your AI client (RECOMMENDED for production)\n"
            "  • Copy the configuration from the 'Configuration' tab\n"
            "  • Add it to your Claude Desktop or Cursor config\n"
            "  • The client will start/stop the server automatically as needed\n"
            "  • This is the standard way to use MCP stdio servers"
        )
        ttk.Label(note_frame, text=note_text, wraplength=500, justify=tk.LEFT).pack(anchor=tk.W)
    
    def create_tools_tab(self):
        """Create the available tools tab."""
        # Use PanedWindow for resizable split between list and details
        paned = ttk.PanedWindow(self.tools_frame, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top pane: Tools list with scrollbar
        list_frame = ttk.Frame(paned)
        
        # Treeview for tools
        columns = ("name", "description")
        self.tools_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        self.tools_tree.heading("name", text="Tool Name")
        self.tools_tree.heading("description", text="Description")
        
        self.tools_tree.column("name", width=200, minwidth=150)
        self.tools_tree.column("description", width=400, minwidth=200)
        
        # Scrollbar for treeview
        tree_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tools_tree.yview)
        self.tools_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.tools_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        paned.add(list_frame, weight=1)
        
        # Populate tools
        self._populate_tools_list()
        
        # Bottom pane: Tool details
        details_frame = ttk.LabelFrame(paned, text="Tool Details", padding=10)
        
        self.tool_details = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.tool_details.pack(fill=tk.BOTH, expand=True)
        
        paned.add(details_frame, weight=1)
        
        # Bind selection
        self.tools_tree.bind("<<TreeviewSelect>>", self._on_tool_select)
    
    def create_config_tab(self):
        """Create the configuration tab."""
        # Get dynamic configuration
        command, args = get_pomera_executable_path()
        
        # Path selection frame
        path_frame = ttk.LabelFrame(self.config_frame, text="Pomera Path Configuration", padding=10)
        path_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Execution mode label
        if getattr(sys, 'frozen', False):
            mode_text = "Mode: Compiled executable"
            default_path = command
        else:
            mode_text = "Mode: Python script"
            default_path = args[0] if args else os.path.join(PROJECT_ROOT, "pomera.py")
        
        ttk.Label(path_frame, text=mode_text, font=("", 9, "bold")).pack(anchor=tk.W)
        
        # Path entry row
        path_row = ttk.Frame(path_frame)
        path_row.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(path_row, text="Path:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.path_var = tk.StringVar(value=default_path)
        self.path_entry = ttk.Entry(path_row, textvariable=self.path_var, width=60)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(path_row, text="Select...", command=self._select_pomera_path).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(path_row, text="Apply", command=self._apply_path_config).pack(side=tk.LEFT)
        
        # Python executable row (only for script mode)
        if not getattr(sys, 'frozen', False):
            python_row = ttk.Frame(path_frame)
            python_row.pack(fill=tk.X, pady=(5, 0))
            
            ttk.Label(python_row, text="Python:").pack(side=tk.LEFT, padx=(0, 5))
            
            self.python_var = tk.StringVar(value=sys.executable)
            self.python_entry = ttk.Entry(python_row, textvariable=self.python_var, width=60)
            self.python_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
            
            ttk.Button(python_row, text="Select...", command=self._select_python_path).pack(side=tk.LEFT)
        
        # Claude Desktop config
        claude_frame = ttk.LabelFrame(self.config_frame, text="Claude Desktop Configuration", padding=10)
        claude_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(claude_frame, text="Add to claude_desktop_config.json:").pack(anchor=tk.W)
        
        self.claude_config = scrolledtext.ScrolledText(claude_frame, height=8, wrap=tk.WORD)
        self.claude_config.pack(fill=tk.X, pady=5)
        
        claude_btn_row = ttk.Frame(claude_frame)
        claude_btn_row.pack(fill=tk.X)
        ttk.Button(claude_btn_row, text="Copy to Clipboard", 
                  command=self._copy_claude_config).pack(side=tk.LEFT)
        
        # Cursor config
        cursor_frame = ttk.LabelFrame(self.config_frame, text="Cursor Configuration", padding=10)
        cursor_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(cursor_frame, text="Add to .cursor/mcp.json in your project:").pack(anchor=tk.W)
        
        self.cursor_config = scrolledtext.ScrolledText(cursor_frame, height=8, wrap=tk.WORD)
        self.cursor_config.pack(fill=tk.X, pady=5)
        
        cursor_btn_row = ttk.Frame(cursor_frame)
        cursor_btn_row.pack(fill=tk.X)
        ttk.Button(cursor_btn_row, text="Copy to Clipboard", 
                  command=self._copy_cursor_config).pack(side=tk.LEFT)
        
        # Command line usage
        cli_frame = ttk.LabelFrame(self.config_frame, text="Command Line Usage", padding=10)
        cli_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.cli_config = scrolledtext.ScrolledText(cli_frame, height=6, wrap=tk.WORD)
        self.cli_config.pack(fill=tk.X, pady=5)
        
        # Initial population of config text areas
        self._update_config_displays()
    
    def _select_pomera_path(self):
        """Open file dialog to select Pomera executable or script."""
        from tkinter import filedialog
        
        if getattr(sys, 'frozen', False):
            filetypes = [("Executable", "*.exe"), ("All files", "*.*")]
            title = "Select pomera.exe"
        else:
            filetypes = [("Python script", "*.py"), ("All files", "*.*")]
            title = "Select pomera.py"
        
        path = filedialog.askopenfilename(
            title=title,
            filetypes=filetypes,
            initialdir=os.path.dirname(self.path_var.get()) if self.path_var.get() else PROJECT_ROOT
        )
        
        if path:
            self.path_var.set(path)
            self._update_config_displays()
    
    def _select_python_path(self):
        """Open file dialog to select Python executable."""
        from tkinter import filedialog
        
        if sys.platform == "win32":
            filetypes = [("Executable", "*.exe"), ("All files", "*.*")]
        else:
            filetypes = [("All files", "*.*")]
        
        path = filedialog.askopenfilename(
            title="Select Python executable",
            filetypes=filetypes,
            initialdir=os.path.dirname(self.python_var.get()) if hasattr(self, 'python_var') and self.python_var.get() else None
        )
        
        if path:
            self.python_var.set(path)
            self._update_config_displays()
    
    def _apply_path_config(self):
        """Apply the current path configuration and update displays."""
        self._update_config_displays()
        self._add_log("INFO", "Configuration updated with new path")
    
    def _generate_config_json(self) -> str:
        """Generate MCP configuration JSON based on current path settings."""
        pomera_path = self.path_var.get().replace("\\", "/")
        
        if getattr(sys, 'frozen', False):
            # Compiled executable mode
            config = {
                "mcpServers": {
                    "pomera": {
                        "command": pomera_path,
                        "args": ["--mcp-server"]
                    }
                }
            }
        else:
            # Python script mode
            python_path = self.python_var.get().replace("\\", "/") if hasattr(self, 'python_var') else sys.executable.replace("\\", "/")
            config = {
                "mcpServers": {
                    "pomera": {
                        "command": python_path,
                        "args": [pomera_path, "--mcp-server"]
                    }
                }
            }
        
        return json.dumps(config, indent=2)
    
    def _generate_cli_text(self) -> str:
        """Generate CLI usage text based on current path settings."""
        pomera_path = self.path_var.get()
        
        if getattr(sys, 'frozen', False):
            return f"""# List available tools:
"{pomera_path}" --mcp-server --list-tools

# Run server (for manual testing):
"{pomera_path}" --mcp-server

# Run with debug logging:
"{pomera_path}" --mcp-server --debug"""
        else:
            python_path = self.python_var.get() if hasattr(self, 'python_var') else sys.executable
            return f"""# List available tools:
"{python_path}" "{pomera_path}" --mcp-server --list-tools

# Run server (for manual testing):
"{python_path}" "{pomera_path}" --mcp-server

# Run with debug logging:
"{python_path}" "{pomera_path}" --mcp-server --debug"""
    
    def _update_config_displays(self):
        """Update all configuration text displays with current path settings."""
        config_json = self._generate_config_json()
        cli_text = self._generate_cli_text()
        
        # Update Claude config
        self.claude_config.config(state=tk.NORMAL)
        self.claude_config.delete("1.0", tk.END)
        self.claude_config.insert(tk.END, config_json)
        self.claude_config.config(state=tk.DISABLED)
        
        # Update Cursor config
        self.cursor_config.config(state=tk.NORMAL)
        self.cursor_config.delete("1.0", tk.END)
        self.cursor_config.insert(tk.END, config_json)
        self.cursor_config.config(state=tk.DISABLED)
        
        # Update CLI text
        self.cli_config.config(state=tk.NORMAL)
        self.cli_config.delete("1.0", tk.END)
        self.cli_config.insert(tk.END, cli_text)
        self.cli_config.config(state=tk.DISABLED)
    
    def _copy_claude_config(self):
        """Copy Claude Desktop config to clipboard."""
        config = self._generate_config_json()
        self._copy_to_clipboard(config)
    
    def _copy_cursor_config(self):
        """Copy Cursor config to clipboard."""
        config = self._generate_config_json()
        self._copy_to_clipboard(config)
    
    def create_test_tab(self):
        """Create the test tool tab for sending MCP requests."""
        # Tool selection frame
        select_frame = ttk.LabelFrame(self.test_frame, text="Select Tool", padding=10)
        select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Tool dropdown
        tool_row = ttk.Frame(select_frame)
        tool_row.pack(fill=tk.X)
        
        ttk.Label(tool_row, text="Tool:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.test_tool_var = tk.StringVar()
        self.test_tool_combo = ttk.Combobox(
            tool_row,
            textvariable=self.test_tool_var,
            state="readonly",
            width=40
        )
        self.test_tool_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.test_tool_combo.bind("<<ComboboxSelected>>", self._on_test_tool_select)
        
        # Parameters frame
        params_frame = ttk.LabelFrame(self.test_frame, text="Parameters (JSON)", padding=10)
        params_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Parameter hints label
        self.param_hints_label = ttk.Label(params_frame, text="Select a tool to see required parameters", foreground="gray")
        self.param_hints_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Parameters text area
        self.test_params = scrolledtext.ScrolledText(params_frame, height=8, wrap=tk.WORD)
        self.test_params.pack(fill=tk.BOTH, expand=True)
        self.test_params.insert(tk.END, "{}")
        
        # Execute button frame
        exec_frame = ttk.Frame(self.test_frame)
        exec_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.test_execute_btn = ttk.Button(
            exec_frame, 
            text="▶ Execute Tool", 
            command=self._execute_test_tool,
            width=20
        )
        self.test_execute_btn.pack(side=tk.LEFT)
        
        ttk.Button(
            exec_frame, 
            text="Clear Result", 
            command=self._clear_test_result,
            width=15
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Server-only checkbox
        self.test_server_only_var = tk.BooleanVar(value=False)
        self.test_server_only_cb = ttk.Checkbutton(
            exec_frame,
            text="Test via server only",
            variable=self.test_server_only_var
        )
        self.test_server_only_cb.pack(side=tk.LEFT, padx=(20, 0))
        
        # Status label
        self.test_status_label = ttk.Label(exec_frame, text="")
        self.test_status_label.pack(side=tk.RIGHT)
        
        # Result frame
        result_frame = ttk.LabelFrame(self.test_frame, text="Result", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.test_result = scrolledtext.ScrolledText(result_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.test_result.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for result display
        self.test_result.tag_configure("success", foreground="green")
        self.test_result.tag_configure("error", foreground="red")
        self.test_result.tag_configure("info", foreground="blue")
        
        # Populate tool dropdown (after all widgets are created)
        self._populate_test_tool_combo()
    
    def _populate_test_tool_combo(self):
        """Populate the test tool dropdown with available tools."""
        if self.registry:
            tool_names = [tool.name for tool in self.registry.list_tools()]
            self.test_tool_combo['values'] = sorted(tool_names)
            if tool_names:
                self.test_tool_combo.set(sorted(tool_names)[0])
                self._on_test_tool_select(None)
    
    def _on_test_tool_select(self, event):
        """Handle tool selection in test tab - show parameter hints."""
        tool_name = self.test_tool_var.get()
        if not tool_name or not self.registry:
            return
        
        # Check if UI elements exist yet
        if not hasattr(self, 'param_hints_label') or not hasattr(self, 'test_params'):
            return
        
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return
        
        mcp_tool = tool.to_mcp_tool()
        schema = mcp_tool.inputSchema
        
        # Build parameter hints
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        hints = []
        for param_name, param_info in properties.items():
            param_type = param_info.get("type", "any")
            param_desc = param_info.get("description", "")
            is_required = param_name in required
            req_marker = "*" if is_required else ""
            hints.append(f"  • {param_name}{req_marker} ({param_type}): {param_desc[:50]}...")
        
        if hints:
            hint_text = "Parameters (* = required):\n" + "\n".join(hints[:5])
            if len(hints) > 5:
                hint_text += f"\n  ... and {len(hints) - 5} more"
        else:
            hint_text = "No parameters required"
        
        self.param_hints_label.config(text=hint_text)
        
        # Generate example JSON with ALL parameters (required + optional with defaults)
        example = {}
        for param_name, param_info in properties.items():
            param_type = param_info.get("type", "string")
            is_required = param_name in required
            
            # Use default value if available, otherwise generate placeholder
            if "default" in param_info:
                example[param_name] = param_info["default"]
            elif "enum" in param_info:
                example[param_name] = param_info["enum"][0]
            elif param_type == "string":
                example[param_name] = f"<{param_name}>" if is_required else ""
            elif param_type == "integer":
                example[param_name] = 0
            elif param_type == "number":
                example[param_name] = 0
            elif param_type == "boolean":
                example[param_name] = False
            else:
                example[param_name] = f"<{param_name}>" if is_required else None
        
        self.test_params.delete("1.0", tk.END)
        self.test_params.insert(tk.END, json.dumps(example, indent=2))
    
    def _execute_test_tool(self):
        """Execute the selected tool with the provided parameters."""
        tool_name = self.test_tool_var.get()
        if not tool_name:
            self._show_test_error("Please select a tool")
            return
        
        # Parse parameters
        try:
            params_text = self.test_params.get("1.0", tk.END).strip()
            params = json.loads(params_text) if params_text else {}
        except json.JSONDecodeError as e:
            self._show_test_error(f"Invalid JSON parameters: {e}")
            return
        
        # Check if "server only" mode is enabled
        server_only = self.test_server_only_var.get()
        server_running = self.server_process and self.server_process.is_running() and self.server_process.process
        
        if server_only and not server_running:
            self._show_test_error("Server is not running. Start the server first or uncheck 'Test via server only'.")
            return
        
        # Check if server is running
        if server_running:
            # Send request to running server via stdin
            self._execute_via_server(tool_name, params)
        else:
            # Execute directly via registry
            self._execute_directly(tool_name, params)
    
    def _execute_via_server(self, tool_name: str, params: dict):
        """Execute tool by sending request to the running server's stdin."""
        self.test_status_label.config(text="Sending request...", foreground="blue")
        self.update_idletasks()
        
        try:
            # Build MCP request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": params
                }
            }
            
            # Need to send initialize first if not already done
            init_request = {
                "jsonrpc": "2.0",
                "id": 0,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "pomera-test", "version": "1.0"}
                }
            }
            
            # Send requests
            process = self.server_process.process
            if process and process.stdin and process.stdout:
                # Send initialize
                process.stdin.write(json.dumps(init_request) + "\n")
                process.stdin.flush()
                
                # Read init response
                init_response = process.stdout.readline()
                
                # Send tool call
                process.stdin.write(json.dumps(request) + "\n")
                process.stdin.flush()
                
                # Read response with timeout
                response_line = process.stdout.readline()
                if response_line:
                    response = json.loads(response_line)
                    self._show_test_result(response)
                else:
                    self._show_test_error("No response from server")
            else:
                self._show_test_error("Server stdin/stdout not available")
                
        except Exception as e:
            self._show_test_error(f"Error communicating with server: {e}")
    
    def _execute_directly(self, tool_name: str, params: dict):
        """Execute tool directly via the registry (no server needed)."""
        self.test_status_label.config(text="Executing directly...", foreground="blue")
        self.update_idletasks()
        
        if not self.registry:
            self._show_test_error("Tool registry not available")
            return
        
        try:
            result = self.registry.execute(tool_name, params)
            
            # Format result
            response = {
                "success": not result.isError,
                "content": result.content
            }
            self._show_test_result(response)
            
        except Exception as e:
            self._show_test_error(f"Execution error: {e}")
    
    def _show_test_result(self, response: dict):
        """Display test result in the result area."""
        self.test_result.config(state=tk.NORMAL)
        self.test_result.delete("1.0", tk.END)
        
        # Check if it's an error response
        if "error" in response:
            self.test_status_label.config(text="Error", foreground="red")
            self.test_result.insert(tk.END, "ERROR:\n", "error")
            self.test_result.insert(tk.END, json.dumps(response["error"], indent=2))
        elif response.get("success") == False or response.get("isError"):
            self.test_status_label.config(text="Tool returned error", foreground="orange")
            self.test_result.insert(tk.END, "Tool Error:\n", "error")
            content = response.get("content", response.get("result", {}).get("content", []))
            if isinstance(content, list):
                for item in content:
                    if item.get("type") == "text":
                        self.test_result.insert(tk.END, item.get("text", ""))
            else:
                self.test_result.insert(tk.END, json.dumps(content, indent=2))
        else:
            self.test_status_label.config(text="Success", foreground="green")
            self.test_result.insert(tk.END, "Result:\n", "success")
            
            # Extract content from MCP response
            content = response.get("content", response.get("result", {}).get("content", []))
            if isinstance(content, list):
                for item in content:
                    if item.get("type") == "text":
                        self.test_result.insert(tk.END, item.get("text", ""))
                        self.test_result.insert(tk.END, "\n")
            else:
                self.test_result.insert(tk.END, json.dumps(content, indent=2))
        
        self.test_result.config(state=tk.DISABLED)
        self._add_log("INFO", f"Test executed: {self.test_tool_var.get()}")
    
    def _show_test_error(self, message: str):
        """Display an error message in the test result area."""
        self.test_status_label.config(text="Error", foreground="red")
        self.test_result.config(state=tk.NORMAL)
        self.test_result.delete("1.0", tk.END)
        self.test_result.insert(tk.END, f"Error: {message}", "error")
        self.test_result.config(state=tk.DISABLED)
        self._add_log("ERROR", f"Test error: {message}")
    
    def _clear_test_result(self):
        """Clear the test result area."""
        self.test_result.config(state=tk.NORMAL)
        self.test_result.delete("1.0", tk.END)
        self.test_result.config(state=tk.DISABLED)
        self.test_status_label.config(text="")
    
    def create_log_tab(self):
        """Create the server log tab."""
        # Control frame at top
        control_frame = ttk.Frame(self.log_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Log level filter
        ttk.Label(control_frame, text="Log Level:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        self.log_level_var = tk.StringVar(value="DEBUG")  # Show all by default
        self.log_level_combo = ttk.Combobox(
            control_frame, 
            textvariable=self.log_level_var, 
            values=self.log_levels, 
            state="readonly",
            width=12
        )
        self.log_level_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.log_level_combo.bind("<<ComboboxSelected>>", self._on_log_level_change)
        
        # Auto-scroll checkbox
        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            control_frame, 
            text="Auto-scroll", 
            variable=self.auto_scroll_var
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        ttk.Button(control_frame, text="Clear Log", command=self._clear_log).pack(side=tk.LEFT)
        
        # Log entry count label
        self.log_count_label = ttk.Label(control_frame, text="Entries: 0")
        self.log_count_label.pack(side=tk.RIGHT)
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(self.log_frame, height=20, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure tags for log levels with colors
        self.log_text.tag_configure("DEBUG", foreground="gray")
        self.log_text.tag_configure("INFO", foreground="green")
        self.log_text.tag_configure("WARNING", foreground="orange")
        self.log_text.tag_configure("ERROR", foreground="red")
        self.log_text.tag_configure("CRITICAL", foreground="red", font=("", 10, "bold"))
        self.log_text.tag_configure("TIMESTAMP", foreground="blue")
        
        # Store all log entries for filtering
        self.all_log_entries = []
        
        # Initial log message
        self._add_log("INFO", "MCP Manager initialized. Ready to start server.")
    
    def _on_log_level_change(self, event=None):
        """Handle log level filter change - refresh display with filtered entries."""
        self._refresh_log_display()
    
    def _get_log_level_priority(self, level: str) -> int:
        """Get numeric priority for a log level (higher = more severe)."""
        priorities = {
            "DEBUG": 0,
            "INFO": 1,
            "WARNING": 2,
            "ERROR": 3,
            "CRITICAL": 4
        }
        return priorities.get(level.upper(), 0)
    
    def _refresh_log_display(self):
        """Refresh the log display based on current filter level."""
        min_level = self._get_log_level_priority(self.log_level_var.get())
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        
        visible_count = 0
        for timestamp, level, message in self.all_log_entries:
            if self._get_log_level_priority(level) >= min_level:
                self.log_text.insert(tk.END, f"[{timestamp}] ", "TIMESTAMP")
                self.log_text.insert(tk.END, f"[{level}] ", level)
                self.log_text.insert(tk.END, f"{message}\n")
                visible_count += 1
        
        self.log_text.config(state=tk.DISABLED)
        
        if self.auto_scroll_var.get():
            self.log_text.see(tk.END)
        
        # Update count label
        total = len(self.all_log_entries)
        if visible_count == total:
            self.log_count_label.config(text=f"Entries: {total}")
        else:
            self.log_count_label.config(text=f"Entries: {visible_count}/{total}")
    
    def _draw_status_indicator(self, running: bool):
        """Draw the status indicator circle."""
        self.status_indicator.delete("all")
        color = "#00CC00" if running else "#CC0000"
        self.status_indicator.create_oval(2, 2, 14, 14, fill=color, outline=color)
    
    def _populate_tools_list(self):
        """Populate the tools treeview."""
        # Clear existing
        for item in self.tools_tree.get_children():
            self.tools_tree.delete(item)
        
        if not self.registry:
            return
        
        for tool in self.registry.list_tools():
            # Truncate description for display
            desc = tool.description[:80] + "..." if len(tool.description) > 80 else tool.description
            self.tools_tree.insert("", tk.END, values=(tool.name, desc))
    
    def _on_tool_select(self, event):
        """Handle tool selection in treeview."""
        selection = self.tools_tree.selection()
        if not selection:
            return
        
        item = self.tools_tree.item(selection[0])
        tool_name = item["values"][0]
        
        if not self.registry:
            return
        
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return
        
        # Display tool details in a readable format
        mcp_tool = tool.to_mcp_tool()
        schema = mcp_tool.inputSchema
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        details = f"Tool: {mcp_tool.name}\n"
        details += "=" * 60 + "\n\n"
        details += f"Description:\n{mcp_tool.description}\n\n"
        
        # Parameters section
        details += "Parameters:\n"
        details += "-" * 40 + "\n"
        
        if properties:
            for param_name, param_info in properties.items():
                is_required = param_name in required
                param_type = param_info.get("type", "any")
                param_desc = param_info.get("description", "No description")
                
                # Format parameter header
                req_marker = " [REQUIRED]" if is_required else " [optional]"
                details += f"\n• {param_name}{req_marker}\n"
                details += f"    Type: {param_type}\n"
                
                # Show enum values if present
                if "enum" in param_info:
                    enum_values = ", ".join(str(v) for v in param_info["enum"])
                    details += f"    Options: {enum_values}\n"
                
                # Show default value if present
                if "default" in param_info:
                    default_val = param_info["default"]
                    if isinstance(default_val, str) and len(default_val) > 50:
                        default_val = default_val[:50] + "..."
                    details += f"    Default: {default_val}\n"
                
                details += f"    Description: {param_desc}\n"
        else:
            details += "\n(No parameters)\n"
        
        self.tool_details.config(state=tk.NORMAL)
        self.tool_details.delete("1.0", tk.END)
        self.tool_details.insert(tk.END, details)
        self.tool_details.config(state=tk.DISABLED)
    
    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard."""
        self.clipboard_clear()
        self.clipboard_append(text)
        self._add_log("INFO", "Configuration copied to clipboard")
    
    def _add_log(self, level: str, message: str):
        """Add a log message to the log display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Store in all entries for filtering
        if hasattr(self, 'all_log_entries'):
            self.all_log_entries.append((timestamp, level.upper(), message))
        
        # Check if this message should be displayed based on current filter
        min_level = self._get_log_level_priority(self.log_level_var.get()) if hasattr(self, 'log_level_var') else 0
        if self._get_log_level_priority(level) >= min_level:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"[{timestamp}] ", "TIMESTAMP")
            self.log_text.insert(tk.END, f"[{level.upper()}] ", level.upper())
            self.log_text.insert(tk.END, f"{message}\n")
            
            if hasattr(self, 'auto_scroll_var') and self.auto_scroll_var.get():
                self.log_text.see(tk.END)
            
            self.log_text.config(state=tk.DISABLED)
        
        # Update count label
        if hasattr(self, 'log_count_label') and hasattr(self, 'all_log_entries'):
            total = len(self.all_log_entries)
            visible = sum(1 for _, lvl, _ in self.all_log_entries 
                         if self._get_log_level_priority(lvl) >= min_level)
            if visible == total:
                self.log_count_label.config(text=f"Entries: {total}")
            else:
                self.log_count_label.config(text=f"Entries: {visible}/{total}")
    
    def _clear_log(self):
        """Clear the log display."""
        if hasattr(self, 'all_log_entries'):
            self.all_log_entries.clear()
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Update count label
        if hasattr(self, 'log_count_label'):
            self.log_count_label.config(text="Entries: 0")
        
        self._add_log("INFO", "Log cleared")
    
    def start_log_polling(self):
        """Start polling the log queue for messages."""
        self._poll_log_queue()
    
    def _poll_log_queue(self):
        """Poll the log queue and display messages."""
        try:
            while True:
                level, message = self.log_queue.get_nowait()
                self._add_log(level, message)
        except queue.Empty:
            pass
        
        # Schedule next poll
        self.after(100, self._poll_log_queue)
    
    def start_server(self):
        """Start the MCP server as a detached subprocess."""
        if self.server_running:
            self._add_log("WARNING", "Server is already running")
            return
        
        # Create server process manager
        self.server_process = MCPServerProcess(
            self.log_queue,
            self._on_server_started,
            self._on_server_stopped
        )
        
        # Start in detached mode so it persists after Pomera closes
        if self.server_process.start(detached=True):
            self._add_log("INFO", "MCP server started in detached mode")
            self._add_log("INFO", "Server will continue running after Pomera closes")
            self._add_log("INFO", "The server is now ready to accept connections from Claude Desktop or Cursor")
        else:
            self._add_log("ERROR", "Failed to start MCP server")
    
    def check_existing_server(self):
        """Check if an MCP server is already running and update UI accordingly."""
        pid = find_running_mcp_server()
        if pid:
            self._add_log("INFO", f"Detected existing MCP server (PID: {pid})")
            # Create process manager to track it
            self.server_process = MCPServerProcess(
                self.log_queue,
                self._on_server_started,
                self._on_server_stopped
            )
            self.server_process._external_pid = pid
            self._update_status(True)
            return True
        return False
    
    def stop_server(self):
        """Stop the MCP server subprocess."""
        if not self.server_running and (not self.server_process or not self.server_process.is_running()):
            self._add_log("WARNING", "Server is not running")
            return
        
        if self.server_process:
            self.server_process.stop()
            self.server_process = None
    
    def _update_status(self, running: bool):
        """Update the server status display."""
        self.server_running = running
        self._draw_status_indicator(running)
        
        if running:
            self.status_label.config(text="Running")
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            # Update PID from process manager
            if self.server_process:
                pid = self.server_process.get_pid()
                if pid:
                    self.pid_label.config(text=str(pid))
                else:
                    self.pid_label.config(text="Running (PID unknown)")
            else:
                self.pid_label.config(text="Running")
        else:
            self.status_label.config(text="Stopped")
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.pid_label.config(text="Not running")
    
    def _on_server_started(self):
        """Callback when server starts."""
        self.after(0, lambda: self._update_status(True))
    
    def _on_server_stopped(self):
        """Callback when server stops."""
        self.after(0, lambda: self._update_status(False))
    
    def refresh_tools(self):
        """Refresh the tools list."""
        self._load_registry()
        self._populate_tools_list()
        self._populate_test_tool_combo()
        
        tool_count = len(self.registry) if self.registry else 0
        self.tools_count_label.config(text=f"{tool_count} available")
        
        self._add_log("INFO", f"Tools refreshed: {tool_count} tools available")


class MCPManager:
    """Main class for MCP Manager integration with Pomera."""
    
    def __init__(self):
        self.widget = None
    
    def create_widget(self, parent, app):
        """Create and return the MCP Manager widget."""
        self.widget = MCPManagerWidget(parent, app)
        return self.widget
    
    def get_default_settings(self):
        """Return default settings for MCP Manager."""
        return {
            "auto_start": False,
            "log_level": "INFO"
        }

