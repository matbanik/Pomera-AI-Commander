"""
Email Header Analyzer Module - Email header analysis utility

This module provides comprehensive email header analysis functionality with UI components
for the Promera AI Commander application.
"""

import tkinter as tk
from tkinter import ttk
import re
import datetime
from email.utils import parsedate_to_datetime


class EmailHeaderAnalyzerProcessor:
    """Email header analyzer processor with detailed analysis capabilities."""
    
    @staticmethod
    def analyze_email_headers(text, show_timestamps=True, show_delays=True, show_authentication=True, show_spam_score=True):
        """Analyzes raw email headers to extract routing information, authentication results, and delivery timing."""
        lines = text.strip().split('\n')
        if not lines:
            return "No email headers found."
        
        # Parse headers
        headers = {}
        current_header = None
        current_value = ""
        
        for line in lines:
            if line.startswith(' ') or line.startswith('\t'):
                # Continuation of previous header
                if current_header:
                    current_value += " " + line.strip()
            else:
                # Save previous header
                if current_header:
                    if current_header not in headers:
                        headers[current_header] = []
                    headers[current_header].append(current_value.strip())
                
                # Start new header
                if ':' in line:
                    current_header, current_value = line.split(':', 1)
                    current_header = current_header.strip().lower()
                    current_value = current_value.strip()
                else:
                    current_header = None
                    current_value = ""
        
        # Save last header
        if current_header:
            if current_header not in headers:
                headers[current_header] = []
            headers[current_header].append(current_value.strip())
        
        # Build analysis report
        report = ["=== EMAIL HEADER ANALYSIS ===", ""]
        
        # Basic Information
        report.append("--- Basic Information ---")
        basic_fields = ['from', 'to', 'subject', 'date', 'message-id']
        for field in basic_fields:
            if field in headers:
                report.append(f"{field.title()}: {headers[field][0]}")
        report.append("")
        
        # Routing Information
        report.append("--- Routing Information ---")
        if 'delivered-to' in headers:
            report.append(f"Delivered-To: {headers['delivered-to'][0]}")
        if 'return-path' in headers:
            report.append(f"Return-Path: {headers['return-path'][0]}")
        report.append("")
        
        # Parse Received headers for server hops
        received_headers = headers.get('received', [])
        if received_headers:
            report.append(f"--- Server Hops ({len(received_headers)} total) ---")
            
            hop_times = []
            for i, received in enumerate(received_headers, 1):
                # Extract server info and timestamp
                server_match = re.search(r'from\s+([^\s]+)(?:\s+\(([^)]+)\))?(?:\s+\[([^\]]+)\])?', received)
                time_match = re.search(r';\s*(.+)$', received)
                
                server_name = server_match.group(1) if server_match else "Unknown"
                server_ip = server_match.group(3) if server_match and server_match.group(3) else "Unknown IP"
                
                report.append(f"Hop {i}: {server_name} [{server_ip}]")
                
                if time_match and show_timestamps:
                    time_str = time_match.group(1).strip()
                    try:
                        hop_time = parsedate_to_datetime(time_str)
                        hop_times.append(hop_time)
                        report.append(f"  Received: {time_str}")
                        
                        # Calculate delay from previous hop
                        if len(hop_times) > 1 and show_delays:
                            delay = (hop_times[-1] - hop_times[-2]).total_seconds()
                            if delay >= 0:
                                report.append(f"  Delay from previous: {int(delay)} seconds")
                            else:
                                report.append(f"  WARNING: Clock skew detected ({int(abs(delay))} seconds)")
                    except:
                        report.append(f"  Received: {time_str} (could not parse)")
                
                report.append("")
            
            # Delivery Timeline
            if len(hop_times) > 1 and show_delays:
                total_time = (hop_times[-1] - hop_times[0]).total_seconds()
                avg_delay = total_time / (len(hop_times) - 1) if len(hop_times) > 1 else 0
                
                report.append("--- Delivery Timeline ---")
                report.append(f"Total delivery time: {int(total_time)} seconds")
                report.append(f"Average hop delay: {int(avg_delay)} seconds")
                report.append("")
        
        # Authentication Results
        if 'authentication-results' in headers and show_authentication:
            report.append("--- Authentication Results ---")
            auth_results = headers['authentication-results'][0]
            
            # Parse SPF
            spf_match = re.search(r'spf=([^;]+)', auth_results)
            if spf_match:
                spf_result = spf_match.group(1).strip()
                report.append(f"SPF: {spf_result.upper()}")
            
            # Parse DKIM
            dkim_match = re.search(r'dkim=([^;]+)', auth_results)
            if dkim_match:
                dkim_result = dkim_match.group(1).strip()
                report.append(f"DKIM: {dkim_result.upper()}")
            
            # Parse DMARC
            dmarc_match = re.search(r'dmarc=([^;]+)', auth_results)
            if dmarc_match:
                dmarc_result = dmarc_match.group(1).strip()
                report.append(f"DMARC: {dmarc_result.upper()}")
            
            report.append("")
            
            # Security Assessment
            report.append("--- Security Assessment ---")
            auth_status = []
            if spf_match and 'pass' in spf_match.group(1).lower():
                auth_status.append("SPF-PASS")
            elif spf_match:
                auth_status.append("SPF-FAIL")
            
            if dkim_match and 'pass' in dkim_match.group(1).lower():
                auth_status.append("DKIM-PASS")
            elif dkim_match:
                auth_status.append("DKIM-FAIL")
            
            if dmarc_match and 'pass' in dmarc_match.group(1).lower():
                auth_status.append("DMARC-PASS")
            elif dmarc_match:
                auth_status.append("DMARC-FAIL")
            
            if all('PASS' in status for status in auth_status):
                report.append("Authentication Status: SECURE (All checks passed)")
            elif any('FAIL' in status for status in auth_status):
                failed = [s.replace('-FAIL', '') for s in auth_status if 'FAIL' in s]
                report.append(f"Authentication Status: INSECURE (Failed: {', '.join(failed)})")
            elif auth_status:
                report.append("Authentication Status: PARTIAL (Mixed results)")
            else:
                report.append("Authentication Status: UNKNOWN (No authentication headers found)")
            
            # DMARC Policy
            dmarc_policy_match = re.search(r'p=([^)\s]+)', auth_results)
            if dmarc_policy_match:
                policy = dmarc_policy_match.group(1).upper()
                report.append(f"DMARC Policy: {policy}")
            
            report.append("")
        
        # Technical Details
        report.append("--- Technical Details ---")
        tech_fields = ['mime-version', 'content-type']
        for field in tech_fields:
            if field in headers:
                report.append(f"{field.replace('-', '-').title()}: {headers[field][0]}")
        
        # Spam Score
        if 'x-spam-status' in headers and show_spam_score:
            spam_status = headers['x-spam-status'][0]
            report.append(f"X-Spam-Status: {spam_status}")
        
        report.append("")
        
        # Summary
        report.append("--- Summary ---")
        if received_headers:
            report.append(f"Total Hops: {len(received_headers)}")
            if len(hop_times) > 1 and show_delays:
                total_time = (hop_times[-1] - hop_times[0]).total_seconds()
                report.append(f"Total Delivery Time: {int(total_time)} seconds")
        
        if 'x-spam-status' in headers and show_spam_score:
            spam_match = re.search(r'score=([^,\s]+)', headers['x-spam-status'][0])
            if spam_match:
                score = spam_match.group(1)
                status = "Not Spam" if float(score) < 5.0 else "Likely Spam"
                report.append(f"Spam Score: {score} ({status})")
        
        if 'authentication-results' in headers and show_authentication:
            auth_results = headers['authentication-results'][0]
            auth_status = []
            
            # Re-parse for summary
            spf_match = re.search(r'spf=([^;]+)', auth_results)
            dkim_match = re.search(r'dkim=([^;]+)', auth_results)
            dmarc_match = re.search(r'dmarc=([^;]+)', auth_results)
            
            if spf_match and 'pass' in spf_match.group(1).lower():
                auth_status.append("SPF-PASS")
            elif spf_match:
                auth_status.append("SPF-FAIL")
            
            if dkim_match and 'pass' in dkim_match.group(1).lower():
                auth_status.append("DKIM-PASS")
            elif dkim_match:
                auth_status.append("DKIM-FAIL")
            
            if dmarc_match and 'pass' in dmarc_match.group(1).lower():
                auth_status.append("DMARC-PASS")
            elif dmarc_match:
                auth_status.append("DMARC-FAIL")
            
            if all('PASS' in status for status in auth_status):
                report.append("Authentication: All Passed")
            elif auth_status:
                report.append("Authentication: Mixed Results")
            else:
                report.append("Authentication: Not Found")
        
        return '\n'.join(report)

    @staticmethod
    def process_text(input_text, settings):
        """Process text using the current settings."""
        return EmailHeaderAnalyzerProcessor.analyze_email_headers(
            input_text,
            settings.get("show_timestamps", True),
            settings.get("show_delays", True),
            settings.get("show_authentication", True),
            settings.get("show_spam_score", True)
        )


class EmailHeaderAnalyzerUI:
    """UI components for the Email Header Analyzer."""
    
    def __init__(self, parent, settings, on_setting_change_callback=None, apply_tool_callback=None):
        """
        Initialize the Email Header Analyzer UI.
        
        Args:
            parent: Parent widget
            settings: Dictionary containing tool settings
            on_setting_change_callback: Callback function for setting changes
            apply_tool_callback: Callback function for applying the tool
        """
        self.parent = parent
        self.settings = settings
        self.on_setting_change_callback = on_setting_change_callback
        self.apply_tool_callback = apply_tool_callback
        
        # Initialize UI variables
        self.email_show_timestamps_var = tk.BooleanVar(value=settings.get("show_timestamps", True))
        self.email_show_delays_var = tk.BooleanVar(value=settings.get("show_delays", True))
        self.email_show_authentication_var = tk.BooleanVar(value=settings.get("show_authentication", True))
        self.email_show_spam_score_var = tk.BooleanVar(value=settings.get("show_spam_score", True))
        
        self.create_widgets()

    def create_widgets(self):
        """Creates the UI widgets for the Email Header Analyzer."""
        # Checkboxes for various display options
        ttk.Checkbutton(
            self.parent, 
            text="Show Timestamps", 
            variable=self.email_show_timestamps_var, 
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(
            self.parent, 
            text="Show Delays", 
            variable=self.email_show_delays_var, 
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(
            self.parent, 
            text="Show Authentication", 
            variable=self.email_show_authentication_var, 
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(
            self.parent, 
            text="Show Spam Score", 
            variable=self.email_show_spam_score_var, 
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        
        # Analyze button
        if self.apply_tool_callback:
            ttk.Button(
                self.parent, 
                text="Analyze", 
                command=self.apply_tool_callback
            ).pack(side=tk.LEFT, padx=10)

    def _on_setting_change(self):
        """Handle setting changes."""
        if self.on_setting_change_callback:
            self.on_setting_change_callback()

    def get_current_settings(self):
        """Get the current settings from the UI."""
        return {
            "show_timestamps": self.email_show_timestamps_var.get(),
            "show_delays": self.email_show_delays_var.get(),
            "show_authentication": self.email_show_authentication_var.get(),
            "show_spam_score": self.email_show_spam_score_var.get()
        }

    def update_settings(self, settings):
        """Update the UI with new settings."""
        self.email_show_timestamps_var.set(settings.get("show_timestamps", True))
        self.email_show_delays_var.set(settings.get("show_delays", True))
        self.email_show_authentication_var.set(settings.get("show_authentication", True))
        self.email_show_spam_score_var.set(settings.get("show_spam_score", True))


class EmailHeaderAnalyzer:
    """Main Email Header Analyzer class that combines processor and UI functionality."""
    
    def __init__(self):
        self.processor = EmailHeaderAnalyzerProcessor()
        self.ui = None
        
    def create_ui(self, parent, settings, on_setting_change_callback=None, apply_tool_callback=None):
        """Create and return the UI component."""
        self.ui = EmailHeaderAnalyzerUI(parent, settings, on_setting_change_callback, apply_tool_callback)
        return self.ui
        
    def process_text(self, input_text, settings):
        """Process text using the current settings."""
        return self.processor.process_text(input_text, settings)
        
    def get_default_settings(self):
        """Get default settings for the Email Header Analyzer."""
        return {
            "show_timestamps": True,
            "show_delays": True,
            "show_authentication": True,
            "show_spam_score": True
        }


# Convenience functions for backward compatibility
def analyze_email_headers(text, show_timestamps=True, show_delays=True, show_authentication=True, show_spam_score=True):
    """Analyze email headers with specified options."""
    return EmailHeaderAnalyzerProcessor.analyze_email_headers(
        text, show_timestamps, show_delays, show_authentication, show_spam_score
    )


def process_email_header_analysis(input_text, settings):
    """Process email header analysis with the specified settings."""
    return EmailHeaderAnalyzerProcessor.process_text(input_text, settings)


# BaseTool-compatible wrapper
try:
    from tools.base_tool import BaseTool
    from typing import Dict, Any
    import tkinter as tk
    from tkinter import ttk
    
    class EmailHeaderAnalyzerV2(BaseTool):
        """
        BaseTool-compatible version of EmailHeaderAnalyzer.
        """
        
        TOOL_NAME = "Email Header Analyzer"
        TOOL_DESCRIPTION = "Analyze email headers for routing, authentication, and timing"
        TOOL_VERSION = "2.0.0"
        
        def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
            """Analyze email headers."""
            return EmailHeaderAnalyzerProcessor.analyze_email_headers(
                input_text,
                settings.get("show_timestamps", True),
                settings.get("show_delays", True),
                settings.get("show_authentication", True),
                settings.get("show_spam_score", True)
            )
        
        def get_default_settings(self) -> Dict[str, Any]:
            return {
                "show_timestamps": True,
                "show_delays": True,
                "show_authentication": True,
                "show_spam_score": True
            }
        
        def create_ui(self, parent: tk.Widget, settings: Dict[str, Any], 
                     on_change=None, on_apply=None) -> tk.Widget:
            """Create UI for Email Header Analyzer."""
            frame = ttk.Frame(parent)
            ttk.Label(frame, text="Analyze email headers").pack(side=tk.LEFT, padx=5)
            if on_apply:
                ttk.Button(frame, text="Analyze", command=on_apply).pack(side=tk.LEFT, padx=5)
            return frame

except ImportError:
    pass