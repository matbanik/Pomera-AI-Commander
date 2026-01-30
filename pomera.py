import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox, font
import re
import json
import os
import sys
import logging
from pathlib import Path

import csv
import io
import platform
from typing import Optional, Dict, Any, List
import requests
import threading
import time
import string
import random
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

# AI Tools import
try:
    from tools.ai_tools import AIToolsWidget
    AI_TOOLS_AVAILABLE = True
except ImportError:
    AI_TOOLS_AVAILABLE = False
    print("AI Tools module not available")

# Find & Replace module import
try:
    from tools.find_replace import FindReplaceWidget, SettingsManager
    FIND_REPLACE_MODULE_AVAILABLE = True
except ImportError:
    FIND_REPLACE_MODULE_AVAILABLE = False
    print("Find & Replace module not available")

# Diff Viewer module import
try:
    from tools.diff_viewer import DiffViewerWidget, DiffViewerSettingsWidget
    DIFF_VIEWER_MODULE_AVAILABLE = True
except ImportError:
    DIFF_VIEWER_MODULE_AVAILABLE = False
    print("Diff Viewer module not available")

# Database Settings Manager import
try:
    from core.database_settings_manager import DatabaseSettingsManager
    DATABASE_SETTINGS_AVAILABLE = True
except ImportError:
    DATABASE_SETTINGS_AVAILABLE = False
    print("Database Settings Manager not available, falling back to JSON")

# Data Directory module import (cross-platform data storage)
try:
    from core.data_directory import (
        get_database_path, get_backup_dir, migrate_legacy_databases,
        is_portable_mode, get_data_directory_info, check_portable_mode_warning,
        check_and_execute_pending_migration, set_custom_data_directory, load_config
    )
    DATA_DIRECTORY_AVAILABLE = True
except ImportError:
    DATA_DIRECTORY_AVAILABLE = False
    print("Data Directory module not available, using legacy paths")

# Case Tool module import
try:
    from tools.case_tool import CaseTool
    CASE_TOOL_MODULE_AVAILABLE = True
except ImportError:
    CASE_TOOL_MODULE_AVAILABLE = False
    print("Case Tool module not available")

# Email Extraction Tool module import
try:
    from tools.email_extraction_tool import EmailExtractionTool
    EMAIL_EXTRACTION_MODULE_AVAILABLE = True
except ImportError:
    EMAIL_EXTRACTION_MODULE_AVAILABLE = False
    print("Email Extraction Tool module not available")

# Email Header Analyzer module import
try:
    from tools.email_header_analyzer import EmailHeaderAnalyzer
    EMAIL_HEADER_ANALYZER_MODULE_AVAILABLE = True
except ImportError:
    EMAIL_HEADER_ANALYZER_MODULE_AVAILABLE = False
    print("Email Header Analyzer module not available")

# URL and Link Extractor module import
try:
    from tools.url_link_extractor import URLLinkExtractor
    URL_LINK_EXTRACTOR_MODULE_AVAILABLE = True
except ImportError:
    URL_LINK_EXTRACTOR_MODULE_AVAILABLE = False
    print("URL and Link Extractor module not available")

# Regex Extractor module import
try:
    from tools.regex_extractor import RegexExtractor
    REGEX_EXTRACTOR_MODULE_AVAILABLE = True
except ImportError:
    REGEX_EXTRACTOR_MODULE_AVAILABLE = False
    print("Regex Extractor module not available")

# URL Parser module import
try:
    from tools.url_parser import URLParser
    URL_PARSER_MODULE_AVAILABLE = True
except ImportError:
    URL_PARSER_MODULE_AVAILABLE = False
    print("URL Parser module not available")

# Word Frequency Counter module import
try:
    from tools.word_frequency_counter import WordFrequencyCounter
    WORD_FREQUENCY_COUNTER_MODULE_AVAILABLE = True
except ImportError:
    WORD_FREQUENCY_COUNTER_MODULE_AVAILABLE = False
    print("Word Frequency Counter module not available")

# Sorter Tools module import
try:
    from tools.sorter_tools import SorterTools
    SORTER_TOOLS_MODULE_AVAILABLE = True
except ImportError:
    SORTER_TOOLS_MODULE_AVAILABLE = False
    print("Sorter Tools module not available")

# Translator Tools module import
try:
    from tools.translator_tools import TranslatorTools
    TRANSLATOR_TOOLS_MODULE_AVAILABLE = True
except ImportError:
    TRANSLATOR_TOOLS_MODULE_AVAILABLE = False
    print("Translator Tools module not available")

# Generator Tools module import
try:
    from tools.generator_tools import GeneratorTools, GeneratorToolsWidget
    GENERATOR_TOOLS_MODULE_AVAILABLE = True
except ImportError:
    GENERATOR_TOOLS_MODULE_AVAILABLE = False
    print("Generator Tools module not available")

# Extraction Tools module import
try:
    from tools.extraction_tools import ExtractionTools
    EXTRACTION_TOOLS_MODULE_AVAILABLE = True
except ImportError:
    EXTRACTION_TOOLS_MODULE_AVAILABLE = False
    print("Extraction Tools module not available")

# Base64 Tools module import
try:
    from tools.base64_tools import Base64Tools, Base64ToolsWidget
    BASE64_TOOLS_MODULE_AVAILABLE = True
except ImportError:
    BASE64_TOOLS_MODULE_AVAILABLE = False

# JSON/XML Tool module import
try:
    from tools.jsonxml_tool import JSONXMLTool
    JSONXML_TOOL_MODULE_AVAILABLE = True
except ImportError:
    JSONXML_TOOL_MODULE_AVAILABLE = False

# Cron Tool module import
try:
    from tools.cron_tool import CronTool
    CRON_TOOL_MODULE_AVAILABLE = True
except ImportError:
    CRON_TOOL_MODULE_AVAILABLE = False
    print("Cron Tool module not available")

# HTML Extraction Tool module import
try:
    from tools.html_tool import HTMLExtractionTool
    HTML_EXTRACTION_TOOL_MODULE_AVAILABLE = True
except ImportError:
    HTML_EXTRACTION_TOOL_MODULE_AVAILABLE = False
    print("HTML Extraction Tool module not available")

# cURL Tool module import
try:
    from tools.curl_tool import CurlToolWidget
    CURL_TOOL_MODULE_AVAILABLE = True
except ImportError:
    CURL_TOOL_MODULE_AVAILABLE = False
    print("cURL Tool module not available")

# List Comparator module import
try:
    from tools.list_comparator import DiffApp
    LIST_COMPARATOR_MODULE_AVAILABLE = True
except ImportError:
    LIST_COMPARATOR_MODULE_AVAILABLE = False
    print("List Comparator module not available")

# Notes Widget module import
try:
    from tools.notes_widget import NotesWidget
    NOTES_WIDGET_MODULE_AVAILABLE = True
except ImportError:
    NOTES_WIDGET_MODULE_AVAILABLE = False
    print("Notes Widget module not available")

# Smart Diff widget module import
try:
    from tools.smart_diff_widget import SmartDiffWidget
    SMART_DIFF_WIDGET_AVAILABLE = True
except ImportError:
    SMART_DIFF_WIDGET_AVAILABLE = False
    print("Smart Diff widget module not available")

# Folder File Reporter module import
try:
    from tools.folder_file_reporter_adapter import FolderFileReporterAdapter
    FOLDER_FILE_REPORTER_MODULE_AVAILABLE = True
except ImportError:
    FOLDER_FILE_REPORTER_MODULE_AVAILABLE = False
    print("Folder File Reporter module not available")

# Line Tools module import
try:
    from tools.line_tools import LineTools
    LINE_TOOLS_MODULE_AVAILABLE = True
except ImportError:
    LINE_TOOLS_MODULE_AVAILABLE = False
    print("Line Tools module not available")

# Whitespace Tools module import
try:
    from tools.whitespace_tools import WhitespaceTools
    WHITESPACE_TOOLS_MODULE_AVAILABLE = True
except ImportError:
    WHITESPACE_TOOLS_MODULE_AVAILABLE = False
    print("Whitespace Tools module not available")

# Text Statistics module import
try:
    from tools.text_statistics_tool import TextStatistics
    TEXT_STATISTICS_MODULE_AVAILABLE = True
except ImportError:
    TEXT_STATISTICS_MODULE_AVAILABLE = False
    print("Text Statistics module not available")

# Hash Generator module import
try:
    from tools.hash_generator import HashGenerator
    HASH_GENERATOR_MODULE_AVAILABLE = True
except ImportError:
    HASH_GENERATOR_MODULE_AVAILABLE = False
    print("Hash Generator module not available")

# Markdown Tools module import
try:
    from tools.markdown_tools import MarkdownTools
    MARKDOWN_TOOLS_MODULE_AVAILABLE = True
except ImportError:
    MARKDOWN_TOOLS_MODULE_AVAILABLE = False
    print("Markdown Tools module not available")

# String Escape Tool module import
try:
    from tools.string_escape_tool import StringEscapeTool
    STRING_ESCAPE_TOOL_MODULE_AVAILABLE = True
except ImportError:
    STRING_ESCAPE_TOOL_MODULE_AVAILABLE = False
    print("String Escape Tool module not available")

# Number Base Converter module import
try:
    from tools.number_base_converter import NumberBaseConverter
    NUMBER_BASE_CONVERTER_MODULE_AVAILABLE = True
except ImportError:
    NUMBER_BASE_CONVERTER_MODULE_AVAILABLE = False
    print("Number Base Converter module not available")

# Text Wrapper module import
try:
    from tools.text_wrapper import TextWrapper
    TEXT_WRAPPER_MODULE_AVAILABLE = True
except ImportError:
    TEXT_WRAPPER_MODULE_AVAILABLE = False
    print("Text Wrapper module not available")

# Slug Generator module import
try:
    from tools.slug_generator import SlugGenerator
    SLUG_GENERATOR_MODULE_AVAILABLE = True
except ImportError:
    SLUG_GENERATOR_MODULE_AVAILABLE = False
    print("Slug Generator module not available")

# Column Tools module import
try:
    from tools.column_tools import ColumnTools
    COLUMN_TOOLS_MODULE_AVAILABLE = True
except ImportError:
    COLUMN_TOOLS_MODULE_AVAILABLE = False
    print("Column Tools module not available")

# Timestamp Converter module import
try:
    from tools.timestamp_converter import TimestampConverter
    TIMESTAMP_CONVERTER_MODULE_AVAILABLE = True
except ImportError:
    TIMESTAMP_CONVERTER_MODULE_AVAILABLE = False
    print("Timestamp Converter module not available")

# ASCII Art Generator module import
try:
    from tools.ascii_art_generator import ASCIIArtGenerator
    ASCII_ART_GENERATOR_MODULE_AVAILABLE = True
except ImportError:
    ASCII_ART_GENERATOR_MODULE_AVAILABLE = False
    print("ASCII Art Generator module not available")

# MCP Manager module import
try:
    from tools.mcp_widget import MCPManager
    MCP_MANAGER_MODULE_AVAILABLE = True
except ImportError:
    MCP_MANAGER_MODULE_AVAILABLE = False
    print("MCP Manager module not available")

try:
    from huggingface_hub import InferenceClient
    from huggingface_hub.utils import HfHubHTTPError
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False



# Async processing imports
try:
    from core.async_text_processor import (
        get_async_text_processor, AsyncTextProcessor, TextProcessingContext, 
        ProcessingResult, ProcessingMode, shutdown_async_processor
    )
    ASYNC_PROCESSING_AVAILABLE = True
except ImportError:
    ASYNC_PROCESSING_AVAILABLE = False
    print("Async processing not available")

# Intelligent caching imports
try:
    from core.smart_stats_calculator import get_smart_stats_calculator, SmartStatsCalculator, TextStats
    from core.regex_pattern_cache import get_regex_pattern_cache, RegexPatternCache
    from core.content_hash_cache import get_content_hash_cache, get_processing_result_cache, ContentHashCache, ProcessingResultCache
    INTELLIGENT_CACHING_AVAILABLE = True
except ImportError as e:
    INTELLIGENT_CACHING_AVAILABLE = False
    print(f"Intelligent caching not available: {e}")

# Efficient line numbers import
try:
    from core.efficient_line_numbers import OptimizedTextWithLineNumbers
    EFFICIENT_LINE_NUMBERS_AVAILABLE = True
except ImportError:
    EFFICIENT_LINE_NUMBERS_AVAILABLE = False
    print("Efficient line numbers not available")

# Memory efficient text widget import (removed - no longer used)
MEMORY_EFFICIENT_TEXT_AVAILABLE = False

# Advanced memory management imports - removed for optimization
ADVANCED_MEMORY_MANAGEMENT_AVAILABLE = False

# Progressive search and highlighting imports
try:
    from core.optimized_search_highlighter import get_search_highlighter, OptimizedSearchHighlighter, HighlightMode
    from core.optimized_find_replace import get_find_replace_processor, OptimizedFindReplace, ProcessingMode
    from core.search_operation_manager import get_operation_manager, SearchOperationManager, CancellationReason
    PROGRESSIVE_SEARCH_AVAILABLE = True
except ImportError as e:
    PROGRESSIVE_SEARCH_AVAILABLE = False
    print(f"Progressive search not available: {e}")

# Dialog Manager import
try:
    from core.dialog_manager import DialogManager
    DIALOG_MANAGER_AVAILABLE = True
except ImportError as e:
    DIALOG_MANAGER_AVAILABLE = False
    print(f"Dialog Manager not available: {e}")

# Event Consolidator import
try:
    from core.event_consolidator import get_event_consolidator, EventConsolidator, DebounceConfig, DebounceStrategy
    EVENT_CONSOLIDATOR_AVAILABLE = True
except ImportError as e:
    EVENT_CONSOLIDATOR_AVAILABLE = False
    print(f"Event Consolidator not available: {e}")

# Visibility Monitor and Statistics Update Manager imports
try:
    from core.visibility_monitor import get_visibility_monitor, VisibilityMonitor, VisibilityState
    from core.statistics_update_manager import get_statistics_update_manager, StatisticsUpdateManager, UpdatePriority
    VISIBILITY_AWARE_UPDATES_AVAILABLE = True
except ImportError as e:
    VISIBILITY_AWARE_UPDATES_AVAILABLE = False
    print(f"Visibility-aware updates not available: {e}")

# Progressive Statistics Calculator import
try:
    from core.progressive_stats_calculator import get_progressive_stats_calculator, ProgressiveStatsCalculator
    PROGRESSIVE_STATS_CALCULATOR_AVAILABLE = True
except ImportError as e:
    PROGRESSIVE_STATS_CALCULATOR_AVAILABLE = False
    print(f"Progressive Statistics Calculator not available: {e}")

# Context Menu import
try:
    from core.context_menu import add_context_menu, add_context_menu_to_children
    CONTEXT_MENU_AVAILABLE = True
except ImportError as e:
    CONTEXT_MENU_AVAILABLE = False
    print(f"Context Menu not available: {e}")

# Streaming Text Handler import
try:
    from core.streaming_text_handler import (
        StreamingTextHandler, StreamingTextManager, IncrementalTextUpdater,
        StreamConfig, StreamMetrics
    )
    STREAMING_TEXT_HANDLER_AVAILABLE = True
except ImportError as e:
    STREAMING_TEXT_HANDLER_AVAILABLE = False
    print(f"Streaming Text Handler not available: {e}")

# Settings Defaults Registry import
try:
    from core.settings_defaults_registry import get_registry, SettingsDefaultsRegistry
    SETTINGS_DEFAULTS_REGISTRY_AVAILABLE = True
except ImportError as e:
    SETTINGS_DEFAULTS_REGISTRY_AVAILABLE = False
    print(f"Settings Defaults Registry not available: {e}")

# Error Service import
try:
    from core.error_service import (
        ErrorService, ErrorContext, ErrorSeverity,
        init_error_service, get_error_service, error_handler
    )
    ERROR_SERVICE_AVAILABLE = True
except ImportError as e:
    ERROR_SERVICE_AVAILABLE = False
    print(f"Error Service not available: {e}")

# App Context import
try:
    from core.app_context import (
        AppContext, AppContextBuilder,
        get_app_context, set_app_context, create_app_context
    )
    APP_CONTEXT_AVAILABLE = True
except ImportError as e:
    APP_CONTEXT_AVAILABLE = False
    print(f"App Context not available: {e}")

# Task Scheduler import
try:
    from core.task_scheduler import (
        TaskScheduler, TaskPriority,
        get_task_scheduler, init_task_scheduler, shutdown_task_scheduler
    )
    TASK_SCHEDULER_AVAILABLE = True
except ImportError as e:
    TASK_SCHEDULER_AVAILABLE = False
    print(f"Task Scheduler not available: {e}")

# Tool Loader import
try:
    from tools.tool_loader import (
        ToolLoader, ToolSpec, ToolCategory,
        get_tool_loader, init_tool_loader
    )
    TOOL_LOADER_AVAILABLE = True
except ImportError as e:
    TOOL_LOADER_AVAILABLE = False
    print(f"Tool Loader not available: {e}")

# Widget Cache import
try:
    from core.widget_cache import (
        WidgetCache, CacheStrategy,
        init_widget_cache, get_widget_cache, shutdown_widget_cache
    )
    WIDGET_CACHE_AVAILABLE = True
except ImportError as e:
    WIDGET_CACHE_AVAILABLE = False
    print(f"Widget Cache not available: {e}")

# Collapsible Panel import (UI redesign)
try:
    from core.collapsible_panel import CollapsiblePanel
    COLLAPSIBLE_PANEL_AVAILABLE = True
except ImportError as e:
    COLLAPSIBLE_PANEL_AVAILABLE = False
    print(f"Collapsible Panel not available: {e}")

# Tool Search Widget import (UI redesign)
try:
    from core.tool_search_widget import ToolSearchPalette
    TOOL_SEARCH_WIDGET_AVAILABLE = True
except ImportError as e:
    TOOL_SEARCH_WIDGET_AVAILABLE = False
    print(f"Tool Search Widget not available: {e}")


class StartupProfiler:
    """
    Startup profiling utility to diagnose slow initialization.
    
    Usage:
        profiler = StartupProfiler()
        profiler.start("Stage Name")
        # ... do work ...
        profiler.end("Stage Name")
        profiler.summary()  # Prints timing report to console
    """
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.stages: Dict[str, Dict[str, float]] = {}
        self.order: List[str] = []
        self._total_start = time.perf_counter()
    
    def start(self, stage_name: str) -> None:
        """Start timing a stage."""
        if not self.enabled:
            return
        self.stages[stage_name] = {"start": time.perf_counter(), "end": None}
        if stage_name not in self.order:
            self.order.append(stage_name)
    
    def end(self, stage_name: str) -> None:
        """End timing a stage."""
        if not self.enabled or stage_name not in self.stages:
            return
        self.stages[stage_name]["end"] = time.perf_counter()
    
    def duration(self, stage_name: str) -> float:
        """Get duration of a completed stage in milliseconds."""
        if stage_name not in self.stages:
            return 0.0
        stage = self.stages[stage_name]
        if stage["end"] is None:
            return 0.0
        return (stage["end"] - stage["start"]) * 1000
    
    def summary(self) -> str:
        """Print formatted timing summary to console and return as string."""
        if not self.enabled:
            return ""
        
        total_elapsed = (time.perf_counter() - self._total_start) * 1000
        
        lines = [
            "\n" + "=" * 60,
            "STARTUP PROFILING REPORT",
            "=" * 60,
        ]
        
        for stage_name in self.order:
            duration_ms = self.duration(stage_name)
            bar_length = min(int(duration_ms / 50), 30)  # 50ms per char, max 30
            bar = "█" * bar_length
            status = "SLOW" if duration_ms > 500 else ""
            lines.append(f"  {stage_name:40} {duration_ms:7.1f}ms {bar} {status}")
        
        lines.append("-" * 60)
        lines.append(f"  {'TOTAL':40} {total_elapsed:7.1f}ms")
        lines.append("=" * 60 + "\n")
        
        report = "\n".join(lines)
        print(report)
        return report


# Global startup profiler instance (enabled by default for diagnostics)
_startup_profiler = StartupProfiler(enabled=True)


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








# Use optimized components when available
if EFFICIENT_LINE_NUMBERS_AVAILABLE:
    # Use the optimized TextWithLineNumbers from efficient_line_numbers.py
    TextWithLineNumbers = OptimizedTextWithLineNumbers
else:
    # Fallback implementation for when optimized components are not available
    class TextWithLineNumbers(tk.Frame):
        """Fallback implementation of TextWithLineNumbers."""
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.text = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=15, width=50, undo=True)
            self.linenumbers = tk.Canvas(self, width=40, bg='#f0f0f0', highlightthickness=0)
            
            self.linenumbers.pack(side=tk.LEFT, fill=tk.Y)
            self.text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

            # Basic event bindings
            self.text.vbar.config(command=self._on_text_scroll)
            self.linenumbers.bind("<MouseWheel>", self._on_mousewheel)
            self.linenumbers.bind("<Button-4>", self._on_mousewheel)
            self.linenumbers.bind("<Button-5>", self._on_mousewheel)
            self.text.bind("<<Modified>>", self._on_text_modified)
            self.text.bind("<Configure>", self._on_text_modified)
            
            # Paste events - insert undo separator after paste
            self.text.bind("<<Paste>>", self._on_paste)
            self.text.bind("<Control-v>", self._on_paste)
            self.text.bind("<Control-V>", self._on_paste)
            self.text.bind("<Shift-Insert>", self._on_paste)
            
            self._on_text_modified()
        
        def _on_paste(self, event=None):
            """Insert undo separator after paste to separate from subsequent typing."""
            def insert_separator():
                try:
                    self.text.edit_separator()
                except Exception:
                    pass
            self.after(10, insert_separator)


        def _on_text_scroll(self, *args):
            self.text.yview(*args)
            self._on_text_modified()

        def _on_mousewheel(self, event):
            if platform.system() == "Windows":
                self.text.yview_scroll(int(-1*(event.delta/120)), "units")
            elif platform.system() == "Darwin":
                 self.text.yview_scroll(int(-1 * event.delta), "units")
            else:
                if event.num == 4:
                    self.text.yview_scroll(-1, "units")
                elif event.num == 5:
                    self.text.yview_scroll(1, "units")
            self._on_text_modified()
            return "break"

        def _on_text_modified(self, event=None):
            self.linenumbers.delete("all")
            line_info_cache = []
            i = self.text.index("@0,0")
            while True:
                dline = self.text.dlineinfo(i)
                if dline is None: 
                    break
                line_info_cache.append((i, dline[1]))
                i = self.text.index("%s+1line" % i)
            
            for i, y in line_info_cache:
                linenum = str(i).split(".")[0]
                self.linenumbers.create_text(20, y, anchor="n", text=linenum, fill="gray")
            
            self.after(10, self.linenumbers.yview_moveto, self.text.yview()[0])
            if event and event.widget.edit_modified():
                event.widget.edit_modified(False)

class PromeraAISettingsManager:
    """Settings manager implementation for Find & Replace widget."""
    
    def __init__(self, app):
        self.app = app
    
    def get_tool_settings(self, tool_name: str) -> Dict[str, Any]:
        """Get settings for a specific tool."""
        return self.app.settings.get("tool_settings", {}).get(tool_name, {})
    
    def save_settings(self):
        """Save current settings to persistent storage."""
        self.app.save_settings()
    
    def get_pattern_library(self) -> List[Dict[str, str]]:
        """Get the regex pattern library."""
        # Initialize pattern library if it doesn't exist OR is empty
        existing = self.app.settings.get("pattern_library", None)
        if not existing or len(existing) == 0:
            # Try to import and use the comprehensive pattern library
            try:
                from core.regex_pattern_library import RegexPatternLibrary
                library = RegexPatternLibrary()
                self.app.settings["pattern_library"] = library._convert_to_settings_format()
                pattern_count = len(self.app.settings.get("pattern_library", []))
                self.app.logger.info(f"Loaded comprehensive pattern library with {pattern_count} patterns")
            except ImportError:
                # Fallback to basic patterns if comprehensive library is not available
                self.app.settings["pattern_library"] = [
                    {"find": "\\d+", "replace": "NUMBER", "purpose": "Match any number"},
                    {"find": "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}", "replace": "[EMAIL]", "purpose": "Match email addresses"},
                    {"find": "\\b\\d{3}-\\d{3}-\\d{4}\\b", "replace": "XXX-XXX-XXXX", "purpose": "Match phone numbers (XXX-XXX-XXXX format)"}
                ]
                self.app.logger.warning("Comprehensive pattern library not available, using basic patterns")
            
            self.app.save_settings()
        
        # Ensure the 7 most common extraction patterns exist
        pattern_library = self.app.settings.get("pattern_library", [])
        common_extraction_patterns = [
            {"find": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "replace": "", "purpose": "Extract Email Addresses - Finds email addresses anywhere in text"},
            {"find": r"https?://[^\s/$.?#].[^\s]*", "replace": "", "purpose": "Extract URLs - Finds HTTP/HTTPS URLs in text"},
            {"find": r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "replace": "", "purpose": "Extract IP Addresses - Finds IPv4 addresses (xxx.xxx.xxx.xxx)"},
            {"find": r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", "replace": "", "purpose": "Extract Phone Numbers - Finds phone numbers in various formats"},
            {"find": r"\d+", "replace": "", "purpose": "Extract Numbers - Finds sequences of digits"},
            {"find": r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", "replace": "", "purpose": "Extract UUIDs/GUIDs - Finds UUID format (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)"},
            {"find": r"\d{4}-\d{2}-\d{2}(?:\s+\d{2}:\d{2}:\d{2})?", "replace": "", "purpose": "Extract Dates/Timestamps - Finds dates in YYYY-MM-DD format with optional time"}
        ]
        
        # Check if patterns already exist and add missing ones
        existing_patterns = {p.get("find", "") for p in pattern_library}
        added_count = 0
        for pattern in common_extraction_patterns:
            if pattern["find"] not in existing_patterns:
                pattern_library.append(pattern)
                existing_patterns.add(pattern["find"])
                added_count += 1
        
        if added_count > 0:
            self.app.settings["pattern_library"] = pattern_library
            self.app.save_settings()
            self.app.logger.info(f"Added {added_count} common extraction patterns to pattern library")
        
        return pattern_library
    
    def set_pattern_library(self, pattern_library: List[Dict[str, str]]):
        """Explicitly update and persist the pattern library."""
        self.app.settings["pattern_library"] = pattern_library
        self.app.save_settings()


class DialogSettingsAdapter:
    """
    Adapter class to provide dialog settings interface to DialogManager.
    
    This adapter bridges the gap between the main application's settings system
    and the DialogManager's requirements. It provides a clean interface for
    the DialogManager to access dialog-related settings without tight coupling
    to the main application structure.
    
    Design Pattern:
        Adapter Pattern - Adapts the main application's settings interface
        to match what DialogManager expects.
    
    Responsibilities:
        - Provide get_setting() method for DialogManager
        - Handle settings retrieval errors gracefully
        - Maintain loose coupling between DialogManager and main app
    
    Args:
        app: Reference to the main PomeraApp instance
        
    Methods:
        get_setting(key, default): Retrieve setting value with fallback default
    """
    
    def __init__(self, app):
        """
        Initialize the adapter with a reference to the main application.
        
        Args:
            app (PomeraApp): Main application instance with settings attribute
        """
        self.app = app
    
    def get_setting(self, key: str, default=None):
        """
        Get setting from the main app's settings with error handling.
        
        This method provides safe access to application settings for the
        DialogManager, handling cases where settings might be corrupted
        or unavailable.
        
        Args:
            key (str): Settings key to retrieve (e.g., "dialog_settings")
            default: Default value to return if key is not found or error occurs
            
        Returns:
            The setting value if found, otherwise the default value
            
        Error Handling:
            - Missing app reference: Returns default
            - Missing settings attribute: Returns default  
            - Key not found: Returns default
            - Any other exception: Logs error and returns default
        """
        try:
            if not self.app:
                return default
                
            if not hasattr(self.app, 'settings'):
                return default
                
            return self.app.settings.get(key, default)
            
        except Exception as e:
            # Log error if logger is available
            if hasattr(self.app, 'logger') and self.app.logger:
                self.app.logger.warning(f"Error retrieving setting '{key}': {e}")
            return default


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
        global DATABASE_SETTINGS_AVAILABLE
        super().__init__()
        
        # Start profiling from here
        _startup_profiler.start("Database/Settings Init")
        
        # Record startup time for performance monitoring
        self.startup_time = time.time()
        
        # Flag to prevent automatic processing during initialization
        self._initializing = True
        
        self.title("Pomera AI Commander")
        self.geometry(AppConfig.DEFAULT_WINDOW_SIZE)
        
        # Set window icon (Pomera dog mascot)
        self._set_window_icon()

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
            "Case Tool", "Find & Replace Text", "AI Tools",
            "Email Header Analyzer", "Extraction Tools", "Folder File Reporter", "Generator Tools", "Sorter Tools",
            "URL Parser",
            "Base64 Encoder/Decoder", "Translator Tools", "Diff Viewer",
            "Line Tools", "Whitespace Tools", "Text Statistics", "Markdown Tools",
            "String Escape Tool", "Number Base Converter", "Text Wrapper",
            "Column Tools", "Timestamp Converter",
            "Web Search", "URL Reader"  # Manual search/fetch only on button click
        ]

        # CORRECTED ORDER: Load settings BEFORE setting up logging
        # Initialize database settings manager or fallback to JSON
        if DATABASE_SETTINGS_AVAILABLE:
            try:
                # Check for and execute any pending data migration FIRST
                # (before any database connections are opened)
                if DATA_DIRECTORY_AVAILABLE:
                    migration_msg = check_and_execute_pending_migration()
                    if migration_msg:
                        print(f"Data migration completed: {migration_msg}")
                    
                    # Migrate legacy databases if needed (console INFO log only)
                    migrate_legacy_databases()
                    db_path = get_database_path("settings.db")
                    backup_path = str(get_backup_dir() / "settings_backup.db")
                    json_path = get_database_path("settings.json")
                    if is_portable_mode():
                        print("Running in portable mode - data stored in installation directory")
                else:
                    # Fallback to legacy relative paths
                    db_path = "settings.db"
                    backup_path = "settings_backup.db"
                    json_path = "settings.json"
                
                self.db_settings_manager = DatabaseSettingsManager(
                    db_path=db_path,
                    backup_path=backup_path,
                    json_settings_path=json_path
                )
                # Provide default settings to database manager
                self.db_settings_manager.set_default_settings_provider(self._get_default_settings)
                self.settings = self.db_settings_manager._settings_proxy
                self.logger = logging.getLogger(__name__)
                self.logger.info("Using database settings manager")
            except Exception as e:
                # Log error (error_service not yet initialized at this point)
                print(f"Failed to initialize database settings manager: {e}")
                print("Falling back to JSON settings")
                DATABASE_SETTINGS_AVAILABLE = False
                self.settings = self.load_settings()
        else:
            self.settings = self.load_settings()
        _startup_profiler.end("Database/Settings Init")
        
        _startup_profiler.start("Logging/Audio Setup")
        self.setup_logging()
        self.setup_audio()
        _startup_profiler.end("Logging/Audio Setup")
        
        _startup_profiler.start("DialogManager Init")
        # Initialize DialogManager BEFORE optimized components
        if DIALOG_MANAGER_AVAILABLE:
            self.dialog_settings_adapter = DialogSettingsAdapter(self)
            self.dialog_manager = DialogManager(self.dialog_settings_adapter, self.logger)
            
            # Register tool-specific dialog categories
            self._register_tool_dialog_categories()
            
            self.logger.info("DialogManager initialized successfully")
        else:
            self.dialog_manager = None
            self.logger.warning("DialogManager not available, using direct messagebox calls")

        # Initialize Error Service for centralized error handling
        if ERROR_SERVICE_AVAILABLE:
            self.error_service = init_error_service(self.logger, self.dialog_manager)
            self.logger.info("Error Service initialized successfully")
        else:
            self.error_service = None
            self.logger.warning("Error Service not available")

        # Initialize App Context for dependency injection
        if APP_CONTEXT_AVAILABLE:
            self.app_context = (AppContextBuilder()
                .with_logger(self.logger)
                .with_settings_manager(getattr(self, 'db_settings_manager', None))
                .with_dialog_manager(self.dialog_manager)
                .with_error_service(self.error_service)
                .with_root_window(self)
                .build())
            set_app_context(self.app_context)
            self.logger.info("App Context initialized successfully")
        else:
            self.app_context = None
            self.logger.warning("App Context not available")

        # Initialize Task Scheduler for background operations
        if TASK_SCHEDULER_AVAILABLE:
            self.task_scheduler = init_task_scheduler(
                max_workers=4, 
                logger=self.logger,
                auto_start=True
            )
            self.logger.info("Task Scheduler initialized successfully")
        else:
            self.task_scheduler = None
            self.logger.warning("Task Scheduler not available")

        # Initialize Tool Loader for lazy tool loading
        if TOOL_LOADER_AVAILABLE:
            self.tool_loader = init_tool_loader()
            available_tools = self.tool_loader.get_available_tools()
            self.logger.info(f"Tool Loader initialized with {len(available_tools)} available tools")
        else:
            self.tool_loader = None
            self.logger.warning("Tool Loader not available")

        # Setup optimized components AFTER DialogManager is available
        _startup_profiler.end("DialogManager Init")
        
        _startup_profiler.start("Optimized Components")
        self.setup_optimized_components()
        _startup_profiler.end("Optimized Components")
        
        _startup_profiler.start("Create Widgets")
        self.create_widgets()
        _startup_profiler.end("Create Widgets")
        
        _startup_profiler.start("Load Last State")
        self.load_last_state()
        _startup_profiler.end("Load Last State")
        
        # Initialization complete - allow automatic processing
        self._initializing = False
        
        # Only apply tool during initialization if there's no existing content
        # This prevents clearing loaded content from settings.json
        if self.tool_var.get() not in self.manual_process_tools:
            # Check if we have existing content in tabs (from settings.json)
            has_existing_content = False
            for i, tab in enumerate(self.input_tabs + self.output_tabs):
                content = tab.text.get("1.0", tk.END).strip()
                if content:
                    has_existing_content = True
                    tab_type = "input" if i < len(self.input_tabs) else "output"
                    tab_num = i + 1 if i < len(self.input_tabs) else i - len(self.input_tabs) + 1
                    self.logger.info(f"Found existing content in {tab_type} tab {tab_num}: '{content[:50]}...'")
            
            # Only apply tool if no existing content
            if not has_existing_content:
                self.logger.info("No existing content found - applying tool")
                self.apply_tool()
            else:
                self.logger.info("Existing content found - skipping apply_tool to preserve loaded content")
        elif self.tool_var.get() == "Diff Viewer":
            self.central_frame.grid_remove()
            # Use row=1 (same as central_frame) to not cover search bar in row=0
            self.diff_frame.grid(row=1, column=0, sticky="nsew", pady=5)
            self.update_tool_settings_ui()
            self.load_diff_viewer_content()
            self.run_diff_viewer()
        
        # Set up global undo/redo key bindings
        self.bind_all("<Control-z>", self.global_undo)
        self.bind_all("<Control-y>", self.global_redo)
        self.bind_all("<Control-Shift-Z>", self.global_redo)  # Alternative redo shortcut
        
        # Set up cURL tool keyboard shortcut
        if CURL_TOOL_MODULE_AVAILABLE:
            self.bind_all("<Control-u>", lambda e: self.open_curl_tool_window())
        
        # Set up Notes widget keyboard shortcuts
        if NOTES_WIDGET_MODULE_AVAILABLE:
            self.bind_all("<Control-s>", lambda e: self.save_as_note())  # Ctrl+S for Save as Note
            self.bind_all("<Control-n>", lambda e: self.open_notes_widget())  # Ctrl+N for Notes window
        
        # Set up MCP Manager keyboard shortcut (Ctrl+M)
        if MCP_MANAGER_MODULE_AVAILABLE:
            self.bind_all("<Control-m>", lambda e: self.open_mcp_manager())
        
        # Set up Tool Search keyboard shortcut (Ctrl+K)
        if TOOL_SEARCH_WIDGET_AVAILABLE:
            self.bind_all("<Control-k>", self.focus_tool_search)
        
        # Set up Options Panel toggle shortcut (Ctrl+Shift+H)
        if COLLAPSIBLE_PANEL_AVAILABLE:
            self.bind_all("<Control-Shift-h>", self.toggle_options_panel)
            self.bind_all("<Control-Shift-H>", self.toggle_options_panel)  # Windows needs uppercase
        
        # Set up Load Presets shortcut (Ctrl+Shift+P) - Reset tool settings to defaults
        if SETTINGS_DEFAULTS_REGISTRY_AVAILABLE:
            self.bind_all("<Control-Shift-p>", lambda e: self.show_load_presets_dialog())
            self.bind_all("<Control-Shift-P>", lambda e: self.show_load_presets_dialog())
        
        # Set up window focus and minimize event handlers for visibility-aware updates
        if hasattr(self, 'statistics_update_manager') and self.statistics_update_manager:
            self.bind("<FocusIn>", self._on_window_focus_in)
            self.bind("<FocusOut>", self._on_window_focus_out)
            self.bind("<Unmap>", self._on_window_minimized)
            self.bind("<Map>", self._on_window_restored)
            self.logger.info("Window focus/minimize event handlers registered for visibility-aware updates")
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Final debug check - see if content survived initialization
        final_input_contents = [tab.text.get("1.0", tk.END).strip() for tab in self.input_tabs]
        final_output_contents = [tab.text.get("1.0", tk.END).strip() for tab in self.output_tabs]
        final_non_empty_inputs = sum(1 for content in final_input_contents if content)
        final_non_empty_outputs = sum(1 for content in final_output_contents if content)
        self.logger.info(f"Initialization complete - {final_non_empty_inputs} non-empty input tabs, {final_non_empty_outputs} non-empty output tabs remain")
        
        # Schedule background maintenance tasks
        self._schedule_maintenance_tasks()
        
        # Print startup profiling report
        _startup_profiler.summary()

    def _schedule_maintenance_tasks(self):
        """Schedule periodic background maintenance tasks using Task Scheduler."""
        if not TASK_SCHEDULER_AVAILABLE or not self.task_scheduler:
            return
        
        # Schedule periodic auto-save (every 5 minutes)
        self.task_scheduler.schedule_recurring(
            task_id="auto_save_settings",
            func=self._auto_save_settings,
            interval_seconds=300,  # 5 minutes
            priority=TaskPriority.LOW,
            initial_delay=300  # Start after 5 minutes
        )
        
        # Schedule cache cleanup (every 10 minutes)
        self.task_scheduler.schedule_recurring(
            task_id="cache_cleanup",
            func=self._cleanup_caches,
            interval_seconds=600,  # 10 minutes
            priority=TaskPriority.LOW,
            initial_delay=600  # Start after 10 minutes
        )
        
        # Schedule memory usage check (every 15 minutes)
        self.task_scheduler.schedule_recurring(
            task_id="memory_check",
            func=self._check_memory_usage,
            interval_seconds=900,  # 15 minutes
            priority=TaskPriority.LOW,
            initial_delay=900  # Start after 15 minutes
        )
        
        # Schedule automatic backup (every 30 minutes)
        self.task_scheduler.schedule_recurring(
            task_id="auto_backup",
            func=self._auto_backup_settings,
            interval_seconds=1800,  # 30 minutes
            priority=TaskPriority.LOW,
            initial_delay=1800  # Start after 30 minutes
        )
        
        self.logger.info("Background maintenance tasks scheduled (including auto-backup)")
    
    def show_load_presets_dialog(self):
        """
        Open the Load Presets dialog to reset tool settings to defaults.
        
        Accessible via Ctrl+Shift+P keyboard shortcut.
        """
        try:
            from core.load_presets_dialog import LoadPresetsDialog
            
            # Get settings manager - prefer database settings manager
            settings_manager = getattr(self, 'db_settings_manager', None)
            if not settings_manager:
                # Fallback to PromeraAISettingsManager
                settings_manager = PromeraAISettingsManager(self)
            
            dialog = LoadPresetsDialog(
                self, 
                settings_manager, 
                logger=self.logger,
                dialog_manager=self.dialog_manager
            )
            dialog.show()
            self.logger.info("Load Presets dialog opened")
            
        except ImportError as e:
            self.logger.error(f"Could not load Load Presets dialog: {e}")
            if self.dialog_manager:
                self.dialog_manager.show_error(
                    "Module Not Available",
                    "Load Presets dialog is not available.\n"
                    "Please ensure core/load_presets_dialog.py exists."
                )
            else:
                messagebox.showerror(
                    "Module Not Available",
                    "Load Presets dialog is not available."
                )
        except Exception as e:
            self.logger.error(f"Error opening Load Presets dialog: {e}")
            if self.dialog_manager:
                self.dialog_manager.show_error("Error", f"Failed to open dialog: {e}")
            else:
                messagebox.showerror("Error", f"Failed to open dialog: {e}")
    
    def _show_data_location_dialog(self):
        """Show the Data Location settings dialog."""
        from tkinter import filedialog
        
        dialog = tk.Toplevel(self)
        dialog.title("Data Location Settings")
        dialog.withdraw()  # Hide until centered
        dialog.transient(self)
        
        # Get current data info
        if DATA_DIRECTORY_AVAILABLE:
            data_info = get_data_directory_info()
            current_path = data_info.get('user_data_dir', 'Unknown')
            portable = data_info.get('portable_mode', False)
            config = load_config()
            custom_path = config.get('data_directory')
        else:
            current_path = "Data directory module not available"
            portable = False
            custom_path = None
        
        # Main frame with padding
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Current location
        ttk.Label(main_frame, text="Current Data Location:", font=('TkDefaultFont', 10, 'bold')).pack(anchor=tk.W)
        
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill=tk.X, pady=(5, 15))
        
        path_entry = ttk.Entry(path_frame, width=60)
        path_entry.insert(0, current_path)
        path_entry.config(state='readonly')
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Mode selection
        ttk.Label(main_frame, text="Data Storage Mode:", font=('TkDefaultFont', 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        
        mode_var = tk.StringVar()
        if custom_path:
            mode_var.set("custom")
        elif portable:
            mode_var.set("portable")
        else:
            mode_var.set("platform")
        
        custom_path_var = tk.StringVar(value=custom_path or "")
        
        # Platform default option
        platform_frame = ttk.Frame(main_frame)
        platform_frame.pack(fill=tk.X, pady=2)
        ttk.Radiobutton(platform_frame, text="Use platform default (recommended)", 
                        variable=mode_var, value="platform").pack(anchor=tk.W)
        
        # Custom location option
        custom_frame = ttk.Frame(main_frame)
        custom_frame.pack(fill=tk.X, pady=2)
        ttk.Radiobutton(custom_frame, text="Use custom location:", 
                        variable=mode_var, value="custom").pack(side=tk.LEFT)
        
        custom_entry = ttk.Entry(custom_frame, textvariable=custom_path_var, width=40)
        custom_entry.pack(side=tk.LEFT, padx=5)
        
        def browse_folder():
            folder = filedialog.askdirectory(title="Select Data Directory")
            if folder:
                custom_path_var.set(folder)
                mode_var.set("custom")
        
        ttk.Button(custom_frame, text="Browse...", command=browse_folder).pack(side=tk.LEFT)
        
        # Portable mode option
        portable_frame = ttk.Frame(main_frame)
        portable_frame.pack(fill=tk.X, pady=2)
        ttk.Radiobutton(portable_frame, text="Portable mode (store in app folder - NOT RECOMMENDED)", 
                        variable=mode_var, value="portable").pack(anchor=tk.W)
        
        # Warning for portable mode
        warning_frame = ttk.Frame(main_frame)
        warning_frame.pack(fill=tk.X, pady=(15, 10))
        
        warning_label = ttk.Label(warning_frame, 
            text="⚠️ Warning: Portable mode data will be LOST during npm/pip updates!",
            foreground='red')
        
        def update_warning(*args):
            if mode_var.get() == "portable":
                warning_label.pack(anchor=tk.W)
            else:
                warning_label.pack_forget()
        
        mode_var.trace_add('write', update_warning)
        update_warning()
        
        # Migrate checkbox
        migrate_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Migrate existing data to new location", 
                        variable=migrate_var).pack(anchor=tk.W, pady=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def apply_changes():
            mode = mode_var.get()
            migrate = migrate_var.get()
            
            if mode == "platform":
                new_path = None
            elif mode == "custom":
                new_path = custom_path_var.get()
                if not new_path:
                    messagebox.showerror("Error", "Please specify a custom directory path.")
                    return
            else:  # portable
                # For portable mode, set to installation directory
                if DATA_DIRECTORY_AVAILABLE:
                    from core.data_directory import _get_installation_dir
                    new_path = str(_get_installation_dir())
                else:
                    messagebox.showerror("Error", "Portable mode not available.")
                    return
            
            if DATA_DIRECTORY_AVAILABLE:
                result = set_custom_data_directory(new_path, migrate=migrate)
                
                if result.get("restart_required"):
                    dialog.destroy()
                    response = messagebox.askyesno(
                        "Restart Required",
                        "Data location changed. The application needs to restart to migrate data.\n\n"
                        "Close the application now?",
                        icon='warning'
                    )
                    if response:
                        self.on_closing()
                else:
                    dialog.destroy()
                    messagebox.showinfo("Success", result.get("message", "Settings saved."))
            else:
                messagebox.showerror("Error", "Data directory module not available.")
        
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Apply & Restart", command=apply_changes).pack(side=tk.RIGHT)
        
        # Center and show dialog (after all widgets created to avoid blink)
        dialog.update_idletasks()
        dialog.geometry("550x380")
        x = self.winfo_x() + (self.winfo_width() - 550) // 2
        y = self.winfo_y() + (self.winfo_height() - 380) // 2
        dialog.geometry(f"550x380+{x}+{y}")
        dialog.deiconify()
        dialog.grab_set()
    
    def _show_update_dialog(self):
        """Show the Check for Updates dialog with GitHub version check."""
        import webbrowser
        import urllib.request
        import json
        import platform
        
        dialog = tk.Toplevel(self)
        dialog.title("Check for Updates")
        dialog.withdraw()  # Hide until centered
        dialog.transient(self)
        
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Pomera AI Commander", font=('TkDefaultFont', 14, 'bold')).pack(pady=(0, 10))
        
        # Get current version from unified version module
        try:
            from pomera.version import __version__
            current_version = __version__
        except ImportError:
            current_version = "unknown"
        
        # Detect OS for download link
        system = platform.system()
        if system == "Windows":
            os_pattern = "windows"
            os_name = "Windows"
        elif system == "Darwin":
            os_pattern = "macos"
            os_name = "macOS"
        else:
            os_pattern = "linux"
            os_name = "Linux"
        
        # Fetch latest version from GitHub
        latest_version = None
        update_available = False
        download_url = None
        release_data = None
        
        try:
            url = "https://api.github.com/repos/matbanik/Pomera-AI-Commander/releases/latest"
            req = urllib.request.Request(url, headers={'User-Agent': 'Pomera-AI-Commander'})
            with urllib.request.urlopen(req, timeout=5) as response:
                release_data = json.loads(response.read().decode())
                latest_version = release_data.get('tag_name', '').lstrip('v')
                
                # Compare versions
                if current_version != "Unknown" and latest_version:
                    try:
                        current_parts = [int(x) for x in current_version.split('.')]
                        latest_parts = [int(x) for x in latest_version.split('.')]
                        update_available = latest_parts > current_parts
                    except ValueError:
                        update_available = current_version != latest_version
                
                # Find platform-specific download URL
                assets = release_data.get('assets', [])
                for asset in assets:
                    name = asset.get('name', '').lower()
                    if os_pattern in name and (name.endswith('.exe') or name.endswith('.zip') or name.endswith('.tar.gz')):
                        download_url = asset.get('browser_download_url')
                        break
        except Exception as e:
            latest_version = f"Unable to check ({type(e).__name__})"
        
        # Version info frame
        version_frame = ttk.Frame(main_frame)
        version_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(version_frame, text=f"Current Version: {current_version}").pack(anchor=tk.W)
        
        if latest_version and not latest_version.startswith("Unable"):
            if update_available:
                # Update available - BOLD BLACK
                ttk.Label(version_frame, text=f"Latest Version: {latest_version}", 
                          font=('TkDefaultFont', 11, 'bold')).pack(anchor=tk.W)
                ttk.Label(version_frame, text="⬆️ Update available!", 
                          font=('TkDefaultFont', 11, 'bold')).pack(anchor=tk.W, pady=(5, 0))
            else:
                # Up to date - GREEN
                ttk.Label(version_frame, text=f"Latest Version: {latest_version}", 
                          foreground='green').pack(anchor=tk.W)
                ttk.Label(version_frame, text="✓ You're up to date!", 
                          foreground='green', font=('TkDefaultFont', 10, 'bold')).pack(anchor=tk.W, pady=(5, 0))
        elif latest_version:
            ttk.Label(version_frame, text=f"Latest Version: {latest_version}", foreground='orange').pack(anchor=tk.W)
        
        # Data location info
        if DATA_DIRECTORY_AVAILABLE:
            data_info = get_data_directory_info()
            mode = "Portable" if data_info.get('portable_mode') else "Platform"
            ttk.Label(main_frame, text=f"Installation Mode: {mode}").pack(anchor=tk.W)
            ttk.Label(main_frame, text=f"Data Location: {data_info.get('user_data_dir', 'Unknown')}", 
                      wraplength=500).pack(anchor=tk.W, pady=(0, 10))
            
            # Warning for portable mode
            if data_info.get('portable_mode'):
                warning_frame = ttk.Frame(main_frame)
                warning_frame.pack(fill=tk.X, pady=5)
                ttk.Label(warning_frame, 
                    text="⚠️ PORTABLE MODE: Backup your data before updating!",
                    foreground='red', font=('TkDefaultFont', 10, 'bold')).pack()
        
        # Download link if update available
        if update_available and download_url:
            download_frame = ttk.Frame(main_frame)
            download_frame.pack(fill=tk.X, pady=(10, 0))
            ttk.Label(download_frame, text=f"📥 {os_name} Download:", font=('TkDefaultFont', 10, 'bold')).pack(anchor=tk.W)
            
            # Create a clickable link-style label
            link_label = ttk.Label(download_frame, text=download_url.split('/')[-1], 
                                   foreground='blue', cursor='hand2', font=('TkDefaultFont', 9, 'underline'))
            link_label.pack(anchor=tk.W)
            link_label.bind('<Button-1>', lambda e: webbrowser.open(download_url))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        def open_releases():
            webbrowser.open("https://github.com/matbanik/Pomera-AI-Commander/releases")
        
        def download_now():
            if download_url:
                webbrowser.open(download_url)
        
        def create_backup():
            if DATA_DIRECTORY_AVAILABLE:
                from core.data_directory import check_portable_mode_warning
                warning_info = check_portable_mode_warning(show_console_warning=False)
                if warning_info:
                    # Create backup
                    from core.mcp.tool_registry import ToolRegistry
                    registry = ToolRegistry(register_builtins=False)
                    registry._register_safe_update_tool()
                    result = registry.execute('pomera_safe_update', {'action': 'backup'})
                    messagebox.showinfo("Backup", f"Backup created!\n\n{result.content[0]['text'] if result.content else 'Check Documents/pomera-backup folder'}")
                else:
                    messagebox.showinfo("Backup", "No backup needed - your data is safely stored in platform directories.")
        
        if update_available and download_url:
            ttk.Button(button_frame, text=f"Download for {os_name}", command=download_now).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Create Backup", command=create_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="All Releases", command=open_releases).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Center and show dialog (after all widgets created to avoid blink)
        dialog.update_idletasks()
        dialog.geometry("550x400")
        x = self.winfo_x() + (self.winfo_width() - 550) // 2
        y = self.winfo_y() + (self.winfo_height() - 400) // 2
        dialog.geometry(f"550x400+{x}+{y}")
        dialog.deiconify()
        dialog.grab_set()
    
    def _show_about_dialog(self):
        """Show About dialog."""
        # Version from unified version module (managed by setuptools_scm)
        try:
            from pomera.version import __version__
            version = __version__
        except ImportError:
            version = "unknown"
        
        messagebox.showinfo(
            "About Pomera AI Commander",
            f"Pomera AI Commander v{version}\n\n"
            "Text processing toolkit with MCP tools for AI assistants.\n\n"
            "https://github.com/matbanik/Pomera-AI-Commander"
        )
    
    def _set_window_icon(self):
        """Set the window icon (Pomera dog mascot)."""
        try:
            # Find icon file - check multiple locations
            script_dir = Path(__file__).parent.resolve()
            icon_locations = [
                script_dir / "resources" / "icon.ico",
                script_dir / "icon.ico",
                script_dir / "resources" / "icon.png",
                script_dir / "icon.png",
            ]
            
            icon_path = None
            for loc in icon_locations:
                if loc.exists():
                    icon_path = loc
                    break
            
            if icon_path is None:
                return  # No icon found, use default
            
            if platform.system() == "Windows" and icon_path.suffix == ".ico":
                # Windows: use iconbitmap for .ico files
                self.iconbitmap(str(icon_path))
            else:
                # Other platforms or PNG: use PhotoImage
                from PIL import Image, ImageTk
                img = Image.open(icon_path)
                # Resize to appropriate icon size - use NEAREST for sharp pixel art
                img = img.resize((32, 32), Image.Resampling.NEAREST)
                self._icon_photo = ImageTk.PhotoImage(img)
                self.iconphoto(True, self._icon_photo)
                
        except Exception as e:
            self.logger.debug(f"Could not set window icon: {e}")

    def _auto_save_settings(self):
        """Auto-save settings periodically (called by Task Scheduler)."""
        try:
            # Only save if not currently initializing
            if not self._initializing:
                self.save_settings()
                self.logger.debug("Auto-saved settings")
        except Exception as e:
            self.logger.debug(f"Auto-save skipped: {e}")
    
    def _auto_backup_settings(self):
        """Create automatic backup periodically (called by Task Scheduler)."""
        try:
            if not self._initializing and hasattr(self, 'db_settings_manager') and self.db_settings_manager:
                # Check if auto-backup is enabled in backup settings
                if hasattr(self.db_settings_manager, 'backup_recovery_manager'):
                    brm = self.db_settings_manager.backup_recovery_manager
                    if brm and getattr(brm, 'auto_backup_enabled', True):
                        success = self.db_settings_manager.create_backup("auto", "Scheduled automatic backup")
                        if success:
                            self.logger.debug("Scheduled auto-backup created")
                        else:
                            self.logger.debug("Scheduled auto-backup skipped (backup manager returned false)")
        except Exception as e:
            self.logger.debug(f"Auto-backup skipped: {e}")
    
    def _cleanup_caches(self):
        """Periodic cache cleanup (called by Task Scheduler)."""
        try:
            # Clear regex cache if it's getting large
            if hasattr(self, '_regex_cache') and len(self._regex_cache) > 100:
                self._regex_cache.clear()
                self.logger.debug("Cleared regex cache")
            
            # Clear smart stats calculator cache if available
            if INTELLIGENT_CACHING_AVAILABLE and hasattr(self, 'smart_stats_calculator') and self.smart_stats_calculator:
                cache_stats = self.smart_stats_calculator.get_cache_stats()
                if cache_stats.get('cache_size', 0) > 500:
                    self.smart_stats_calculator.clear_cache()
                    self.logger.debug("Cleared smart stats cache")
            
            # Trigger garbage collection for large memory cleanup
            import gc
            gc.collect()
            self.logger.debug("Cache cleanup completed")
        except Exception as e:
            self.logger.debug(f"Cache cleanup error: {e}")
    
    def _check_memory_usage(self):
        """Check memory usage and log warnings if high (called by Task Scheduler)."""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            
            if memory_mb > 500:  # Warning threshold: 500MB
                self.logger.warning(f"High memory usage: {memory_mb:.1f} MB")
                # Trigger aggressive cleanup
                self._cleanup_caches()
            else:
                self.logger.debug(f"Memory usage: {memory_mb:.1f} MB")
        except ImportError:
            pass  # psutil not available
        except Exception as e:
            self.logger.debug(f"Memory check error: {e}")

    def _register_tool_dialog_categories(self):
        """Register tool-specific dialog categories with DialogManager."""
        if not self.dialog_manager:
            return
            
        # Register categories for different tool operations
        self.dialog_manager.register_dialog_type(
            "tool_export",
            "Export completion notifications from tools",
            default_enabled=True,
            examples=["Data exported to CSV", "File saved successfully", "Export complete"]
        )
        
        self.dialog_manager.register_dialog_type(
            "tool_import", 
            "Import completion notifications from tools",
            default_enabled=True,
            examples=["Data imported successfully", "Configuration loaded", "Command imported"]
        )
        
        self.dialog_manager.register_dialog_type(
            "tool_validation",
            "Validation warnings from tools",
            default_enabled=True,
            examples=["No data specified", "Invalid input format", "Missing required field"]
        )
        
        self.dialog_manager.register_dialog_type(
            "tool_operation",
            "General tool operation notifications", 
            default_enabled=True,
            examples=["Operation complete", "Processing finished", "Task completed"]
        )
        
        self.logger.info("Tool-specific dialog categories registered")

    def _handle_error(self, 
                      error: Exception, 
                      operation: str, 
                      component: str = "",
                      user_message: str = "",
                      show_dialog: bool = True,
                      severity: str = "error") -> None:
        """
        Centralized error handling using the Error Service.
        
        Falls back to direct logging if Error Service is not available.
        
        Args:
            error: The exception that occurred
            operation: Description of what operation was being performed
            component: Component/module where error occurred
            user_message: User-friendly message (uses str(error) if empty)
            show_dialog: Whether to show error dialog to user
            severity: Error severity ('debug', 'info', 'warning', 'error', 'critical')
        """
        if self.error_service and ERROR_SERVICE_AVAILABLE:
            # Map severity string to enum
            severity_map = {
                'debug': ErrorSeverity.DEBUG,
                'info': ErrorSeverity.INFO,
                'warning': ErrorSeverity.WARNING,
                'error': ErrorSeverity.ERROR,
                'critical': ErrorSeverity.CRITICAL
            }
            sev = severity_map.get(severity, ErrorSeverity.ERROR)
            
            context = ErrorContext(
                operation=operation,
                component=component,
                user_message=user_message or str(error)
            )
            self.error_service.handle(error, context, sev, show_dialog=show_dialog)
        else:
            # Fallback to direct logging
            log_method = getattr(self.logger, severity, self.logger.error)
            msg = f"[{component}] {operation}: {error}" if component else f"{operation}: {error}"
            log_method(msg)
            
            # Show dialog if requested and dialog_manager available
            if show_dialog and self.dialog_manager:
                self.dialog_manager.show_error(operation, user_message or str(error))
            elif show_dialog:
                messagebox.showerror(operation, user_message or str(error))

    def _handle_warning(self, 
                        message: str, 
                        operation: str, 
                        component: str = "",
                        show_dialog: bool = False) -> None:
        """
        Centralized warning handling.
        
        Args:
            message: Warning message
            operation: What operation triggered the warning
            component: Component/module name
            show_dialog: Whether to show warning dialog
        """
        if self.error_service and ERROR_SERVICE_AVAILABLE:
            context = ErrorContext(operation=operation, component=component)
            self.error_service.log_warning(message, context, show_dialog=show_dialog)
        else:
            msg = f"[{component}] {operation}: {message}" if component else f"{operation}: {message}"
            self.logger.warning(msg)
            if show_dialog and self.dialog_manager:
                self.dialog_manager.show_warning(operation, message)

    def _init_tool_with_loader(self, tool_name: str, attr_name: str, *args, **kwargs):
        """
        Initialize a tool using the Tool Loader.
        
        Uses lazy loading via Tool Loader when available, falls back to direct
        instantiation using the legacy availability flags.
        
        Args:
            tool_name: Name of the tool in Tool Loader registry
            attr_name: Attribute name to set on self (e.g., 'case_tool')
            *args, **kwargs: Arguments to pass to tool constructor
            
        Returns:
            The tool instance or None if not available
        """
        if TOOL_LOADER_AVAILABLE and self.tool_loader:
            if self.tool_loader.is_available(tool_name):
                instance = self.tool_loader.create_instance(tool_name, *args, **kwargs)
                if instance:
                    setattr(self, attr_name, instance)
                    self.logger.info(f"{tool_name} initialized via Tool Loader")
                    return instance
                else:
                    self.logger.warning(f"Failed to create {tool_name} instance")
            else:
                error = self.tool_loader.get_load_error(tool_name)
                self.logger.debug(f"{tool_name} not available: {error}")
        
        setattr(self, attr_name, None)
        return None

    def _is_tool_available(self, tool_name: str, legacy_flag: bool = None) -> bool:
        """
        Check if a tool is available using Tool Loader or legacy flag.
        
        Prefers Tool Loader when available for more accurate checking.
        
        Args:
            tool_name: Name of the tool in Tool Loader registry
            legacy_flag: Legacy availability flag (e.g., CASE_TOOL_MODULE_AVAILABLE)
            
        Returns:
            True if tool is available
        """
        if TOOL_LOADER_AVAILABLE and self.tool_loader:
            return self.tool_loader.is_available(tool_name)
        return legacy_flag if legacy_flag is not None else False

    def _init_tools_batch(self):
        """
        Initialize multiple tools using the Tool Loader.
        
        This method replaces repetitive if/else blocks for tool initialization
        with a data-driven approach using the Tool Loader.
        """
        # Define tools to initialize: (tool_name, attr_name, legacy_flag, args)
        tools_to_init = [
            ("Case Tool", "case_tool", CASE_TOOL_MODULE_AVAILABLE, ()),
            ("Email Extraction", "email_extraction_tool", EMAIL_EXTRACTION_MODULE_AVAILABLE, ()),
            ("Email Header Analyzer", "email_header_analyzer", EMAIL_HEADER_ANALYZER_MODULE_AVAILABLE, ()),
            ("URL Link Extractor", "url_link_extractor", URL_LINK_EXTRACTOR_MODULE_AVAILABLE, ()),
            ("Regex Extractor", "regex_extractor", REGEX_EXTRACTOR_MODULE_AVAILABLE, ()),
            ("URL Parser", "url_parser", URL_PARSER_MODULE_AVAILABLE, ()),
            ("Word Frequency Counter", "word_frequency_counter", WORD_FREQUENCY_COUNTER_MODULE_AVAILABLE, ()),
            ("Sorter Tools", "sorter_tools", SORTER_TOOLS_MODULE_AVAILABLE, ()),
            ("Translator Tools", "translator_tools", TRANSLATOR_TOOLS_MODULE_AVAILABLE, ()),
            ("Generator Tools", "generator_tools", GENERATOR_TOOLS_MODULE_AVAILABLE, ()),
            ("Extraction Tools", "extraction_tools", EXTRACTION_TOOLS_MODULE_AVAILABLE, ()),
            ("Base64 Tools", "base64_tools", BASE64_TOOLS_MODULE_AVAILABLE, ()),
            ("Line Tools", "line_tools", LINE_TOOLS_MODULE_AVAILABLE, ()),
            ("Whitespace Tools", "whitespace_tools", WHITESPACE_TOOLS_MODULE_AVAILABLE, ()),
            ("Text Statistics", "text_statistics", TEXT_STATISTICS_MODULE_AVAILABLE, ()),
            ("Hash Generator", "hash_generator", HASH_GENERATOR_MODULE_AVAILABLE, ()),
            ("Markdown Tools", "markdown_tools", MARKDOWN_TOOLS_MODULE_AVAILABLE, ()),
            ("String Escape Tool", "string_escape_tool", STRING_ESCAPE_TOOL_MODULE_AVAILABLE, ()),
            ("Number Base Converter", "number_base_converter", NUMBER_BASE_CONVERTER_MODULE_AVAILABLE, ()),
            ("Text Wrapper", "text_wrapper", TEXT_WRAPPER_MODULE_AVAILABLE, ()),
            ("Slug Generator", "slug_generator", SLUG_GENERATOR_MODULE_AVAILABLE, ()),
            ("Column Tools", "column_tools", COLUMN_TOOLS_MODULE_AVAILABLE, ()),
            ("Timestamp Converter", "timestamp_converter", TIMESTAMP_CONVERTER_MODULE_AVAILABLE, ()),
            ("ASCII Art Generator", "ascii_art_generator", ASCII_ART_GENERATOR_MODULE_AVAILABLE, ()),
        ]
        
        initialized_count = 0
        failed_count = 0
        
        for tool_name, attr_name, legacy_flag, args in tools_to_init:
            if TOOL_LOADER_AVAILABLE and self.tool_loader:
                # Use Tool Loader
                instance = self._init_tool_with_loader(tool_name, attr_name, *args)
                if instance:
                    initialized_count += 1
                else:
                    failed_count += 1
            elif legacy_flag:
                # Fallback to legacy initialization (already imported at top)
                # The tool classes are already available from imports
                setattr(self, attr_name, None)  # Will be initialized by legacy code
                self.logger.debug(f"{tool_name} will use legacy initialization")
            else:
                setattr(self, attr_name, None)
                failed_count += 1
        
        self.logger.info(f"Tool batch initialization: {initialized_count} loaded, {failed_count} unavailable")

    def global_undo(self, event=None):
        """Global undo handler that works on the currently focused text widget."""
        focused_widget = self.focus_get()
        
        # Check if the focused widget is a Text widget or ScrolledText widget
        if isinstance(focused_widget, (tk.Text, scrolledtext.ScrolledText)):
            try:
                focused_widget.edit_undo()
                return "break"  # Prevent default handling
            except tk.TclError:
                # No undo information available
                pass
        
        # If not a direct text widget, check if it's part of a TextWithLineNumbers
        parent = focused_widget
        while parent and parent != self:
            if hasattr(parent, 'text') and isinstance(parent.text, (tk.Text, scrolledtext.ScrolledText)):
                try:
                    parent.text.edit_undo()
                    return "break"
                except tk.TclError:
                    pass
                break
            parent = parent.master if hasattr(parent, 'master') else None
        
        return None

    def global_redo(self, event=None):
        """Global redo handler that works on the currently focused text widget."""
        focused_widget = self.focus_get()
        
        # Check if the focused widget is a Text widget or ScrolledText widget
        if isinstance(focused_widget, (tk.Text, scrolledtext.ScrolledText)):
            try:
                focused_widget.edit_redo()
                return "break"  # Prevent default handling
            except tk.TclError:
                # No redo information available
                pass
        
        # If not a direct text widget, check if it's part of a TextWithLineNumbers
        parent = focused_widget
        while parent and parent != self:
            if hasattr(parent, 'text') and isinstance(parent.text, (tk.Text, scrolledtext.ScrolledText)):
                try:
                    parent.text.edit_redo()
                    return "break"
                except tk.TclError:
                    pass
                break
            parent = parent.master if hasattr(parent, 'master') else None
        
        return None

    def load_settings(self):
        """Loads settings from the 'settings.json' file or database."""
        # If database settings manager is available, use it
        if hasattr(self, 'db_settings_manager') and self.db_settings_manager:
            try:
                settings = self.db_settings_manager.load_settings()
                if settings:
                    return settings
                else:
                    # Fallback to defaults if database is empty
                    return self._get_default_settings()
            except Exception as e:
                print(f"Database settings load error: {e}, falling back to JSON")
                # Fall through to JSON loading
        
        # Original JSON loading logic
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
        
        for key in ["input_tabs", "output_tabs", "tool_settings", "performance_settings", "font_settings", "dialog_settings"]:
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
        
        # Remove deprecated performance monitoring settings if they exist
        if "performance_settings" in settings and "monitoring" in settings["performance_settings"]:
            del settings["performance_settings"]["monitoring"]
        
        # Validate dialog settings structure and ensure all required categories exist
        if "dialog_settings" in settings:
            default_dialog_settings = default_settings["dialog_settings"]
            for category, category_data in default_dialog_settings.items():
                if category not in settings["dialog_settings"]:
                    settings["dialog_settings"][category] = category_data.copy()
                else:
                    # Ensure all required fields exist for each category
                    for field, default_value in category_data.items():
                        if field not in settings["dialog_settings"][category]:
                            settings["dialog_settings"][category][field] = default_value
                    
                    # Validate enabled field is boolean
                    if not isinstance(settings["dialog_settings"][category].get("enabled"), bool):
                        settings["dialog_settings"][category]["enabled"] = category_data["enabled"]
                    
                    # Ensure error dialogs cannot be disabled
                    if category == "error":
                        settings["dialog_settings"][category]["enabled"] = True
                        settings["dialog_settings"][category]["locked"] = True
    
    def _get_default_settings(self):
        """Returns default settings when none exist or are invalid.
        
        Uses the centralized Settings Defaults Registry as the single source of truth.
        Only falls back to minimal emergency defaults if registry is unavailable.
        """
        # Use the centralized Settings Defaults Registry (single source of truth)
        if SETTINGS_DEFAULTS_REGISTRY_AVAILABLE:
            try:
                registry = get_registry()
                return registry.get_all_defaults(tab_count=AppConfig.TAB_COUNT)
            except Exception as e:
                if hasattr(self, 'logger') and self.logger:
                    self.logger.warning(f"Failed to get defaults from registry: {e}")
        
        # Minimal emergency fallback - registry should always be available
        # This is only used if core/settings_defaults_registry.py fails to load
        default_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        return {
            "export_path": default_path,
            "debug_level": "INFO",
            "selected_tool": "Case Tool",
            "input_tabs": [""] * AppConfig.TAB_COUNT,
            "output_tabs": [""] * AppConfig.TAB_COUNT,
            "active_input_tab": 0,
            "active_output_tab": 0,
            "tool_settings": {},
            "performance_settings": {"mode": "automatic"},
            "font_settings": {"text_font": {"family": "Consolas", "size": 11}},
            "dialog_settings": {"error": {"enabled": True, "locked": True}}
        }
        
    def save_settings(self):
        """Saves the current settings to database or 'settings.json'."""
        # Don't save during initialization to prevent overwriting loaded content
        if hasattr(self, '_initializing') and self._initializing:
            self.logger.info("Skipping save_settings during initialization")
            return
            
        input_contents = [tab.text.get("1.0", tk.END).strip() for tab in self.input_tabs]
        output_contents = [tab.text.get("1.0", tk.END).strip() for tab in self.output_tabs]
        
        self.settings["input_tabs"] = input_contents
        self.settings["output_tabs"] = output_contents
        self.settings["active_input_tab"] = self.input_notebook.index(self.input_notebook.select())
        self.settings["active_output_tab"] = self.output_notebook.index(self.output_notebook.select())
        
        # Save current tool selection (including Diff Viewer)
        self.settings["selected_tool"] = self.tool_var.get()
        
        # Debug logging to track what's being saved
        non_empty_inputs = sum(1 for content in input_contents if content)
        non_empty_outputs = sum(1 for content in output_contents if content)
        self.logger.info(f"Settings saved - {non_empty_inputs} non-empty input tabs, {non_empty_outputs} non-empty output tabs")
        
        # Save to database if available, otherwise save to JSON
        if hasattr(self, 'db_settings_manager') and self.db_settings_manager:
            try:
                # Database manager handles saving automatically through the proxy
                # Only backup to disk periodically (every 5 seconds max) to avoid performance issues
                import time
                current_time = time.time()
                if not hasattr(self, '_last_disk_backup_time'):
                    self._last_disk_backup_time = 0
                
                # Only force disk backup every 5 seconds to prevent freezing during typing
                if current_time - self._last_disk_backup_time > 5.0:
                    self.db_settings_manager.connection_manager.backup_to_disk()
                    self._last_disk_backup_time = current_time
                    self.logger.info("Settings saved to database")
                else:
                    self.logger.debug("Settings updated (disk backup deferred)")
            except Exception as e:
                self._handle_error(e, "Saving to database", "Settings", 
                                   user_message="Failed to save settings to database, trying JSON fallback",
                                   show_dialog=False)
                # Fall through to JSON saving - get proper dictionary from database manager
                try:
                    settings_dict = self.db_settings_manager.load_settings()
                    with open("settings.json", "w") as f:
                        json.dump(settings_dict, f, indent=4)
                except Exception as json_error:
                    self.logger.error(f"Failed to save to JSON as well: {json_error}")
                    # Create minimal fallback settings
                    fallback_settings = {
                        "export_path": str(Path.home() / "Downloads"),
                        "debug_level": "INFO",
                        "selected_tool": "Case Tool",
                        "active_input_tab": 0,
                        "active_output_tab": 0,
                        "input_tabs": [""] * 7,
                        "output_tabs": [""] * 7,
                        "tool_settings": {}
                    }
                    with open("settings.json", "w") as f:
                        json.dump(fallback_settings, f, indent=4)
        else:
            # Original JSON saving logic
            with open("settings.json", "w") as f:
                json.dump(self.settings, f, indent=4)

    def load_last_state(self):
        """Loads the last saved text and tab selections into the UI."""
        input_tabs_data = self.settings.get("input_tabs", [""]*AppConfig.TAB_COUNT)
        output_tabs_data = self.settings.get("output_tabs", [""]*AppConfig.TAB_COUNT)
        
        # Debug logging
        non_empty_inputs = sum(1 for content in input_tabs_data if content.strip())
        non_empty_outputs = sum(1 for content in output_tabs_data if content.strip())
        self.logger.info(f"Loading state - {non_empty_inputs} non-empty input tabs, {non_empty_outputs} non-empty output tabs")
        
        for i, content in enumerate(input_tabs_data):
            if content.strip():
                self.logger.info(f"Loading input tab {i+1}: '{content[:50]}...' ({len(content)} chars)")
            self.input_tabs[i].text.insert("1.0", content)
            
        for i, content in enumerate(output_tabs_data):
            if content.strip():
                self.logger.info(f"Loading output tab {i+1}: '{content[:50]}...' ({len(content)} chars)")
            self.output_tabs[i].text.config(state="normal")
            self.output_tabs[i].text.insert("1.0", content)
            self.output_tabs[i].text.config(state="disabled")
        
        self.input_notebook.select(self.settings.get("active_input_tab", 0))
        self.output_notebook.select(self.settings.get("active_output_tab", 0))
        
        # Verify content after loading
        loaded_input_contents = [tab.text.get("1.0", tk.END).strip() for tab in self.input_tabs]
        loaded_output_contents = [tab.text.get("1.0", tk.END).strip() for tab in self.output_tabs]
        actual_non_empty_inputs = sum(1 for content in loaded_input_contents if content)
        actual_non_empty_outputs = sum(1 for content in loaded_output_contents if content)
        self.logger.info(f"After loading - {actual_non_empty_inputs} non-empty input tabs, {actual_non_empty_outputs} non-empty output tabs in UI")
        
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
    
        # Initialize async processing
        if ASYNC_PROCESSING_AVAILABLE:
            self.async_processor = get_async_text_processor()
            self.async_processor.logger = self.logger
            
            # Track async processing operations
            self.pending_async_operations = {}
            self.async_progress_indicators = {}
            
            self.logger.info("Async text processing initialized")
        else:
            self.async_processor = None
            self.pending_async_operations = {}
            self.async_progress_indicators = {}
            self.logger.warning("Async processing not available")
        
        # Text chunking functionality not available
        self.text_chunker = None
        
        # Initialize intelligent caching
        if INTELLIGENT_CACHING_AVAILABLE:
            self.smart_stats_calculator = get_smart_stats_calculator()
            self.regex_cache = get_regex_pattern_cache()
            self.content_cache = get_content_hash_cache()
            self.processing_cache = get_processing_result_cache()
            
            self.logger.info("Intelligent caching initialized")
        else:
            self.smart_stats_calculator = None
            self.regex_cache = None
            self.content_cache = None
            self.processing_cache = None
            self.logger.warning("Intelligent caching not available")
        
        # Initialize progressive search and highlighting
        if PROGRESSIVE_SEARCH_AVAILABLE:
            self.search_highlighter = get_search_highlighter()
            self.find_replace_processor = get_find_replace_processor()
            self.operation_manager = get_operation_manager()
            
            # Track active search operations
            self.active_search_operations = {}
            
            self.logger.info("Progressive search and highlighting initialized")
        else:
            self.search_highlighter = None
            self.find_replace_processor = None
            self.operation_manager = None
            self.active_search_operations = {}
            self.logger.warning("Progressive search not available")
    
    def setup_optimized_components(self):
        """Initialize optimized components for better performance."""
        # Get performance settings
        perf_settings = self.settings.get("performance_settings", {})
        performance_mode = perf_settings.get("mode", "automatic")
        
        # Check if optimizations should be enabled
        optimizations_enabled = (
            performance_mode == "always_on" or 
            (performance_mode == "automatic" and self._should_enable_optimizations())
        )
        
        if performance_mode == "always_off":
            self.logger.info("Performance optimizations disabled by user setting")
            self._disable_all_optimizations()
            return
        
        # Advanced memory management modules not available
        self.memory_pool_allocator = None
        self.gc_optimizer = None
        self.memory_leak_detector = None
        
        # Memory efficient text widgets removed - no longer used
        self.use_memory_efficient_widgets = False
        
        # Activity tracking for GC optimization removed (advanced memory management disabled)
        
        # Update debounce delay from settings
        ui_settings = perf_settings.get("ui_optimizations", {})
        AppConfig.DEBOUNCE_DELAY = ui_settings.get("debounce_delay_ms", 300)
        
        # Initialize Find & Replace widget if available
        if FIND_REPLACE_MODULE_AVAILABLE:
            self.settings_manager = PromeraAISettingsManager(self)
            self.find_replace_widget = FindReplaceWidget(self, self.settings_manager, self.logger, self.dialog_manager)
            self.logger.info("Find & Replace module initialized")
        else:
            self.find_replace_widget = None
            self.logger.warning("Find & Replace module not available")
            
        # ============================================================
        # BATCH TOOL INITIALIZATION
        # Uses Tool Loader when available for lazy loading and
        # centralized error tracking. Falls back to legacy imports.
        # ============================================================
        self._init_tools_batch()
        
        # Special case tools that require constructor arguments
        # Folder File Reporter needs 'self' reference
        if FOLDER_FILE_REPORTER_MODULE_AVAILABLE:
            self.folder_file_reporter = FolderFileReporterAdapter(self)
            self.logger.info("Folder File Reporter module initialized")
        else:
            self.folder_file_reporter = None
            self.logger.warning("Folder File Reporter module not available")
        
        # HTML Extraction Tool needs logger reference
        if HTML_EXTRACTION_TOOL_MODULE_AVAILABLE:
            self.html_extraction_tool = HTMLExtractionTool(self.logger)
            self.logger.info("HTML Extraction Tool module initialized")
        else:
            self.html_extraction_tool = None
            self.logger.warning("HTML Extraction Tool module not available")
        
        # JSON/XML Tool and Cron Tool - just log availability (used on-demand)
        if JSONXML_TOOL_MODULE_AVAILABLE:
            self.logger.info("JSON/XML Tool module available")
        else:
            self.logger.warning("JSON/XML Tool module not available")
        
        if CRON_TOOL_MODULE_AVAILABLE:
            self.logger.info("Cron Tool module available")
        else:
            self.logger.warning("Cron Tool module not available")

        # Initialize MCP Manager
        if MCP_MANAGER_MODULE_AVAILABLE:
            self.mcp_manager = MCPManager()
            self.logger.info("MCP Manager module initialized")
        else:
            self.mcp_manager = None

        # Initialize Event Consolidator
        if EVENT_CONSOLIDATOR_AVAILABLE:
            # Create debounce configuration based on performance settings
            ui_settings = perf_settings.get("ui_optimizations", {})
            debounce_config = DebounceConfig(
                strategy=DebounceStrategy.ADAPTIVE,
                fast_delay_ms=ui_settings.get("fast_debounce_ms", 50),
                normal_delay_ms=ui_settings.get("normal_debounce_ms", 300),
                slow_delay_ms=ui_settings.get("slow_debounce_ms", 500),
                large_content_threshold=ui_settings.get("large_content_threshold", 10000),
                very_large_threshold=ui_settings.get("very_large_threshold", 100000)
            )
            
            self.event_consolidator = EventConsolidator(debounce_config)
            self.event_consolidator.set_tk_root(self)
            self.logger.info(f"Event Consolidator initialized with adaptive debouncing (strategy: {debounce_config.strategy.value})")
            self.logger.info(f"Debounce delays - Fast: {debounce_config.fast_delay_ms}ms, Normal: {debounce_config.normal_delay_ms}ms, Slow: {debounce_config.slow_delay_ms}ms")
        else:
            self.event_consolidator = None
            self.logger.warning("Event Consolidator not available - using legacy event handling")
        
        # Initialize Visibility Monitor and Statistics Update Manager
        if VISIBILITY_AWARE_UPDATES_AVAILABLE:
            # Initialize visibility monitor
            self.visibility_monitor = get_visibility_monitor()
            self.visibility_monitor.set_tk_root(self)
            
            # Initialize statistics update manager
            self.statistics_update_manager = get_statistics_update_manager()
            self.statistics_update_manager.set_tk_root(self)
            
            self.logger.info("Visibility Monitor and Statistics Update Manager initialized")
            self.logger.info("Visibility-aware statistics updates enabled")
        else:
            self.visibility_monitor = None
            self.statistics_update_manager = None
            self.logger.warning("Visibility-aware updates not available - using direct statistics updates")
        
        # Initialize Progressive Statistics Calculator
        if PROGRESSIVE_STATS_CALCULATOR_AVAILABLE:
            # Get configuration from performance settings
            progressive_settings = perf_settings.get("progressive_calculation", {})
            chunk_size = progressive_settings.get("chunk_size", 10000)
            progress_threshold_ms = progressive_settings.get("progress_indicator_threshold_ms", 100.0)
            
            self.progressive_stats_calculator = get_progressive_stats_calculator()
            self.logger.info(f"Progressive Statistics Calculator initialized (chunk_size: {chunk_size}, threshold: {progress_threshold_ms}ms)")
            self.logger.info("Progressive calculation enabled for large content (>50,000 characters)")
        else:
            self.progressive_stats_calculator = None
            self.logger.warning("Progressive Statistics Calculator not available - using standard calculation for all content sizes")
        
        # Initialize Streaming Text Handler
        if STREAMING_TEXT_HANDLER_AVAILABLE:
            # Get streaming settings from performance settings
            streaming_settings = perf_settings.get("streaming", {})
            self._streaming_enabled = streaming_settings.get("enabled", True)
            self._streaming_chunk_delay_ms = streaming_settings.get("chunk_delay_ms", 10)
            self._streaming_batch_size = streaming_settings.get("batch_size", 5)
            self._streaming_auto_scroll = streaming_settings.get("auto_scroll", True)
            
            # Create default streaming config
            self._default_stream_config = StreamConfig(
                chunk_delay_ms=self._streaming_chunk_delay_ms,
                batch_size=self._streaming_batch_size,
                auto_scroll=self._streaming_auto_scroll,
                highlight_new_text=False,
                use_threading=True
            )
            
            self.logger.info(f"Streaming Text Handler initialized (enabled: {self._streaming_enabled})")
            self.logger.info(f"Streaming config - delay: {self._streaming_chunk_delay_ms}ms, batch: {self._streaming_batch_size}")
        else:
            self._streaming_enabled = False
            self._default_stream_config = None
            self.logger.warning("Streaming Text Handler not available - text will be displayed at once")
    
    def _should_enable_optimizations(self):
        """Determine if optimizations should be enabled in automatic mode."""
        # In automatic mode, enable optimizations if any performance components are available
        return (ASYNC_PROCESSING_AVAILABLE or 
                INTELLIGENT_CACHING_AVAILABLE or 
                PROGRESSIVE_SEARCH_AVAILABLE or
                ADVANCED_MEMORY_MANAGEMENT_AVAILABLE or
                MEMORY_EFFICIENT_TEXT_AVAILABLE or
                EVENT_CONSOLIDATOR_AVAILABLE)
    
    def _disable_all_optimizations(self):
        """Disable all performance optimizations."""
        self.memory_pool_allocator = None
        self.gc_optimizer = None
        self.memory_leak_detector = None
        self.use_memory_efficient_widgets = False
    
    def _record_activity(self, event=None):
        """Record user activity for GC optimization - not available."""
        # Advanced memory management modules not available
        pass
    

        
    def setup_audio(self):
        """Initializes the PyAudio stream for Morse code playback."""
        global PYAUDIO_AVAILABLE
        self.audio_stream = None
        self.pyaudio_instance = None

        
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


    def create_widgets(self):
        """Creates and arranges all the GUI widgets in the main window."""
        # Create menu bar
        self.create_menu_bar()
        
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.rowconfigure(1, weight=1)  # Central frame gets the weight
        main_frame.columnconfigure(0, weight=1)
        
        # Row 0: Search bar (below menu, above Input/Output)
        self.top_search_frame = ttk.Frame(main_frame)
        self.top_search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        self._create_top_search_bar(self.top_search_frame)

        # Row 1: Central frame with Input/Output panels
        self.central_frame = ttk.Frame(main_frame, padding="10")
        self.central_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        self.central_frame.grid_columnconfigure(0, weight=1)
        self.central_frame.grid_columnconfigure(1, weight=1)
        self.central_frame.grid_rowconfigure(1, weight=1)

        self.create_input_widgets(self.central_frame)
        self.create_output_widgets(self.central_frame)
        
        # Register tabs with visibility monitor and statistics update manager
        self.register_tabs_with_visibility_system()

        self.create_diff_viewer(main_frame)

        # Row 2: Separator
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.grid(row=2, column=0, sticky="ew", pady=10)

        # Row 3: Tool options frame (collapsible)
        tool_frame = ttk.Frame(main_frame, padding="10")
        tool_frame.grid(row=3, column=0, sticky="ew", pady=5)
        self.create_tool_widgets(tool_frame)
        
        # Setup context menus for all text widgets
        self.setup_context_menus()
        
        # Initialize console window as None (will be created when needed)
        self.console_window = None
        
        # Initialize cURL tool window as None (will be created when needed)
        self.curl_tool_window = None
        
        # Initialize List Comparator window as None (will be created when needed)
        self.list_comparator_window = None
        
        # Initialize Notes widget window as None (will be created when needed)
        self.notes_window = None

    def get_system_fonts(self):
        """Get list of available system fonts."""
        try:
            import tkinter.font as tkfont
            return sorted(tkfont.families())
        except:
            return ["Arial", "Helvetica", "Times", "Courier", "Consolas", "Monaco", "DejaVu Sans Mono"]
    
    def is_monospace_font(self, font_name):
        """Check if a font is monospace by testing character widths."""
        # Known monospace fonts (always return True for these)
        known_monospace = {
            'source code pro', 'consolas', 'monaco', 'courier', 'courier new',
            'dejavu sans mono', 'liberation mono', 'ubuntu mono', 'fira code',
            'inconsolata', 'roboto mono', 'jetbrains mono', 'cascadia code',
            'sf mono', 'menlo', 'andale mono', 'lucida console', 'hack',
            'noto mono', 'droid sans mono', 'pt mono', 'space mono'
        }
        
        if font_name.lower() in known_monospace:
            return True
        
        try:
            import tkinter.font as tkfont
            font = tkfont.Font(family=font_name, size=12)
            # Test multiple character pairs for better accuracy
            i_width = font.measure('i')
            w_width = font.measure('W')
            m_width = font.measure('M')
            l_width = font.measure('l')
            
            # All characters should have the same width in monospace fonts
            return i_width == w_width == m_width == l_width
        except:
            return False
    
    def get_monospace_fonts(self):
        """Get list of monospace fonts."""
        all_fonts = self.get_system_fonts()
        monospace = []
        
        # Always add Source Code Pro first (even if not installed, for selection purposes)
        monospace.append("Source Code Pro")
        
        # Add other monospace fonts from system
        for font in all_fonts:
            if font != "Source Code Pro" and self.is_monospace_font(font):
                monospace.append(font)
        
        # Ensure we have essential fallbacks (add if not already present)
        essential_fallbacks = ["Consolas", "Monaco", "Courier New", "DejaVu Sans Mono", "Courier"]
        for fallback in essential_fallbacks:
            if fallback not in monospace:
                monospace.append(fallback)
        
        return monospace
    


    def get_best_font(self, font_type="text"):
        """Get the best available font based on settings and system."""
        font_settings = self.settings.get("font_settings", {})
        
        # Handle legacy settings format
        if "family" in font_settings:
            # Convert old format to new format
            font_settings = {
                "text_font": {
                    "family": font_settings.get("family", "Source Code Pro"),
                    "size": font_settings.get("size", 11),
                    "fallback_family": font_settings.get("fallback_family", "Consolas"),
                    "fallback_family_mac": font_settings.get("fallback_family_mac", "Monaco"),
                    "fallback_family_linux": font_settings.get("fallback_family_linux", "DejaVu Sans Mono")
                }
            }
            self.settings["font_settings"] = font_settings
        
        # Only handle text fonts now
        type_settings = font_settings.get("text_font", {})
        preferred_font = type_settings.get("family", "Source Code Pro")
        font_size = type_settings.get("size", 11)
        
        # Get available system fonts
        available_fonts = self.get_system_fonts()
        
        # Try preferred font first
        if preferred_font in available_fonts:
            return (preferred_font, font_size)
        
        # Special handling for Source Code Pro - if selected but not installed, show a helpful message
        if preferred_font == "Source Code Pro" and preferred_font not in available_fonts:
            self.logger.warning("Source Code Pro selected but not installed. Using fallback font. Download from: https://fonts.google.com/specimen/Source+Code+Pro")
        
        # Try platform-specific fallbacks
        import platform
        system = platform.system().lower()
        
        fallback_key = "fallback_family"
        if system == "darwin":
            fallback_key = "fallback_family_mac"
        elif system == "linux":
            fallback_key = "fallback_family_linux"
        
        fallback_font = type_settings.get(fallback_key, "Consolas" if font_type == "text" else "Arial")
        if fallback_font in available_fonts:
            return (fallback_font, font_size)
        
        # Final fallbacks based on font type
        if font_type == "text":
            fallbacks = ["Consolas", "Monaco", "DejaVu Sans Mono", "Courier New", "monospace"]
        else:
            fallbacks = ["Arial", "Helvetica", "Verdana", "Tahoma", "sans-serif"]
        
        for font in fallbacks:
            if font in available_fonts:
                return (font, font_size)
        
        # System default
        return ("TkDefaultFont", font_size)

    def apply_font_to_text_widgets(self):
        """Apply font settings to all text widgets throughout the application."""
        text_font_family, text_font_size = self.get_best_font("text")
        text_font_tuple = (text_font_family, text_font_size)
        
        try:
            # Apply text font to input tabs
            for tab in self.input_tabs:
                if hasattr(tab, 'text'):
                    tab.text.configure(font=text_font_tuple)
            
            # Apply text font to output tabs
            for tab in self.output_tabs:
                if hasattr(tab, 'text'):
                    tab.text.configure(font=text_font_tuple)
            
            # Apply text font to console log if it exists
            if hasattr(self, 'console_log') and self.console_log:
                self.console_log.configure(font=text_font_tuple)
            
            # Apply to AI Tools text areas
            self.apply_font_to_ai_tools(text_font_tuple)
            
            # Apply to JSON/XML Tool if it exists
            if hasattr(self, 'jsonxml_tool') and self.jsonxml_tool:
                self.jsonxml_tool.apply_font_to_widgets(text_font_tuple)
            
            # Apply to Cron Tool if it exists
            if hasattr(self, 'cron_tool') and self.cron_tool:
                self.cron_tool.apply_font_to_widgets(text_font_tuple)
            
            # Apply to diff viewer using its method if available
            if hasattr(self, 'diff_viewer_widget') and self.diff_viewer_widget:
                if hasattr(self.diff_viewer_widget, 'apply_font_to_widgets'):
                    self.diff_viewer_widget.apply_font_to_widgets(text_font_tuple)
                else:
                    # Fallback to direct application
                    if hasattr(self, 'diff_input_tabs'):
                        for tab in self.diff_input_tabs:
                            if hasattr(tab, 'text'):
                                tab.text.configure(font=text_font_tuple)
                    
                    if hasattr(self, 'diff_output_tabs'):
                        for tab in self.diff_output_tabs:
                            if hasattr(tab, 'text'):
                                tab.text.configure(font=text_font_tuple)
            
            # Apply to any other text widgets that might exist
            self.apply_font_to_tool_widgets(text_font_tuple)
            
            self.logger.info(f"Applied text font: {text_font_family} {text_font_size}pt to all text widgets")
            
        except Exception as e:
            self._handle_error(e, "Applying font settings", "UI", show_dialog=False)
    
    def apply_font_to_ai_tools(self, font_tuple):
        """Apply font to AI Tools text areas."""
        try:
            # Check if AI Tools widget exists and has the apply_font_to_widgets method
            if hasattr(self, 'ai_tools_widget') and self.ai_tools_widget:
                if hasattr(self.ai_tools_widget, 'apply_font_to_widgets'):
                    self.ai_tools_widget.apply_font_to_widgets(font_tuple)
                else:
                    # Fallback to manual application
                    for provider_name, widgets in self.ai_tools_widget.ai_widgets.items():
                        for widget_name, widget in widgets.items():
                            if isinstance(widget, tk.Text):
                                try:
                                    widget.configure(font=font_tuple)
                                except:
                                    pass
                
                self.logger.debug("Applied font to AI Tools text areas")
        except Exception as e:
            self._handle_error(e, "Applying font to AI Tools", "AI Tools", show_dialog=False, severity="debug")
    
    def apply_font_to_tool_widgets(self, font_tuple):
        """Apply font to other tool text widgets."""
        try:
            # Apply to any Text widgets in the tool frames
            for widget_name in dir(self):
                widget = getattr(self, widget_name)
                
                # Check for text widgets by common naming patterns
                if (widget_name.endswith('_text') or 
                    widget_name.endswith('_entry') or 
                    'text' in widget_name.lower()):
                    
                    if hasattr(widget, 'configure'):
                        try:
                            # Try to configure font - will work for Text, Entry, etc.
                            widget.configure(font=font_tuple)
                        except:
                            pass  # Skip if widget doesn't support font
            
            # Recursively apply to child widgets in frames
            self.apply_font_to_child_widgets(self, font_tuple)
            
        except Exception as e:
            self._handle_error(e, "Applying font to tool widgets", "Tools", show_dialog=False, severity="debug")
    
    def apply_font_to_child_widgets(self, parent, font_tuple):
        """Recursively apply font to child text widgets."""
        try:
            for child in parent.winfo_children():
                # Apply to Text widgets
                if isinstance(child, (tk.Text, tk.Entry)):
                    try:
                        child.configure(font=font_tuple)
                    except:
                        pass
                
                # Recursively check children
                if hasattr(child, 'winfo_children'):
                    self.apply_font_to_child_widgets(child, font_tuple)
                    
        except Exception as e:
            pass  # Silently continue if there are issues
    
    def setup_context_menus(self):
        """Setup right-click context menus for all text widgets in the application."""
        if not CONTEXT_MENU_AVAILABLE:
            self.logger.warning("Context menu module not available")
            return
        
        try:
            self.logger.info("Setting up context menus for text widgets...")
            
            # Add context menus to input tabs
            for i, tab in enumerate(self.input_tabs):
                if hasattr(tab, 'text'):
                    add_context_menu(tab.text)
                    self.logger.debug(f"Added context menu to input tab {i+1}")
            
            # Add context menus to output tabs
            for i, tab in enumerate(self.output_tabs):
                if hasattr(tab, 'text'):
                    add_context_menu(tab.text)
                    self.logger.debug(f"Added context menu to output tab {i+1}")
            
            # Add context menus to diff viewer tabs if available
            if hasattr(self, 'diff_input_tabs'):
                for i, tab in enumerate(self.diff_input_tabs):
                    if hasattr(tab, 'text'):
                        add_context_menu(tab.text)
                        self.logger.debug(f"Added context menu to diff input tab {i+1}")
            
            if hasattr(self, 'diff_output_tabs'):
                for i, tab in enumerate(self.diff_output_tabs):
                    if hasattr(tab, 'text'):
                        add_context_menu(tab.text)
                        self.logger.debug(f"Added context menu to diff output tab {i+1}")
            
            # Add context menus to filter entries
            if hasattr(self, 'input_filter_entry'):
                add_context_menu(self.input_filter_entry)
                self.logger.debug("Added context menu to input filter entry")
            
            if hasattr(self, 'output_filter_entry'):
                add_context_menu(self.output_filter_entry)
                self.logger.debug("Added context menu to output filter entry")
            
            # Add context menus to diff viewer filter entries if available
            if hasattr(self, 'diff_viewer_widget'):
                if hasattr(self.diff_viewer_widget, 'input_filter_entry'):
                    add_context_menu(self.diff_viewer_widget.input_filter_entry)
                    self.logger.debug("Added context menu to diff viewer input filter")
                if hasattr(self.diff_viewer_widget, 'output_filter_entry'):
                    add_context_menu(self.diff_viewer_widget.output_filter_entry)
                    self.logger.debug("Added context menu to diff viewer output filter")
            
            # Add context menus to any other text widgets in tool settings
            if hasattr(self, 'tool_settings_frame'):
                add_context_menu_to_children(self.tool_settings_frame)
                self.logger.debug("Added context menus to tool settings widgets")
            
            self.logger.info("Context menus setup complete")
            
        except Exception as e:
            self._handle_error(e, "Setting up context menus", "UI", show_dialog=False)

    def open_font_settings(self):
        """Open font settings dialog."""
        if hasattr(self, 'font_settings_window') and self.font_settings_window and self.font_settings_window.winfo_exists():
            self.font_settings_window.lift()
            return
        
        self.font_settings_window = tk.Toplevel(self)
        self.font_settings_window.title("Font Settings")
        self.font_settings_window.geometry("750x650")
        self.font_settings_window.minsize(700, 600)
        self.font_settings_window.transient(self)
        self.font_settings_window.grab_set()
        
        def on_dialog_close():
            # Clean up the dialog
            self.font_settings_window.destroy()
            self.font_settings_window = None
        
        # Create scrollable main frame
        canvas = tk.Canvas(self.font_settings_window)
        scrollbar = ttk.Scrollbar(self.font_settings_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
        
        # Current font settings
        font_settings = self.settings.get("font_settings", {})
        
        # Handle legacy format
        if "family" in font_settings:
            text_font_settings = {
                "family": font_settings.get("family", "Source Code Pro"),
                "size": font_settings.get("size", 11)
            }
        else:
            text_font_settings = font_settings.get("text_font", {"family": "Source Code Pro", "size": 11})
        
        # === INPUT/OUTPUT TEXT FONTS (MONOSPACE) ===
        text_frame = ttk.LabelFrame(scrollable_frame, text="Input/Output Text Font (Monospace)")
        text_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        # Text font family
        ttk.Label(text_frame, text="Font Family:", font=("TkDefaultFont", 9, "bold")).pack(anchor=tk.W, padx=5, pady=(10, 5))
        
        text_font_frame = ttk.Frame(text_frame)
        text_font_frame.pack(fill=tk.X, padx=5, pady=(0, 10))
        
        self.text_font_var = tk.StringVar(value=text_font_settings.get("family", "Source Code Pro"))
        monospace_fonts = self.get_monospace_fonts()
        
        text_font_combo = ttk.Combobox(text_font_frame, textvariable=self.text_font_var, values=monospace_fonts, width=40)
        text_font_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Placeholder for buttons (will be defined after preview functions)
        self.text_font_buttons_frame = text_font_frame
        
        # Text font size
        ttk.Label(text_frame, text="Font Size:", font=("TkDefaultFont", 9, "bold")).pack(anchor=tk.W, padx=5, pady=(5, 5))
        
        text_size_frame = ttk.Frame(text_frame)
        text_size_frame.pack(fill=tk.X, padx=5, pady=(0, 10))
        
        self.text_size_var = tk.StringVar(value=str(text_font_settings.get("size", 11)))
        text_size_spinbox = ttk.Spinbox(text_size_frame, from_=8, to=24, width=10, textvariable=self.text_size_var)
        text_size_spinbox.pack(side=tk.LEFT)
        

        
        # === PREVIEW ===
        preview_frame = ttk.LabelFrame(scrollable_frame, text="Preview")
        preview_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        # Text font preview
        ttk.Label(preview_frame, text="Input/Output Text Preview:", font=("TkDefaultFont", 9, "bold")).pack(anchor=tk.W, padx=5, pady=(10, 5))
        
        self.text_preview = tk.Text(preview_frame, height=6, wrap=tk.WORD)
        self.text_preview.pack(fill=tk.X, padx=5, pady=(0, 10))
        
        text_sample = """def hello_world():
    print("Hello, World!")
    return "Success"

# ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz
# 0123456789 !@#$%^&*()_+-=[]{}|;:,.<>?"""
        
        self.text_preview.insert("1.0", text_sample)
        

        
        # Update preview functions
        def update_text_preview(*args):
            try:
                family = self.text_font_var.get()
                size = int(self.text_size_var.get())
                self.text_preview.configure(font=(family, size))
            except:
                pass
        

        
        # Bind preview updates
        self.text_font_var.trace_add("write", update_text_preview)
        self.text_size_var.trace_add("write", update_text_preview)
        
        # Now add the Source Code Pro buttons (after preview functions are defined)
        def select_source_code_pro():
            self.text_font_var.set("Source Code Pro")
            update_text_preview()
        
        ttk.Button(self.text_font_buttons_frame, text="Use Source Code Pro", command=select_source_code_pro).pack(side=tk.LEFT, padx=(0, 5))
        
        # Download Source Code Pro button
        def download_source_code_pro():
            import webbrowser
            webbrowser.open("https://fonts.google.com/specimen/Source+Code+Pro")
        
        ttk.Button(self.text_font_buttons_frame, text="Download", command=download_source_code_pro).pack(side=tk.LEFT)
        
        # Initial preview
        update_text_preview()
        
        # === FONT INFO ===
        info_frame = ttk.LabelFrame(scrollable_frame, text="Font Information")
        info_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        current_text_font, current_text_size = self.get_best_font("text")
        
        info_text = f"Currently using:\n"
        info_text += f"• Text: {current_text_font} {current_text_size}pt\n\n"
        
        # Check if Source Code Pro is actually installed
        available_fonts = self.get_system_fonts()
        if "Source Code Pro" in available_fonts:
            info_text += "✅ Source Code Pro: Installed and available\n"
        else:
            info_text += "⚠️ Source Code Pro: Not installed (click Download to get it)\n"
        
        info_text += "License: SIL Open Font License (commercial use allowed)"
        
        ttk.Label(info_frame, text=info_text, foreground="blue").pack(anchor=tk.W, padx=5, pady=10)
        
        # === BUTTONS ===
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 20))
        
        def apply_font_settings():
            try:
                text_family = self.text_font_var.get()
                text_size = int(self.text_size_var.get())
                
                # Update settings
                self.settings["font_settings"] = {
                    "text_font": {
                        "family": text_family,
                        "size": text_size,
                        "fallback_family": "Consolas",
                        "fallback_family_mac": "Monaco",
                        "fallback_family_linux": "DejaVu Sans Mono"
                    }
                }
                
                # Apply to widgets
                self.apply_font_to_text_widgets()
                
                # Save settings
                self.save_settings()
                
                if self.dialog_manager:
                    self.dialog_manager.show_info("Font Settings", 
                        f"Font applied:\n• Text: {text_family} {text_size}pt", "success")
                else:
                    messagebox.showinfo("Font Settings", 
                        f"Font applied:\n• Text: {text_family} {text_size}pt")
                
            except Exception as e:
                self._handle_error(e, "Font Settings", "Error applying font settings")
        
        def reset_font_settings():
            if self.dialog_manager and self.dialog_manager.ask_yes_no("Reset Fonts", "Reset font settings to defaults?", "confirmation") or \
               not self.dialog_manager and messagebox.askyesno("Reset Fonts", "Reset font settings to defaults?"):
                self.text_font_var.set("Source Code Pro")
                self.text_size_var.set("11")
                update_text_preview()
        
        ttk.Button(button_frame, text="Apply", command=apply_font_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Reset to Defaults", command=reset_font_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=on_dialog_close).pack(side=tk.RIGHT)
        
        # Mouse wheel scrolling with safe canvas reference
        
    def open_dialog_settings(self):
        """Open dialog settings configuration window."""
        if hasattr(self, 'dialog_settings_window') and self.dialog_settings_window and self.dialog_settings_window.winfo_exists():
            self.dialog_settings_window.lift()
            return
        
        self.dialog_settings_window = tk.Toplevel(self)
        self.dialog_settings_window.title("Dialog Settings")
        self.dialog_settings_window.geometry("650x550")
        self.dialog_settings_window.minsize(600, 500)
        self.dialog_settings_window.transient(self)
        self.dialog_settings_window.grab_set()
        
        def on_dialog_close():
            # Clean up the dialog
            self.dialog_settings_window.destroy()
            self.dialog_settings_window = None
        
        # Create scrollable main frame
        canvas = tk.Canvas(self.dialog_settings_window)
        scrollbar = ttk.Scrollbar(self.dialog_settings_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
        
        # Current dialog settings
        dialog_settings = self.settings.get("dialog_settings", {})
        
        # Store checkbox variables for each category
        self.dialog_checkboxes = {}
        
        # === HEADER ===
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        header_text = "Configure which notification and confirmation dialogs are shown throughout the application."
        ttk.Label(header_frame, text=header_text, wraplength=580, justify=tk.LEFT).pack(anchor=tk.W)
        
        # === NOTIFICATION DIALOGS ===
        notifications_frame = ttk.LabelFrame(scrollable_frame, text="Notification Dialogs")
        notifications_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        # Success notifications
        success_frame = ttk.Frame(notifications_frame)
        success_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        success_settings = dialog_settings.get("success", {"enabled": True})
        self.dialog_checkboxes["success"] = tk.BooleanVar(value=success_settings.get("enabled", True))
        
        success_checkbox = ttk.Checkbutton(
            success_frame, 
            text="Success Notifications", 
            variable=self.dialog_checkboxes["success"],
            command=lambda: self._on_dialog_setting_changed("success")
        )
        success_checkbox.pack(anchor=tk.W)
        
        success_desc = "Show notifications when operations complete successfully"
        ttk.Label(success_frame, text=success_desc, foreground="gray", font=("TkDefaultFont", 8)).pack(anchor=tk.W, padx=(20, 0))
        
        success_examples = "Examples: \"File saved successfully\", \"Settings applied\", \"Export complete\""
        ttk.Label(success_frame, text=success_examples, foreground="blue", font=("TkDefaultFont", 8)).pack(anchor=tk.W, padx=(20, 0), pady=(2, 0))
        
        # Warning notifications
        warning_frame = ttk.Frame(notifications_frame)
        warning_frame.pack(fill=tk.X, padx=10, pady=(10, 10))
        
        warning_settings = dialog_settings.get("warning", {"enabled": True})
        self.dialog_checkboxes["warning"] = tk.BooleanVar(value=warning_settings.get("enabled", True))
        
        warning_checkbox = ttk.Checkbutton(
            warning_frame, 
            text="Warning Notifications", 
            variable=self.dialog_checkboxes["warning"],
            command=lambda: self._on_dialog_setting_changed("warning")
        )
        warning_checkbox.pack(anchor=tk.W)
        
        warning_desc = "Show warnings for potential issues or invalid inputs"
        ttk.Label(warning_frame, text=warning_desc, foreground="gray", font=("TkDefaultFont", 8)).pack(anchor=tk.W, padx=(20, 0))
        
        warning_examples = "Examples: \"No data specified\", \"Invalid input detected\", \"Feature unavailable\""
        ttk.Label(warning_frame, text=warning_examples, foreground="blue", font=("TkDefaultFont", 8)).pack(anchor=tk.W, padx=(20, 0), pady=(2, 0))
        
        # === CONFIRMATION DIALOGS ===
        confirmations_frame = ttk.LabelFrame(scrollable_frame, text="Confirmation Dialogs")
        confirmations_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        confirmation_frame = ttk.Frame(confirmations_frame)
        confirmation_frame.pack(fill=tk.X, padx=10, pady=(10, 10))
        
        confirmation_settings = dialog_settings.get("confirmation", {"enabled": True})
        self.dialog_checkboxes["confirmation"] = tk.BooleanVar(value=confirmation_settings.get("enabled", True))
        
        confirmation_checkbox = ttk.Checkbutton(
            confirmation_frame, 
            text="Confirmation Dialogs", 
            variable=self.dialog_checkboxes["confirmation"],
            command=lambda: self._on_dialog_setting_changed("confirmation")
        )
        confirmation_checkbox.pack(anchor=tk.W)
        
        confirmation_desc = "Ask for confirmation before destructive or irreversible actions"
        ttk.Label(confirmation_frame, text=confirmation_desc, foreground="gray", font=("TkDefaultFont", 8)).pack(anchor=tk.W, padx=(20, 0))
        
        confirmation_examples = "Examples: \"Clear all tabs?\", \"Delete entry?\", \"Reset settings?\""
        ttk.Label(confirmation_frame, text=confirmation_examples, foreground="blue", font=("TkDefaultFont", 8)).pack(anchor=tk.W, padx=(20, 0), pady=(2, 0))
        
        confirmation_note = "Note: When disabled, actions will proceed automatically with default choices"
        ttk.Label(confirmation_frame, text=confirmation_note, foreground="orange", font=("TkDefaultFont", 8)).pack(anchor=tk.W, padx=(20, 0), pady=(2, 0))
        
        # === SYSTEM MESSAGES ===
        system_frame = ttk.LabelFrame(scrollable_frame, text="System Messages")
        system_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        error_frame = ttk.Frame(system_frame)
        error_frame.pack(fill=tk.X, padx=10, pady=(10, 10))
        
        # Error dialogs (always enabled, cannot be disabled)
        error_checkbox = ttk.Checkbutton(
            error_frame, 
            text="Error Messages", 
            state="disabled"
        )
        error_checkbox.pack(anchor=tk.W)
        # Set checkbox to checked and disabled
        error_var = tk.BooleanVar(value=True)
        error_checkbox.configure(variable=error_var)
        
        error_desc = "Critical error messages (cannot be disabled for safety)"
        ttk.Label(error_frame, text=error_desc, foreground="gray", font=("TkDefaultFont", 8)).pack(anchor=tk.W, padx=(20, 0))
        
        error_examples = "Examples: \"File not found\", \"Network error\", \"Invalid configuration\""
        ttk.Label(error_frame, text=error_examples, foreground="blue", font=("TkDefaultFont", 8)).pack(anchor=tk.W, padx=(20, 0), pady=(2, 0))
        
        error_note = "Error dialogs are always shown to ensure you're informed of critical issues"
        ttk.Label(error_frame, text=error_note, foreground="red", font=("TkDefaultFont", 8)).pack(anchor=tk.W, padx=(20, 0), pady=(2, 0))
        
        # === INFORMATION ===
        info_frame = ttk.LabelFrame(scrollable_frame, text="Information")
        info_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        info_text = "• Disabled dialogs will be logged to the application log for debugging\n"
        info_text += "• Changes apply immediately without requiring application restart\n"
        info_text += "• Settings are automatically saved when you click Apply"
        
        ttk.Label(info_frame, text=info_text, foreground="blue", font=("TkDefaultFont", 8)).pack(anchor=tk.W, padx=10, pady=10)
        
        # === BUTTONS ===
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 20))
        
        def apply_dialog_settings():
            try:
                # Update dialog settings
                new_dialog_settings = {}
                
                # Get default settings structure
                default_settings = self._get_default_settings()
                default_dialog_settings = default_settings["dialog_settings"]
                
                # Update each category
                for category in ["success", "confirmation", "warning", "error"]:
                    if category in default_dialog_settings:
                        new_dialog_settings[category] = default_dialog_settings[category].copy()
                        
                        # Update enabled status from checkboxes (except for error which is always enabled)
                        if category != "error" and category in self.dialog_checkboxes:
                            new_dialog_settings[category]["enabled"] = self.dialog_checkboxes[category].get()
                
                # Update settings
                self.settings["dialog_settings"] = new_dialog_settings
                
                # Apply to DialogManager immediately if it exists
                if hasattr(self, 'dialog_manager') and self.dialog_manager:
                    # Refresh DialogManager settings to apply changes immediately
                    self.dialog_manager.refresh_settings()
                    self.logger.info("DialogManager settings refreshed for immediate application")
                
                # Save settings to ensure persistence across sessions
                self.save_settings()
                self.logger.info("Dialog settings saved to persistent storage")
                
                # Show confirmation
                enabled_categories = [cat for cat, var in self.dialog_checkboxes.items() if var.get()]
                disabled_categories = [cat for cat, var in self.dialog_checkboxes.items() if not var.get()]
                
                message = "Dialog settings applied and saved successfully!\n\n"
                if enabled_categories:
                    message += f"Enabled: {', '.join(enabled_categories)}\n"
                if disabled_categories:
                    message += f"Disabled: {', '.join(disabled_categories)}\n"
                message += "\nChanges are active immediately and will persist across application sessions."
                
                if self.dialog_manager:
                    self.dialog_manager.show_info("Dialog Settings", message, "success")
                else:
                    messagebox.showinfo("Dialog Settings", message)
                
            except Exception as e:
                self._handle_error(e, "Dialog Settings", "Error applying dialog settings")
        
        def reset_dialog_settings():
            if self.dialog_manager and self.dialog_manager.ask_yes_no("Reset Dialog Settings", 
                                 "Reset all dialog settings to defaults?\n\n" +
                                 "This will enable all notification and confirmation dialogs.", "confirmation") or \
               not self.dialog_manager and messagebox.askyesno("Reset Dialog Settings", 
                                 "Reset all dialog settings to defaults?\n\n" +
                                 "This will enable all notification and confirmation dialogs."):
                
                self.logger.info("Resetting dialog settings to defaults")
                
                # Reset all checkboxes to enabled (except error which is always enabled)
                for category, var in self.dialog_checkboxes.items():
                    var.set(True)
                    # Apply real-time updates for each category
                    self._on_dialog_setting_changed(category)
                
                # Apply the reset settings immediately and save
                apply_dialog_settings()
        
        ttk.Button(button_frame, text="Apply", command=apply_dialog_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Reset to Defaults", command=reset_dialog_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=on_dialog_close).pack(side=tk.RIGHT)
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                # Canvas has been destroyed, ignore the event
                pass
        
        # Bind mouse wheel to canvas and scrollable frame
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        
        # Also bind to the dialog settings window to catch events
        self.dialog_settings_window.bind("<MouseWheel>", _on_mousewheel)
        
        self.dialog_settings_window.protocol("WM_DELETE_WINDOW", on_dialog_close)

    def _on_dialog_setting_changed(self, category):
        """Handle real-time dialog setting changes when checkboxes are toggled."""
        if not hasattr(self, 'dialog_checkboxes') or category not in self.dialog_checkboxes:
            return
            
        try:
            # Get the new enabled status
            enabled = self.dialog_checkboxes[category].get()
            
            # Update DialogManager immediately for real-time effect
            if hasattr(self, 'dialog_manager') and self.dialog_manager:
                success = self.dialog_manager.update_category_setting(category, enabled)
                if success:
                    self.logger.info(f"Real-time update: {category} dialogs {'enabled' if enabled else 'disabled'}")
                else:
                    self.logger.warning(f"Failed to update {category} dialog setting in real-time")
            
            # Update settings in memory (but don't save yet - wait for Apply button)
            if "dialog_settings" not in self.settings:
                self.settings["dialog_settings"] = self._get_default_settings()["dialog_settings"]
            
            if category in self.settings["dialog_settings"]:
                self.settings["dialog_settings"][category]["enabled"] = enabled
                
        except Exception as e:
            self._handle_error(e, f"Dialog setting change for {category}", "Settings", show_dialog=False)

    def create_menu_bar(self):
        """Creates the menu bar with File, Settings, and Help menus."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # Initialize export path variable
        self.export_path_var = tk.StringVar(value=self.settings.get("export_path", ""))
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Data Location...", command=self._show_data_location_dialog)
        file_menu.add_command(label="Export Location", command=self.browse_export_path)
        file_menu.add_separator()
        
        # Export Selected Output submenu
        export_output_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Export Selected Output as", menu=export_output_menu)
        export_output_menu.add_command(label="CSV", command=lambda: self.export_file("csv"))
        export_output_menu.add_command(label="PDF", command=lambda: self.export_file("pdf"))
        export_output_menu.add_command(label="TXT", command=lambda: self.export_file("txt"))
        export_output_menu.add_command(label="DOCX", command=lambda: self.export_file("docx"))
        
        # Export Selected Input submenu
        export_input_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Export Selected Input as", menu=export_input_menu)
        export_input_menu.add_command(label="CSV", command=lambda: self.export_input_file("csv"))
        export_input_menu.add_command(label="PDF", command=lambda: self.export_input_file("pdf"))
        export_input_menu.add_command(label="TXT", command=lambda: self.export_input_file("txt"))
        export_input_menu.add_command(label="DOCX", command=lambda: self.export_input_file("docx"))
        
        file_menu.add_separator()
        
        # Load Presets (reset tool settings to defaults)
        if SETTINGS_DEFAULTS_REGISTRY_AVAILABLE:
            file_menu.add_command(label="Load Presets...", command=self.show_load_presets_dialog, accelerator="Ctrl+Shift+P")
        
        # Settings Backup and Recovery submenu
        if DATABASE_SETTINGS_AVAILABLE and hasattr(self, 'db_settings_manager'):
            backup_menu = tk.Menu(file_menu, tearoff=0)
            file_menu.add_cascade(label="Settings Backup & Recovery", menu=backup_menu)
            
            # Backup operations
            backup_menu.add_command(label="Create Manual Backup", command=self.create_manual_backup)
            backup_menu.add_command(label="View Backup History", command=self.show_backup_history)
            backup_menu.add_separator()
            
            # Import/Export operations
            backup_menu.add_command(label="Export Settings to JSON...", command=self.export_settings_to_json)
            backup_menu.add_command(label="Import Settings from JSON...", command=self.import_settings_from_json)
            backup_menu.add_separator()
            
            # Recovery operations
            backup_menu.add_command(label="Restore from Backup...", command=self.restore_from_backup_dialog)
            backup_menu.add_command(label="Repair Database", command=self.repair_database_dialog)
            backup_menu.add_separator()
            
            # Validation and maintenance
            backup_menu.add_command(label="Validate Settings Integrity", command=self.validate_settings_integrity_dialog)
            backup_menu.add_command(label="Cleanup Old Backups", command=self.cleanup_old_backups_dialog)
        
        file_menu.add_separator()
        
        # Add Save as Note if Notes widget is available
        if NOTES_WIDGET_MODULE_AVAILABLE:
            file_menu.add_command(label="Save as Note", command=self.save_as_note, accelerator="Ctrl+S")
            file_menu.add_separator()
        
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Settings Menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Font Settings...", command=self.open_font_settings)
        settings_menu.add_command(label="Dialog Settings...", command=self.open_dialog_settings)
        settings_menu.add_command(label="Performance Settings...", command=self.show_performance_settings)
        
        # Add Retention Settings if database is available
        if DATABASE_SETTINGS_AVAILABLE and hasattr(self, 'db_settings_manager'):
            settings_menu.add_command(label="Retention Settings...", command=self.open_retention_settings)
        
        # Add MCP Security settings
        settings_menu.add_command(label="MCP Security...", command=self.open_mcp_security_settings)
        
        settings_menu.add_separator()
        settings_menu.add_command(label="Console Log", command=self.show_console_log)
        
        # Widgets Menu
        widgets_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Widgets", menu=widgets_menu)
        
        # Add cURL Tool if available
        if CURL_TOOL_MODULE_AVAILABLE:
            widgets_menu.add_command(
                label="cURL Tool", 
                command=self.open_curl_tool_window,
                accelerator="Ctrl+U"
            )
        
        # Add List Comparator
        widgets_menu.add_command(
            label="List Comparator",
            command=self.open_list_comparator_window
        )
        
        # Add Notes widget if available
        if NOTES_WIDGET_MODULE_AVAILABLE:
            widgets_menu.add_command(
                label="Notes",
                command=self.open_notes_widget,
                accelerator="Ctrl+N"
            )
        
        # Add MCP Manager if available
        if MCP_MANAGER_MODULE_AVAILABLE:
            widgets_menu.add_command(
                label="MCP Manager",
                command=self.open_mcp_manager,
                accelerator="Ctrl+M"
            )
        
        # Add Smart Diff if available
        if SMART_DIFF_WIDGET_AVAILABLE:
            widgets_menu.add_command(
                label="Smart Diff",
                command=self.open_smart_diff_window,
                accelerator="Ctrl+D"
            )
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Check for Updates...", command=self._show_update_dialog)
        help_menu.add_separator()
        help_menu.add_command(label="GitHub", command=lambda: webbrowser.open_new("https://github.com/matbanik/Pomera-AI-Commander"))
        help_menu.add_command(label="Report Issue", command=self.open_report_issue)
        help_menu.add_command(label="Ask AI", command=self.open_ai_tools)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self._show_about_dialog)

    def open_report_issue(self):
        """Opens the GitHub issues page in the default browser."""
        try:
            webbrowser.open_new("https://github.com/matbanik/Pomera-AI-Commander/issues/new")
            self.logger.info("Opened GitHub issues page")
        except Exception as e:
            self._handle_error(e, "Opening GitHub issues page", "Browser")

    def open_ai_tools(self):
        """Opens the AI Tools from the Help menu."""
        try:
            if AI_TOOLS_AVAILABLE:
                self.select_tool("AI Tools")
                self.logger.info("Switched to AI Tools from Help menu")
            else:
                self.logger.warning("AI Tools not available")
                if self.dialog_manager:
                    self.dialog_manager.show_warning(
                        "AI Tools Unavailable",
                        "AI Tools functionality is not available. Please ensure the ai_tools.py module is installed.",
                        "tool_validation"
                    )
                else:
                    messagebox.showwarning("AI Tools Unavailable", "AI Tools functionality is not available. Please ensure the ai_tools.py module is installed.")
        except Exception as e:
            self._handle_error(e, "Opening AI Tools", "Tool Operations")

    def create_input_widgets(self, parent):
        """Creates widgets for the input text section."""
        input_frame = ttk.Frame(parent)
        input_frame.grid(row=0, column=0, rowspan=2, padx=(0, 5), sticky="nsew")
        input_frame.grid_rowconfigure(1, weight=1)
        input_frame.grid_columnconfigure(0, weight=1)

        title_row = ttk.Frame(input_frame)
        title_row.grid(row=0, column=0, sticky="w")
        ttk.Label(title_row, text="Input", font=("Helvetica", 12, "bold")).pack(side=tk.LEFT)
        
        # Create load from file button
        load_file_btn = ttk.Button(title_row, text="📁", command=self.load_file_to_input, width=3)
        load_file_btn.pack(side=tk.LEFT, padx=(10, 0))
        self.Tooltip(load_file_btn, "Load from File")
        
        # Create erase button with better icon and tooltip
        erase_input_btn = ttk.Button(title_row, text="⌫", command=self.clear_all_input_tabs, width=3)
        erase_input_btn.pack(side=tk.LEFT, padx=(5, 0))
        self.Tooltip(erase_input_btn, "Erase Tabs")
        
        self.input_notebook = ttk.Notebook(input_frame)
        self.input_notebook.grid(row=1, column=0, sticky="nsew")
        self.input_tabs = []
        for i in range(AppConfig.TAB_COUNT):
            # Use optimized components when available
            if EFFICIENT_LINE_NUMBERS_AVAILABLE:
                tab = OptimizedTextWithLineNumbers(self.input_notebook)
            else:
                tab = TextWithLineNumbers(self.input_notebook)
            
            # Apply font settings
            font_family, font_size = self.get_best_font()
            tab.text.configure(font=(font_family, font_size))
            
            # Use EventConsolidator if available, otherwise fall back to original bindings
            if hasattr(self, 'event_consolidator') and self.event_consolidator:
                # Register with EventConsolidator for consolidated event handling
                # This replaces multiple event handlers (<<Modified>>, <KeyRelease>, <Button-1>)
                # with a single consolidated handler per widget
                widget_id = f"input_tab_{i}"
                self.event_consolidator.register_text_widget(
                    widget_id, 
                    tab.text, 
                    lambda wid, idx=i: self._consolidated_input_changed(wid, idx)
                )
                # Still bind tab content changed for label updates (not handled by consolidator)
                tab.text.bind("<<Modified>>", self.on_tab_content_changed, add=True)
                self.logger.debug(f"Registered input tab {i} with EventConsolidator (widget_id: {widget_id})")
            else:
                # Fallback to original event bindings when EventConsolidator is not available
                tab.text.bind("<KeyRelease>", self.on_input_changed)
                tab.text.bind("<<Modified>>", self.on_tab_content_changed)
                self.logger.debug(f"Using legacy event bindings for input tab {i}")
            
            tab.text.tag_configure("yellow_highlight", background="yellow")
            self.input_tabs.append(tab)
            self.input_notebook.add(tab, text=f"{i+1}:")
        self.input_notebook.bind("<<NotebookTabChanged>>", self.on_input_tab_change)

        # Create status bar frame
        status_frame = ttk.Frame(input_frame)
        status_frame.grid(row=2, column=0, sticky="ew")
        status_frame.grid_columnconfigure(0, weight=1)
        
        self.input_status_bar = ttk.Label(status_frame, text="Bytes: 0 | Word: 0 | Sentence: 0 | Line: 0 | Tokens: 0")
        self.input_status_bar.grid(row=0, column=0, sticky="w")
        
        # Create line filter frame
        filter_frame = ttk.Frame(input_frame)
        filter_frame.grid(row=3, column=0, sticky="ew", pady=(2, 0))
        filter_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(filter_frame, text="Line Filter:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.input_filter_var = tk.StringVar()
        self.input_filter_entry = ttk.Entry(filter_frame, textvariable=self.input_filter_var, width=30)
        self.input_filter_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        self.input_filter_var.trace_add("write", self.on_input_filter_changed)
        self.Tooltip(self.input_filter_entry, "Filter lines containing this text (case-insensitive)")
        
        # Clear filter button
        clear_input_filter_btn = ttk.Button(filter_frame, text="✖", command=self.clear_input_filter, width=3)
        clear_input_filter_btn.grid(row=0, column=2, padx=(0, 5))
        self.Tooltip(clear_input_filter_btn, "Clear Filter")
        
        # Store original content for filtering
        self.input_original_content = [""] * AppConfig.TAB_COUNT
        
        # Performance status is now in window title

    def create_output_widgets(self, parent):
        """Creates widgets for the output text section."""
        output_frame = ttk.Frame(parent)
        output_frame.grid(row=0, column=1, rowspan=2, padx=(5, 0), sticky="nsew")
        output_frame.grid_rowconfigure(1, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)

        title_row = ttk.Frame(output_frame)
        title_row.grid(row=0, column=0, sticky="w")
        ttk.Label(title_row, text="Output", font=("Helvetica", 12, "bold")).pack(side=tk.LEFT)
        
        # Create dropdown for "Send to Input"
        self.send_to_input_var = tk.StringVar(value="Send to Input")
        send_to_input_menu = ttk.Menubutton(title_row, textvariable=self.send_to_input_var, direction="below")
        send_to_input_menu.pack(side=tk.LEFT, padx=(10, 6))
        
        # Create the dropdown menu
        dropdown_menu = tk.Menu(send_to_input_menu, tearoff=0)
        send_to_input_menu.config(menu=dropdown_menu)
        for i in range(AppConfig.TAB_COUNT):
            dropdown_menu.add_command(label=f"Tab {i+1}", command=lambda tab=i: self.copy_to_specific_input_tab(tab, None))
        
        # Create copy to clipboard button with better icon and tooltip
        copy_btn = ttk.Button(title_row, text="⎘", command=self.copy_to_clipboard, width=3)
        copy_btn.pack(side=tk.LEFT, padx=(0, 6))
        self.Tooltip(copy_btn, "Copy to Clipboard")
        
        # Add cancel button for async operations (initially hidden)
        if ASYNC_PROCESSING_AVAILABLE:
            self.cancel_async_button = ttk.Button(title_row, text="❌", command=self.cancel_current_async_processing, width=3)
            # Initially hidden - will be shown during async operations
        
        # Create erase button with better icon and tooltip
        erase_output_btn = ttk.Button(title_row, text="⌫", command=self.clear_all_output_tabs, width=3)
        erase_output_btn.pack(side=tk.LEFT)
        self.Tooltip(erase_output_btn, "Erase Tabs")

        self.output_notebook = ttk.Notebook(output_frame)
        self.output_notebook.grid(row=1, column=0, sticky="nsew")
        self.output_tabs = []
        for i in range(AppConfig.TAB_COUNT):
            # Use optimized components when available
            if EFFICIENT_LINE_NUMBERS_AVAILABLE:
                tab = OptimizedTextWithLineNumbers(self.output_notebook)
            else:
                tab = TextWithLineNumbers(self.output_notebook)
            
            # Apply font settings
            font_family, font_size = self.get_best_font()
            tab.text.configure(font=(font_family, font_size))
            
            tab.text.config(state="disabled")
            tab.text.bind("<<Modified>>", self.on_tab_content_changed)
            tab.text.tag_configure("pink_highlight", background="pink")
            self.output_tabs.append(tab)
            self.output_notebook.add(tab, text=f"{i+1}:")
        self.output_notebook.bind("<<NotebookTabChanged>>", self.on_output_tab_change)

        self.output_status_bar = ttk.Label(output_frame, text="Bytes: 0 | Word: 0 | Sentence: 0 | Line: 0 | Tokens: 0")
        self.output_status_bar.grid(row=2, column=0, sticky="ew")
        
        # Create line filter frame
        output_filter_frame = ttk.Frame(output_frame)
        output_filter_frame.grid(row=3, column=0, sticky="ew", pady=(2, 0))
        output_filter_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(output_filter_frame, text="Line Filter:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.output_filter_var = tk.StringVar()
        self.output_filter_entry = ttk.Entry(output_filter_frame, textvariable=self.output_filter_var, width=30)
        self.output_filter_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        self.output_filter_var.trace_add("write", self.on_output_filter_changed)
        self.Tooltip(self.output_filter_entry, "Filter lines containing this text (case-insensitive)")
        
        # Clear filter button
        clear_output_filter_btn = ttk.Button(output_filter_frame, text="✖", command=self.clear_output_filter, width=3)
        clear_output_filter_btn.grid(row=0, column=2, padx=(0, 5))
        self.Tooltip(clear_output_filter_btn, "Clear Filter")
        
        # Store original content for filtering
        self.output_original_content = [""] * AppConfig.TAB_COUNT
    
    def register_tabs_with_visibility_system(self):
        """
        Register all tabs with the visibility monitor and statistics update manager.
        
        This enables visibility-aware statistics updates that skip hidden tabs,
        inactive components, and minimized windows.
        """
        if not hasattr(self, 'visibility_monitor') or not self.visibility_monitor:
            self.logger.debug("Visibility monitor not available - skipping tab registration")
            return
        
        if not hasattr(self, 'statistics_update_manager') or not self.statistics_update_manager:
            self.logger.debug("Statistics update manager not available - skipping tab registration")
            return
        
        # Get currently active tabs
        active_input_index = self.input_notebook.index(self.input_notebook.select())
        active_output_index = self.output_notebook.index(self.output_notebook.select())
        
        # Register input tabs
        for i, tab in enumerate(self.input_tabs):
            component_id = f"input_tab_{i}"
            tab_id = f"input_notebook_tab_{i}"
            
            # Determine initial visibility state
            is_active = (i == active_input_index)
            initial_state = VisibilityState.VISIBLE_ACTIVE if is_active else VisibilityState.HIDDEN
            
            # Register with visibility monitor
            self.visibility_monitor.register_component(
                component_id=component_id,
                widget=tab.text,
                tab_id=tab_id,
                initial_state=initial_state
            )
            
            # Register with statistics update manager
            self.statistics_update_manager.register_component(
                component_id=component_id,
                widget=tab.text,
                initial_visibility=initial_state
            )
            
            self.logger.debug(f"Registered {component_id} with visibility system (active: {is_active})")
        
        # Register output tabs
        for i, tab in enumerate(self.output_tabs):
            component_id = f"output_tab_{i}"
            tab_id = f"output_notebook_tab_{i}"
            
            # Determine initial visibility state
            is_active = (i == active_output_index)
            initial_state = VisibilityState.VISIBLE_ACTIVE if is_active else VisibilityState.HIDDEN
            
            # Register with visibility monitor
            self.visibility_monitor.register_component(
                component_id=component_id,
                widget=tab.text,
                tab_id=tab_id,
                initial_state=initial_state
            )
            
            # Register with statistics update manager
            self.statistics_update_manager.register_component(
                component_id=component_id,
                widget=tab.text,
                initial_visibility=initial_state
            )
            
            self.logger.debug(f"Registered {component_id} with visibility system (active: {is_active})")
        
        # Register status bars as components
        self.visibility_monitor.register_component(
            component_id="input_status_bar",
            widget=self.input_status_bar,
            initial_state=VisibilityState.VISIBLE_ACTIVE
        )
        
        self.visibility_monitor.register_component(
            component_id="output_status_bar",
            widget=self.output_status_bar,
            initial_state=VisibilityState.VISIBLE_ACTIVE
        )
        
        self.logger.info(f"Registered {len(self.input_tabs) + len(self.output_tabs)} tabs with visibility system")

    def clear_all_input_tabs(self):
        """Asks for confirmation and clears all input tab contents."""
        if self.dialog_manager and self.dialog_manager.ask_yes_no("Confirm", "Clear all Input tabs? This cannot be undone.", "confirmation") or \
           not self.dialog_manager and messagebox.askyesno("Confirm", "Clear all Input tabs? This cannot be undone."):
            for tab in self.input_tabs:
                tab.text.delete("1.0", tk.END)
            if hasattr(self, 'diff_input_tabs'):
                for tab in self.diff_input_tabs:
                    tab.text.delete("1.0", tk.END)
            
            # Clear original content storage
            if hasattr(self, 'input_original_content'):
                self.input_original_content = [""] * AppConfig.TAB_COUNT

    def load_file_to_input(self):
        """Load file content into the current active input tab."""
        try:
            # Get the current active tab
            current_tab_index = self.input_notebook.index(self.input_notebook.select())
            current_tab = self.input_tabs[current_tab_index]
            
            # Open file dialog
            file_path = filedialog.askopenfilename(
                title="Load File Content",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("JSON files", "*.json"),
                    ("XML files", "*.xml"),
                    ("CSV files", "*.csv"),
                    ("Python files", "*.py"),
                    ("JavaScript files", "*.js"),
                    ("HTML files", "*.html"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                # Show confirmation dialog
                file_name = os.path.basename(file_path)
                tab_number = current_tab_index + 1
                
                confirm_message = f"Load content from '{file_name}' into Tab {tab_number}?\n\n"
                confirm_message += "• The file will NOT be modified\n"
                confirm_message += "• Content will be copied into the tab\n"
                confirm_message += "• Any existing content in the tab will be replaced"
                
                if self.dialog_manager and self.dialog_manager.ask_yes_no("Confirm Load", confirm_message, "confirmation") or \
                   not self.dialog_manager and messagebox.askyesno("Confirm Load", confirm_message):
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                    
                    # Clear current tab and insert content
                    current_tab.text.delete("1.0", tk.END)
                    current_tab.text.insert("1.0", content)
                    
                    # Update tab title to show file name
                    self.input_notebook.tab(current_tab_index, text=f"{tab_number}: {file_name}")
                    
                    # Show success message
                    if self.dialog_manager:
                        self.dialog_manager.show_info(
                            "File Loaded", 
                            f"Content from '{file_name}' has been loaded into Tab {tab_number}.\n\n"
                            f"The original file remains unchanged.", "success")
                    else:
                        messagebox.showinfo(
                            "File Loaded", 
                            f"Content from '{file_name}' has been loaded into Tab {tab_number}.\n\n"
                            f"The original file remains unchanged.")
                    
                    self.logger.info(f"Loaded file content from {file_path} into input tab {tab_number}")
                    
                    # Apply tool if not manual processing
                    if self.tool_var.get() not in self.manual_process_tools:
                        self.apply_tool()
        
        except Exception as e:
            self._handle_error(e, "Loading file", "File Operations", 
                               user_message=f"Failed to load file:\n\n{str(e)}")
            
            # Clear any active filter
            if hasattr(self, 'input_filter_var'):
                self.input_filter_var.set("")
            
            self.update_tab_labels()
            self.save_settings()
            self.after(10, self.update_all_stats)

    def clear_all_output_tabs(self):
        """Asks for confirmation and clears all output tab contents."""
        if self.dialog_manager and self.dialog_manager.ask_yes_no("Confirm", "Clear all Output tabs? This cannot be undone.", "confirmation") or \
           not self.dialog_manager and messagebox.askyesno("Confirm", "Clear all Output tabs? This cannot be undone."):
            for tab in self.output_tabs:
                tab.text.config(state="normal")
                tab.text.delete("1.0", tk.END)
                tab.text.config(state="disabled")
            if hasattr(self, 'diff_output_tabs'):
                for tab in self.diff_output_tabs:
                    tab.text.delete("1.0", tk.END)
            
            # Clear original content storage
            if hasattr(self, 'output_original_content'):
                self.output_original_content = [""] * AppConfig.TAB_COUNT
            
            # Clear any active filter
            if hasattr(self, 'output_filter_var'):
                self.output_filter_var.set("")
            
            self.update_tab_labels()
            self.save_settings()
            self.after(10, self.update_all_stats)

    def on_input_filter_changed(self, *args):
        """Handle changes to the input line filter."""
        self.apply_input_filter()
    
    def on_output_filter_changed(self, *args):
        """Handle changes to the output line filter."""
        self.apply_output_filter()
    
    def apply_input_filter(self):
        """Apply line filter to the current input tab."""
        try:
            current_tab_index = self.input_notebook.index(self.input_notebook.select())
            current_tab = self.input_tabs[current_tab_index]
            filter_text = self.input_filter_var.get().lower()
            
            # Store original content if not already stored
            if not self.input_original_content[current_tab_index]:
                self.input_original_content[current_tab_index] = current_tab.text.get("1.0", tk.END)
            
            original_content = self.input_original_content[current_tab_index]
            
            if not filter_text:
                # No filter, show original content if we have it
                if original_content and original_content.strip():
                    current_tab.text.delete("1.0", tk.END)
                    current_tab.text.insert("1.0", original_content)
                # If no original content, keep current content unchanged
            else:
                # Apply filter
                lines = original_content.split('\n')
                filtered_lines = [line for line in lines if filter_text in line.lower()]
                filtered_content = '\n'.join(filtered_lines)
                
                current_tab.text.delete("1.0", tk.END)
                current_tab.text.insert("1.0", filtered_content)
            
            self.after(10, self.update_all_stats)
        except Exception as e:
            self._handle_error(e, "Applying input filter", "UI", show_dialog=False)
    
    def apply_output_filter(self):
        """Apply line filter to the current output tab."""
        try:
            current_tab_index = self.output_notebook.index(self.output_notebook.select())
            current_tab = self.output_tabs[current_tab_index]
            filter_text = self.output_filter_var.get().strip()
            
            # Enable text widget temporarily
            current_tab.text.config(state="normal")
            
            # Get current content from the widget
            current_content = current_tab.text.get("1.0", tk.END)
            
            if not filter_text:
                # No filter - if we have stored original content, restore it
                # Otherwise, keep current content unchanged
                stored_original = self.output_original_content[current_tab_index]
                if stored_original and stored_original.strip():
                    current_tab.text.delete("1.0", tk.END)
                    current_tab.text.insert("1.0", stored_original)
                    # Clear the stored content since we're no longer filtering
                    self.output_original_content[current_tab_index] = ""
                # If no stored content, don't change anything - keep current content
            else:
                # We want to filter - check if we need to store original content
                stored_original = self.output_original_content[current_tab_index]
                
                if not stored_original:
                    # First time filtering - store current content as original
                    self.output_original_content[current_tab_index] = current_content
                    content_to_filter = current_content
                else:
                    # Already filtering - use stored original
                    content_to_filter = stored_original
                
                # Apply filter
                lines = content_to_filter.split('\n')
                filtered_lines = [line for line in lines if filter_text.lower() in line.lower()]
                filtered_content = '\n'.join(filtered_lines)
                
                current_tab.text.delete("1.0", tk.END)
                current_tab.text.insert("1.0", filtered_content)
            
            # Disable the text widget again
            current_tab.text.config(state="disabled")
            self.after(10, self.update_all_stats)
            
        except Exception as e:
            self._handle_error(e, "Applying output filter", "UI", show_dialog=False)
    
    def clear_input_filter(self):
        """Clear the input line filter."""
        self.input_filter_var.set("")
    
    def clear_output_filter(self):
        """Clear the output line filter."""
        self.output_filter_var.set("")
    
    def clear_all_filters(self):
        """Clear both input and output line filters safely."""
        # Just clear the stored filter content, don't clear the filter fields
        # This prevents the content erasure issue while still clearing filter state
        try:
            current_tab_index = self.output_notebook.index(self.output_notebook.select())
            self.output_original_content[current_tab_index] = ""
        except:
            pass
        
        # Clear the filter fields silently
        if hasattr(self, 'input_filter_var'):
            self.input_filter_var.set("")
        if hasattr(self, 'output_filter_var'):
            self.output_filter_var.set("")
    
    def store_original_input_content(self, tab_index):
        """Store the original content of an input tab before filtering."""
        if tab_index < len(self.input_tabs):
            self.input_original_content[tab_index] = self.input_tabs[tab_index].text.get("1.0", tk.END)
    
    def store_original_output_content(self, tab_index):
        """Store the original content of an output tab before filtering."""
        if tab_index < len(self.output_tabs):
            self.output_original_content[tab_index] = self.output_tabs[tab_index].text.get("1.0", tk.END)
    
    def force_update_original_output_content(self):
        """Force update the original content from the current text widget content."""
        try:
            current_tab_index = self.output_notebook.index(self.output_notebook.select())
            current_tab = self.output_tabs[current_tab_index]
            current_tab.text.config(state="normal")
            current_content = current_tab.text.get("1.0", tk.END)
            current_tab.text.config(state="disabled")
            self.output_original_content[current_tab_index] = current_content
        except Exception as e:
            self._handle_error(e, "Updating output content", "UI", show_dialog=False)
    
    def debug_output_content(self):
        """Debug method to check what content is stored."""
        try:
            current_tab_index = self.output_notebook.index(self.output_notebook.select())
            stored_content = self.output_original_content[current_tab_index]
            current_tab = self.output_tabs[current_tab_index]
            current_tab.text.config(state="normal")
            widget_content = current_tab.text.get("1.0", tk.END)
            current_tab.text.config(state="disabled")
            
            print(f"DEBUG - Tab {current_tab_index}:")
            print(f"Stored original: {repr(stored_content[:100])}")
            print(f"Widget content: {repr(widget_content[:100])}")
            print(f"Filter text: {repr(self.output_filter_var.get())}")
        except Exception as e:
            print(f"Debug error: {e}")
    
    def _create_top_search_bar(self, parent):
        """Create the top search bar (below menu, above Input/Output panels)."""
        self.tool_var = tk.StringVar(value=self.settings.get("selected_tool", "Case Tool"))
        
        # Use ToolSearchPalette if available
        if TOOL_SEARCH_WIDGET_AVAILABLE and TOOL_LOADER_AVAILABLE and self.tool_loader:
            self.tool_search_palette = ToolSearchPalette(
                parent,
                tool_loader=self.tool_loader,
                on_tool_selected=self._on_palette_tool_selected,
                settings=self.settings,
                on_settings_change=self._on_ui_settings_change
            )
            self.tool_search_palette.pack(fill=tk.X, expand=True, padx=5)
            self.tool_menu = self.tool_search_palette
            self.tool_dropdown_menu = None
            self.logger.info("Top search bar created with ToolSearchPalette")
        else:
            # Fallback: simple label
            self.tool_search_palette = None
            self.tool_menu = None
            self.tool_dropdown_menu = None
            ttk.Label(parent, text="Tool search not available").pack()


    def create_tool_widgets(self, parent):
        """Creates widgets for the tool options/settings section (bottom panel).
        
        Note: The search bar is now created separately by _create_top_search_bar()
        at the top of the main layout.
        """
        # Get tool list for fallback
        if TOOL_LOADER_AVAILABLE and self.tool_loader:
            self.tool_options = self.tool_loader.get_available_tools()
        else:
            self.tool_options = [
                "AI Tools", "Base64 Encoder/Decoder", "Case Tool", "Column Tools",
                "Cron Tool", "Diff Viewer", "Email Header Analyzer", "Extraction Tools",
                "Find & Replace Text", "Folder File Reporter", "Generator Tools",
                "JSON/XML Tool", "Line Tools", "Markdown Tools",
                "Number Base Converter", "Sorter Tools",
                "String Escape Tool", "Text Statistics", "Text Wrapper", "Timestamp Converter",
                "Translator Tools", "URL Parser", "Whitespace Tools"
            ]
        self.filtered_tool_options = list(self.tool_options)

        # Tool settings panel (with collapsible wrapper if available)
        if COLLAPSIBLE_PANEL_AVAILABLE:
            # Get collapsed state from settings
            ui_layout = self.settings.get("ui_layout", {})
            initial_collapsed = ui_layout.get("options_panel_collapsed", False)
            
            # Create CollapsiblePanel to wrap tool settings
            self.options_collapsible = CollapsiblePanel(
                parent,
                title="Tool Options",
                collapsed=initial_collapsed,
                on_state_change=self._on_options_panel_toggle
            )
            self.options_collapsible.pack(fill=tk.BOTH, expand=True, padx=5)
            
            # Tool settings go inside the collapsible panel's content
            self.tool_settings_frame = ttk.Frame(self.options_collapsible.content_frame)
            self.tool_settings_frame.pack(fill=tk.BOTH, expand=True)
            
            self.logger.info(f"Options panel wrapped in CollapsiblePanel (collapsed={initial_collapsed})")
        else:
            # Fallback: Tool settings frame without collapsible wrapper
            self.tool_settings_frame = ttk.Frame(parent)
            self.tool_settings_frame.pack(fill=tk.BOTH, expand=True, padx=5)
            self.options_collapsible = None
        
        # Initialize Widget Cache for tool settings UI
        if WIDGET_CACHE_AVAILABLE:
            self.widget_cache = init_widget_cache(
                self.tool_settings_frame,
                strategy=CacheStrategy.ALWAYS,
                max_cached=20
            )
            self._register_widget_factories()
            self.logger.info("Widget Cache initialized for tool settings")
        else:
            self.widget_cache = None
        
        # Defer tool settings UI creation until after window is visible
        # This makes startup feel faster by moving ~300ms of UI creation to after mainloop starts
        self._tool_ui_initialized = False
        self._show_tool_loading_placeholder()
        self.after_idle(self._deferred_tool_settings_init)
    
    def _show_tool_loading_placeholder(self):
        """Show lightweight placeholder while tool UI is loading."""
        self._loading_label = ttk.Label(
            self.tool_settings_frame, 
            text="Loading tool options...",
            font=("TkDefaultFont", 10, "italic"),
            foreground="gray"
        )
        self._loading_label.pack(pady=20)
    
    def _deferred_tool_settings_init(self):
        """Initialize tool settings UI after window is visible (faster perceived startup)."""
        # Remove placeholder
        if hasattr(self, '_loading_label') and self._loading_label.winfo_exists():
            self._loading_label.destroy()
        
        # Now create the actual tool settings UI
        self._tool_ui_initialized = True
        self.update_tool_settings_ui()
        self.logger.info("Deferred tool settings UI initialization complete")
    
    def _create_tool_search_palette(self, parent):
        """Create the new ToolSearchPalette for tool selection."""
        # Get UI layout settings
        ui_layout = self.settings.get("ui_layout", {})
        
        self.tool_search_palette = ToolSearchPalette(
            parent,
            tool_loader=self.tool_loader,
            on_tool_selected=self._on_palette_tool_selected,
            settings=self.settings,
            on_settings_change=self._on_ui_settings_change
        )
        # Pack to fill horizontally (top-center layout)
        self.tool_search_palette.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # For backwards compatibility, also keep a reference as tool_menu
        self.tool_menu = self.tool_search_palette
        self.tool_dropdown_menu = None  # Not used with palette
        
        self.logger.info("Tool Search Palette initialized with fuzzy search")
    
    def _create_legacy_tool_dropdown(self, parent):
        """Create the legacy dropdown menu for tool selection (fallback)."""
        # Create custom dropdown that opens upwards
        self.tool_menu = ttk.Menubutton(parent, textvariable=self.tool_var, direction="above", width=25)
        self.tool_menu.pack(side=tk.LEFT, padx=5)
        
        # Create the dropdown menu
        self.tool_dropdown_menu = tk.Menu(self.tool_menu, tearoff=0)
        self.tool_menu.config(menu=self.tool_dropdown_menu)
        
        # Populate the dropdown menu with all tools
        self.update_tool_dropdown_menu()
        
        self.tool_search_palette = None  # Not available in legacy mode
        self.logger.info("Using legacy tool dropdown (ToolSearchPalette not available)")
    
    # Sub-tools that should redirect to their parent category
    SUB_TOOL_TO_PARENT = {
        # AI Tools (11 sub-tools)
        "Google AI": "AI Tools",
        "Vertex AI": "AI Tools",
        "Azure AI": "AI Tools",
        "Anthropic AI": "AI Tools",
        "OpenAI": "AI Tools",
        "Cohere AI": "AI Tools",
        "HuggingFace AI": "AI Tools",
        "Groq AI": "AI Tools",
        "OpenRouterAI": "AI Tools",
        "LM Studio": "AI Tools",
        "AWS Bedrock": "AI Tools",
        # Generator Tools (8 sub-tools)
        "Strong Password Generator": "Generator Tools",
        "Repeating Text Generator": "Generator Tools",
        "Lorem Ipsum Generator": "Generator Tools",
        "UUID/GUID Generator": "Generator Tools",
        "Random Email Generator": "Generator Tools",
        "ASCII Art Generator": "Generator Tools",
        "Hash Generator": "Generator Tools",
        "Slug Generator": "Generator Tools",
        # Extraction Tools (4 sub-tools)
        "Email Extraction": "Extraction Tools",
        "HTML Tool": "Extraction Tools",
        "Regex Extractor": "Extraction Tools",
        "URL Link Extractor": "Extraction Tools",
        # Line Tools (6 sub-tools)
        "Remove Duplicates": "Line Tools",
        "Remove Empty Lines": "Line Tools",
        "Add Line Numbers": "Line Tools",
        "Remove Line Numbers": "Line Tools",
        "Reverse Lines": "Line Tools",
        "Shuffle Lines": "Line Tools",
        # Markdown Tools (5 sub-tools)
        "Strip Markdown": "Markdown Tools",
        "Extract Links": "Markdown Tools",
        "Extract Headers": "Markdown Tools",
        "Table to CSV": "Markdown Tools",
        "Format Table": "Markdown Tools",
        # Sorter Tools (2 sub-tools)
        "Number Sorter": "Sorter Tools",
        "Alphabetical Sorter": "Sorter Tools",
        # Text Wrapper (5 sub-tools)
        "Word Wrap": "Text Wrapper",
        "Justify Text": "Text Wrapper",
        "Prefix/Suffix": "Text Wrapper",
        "Indent Text": "Text Wrapper",
        "Quote Text": "Text Wrapper",
        # Translator Tools (2 sub-tools)
        "Morse Code Translator": "Translator Tools",
        "Binary Code Translator": "Translator Tools",
        # Whitespace Tools (4 sub-tools)
        "Trim Lines": "Whitespace Tools",
        "Remove Extra Spaces": "Whitespace Tools",
        "Tabs/Spaces Converter": "Whitespace Tools",
        "Normalize Line Endings": "Whitespace Tools",
        # Other sub-tools
        "Word Frequency Counter": "Text Statistics",
    }
    
    # Tab index within parent category for sub-tools (0-indexed)
    # Based on actual tab order in UI from screenshot
    SUB_TOOL_TAB_INDEX = {
        # AI Tools tabs (11 tabs):
        "Google AI": 0,
        "Vertex AI": 1,
        "Azure AI": 2,
        "Anthropic AI": 3,
        "OpenAI": 4,
        "Cohere AI": 5,
        "HuggingFace AI": 6,
        "Groq AI": 7,
        "OpenRouterAI": 8,
        "LM Studio": 9,
        "AWS Bedrock": 10,
        # Generator Tools tabs (8 tabs):
        "Strong Password Generator": 0,
        "Repeating Text Generator": 1,
        "Lorem Ipsum Generator": 2,
        "UUID/GUID Generator": 3,
        "Random Email Generator": 4,
        "ASCII Art Generator": 5,
        "Hash Generator": 6,
        "Slug Generator": 7,
        # Extraction Tools tabs (4 tabs):
        "Email Extraction": 0,
        "HTML Tool": 1,
        "Regex Extractor": 2,
        "URL Link Extractor": 3,
        # Line Tools tabs (6 tabs):
        "Remove Duplicates": 0,
        "Remove Empty Lines": 1,
        "Add Line Numbers": 2,
        "Remove Line Numbers": 3,
        "Reverse Lines": 4,
        "Shuffle Lines": 5,
        # Markdown Tools tabs (5 tabs):
        "Strip Markdown": 0,
        "Extract Links": 1,
        "Extract Headers": 2,
        "Table to CSV": 3,
        "Format Table": 4,
        # Sorter Tools tabs (2 tabs):
        "Number Sorter": 0,
        "Alphabetical Sorter": 1,
        # Text Wrapper tabs (5 tabs):
        "Word Wrap": 0,
        "Justify Text": 1,
        "Prefix/Suffix": 2,
        "Indent Text": 3,
        "Quote Text": 4,
        # Translator Tools tabs (2 tabs):
        "Morse Code Translator": 0,
        "Binary Code Translator": 1,
        # Whitespace Tools tabs (4 tabs):
        "Trim Lines": 0,
        "Remove Extra Spaces": 1,
        "Tabs/Spaces Converter": 2,
        "Normalize Line Endings": 3,
    }
    
    def _on_palette_tool_selected(self, tool_name):
        """Handle tool selection from the ToolSearchPalette."""
        # Map sub-tools to their parent category
        actual_tool = self.SUB_TOOL_TO_PARENT.get(tool_name, tool_name)
        sub_tool_tab = self.SUB_TOOL_TAB_INDEX.get(tool_name)
        
        if actual_tool != tool_name:
            self.logger.debug(f"Mapped sub-tool '{tool_name}' to parent '{actual_tool}' (tab {sub_tool_tab})")
        
        self.tool_var.set(actual_tool)
        
        # Auto-expand options panel if collapsed
        if hasattr(self, 'options_collapsible') and self.options_collapsible:
            if self.options_collapsible.collapsed:
                self.options_collapsible.expand()
                self.logger.debug("Auto-expanded options panel on tool select")
        
        self.on_tool_selected()
        
        # Schedule tab selection after UI updates (if sub-tool with tab index)
        if sub_tool_tab is not None:
            self.after(100, lambda: self._select_tool_tab(actual_tool, sub_tool_tab))
    
    def _select_tool_tab(self, tool_name: str, tab_index: int):
        """Select a specific tab within a tool's tabbed interface."""
        try:
            # Recursively find notebooks in tool_settings_frame
            def find_notebook(widget):
                if isinstance(widget, ttk.Notebook):
                    return widget
                for child in widget.winfo_children():
                    result = find_notebook(child)
                    if result:
                        return result
                return None
            
            notebook = find_notebook(self.tool_settings_frame)
            if notebook:
                if 0 <= tab_index < notebook.index('end'):
                    notebook.select(tab_index)
                    self.logger.debug(f"Selected tab {tab_index} for {tool_name}")
                else:
                    self.logger.warning(f"Tab index {tab_index} out of range for {tool_name}")
        except Exception as e:
            self.logger.warning(f"Could not select tab {tab_index} for {tool_name}: {e}")
    
    def _on_ui_settings_change(self, settings_update):
        """Handle UI settings change from ToolSearchPalette."""
        try:
            # Merge with existing settings
            if "ui_layout" in settings_update:
                current_layout = self.settings.get("ui_layout", {})
                current_layout.update(settings_update["ui_layout"])
                self.settings["ui_layout"] = current_layout
                
                # Save settings
                if hasattr(self, 'db_settings_manager'):
                    self.db_settings_manager.save_settings(self.settings)
        except Exception as e:
            self.logger.warning(f"Error saving UI settings: {e}")
    
    def _on_options_panel_toggle(self, collapsed: bool):
        """Handle options panel toggle (save collapsed state to settings)."""
        try:
            current_layout = self.settings.get("ui_layout", {})
            current_layout["options_panel_collapsed"] = collapsed
            self.settings["ui_layout"] = current_layout
            
            # Save settings
            if hasattr(self, 'db_settings_manager'):
                self.db_settings_manager.save_settings(self.settings)
            
            self.logger.debug(f"Options panel collapsed: {collapsed}")
        except Exception as e:
            self.logger.warning(f"Error saving options panel state: {e}")
    
    def toggle_options_panel(self, event=None):
        """Toggle the options panel visibility (Ctrl+Shift+H shortcut)."""
        if hasattr(self, 'options_collapsible') and self.options_collapsible:
            self.options_collapsible.toggle()
            return "break"
        return None
    
    def focus_tool_search(self, event=None):
        """Focus the tool search entry (Ctrl+K shortcut)."""
        if self.tool_search_palette:
            self.tool_search_palette.focus_search()
            return "break"
        return None

    def update_tool_dropdown_menu(self):
        """Updates the tool dropdown menu with all available tools."""
        if self.tool_dropdown_menu is None:
            return  # Using ToolSearchPalette instead
            
        # Clear existing menu items
        self.tool_dropdown_menu.delete(0, tk.END)
        
        # Add all tool options to the menu
        for tool in self.tool_options:
            self.tool_dropdown_menu.add_command(
                label=tool, 
                command=lambda t=tool: self.select_tool(t)
            )

    def select_tool(self, tool_name):
        """Selects a tool from the dropdown menu."""
        self.tool_var.set(tool_name)
        self.on_tool_selected()

    def show_console_log(self):
        """Shows the console log in a separate window."""
        if self.console_window is not None and self.console_window.winfo_exists():
            self.console_window.lift()
            return
            
        self.console_window = tk.Toplevel(self)
        self.console_window.title("Console Log")
        self.console_window.geometry("800x400")
        
        # Create frame for controls
        control_frame = ttk.Frame(self.console_window)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Debug level dropdown
        ttk.Label(control_frame, text="Log Level:").pack(side=tk.LEFT)
        debug_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        self.log_level_combo = ttk.Combobox(control_frame, textvariable=self.log_level, values=debug_levels, state="readonly")
        self.log_level_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.log_level_combo.bind("<<ComboboxSelected>>", self.update_log_level)
        
        # Console log text widget
        self.console_log = scrolledtext.ScrolledText(self.console_window, wrap=tk.WORD, state="disabled", undo=True)
        
        # Apply current font settings to console
        text_font_family, text_font_size = self.get_best_font("text")
        self.console_log.configure(font=(text_font_family, text_font_size))
        
        self.console_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                logging.Handler.__init__(self)
                self.text_widget = text_widget

            def emit(self, record):
                msg = self.format(record)
                def append():
                    if self.text_widget.winfo_exists():
                        self.text_widget.configure(state='normal')
                        self.text_widget.insert(tk.END, msg + '\n')
                        self.text_widget.configure(state='disabled')
                        self.text_widget.yview(tk.END)
                self.text_widget.after(0, append)

        # Remove existing text handler if it exists
        for handler in self.logger.handlers[:]:
            if isinstance(handler, type(self).TextHandler if hasattr(type(self), 'TextHandler') else type(None)):
                self.logger.removeHandler(handler)
        
        text_handler = TextHandler(self.console_log)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(text_handler)

    def open_curl_tool_window(self):
        """Opens the cURL Tool in a separate window."""
        if not CURL_TOOL_MODULE_AVAILABLE:
            self._handle_warning("cURL Tool module is not available", "Opening cURL Tool", "Module", show_dialog=True)
            return
            
        if self.curl_tool_window is not None and self.curl_tool_window.winfo_exists():
            self.curl_tool_window.lift()
            return
            
        self.curl_tool_window = tk.Toplevel(self)
        self.curl_tool_window.title("cURL Tool")
        self.curl_tool_window.geometry("1000x700")
        
        # Configure window grid
        self.curl_tool_window.grid_columnconfigure(0, weight=1)
        self.curl_tool_window.grid_rowconfigure(0, weight=1)
        
        try:
            # Create the cURL tool widget with callback to send to input tabs
            self.curl_tool_widget = CurlToolWidget(
                self.curl_tool_window, 
                logger=self.logger,
                send_to_input_callback=self.send_content_to_input_tab,
                dialog_manager=self.dialog_manager,
                db_settings_manager=getattr(self, 'db_settings_manager', None)
            )
            
            # Add context menus to cURL tool widgets
            if CONTEXT_MENU_AVAILABLE:
                add_context_menu_to_children(self.curl_tool_window)
                self.logger.debug("Added context menus to cURL tool widgets")
            
            # Handle window closing
            def on_curl_window_close():
                self.curl_tool_window.destroy()
                self.curl_tool_window = None
                
            self.curl_tool_window.protocol("WM_DELETE_WINDOW", on_curl_window_close)
            
        except Exception as e:
            self._handle_error(e, "Opening cURL Tool", "Tool Operations")
            if self.curl_tool_window:
                self.curl_tool_window.destroy()
                self.curl_tool_window = None

    def open_mcp_manager(self):
        """Opens the MCP Manager in a separate window."""
        if not MCP_MANAGER_MODULE_AVAILABLE:
            self._handle_warning("MCP Manager module is not available", "Opening MCP Manager", "Module", show_dialog=True)
            return
        
        # Check if window already exists and bring it to front
        if hasattr(self, 'mcp_manager_window') and self.mcp_manager_window is not None and self.mcp_manager_window.winfo_exists():
            self.mcp_manager_window.lift()
            return
        
        try:
            # Create a new window for the MCP Manager
            self.mcp_manager_window = tk.Toplevel(self)
            self.mcp_manager_window.title("MCP Manager - Pomera Text Tools Server")
            self.mcp_manager_window.geometry("800x600")
            
            # Configure window grid
            self.mcp_manager_window.grid_columnconfigure(0, weight=1)
            self.mcp_manager_window.grid_rowconfigure(0, weight=1)
            
            # Create the MCP Manager widget
            from tools.mcp_widget import MCPManagerWidget
            self.mcp_manager_widget_window = MCPManagerWidget(self.mcp_manager_window, self)
            self.mcp_manager_widget_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Handle window closing
            def on_mcp_window_close():
                self.mcp_manager_window.destroy()
                self.mcp_manager_window = None
                
            self.mcp_manager_window.protocol("WM_DELETE_WINDOW", on_mcp_window_close)
            
            self.logger.info("Opened MCP Manager window")
            
        except Exception as e:
            self._handle_error(e, "Opening MCP Manager", "Tool Operations")
    
    def open_smart_diff_window(self):
        """Opens the Smart Diff widget in a separate window."""
        if not SMART_DIFF_WIDGET_AVAILABLE:
            self._handle_warning("Smart Diff widget is not available", "Opening Smart Diff", "Module", show_dialog=True)
            return
        
        # Show existing window if it exists
        if hasattr(self, 'smart_diff_window') and self.smart_diff_window and self.smart_diff_window.winfo_exists():
            self.smart_diff_window.lift()
            self.logger.info("Smart Diff window already exists, bringing to front")
            return
        
        try:
            # Create a new window for Smart Diff
            self.smart_diff_window = tk.Toplevel(self)
            self.smart_diff_window.title("Smart Diff - Semantic Comparison Tool")
            self.smart_diff_window.geometry("1000x700")
            self.smart_diff_window.transient(self)
            
            # Create the Smart Diff widget
            self.smart_diff_widget = SmartDiffWidget(
                self.smart_diff_window,
                logger=self.logger,
                parent_app=self,
                tab_count=len(self.input_tabs)
            )
            # Handle window close - save state before closing
            def on_smart_diff_close():
                if hasattr(self, 'smart_diff_widget') and self.smart_diff_widget:
                    self.smart_diff_widget._save_state()
                self.smart_diff_window.destroy()
                self.smart_diff_window = None
                self.smart_diff_widget = None
            
            self.smart_diff_window.protocol("WM_DELETE_WINDOW", on_smart_diff_close)
            
            self.logger.info("Smart Diff window opened successfully")
        
        except Exception as e:
            self._handle_error(e, "Opening Smart Diff", "Tool Operations")
            if hasattr(self, 'mcp_manager_window') and self.mcp_manager_window:
                self.mcp_manager_window.destroy()
                self.mcp_manager_window = None

    def open_list_comparator_window(self):
        """Opens the List Comparator in a separate window."""
        if not LIST_COMPARATOR_MODULE_AVAILABLE:
            self._handle_warning("List Comparator module is not available", "Opening List Comparator", "Module", show_dialog=True)
            return
        
        # Check if window already exists and bring it to front
        if self.list_comparator_window is not None and self.list_comparator_window.winfo_exists():
            self.list_comparator_window.lift()
            return
            
        try:
            # Create a new window for the List Comparator
            self.list_comparator_window = tk.Toplevel(self)
            self.list_comparator_window.title("Advanced List Comparison Tool")
            self.list_comparator_window.geometry("1200x800")
            
            comparator_app = DiffApp(
                self.list_comparator_window, 
                dialog_manager=self.dialog_manager,
                send_to_input_callback=self.send_content_to_input_tab
            )
            
            # Handle window closing
            def on_comparator_window_close():
                self.list_comparator_window.destroy()
                self.list_comparator_window = None
                
            self.list_comparator_window.protocol("WM_DELETE_WINDOW", on_comparator_window_close)
            
            self.logger.info("List Comparator opened successfully")
            
        except Exception as e:
            self._handle_error(e, "Opening List Comparator", "Tool Operations")
            if self.list_comparator_window:
                self.list_comparator_window.destroy()
            self.list_comparator_window = None
    
    def open_notes_widget(self):
        """Opens the Notes widget in a separate window."""
        if not NOTES_WIDGET_MODULE_AVAILABLE:
            self._handle_warning("Notes Widget module is not available", "Opening Notes Widget", "Module", show_dialog=True)
            return
        
        if self.notes_window is not None and self.notes_window.winfo_exists():
            self.notes_window.lift()
            return
        
        self.notes_window = tk.Toplevel(self)
        self.notes_window.title("Notes")
        self.notes_window.geometry("1200x800")
        
        # Configure window grid
        self.notes_window.grid_columnconfigure(0, weight=1)
        self.notes_window.grid_rowconfigure(0, weight=1)
        
        try:
            # Create the Notes widget with callback to send to input tabs
            self.notes_widget = NotesWidget(
                self.notes_window,
                logger=self.logger,
                send_to_input_callback=self.send_content_to_input_tab,
                dialog_manager=self.dialog_manager
            )
            
            # Add context menus to Notes widget if available
            if CONTEXT_MENU_AVAILABLE:
                add_context_menu_to_children(self.notes_window)
                self.logger.debug("Added context menus to Notes widget")
            
            # Handle window closing
            def on_notes_window_close():
                self.notes_window.destroy()
                self.notes_window = None
                if hasattr(self, 'notes_widget') and hasattr(self.notes_widget, 'search_executor'):
                    self.notes_widget.search_executor.shutdown(wait=False)
            
            self.notes_window.protocol("WM_DELETE_WINDOW", on_notes_window_close)
            
        except Exception as e:
            self._handle_error(e, "Opening Notes Widget", "Tool Operations")
            if self.notes_window:
                self.notes_window.destroy()
            self.notes_window = None
    
    def save_as_note(self, event=None):
        """Save active INPUT and OUTPUT tabs as a note."""
        if not NOTES_WIDGET_MODULE_AVAILABLE:
            self._handle_warning("Notes Widget module is not available", "Saving as note", "Module", show_dialog=True)
            return
        
        try:
            # Get active tab indices
            input_index = self.input_notebook.index(self.input_notebook.select())
            output_index = self.output_notebook.index(self.output_notebook.select())
            
            # Get content from active tabs
            input_content = self.input_tabs[input_index].text.get("1.0", tk.END).strip()
            output_content = self.output_tabs[output_index].text.get("1.0", tk.END).strip()
            
            # Generate title from first 144 chars of input (or output if input empty)
            title_source = input_content or output_content
            if title_source:
                title = title_source[:144].replace('\n', ' ').strip()
            else:
                title = "Untitled Note"
            
            # Create a temporary NotesWidget instance to save the note
            # We'll use a temporary window that we'll destroy immediately
            temp_window = tk.Toplevel(self)
            temp_window.withdraw()  # Hide the window
            
            notes_widget = NotesWidget(
                temp_window,
                logger=self.logger,
                send_to_input_callback=self.send_content_to_input_tab,
                dialog_manager=self.dialog_manager
            )
            
            # Save the note
            note_id = notes_widget.save_note(title, input_content, output_content)
            
            # Clean up
            temp_window.destroy()
            
            if note_id:
                if self.dialog_manager:
                    self.dialog_manager.show_info("Success", f"Note saved successfully (ID: {note_id})")
                else:
                    messagebox.showinfo("Success", f"Note saved successfully (ID: {note_id})")
                self.logger.info(f"Saved note with ID {note_id} from tabs {input_index+1} and {output_index+1}")
            else:
                self._handle_warning("Failed to save note", "Saving note", "Notes", show_dialog=True)
                    
        except Exception as e:
            self._handle_error(e, "Saving as note", "Notes")


    
    def show_performance_settings(self):
        """Shows the performance settings configuration dialog."""
        if hasattr(self, 'performance_settings_window') and self.performance_settings_window and self.performance_settings_window.winfo_exists():
            self.performance_settings_window.lift()
            return
        
        self.performance_settings_window = tk.Toplevel(self)
        self.performance_settings_window.title("Performance Settings")
        self.performance_settings_window.geometry("600x700")
        self.performance_settings_window.resizable(True, True)
        self.performance_settings_window.transient(self)
        self.performance_settings_window.grab_set()
        
        # Create main frame with scrollbar
        main_frame = ttk.Frame(self.performance_settings_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Get current performance settings
        perf_settings = self.settings.get("performance_settings", {})
        
        # Performance Mode Section
        mode_frame = ttk.LabelFrame(scrollable_frame, text="Performance Mode", padding="10")
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.perf_mode_var = tk.StringVar(value=perf_settings.get("mode", "automatic"))
        ttk.Label(mode_frame, text="Performance optimization mode:").pack(anchor=tk.W)
        
        mode_options = [
            ("Automatic", "automatic", "Automatically enable optimizations based on content size"),
            ("Always On", "always_on", "Always use performance optimizations"),
            ("Always Off", "always_off", "Disable all performance optimizations")
        ]
        
        for text, value, description in mode_options:
            frame = ttk.Frame(mode_frame)
            frame.pack(fill=tk.X, pady=2)
            ttk.Radiobutton(frame, text=text, variable=self.perf_mode_var, value=value).pack(side=tk.LEFT)
            ttk.Label(frame, text=f"- {description}", foreground="gray").pack(side=tk.LEFT, padx=(10, 0))
        
        # Async Processing Section
        async_frame = ttk.LabelFrame(scrollable_frame, text="Async Processing", padding="10")
        async_frame.pack(fill=tk.X, pady=(0, 10))
        
        async_settings = perf_settings.get("async_processing", {})
        
        self.async_enabled_var = tk.BooleanVar(value=async_settings.get("enabled", True))
        ttk.Checkbutton(async_frame, text="Enable async processing for large content", 
                       variable=self.async_enabled_var).pack(anchor=tk.W)
        
        # Threshold setting
        threshold_frame = ttk.Frame(async_frame)
        threshold_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(threshold_frame, text="Async threshold (KB):").pack(side=tk.LEFT)
        self.async_threshold_var = tk.StringVar(value=str(async_settings.get("threshold_kb", 10)))
        threshold_spinbox = ttk.Spinbox(threshold_frame, from_=1, to=1000, width=10, 
                                       textvariable=self.async_threshold_var)
        threshold_spinbox.pack(side=tk.LEFT, padx=(10, 0))
        
        # Max workers setting
        workers_frame = ttk.Frame(async_frame)
        workers_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(workers_frame, text="Max worker threads:").pack(side=tk.LEFT)
        self.async_workers_var = tk.StringVar(value=str(async_settings.get("max_workers", 2)))
        workers_spinbox = ttk.Spinbox(workers_frame, from_=1, to=8, width=10, 
                                     textvariable=self.async_workers_var)
        workers_spinbox.pack(side=tk.LEFT, padx=(10, 0))
        
        # Caching Section
        cache_frame = ttk.LabelFrame(scrollable_frame, text="Caching", padding="10")
        cache_frame.pack(fill=tk.X, pady=(0, 10))
        
        cache_settings = perf_settings.get("caching", {})
        
        self.cache_enabled_var = tk.BooleanVar(value=cache_settings.get("enabled", True))
        ttk.Checkbutton(cache_frame, text="Enable intelligent caching", 
                       variable=self.cache_enabled_var).pack(anchor=tk.W)
        
        # Cache size settings
        cache_sizes = [
            ("Stats cache size:", "stats_cache_size", 1000),
            ("Regex cache size:", "regex_cache_size", 100),
            ("Processing cache size:", "processing_cache_size", 500)
        ]
        
        self.cache_size_vars = {}
        for label, key, default in cache_sizes:
            frame = ttk.Frame(cache_frame)
            frame.pack(fill=tk.X, pady=(5, 0))
            ttk.Label(frame, text=label).pack(side=tk.LEFT)
            var = tk.StringVar(value=str(cache_settings.get(key, default)))
            self.cache_size_vars[key] = var
            spinbox = ttk.Spinbox(frame, from_=10, to=10000, width=10, textvariable=var)
            spinbox.pack(side=tk.LEFT, padx=(10, 0))
        
        # Content cache size (MB)
        content_frame = ttk.Frame(cache_frame)
        content_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(content_frame, text="Content cache size (MB):").pack(side=tk.LEFT)
        self.content_cache_var = tk.StringVar(value=str(cache_settings.get("content_cache_size_mb", 50)))
        content_spinbox = ttk.Spinbox(content_frame, from_=1, to=1000, width=10, 
                                     textvariable=self.content_cache_var)
        content_spinbox.pack(side=tk.LEFT, padx=(10, 0))
        
        # Memory Management Section
        memory_frame = ttk.LabelFrame(scrollable_frame, text="Memory Management", padding="10")
        memory_frame.pack(fill=tk.X, pady=(0, 10))
        
        memory_settings = perf_settings.get("memory_management", {})
        
        self.memory_enabled_var = tk.BooleanVar(value=memory_settings.get("enabled", True))
        ttk.Checkbutton(memory_frame, text="Enable advanced memory management", 
                       variable=self.memory_enabled_var).pack(anchor=tk.W)
        
        # Note: GC optimization, memory pool, and leak detection options were removed
        # as they are not currently implemented. Memory threshold is functional.
        self.memory_option_vars = {}  # Keep for backwards compatibility
        
        # Memory threshold
        mem_threshold_frame = ttk.Frame(memory_frame)
        mem_threshold_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(mem_threshold_frame, text="Memory threshold (MB):").pack(side=tk.LEFT)
        self.memory_threshold_var = tk.StringVar(value=str(memory_settings.get("memory_threshold_mb", 500)))
        mem_threshold_spinbox = ttk.Spinbox(mem_threshold_frame, from_=100, to=2000, width=10, 
                                           textvariable=self.memory_threshold_var)
        mem_threshold_spinbox.pack(side=tk.LEFT, padx=(10, 0))
        
        # UI Optimizations Section
        ui_frame = ttk.LabelFrame(scrollable_frame, text="UI Optimizations", padding="10")
        ui_frame.pack(fill=tk.X, pady=(0, 10))
        
        ui_settings = perf_settings.get("ui_optimizations", {})
        
        self.ui_enabled_var = tk.BooleanVar(value=ui_settings.get("enabled", True))
        ttk.Checkbutton(ui_frame, text="Enable UI optimizations", 
                       variable=self.ui_enabled_var).pack(anchor=tk.W)
        
        ui_options = [
            ("Efficient line numbers", "efficient_line_numbers", True),
            ("Progressive search", "progressive_search", True),
            ("Lazy updates", "lazy_updates", True)
        ]
        
        self.ui_option_vars = {}
        for text, key, default in ui_options:
            var = tk.BooleanVar(value=ui_settings.get(key, default))
            self.ui_option_vars[key] = var
            ttk.Checkbutton(ui_frame, text=text, variable=var).pack(anchor=tk.W, padx=(20, 0))
        
        # Debounce delay
        debounce_frame = ttk.Frame(ui_frame)
        debounce_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(debounce_frame, text="Debounce delay (ms):").pack(side=tk.LEFT)
        self.debounce_var = tk.StringVar(value=str(ui_settings.get("debounce_delay_ms", 300)))
        debounce_spinbox = ttk.Spinbox(debounce_frame, from_=50, to=2000, width=10, 
                                      textvariable=self.debounce_var)
        debounce_spinbox.pack(side=tk.LEFT, padx=(10, 0))
        

        
        # Define dialog close function first
        def on_dialog_close():
            self.performance_settings_window.destroy()
        
        # Buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Apply", command=self.apply_performance_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Reset to Defaults", command=self.reset_performance_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=on_dialog_close).pack(side=tk.RIGHT)
        
        # Enable mouse wheel scrolling with safe canvas reference
        def _on_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                # Canvas has been destroyed, ignore the event
                pass
        
        # Bind to the canvas and scrollable frame instead of globally
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        self.performance_settings_window.bind("<MouseWheel>", _on_mousewheel)
        
        self.performance_settings_window.protocol("WM_DELETE_WINDOW", on_dialog_close)
    
    def apply_performance_settings(self):
        """Apply the performance settings from the dialog."""
        try:
            # Collect all settings from the UI
            performance_settings = {
                "mode": self.perf_mode_var.get(),
                "async_processing": {
                    "enabled": self.async_enabled_var.get(),
                    "threshold_kb": int(self.async_threshold_var.get()),
                    "max_workers": int(self.async_workers_var.get()),
                    "chunk_size_kb": 50  # Keep existing default
                },
                "caching": {
                    "enabled": self.cache_enabled_var.get(),
                    "stats_cache_size": int(self.cache_size_vars["stats_cache_size"].get()),
                    "regex_cache_size": int(self.cache_size_vars["regex_cache_size"].get()),
                    "content_cache_size_mb": int(self.content_cache_var.get()),
                    "processing_cache_size": int(self.cache_size_vars["processing_cache_size"].get())
                },
                "memory_management": {
                    "enabled": self.memory_enabled_var.get(),
                    "memory_threshold_mb": int(self.memory_threshold_var.get())
                },
                "ui_optimizations": {
                    "enabled": self.ui_enabled_var.get(),
                    "efficient_line_numbers": self.ui_option_vars["efficient_line_numbers"].get(),
                    "progressive_search": self.ui_option_vars["progressive_search"].get(),
                    "debounce_delay_ms": int(self.debounce_var.get()),
                    "lazy_updates": self.ui_option_vars["lazy_updates"].get()
                },

            }
            
            # Update settings
            self.settings["performance_settings"] = performance_settings
            self.save_settings()
            
            # Apply settings to running components
            self._apply_performance_settings_to_components(performance_settings)
            

            
            # Show confirmation
            if self.dialog_manager:
                self.dialog_manager.show_info("Performance Settings", 
                                  "Performance settings applied successfully!\n\n"
                                  "Some changes may require restarting the application to take full effect.", "success")
            else:
                messagebox.showinfo("Performance Settings", 
                                  "Performance settings applied successfully!\n\n"
                                  "Some changes may require restarting the application to take full effect.")
            
            # Close the dialog
            self.performance_settings_window.destroy()
            
            self.logger.info("Performance settings updated and applied")
            
        except ValueError as e:
            self._handle_warning(f"Please enter valid numeric values: {e}", "Performance settings", "Settings", show_dialog=True)
        except Exception as e:
            self._handle_error(e, "Applying performance settings", "Settings")
    
    def reset_performance_settings(self):
        """Reset performance settings to defaults."""
        if self.dialog_manager and self.dialog_manager.ask_yes_no("Reset Settings", "Reset all performance settings to defaults?", "confirmation") or \
           not self.dialog_manager and messagebox.askyesno("Reset Settings", "Reset all performance settings to defaults?"):
            # Get default performance settings
            default_settings = self._get_default_settings()
            default_perf = default_settings["performance_settings"]
            
            # Update UI with defaults
            self.perf_mode_var.set(default_perf["mode"])
            
            # Async processing
            async_settings = default_perf["async_processing"]
            self.async_enabled_var.set(async_settings["enabled"])
            self.async_threshold_var.set(str(async_settings["threshold_kb"]))
            self.async_workers_var.set(str(async_settings["max_workers"]))
            
            # Caching
            cache_settings = default_perf["caching"]
            self.cache_enabled_var.set(cache_settings["enabled"])
            self.cache_size_vars["stats_cache_size"].set(str(cache_settings["stats_cache_size"]))
            self.cache_size_vars["regex_cache_size"].set(str(cache_settings["regex_cache_size"]))
            self.content_cache_var.set(str(cache_settings["content_cache_size_mb"]))
            self.cache_size_vars["processing_cache_size"].set(str(cache_settings["processing_cache_size"]))
            
            # Memory management
            memory_settings = default_perf["memory_management"]
            self.memory_enabled_var.set(memory_settings["enabled"])
            for key, var in self.memory_option_vars.items():
                var.set(memory_settings[key])
            self.memory_threshold_var.set(str(memory_settings["memory_threshold_mb"]))
            
            # UI optimizations
            ui_settings = default_perf["ui_optimizations"]
            self.ui_enabled_var.set(ui_settings["enabled"])
            for key, var in self.ui_option_vars.items():
                var.set(ui_settings[key])
            self.debounce_var.set(str(ui_settings["debounce_delay_ms"]))
            

    
    def _apply_performance_settings_to_components(self, performance_settings):
        """Apply performance settings to running components."""
        try:
            # Update async processing settings
            if ASYNC_PROCESSING_AVAILABLE and self.async_processor:
                async_settings = performance_settings.get("async_processing", {})
                if hasattr(self.async_processor, 'update_settings'):
                    self.async_processor.update_settings({
                        'max_workers': async_settings.get("max_workers", 2),
                        'chunk_size_kb': async_settings.get("chunk_size_kb", 50)
                    })
            
            # Update caching settings
            if INTELLIGENT_CACHING_AVAILABLE:
                cache_settings = performance_settings.get("caching", {})
                
                if self.smart_stats_calculator and hasattr(self.smart_stats_calculator, 'update_cache_size'):
                    self.smart_stats_calculator.update_cache_size(cache_settings.get("stats_cache_size", 1000))
                
                if self.regex_cache and hasattr(self.regex_cache, 'update_cache_size'):
                    self.regex_cache.update_cache_size(cache_settings.get("regex_cache_size", 100))
                
                if self.content_cache and hasattr(self.content_cache, 'update_cache_size'):
                    self.content_cache.update_cache_size(cache_settings.get("content_cache_size_mb", 50) * 1024 * 1024)
            

            
            # Update UI debounce delay
            ui_settings = performance_settings.get("ui_optimizations", {})
            AppConfig.DEBOUNCE_DELAY = ui_settings.get("debounce_delay_ms", 300)
            
            self.logger.info("Performance settings applied to running components")
            
        except Exception as e:
            self.logger.warning(f"Some performance settings could not be applied: {e}")

    def create_diff_viewer(self, parent):
        """Creates the diff viewer widgets, initially hidden."""
        if DIFF_VIEWER_MODULE_AVAILABLE:
            # Use the new modular diff viewer with callback for tab updates
            self.diff_viewer_widget = DiffViewerWidget(
                parent, 
                AppConfig.TAB_COUNT, 
                self.logger,
                parent_callback=self.on_diff_viewer_content_changed,
                dialog_manager=self.dialog_manager
            )
            self.diff_frame = self.diff_viewer_widget.get_frame()
            
            # Set up references for backward compatibility
            self.diff_input_notebook = self.diff_viewer_widget.input_notebook
            self.diff_output_notebook = self.diff_viewer_widget.output_notebook
            self.diff_input_tabs = self.diff_viewer_widget.input_tabs
            self.diff_output_tabs = self.diff_viewer_widget.output_tabs
            
            # Set up references to statistics bars
            self.diff_input_stats_bar = self.diff_viewer_widget.input_stats_bar
            self.diff_output_stats_bar = self.diff_viewer_widget.output_stats_bar
            
            # Override the tab content change callback
            self.diff_viewer_widget._on_tab_content_changed = self.on_tab_content_changed
            
            # Override the copy methods to use main app functionality
            self.diff_viewer_widget.copy_to_clipboard = self.copy_to_clipboard
            self.diff_viewer_widget.copy_to_specific_input_tab = lambda tab: self.copy_to_specific_input_tab(tab, None)
            self.diff_viewer_widget.clear_all_input_tabs = self.clear_all_input_tabs
            self.diff_viewer_widget.clear_all_output_tabs = self.clear_all_output_tabs
            self.diff_viewer_widget.open_list_comparator = lambda: self.open_list_comparator_window()
            
            # Apply current font settings to diff viewer
            try:
                text_font_family, text_font_size = self.get_best_font("text")
                text_font_tuple = (text_font_family, text_font_size)
                self.diff_viewer_widget.apply_font_to_widgets(text_font_tuple)
                self.logger.info(f"Applied font {text_font_tuple} to diff viewer")
            except Exception as e:
                self.logger.error(f"Error applying font to diff viewer: {e}")
        else:
            # Diff viewer module not available - create placeholder
            self.logger.warning("Diff Viewer module not available")
            self.diff_frame = ttk.Frame(parent, padding="10")
            ttk.Label(self.diff_frame, text="Diff Viewer module not available", 
                     font=("Helvetica", 12)).pack(pady=20)









    def on_tool_selected(self, event=None):
        """Handles the selection of a new tool from the dropdown."""
        tool_name = self.tool_var.get()
        self.settings["selected_tool"] = tool_name
        self.logger.info(f"Tool selected: {tool_name}")

        # Check if we're switching FROM Diff Viewer (before hiding it)
        was_diff_viewer = hasattr(self, 'diff_frame') and self.diff_frame.winfo_viewable()

        if tool_name == "Diff Viewer":
            self.central_frame.grid_remove()
            if DIFF_VIEWER_MODULE_AVAILABLE:
                self.diff_viewer_widget.show()
                self.load_diff_viewer_content()
                # Update tab labels immediately after loading content
                self.after(10, self.diff_viewer_widget.update_tab_labels)
                self.diff_viewer_widget.run_comparison()
            else:
                # Show placeholder when module not available (row=1 same as central_frame)
                self.diff_frame.grid(row=1, column=0, sticky="nsew", pady=5)
            self.update_tool_settings_ui()
        else:
            # Sync diff viewer content before switching away
            if was_diff_viewer:
                self.logger.info("Switching FROM Diff Viewer - syncing content")
                self.sync_diff_viewer_to_main_tabs()
                # Don't save settings here - sync method already does it
            
            if DIFF_VIEWER_MODULE_AVAILABLE and hasattr(self, 'diff_viewer_widget'):
                self.diff_viewer_widget.hide()
            else:
                self.diff_frame.grid_remove()
            self.central_frame.grid()
            
            self.update_tool_settings_ui()

            # Don't apply tool immediately after switching from Diff Viewer
            # This prevents overwriting the synced content
            if tool_name not in self.manual_process_tools and not was_diff_viewer:
                self.apply_tool()
            elif was_diff_viewer:
                self.logger.info("Skipping apply_tool after Diff Viewer switch to preserve synced content")
            
        # Save settings (sync method already saved if switching from Diff Viewer)
        if not was_diff_viewer:
            self.save_settings()

    def _register_widget_factories(self):
        """
        Register widget factories for tools that have BaseTool V2 implementations.
        
        This enables the Widget Cache to create and cache tool widgets efficiently.
        """
        if not WIDGET_CACHE_AVAILABLE or not self.widget_cache:
            return
        
        # Import V2 tool classes
        try:
            from tools.case_tool import CaseToolV2
            self.widget_cache.register_factory(
                "Case Tool",
                lambda: self._create_basetool_widget(CaseToolV2, "Case Tool")
            )
        except ImportError:
            pass
        
        try:
            from tools.base64_tools import Base64ToolsV2
            self.widget_cache.register_factory(
                "Base64 Encoder/Decoder",
                lambda: self._create_basetool_widget(Base64ToolsV2, "Base64 Encoder/Decoder")
            )
        except ImportError:
            pass
        
        try:
            from tools.sorter_tools import SorterToolsV2
            self.widget_cache.register_factory(
                "Sorter Tools",
                lambda: self._create_basetool_widget(SorterToolsV2, "Sorter Tools")
            )
        except ImportError:
            pass
        
        try:
            from tools.line_tools import LineToolsV2
            self.widget_cache.register_factory(
                "Line Tools",
                lambda: self._create_basetool_widget(LineToolsV2, "Line Tools")
            )
        except ImportError:
            pass
        
        try:
            from tools.whitespace_tools import WhitespaceToolsV2
            self.widget_cache.register_factory(
                "Whitespace Tools",
                lambda: self._create_basetool_widget(WhitespaceToolsV2, "Whitespace Tools")
            )
        except ImportError:
            pass
        
        try:
            from tools.translator_tools import TranslatorToolsV2
            self.widget_cache.register_factory(
                "Translator Tools",
                lambda: self._create_basetool_widget(TranslatorToolsV2, "Translator Tools")
            )
        except ImportError:
            pass
        
        try:
            from tools.jsonxml_tool import JSONXMLToolV2
            self.widget_cache.register_factory(
                "JSON/XML Tool",
                lambda: self._create_basetool_widget(JSONXMLToolV2, "JSON/XML Tool")
            )
        except ImportError:
            pass
        
        try:
            from tools.string_escape_tool import StringEscapeToolV2
            self.widget_cache.register_factory(
                "String Escape Tool",
                lambda: self._create_basetool_widget(StringEscapeToolV2, "String Escape Tool")
            )
        except ImportError:
            pass
        
        try:
            from tools.cron_tool import CronToolV2
            self.widget_cache.register_factory(
                "Cron Tool",
                lambda: self._create_basetool_widget(CronToolV2, "Cron Tool")
            )
        except ImportError:
            pass
        
        try:
            from tools.number_base_converter import NumberBaseConverterV2
            self.widget_cache.register_factory(
                "Number Base Converter",
                lambda: self._create_basetool_widget(NumberBaseConverterV2, "Number Base Converter")
            )
        except ImportError:
            pass
        
        try:
            from tools.timestamp_converter import TimestampConverterV2
            self.widget_cache.register_factory(
                "Timestamp Converter",
                lambda: self._create_basetool_widget(TimestampConverterV2, "Timestamp Converter")
            )
        except ImportError:
            pass
        
        try:
            from tools.text_statistics_tool import TextStatisticsV2
            self.widget_cache.register_factory(
                "Text Statistics",
                lambda: self._create_basetool_widget(TextStatisticsV2, "Text Statistics")
            )
        except ImportError:
            pass
        
        try:
            from tools.word_frequency_counter import WordFrequencyCounterV2
            self.widget_cache.register_factory(
                "Word Frequency Counter",
                lambda: self._create_basetool_widget(WordFrequencyCounterV2, "Word Frequency Counter")
            )
        except ImportError:
            pass
        
        try:
            from tools.url_parser import URLParserV2
            self.widget_cache.register_factory(
                "URL Parser",
                lambda: self._create_basetool_widget(URLParserV2, "URL Parser")
            )
        except ImportError:
            pass
        
        try:
            from tools.regex_extractor import RegexExtractorV2
            self.widget_cache.register_factory(
                "Regex Extractor",
                lambda: self._create_basetool_widget(RegexExtractorV2, "Regex Extractor")
            )
        except ImportError:
            pass
        
        try:
            from tools.email_extraction_tool import EmailExtractionToolV2
            self.widget_cache.register_factory(
                "Email Extraction Tool",
                lambda: self._create_basetool_widget(EmailExtractionToolV2, "Email Extraction Tool")
            )
        except ImportError:
            pass
        
        try:
            from tools.url_link_extractor import URLLinkExtractorV2
            self.widget_cache.register_factory(
                "URL and Link Extractor",
                lambda: self._create_basetool_widget(URLLinkExtractorV2, "URL and Link Extractor")
            )
        except ImportError:
            pass
        
        try:
            from tools.column_tools import ColumnToolsV2
            self.widget_cache.register_factory(
                "Column Tools",
                lambda: self._create_basetool_widget(ColumnToolsV2, "Column Tools")
            )
        except ImportError:
            pass
        
        try:
            from tools.markdown_tools import MarkdownToolsV2
            self.widget_cache.register_factory(
                "Markdown Tools",
                lambda: self._create_basetool_widget(MarkdownToolsV2, "Markdown Tools")
            )
        except ImportError:
            pass
        
        try:
            from tools.html_tool import HTMLToolV2
            self.widget_cache.register_factory(
                "HTML Tool",
                lambda: self._create_basetool_widget(HTMLToolV2, "HTML Tool")
            )
        except ImportError:
            pass
        
        try:
            from tools.email_header_analyzer import EmailHeaderAnalyzerV2
            self.widget_cache.register_factory(
                "Email Header Analyzer",
                lambda: self._create_basetool_widget(EmailHeaderAnalyzerV2, "Email Header Analyzer")
            )
        except ImportError:
            pass
        
        try:
            from tools.ascii_art_generator import ASCIIArtGeneratorV2
            self.widget_cache.register_factory(
                "ASCII Art Generator",
                lambda: self._create_basetool_widget(ASCIIArtGeneratorV2, "ASCII Art Generator")
            )
        except ImportError:
            pass
        
        self.logger.debug(f"Registered {self.widget_cache.factory_count} widget factories")
    
    def _create_basetool_widget(self, tool_class, tool_name):
        """
        Create a widget for a BaseTool V2 class.
        
        Args:
            tool_class: The V2 tool class
            tool_name: Name of the tool for settings lookup
            
        Returns:
            The created widget frame
        """
        tool = tool_class()
        settings = self.settings["tool_settings"].get(tool_name, tool.get_default_settings())
        return tool.create_ui(
            self.tool_settings_frame,
            settings,
            on_setting_change_callback=self.on_tool_setting_change,
            apply_tool_callback=self.apply_tool
        )

    def update_tool_settings_ui(self):
        """Updates the UI to show settings for the currently selected tool.
        
        Uses Widget Cache when available to avoid recreating widgets unnecessarily.
        """
        tool_name = self.tool_var.get()
        
        # Skip if same tool is already displayed (optimization)
        if hasattr(self, '_current_tool_ui') and self._current_tool_ui == tool_name:
            self.logger.debug(f"Tool UI already showing {tool_name}, skipping recreation")
            return
        
        # Destroy existing widgets
        for widget in self.tool_settings_frame.winfo_children():
            widget.destroy()
        
        self._current_tool_ui = tool_name
        tool_settings = self.settings["tool_settings"].get(tool_name, {})
        
        # Use tool_settings_frame directly as parent
        # Note: Centering was causing layout issues (e.g. Folder File Reporter cut off)
        parent_frame = self.tool_settings_frame
        
        if tool_name in ["Google AI", "Anthropic AI", "OpenAI", "Cohere AI", "HuggingFace AI", "Groq AI", "OpenRouterAI"]:
            self.create_ai_provider_widgets(parent_frame, tool_name)
        elif tool_name == "AI Tools":
            self.create_ai_tools_widget(parent_frame)
        elif tool_name == "Case Tool":
            if CASE_TOOL_MODULE_AVAILABLE and self.case_tool:
                self.case_tool_ui = self.case_tool.create_ui(
                    parent_frame, 
                    tool_settings,
                    on_setting_change_callback=self.on_tool_setting_change,
                    apply_tool_callback=self.apply_tool
                )
            else:
                ttk.Label(parent_frame, text="Case Tool module not available").pack()
        elif tool_name == "Translator Tools":
            self.create_translator_tools_widget(parent_frame)
        elif tool_name == "Base64 Encoder/Decoder":
            self.create_base64_tools_widget(parent_frame)
        elif tool_name == "JSON/XML Tool":
            self.create_jsonxml_tool_widget(parent_frame)
        elif tool_name == "Cron Tool":
            self.create_cron_tool_widget(parent_frame)
        elif tool_name == "Extraction Tools":
            self.create_extraction_tools_widget(parent_frame)
        elif tool_name == "Sorter Tools":
            self.create_sorter_tools_widget(parent_frame)
        elif tool_name == "Find & Replace Text":
            if FIND_REPLACE_MODULE_AVAILABLE and self.find_replace_widget:
                # Set up callback for settings changes
                self.find_replace_widget.on_setting_change = self.on_tool_setting_change
                # Set up callback for Replace All functionality
                self.find_replace_widget.apply_tool_callback = self.apply_tool
                # Set text widgets for the Find & Replace widget
                self.find_replace_widget.set_text_widgets(
                    self.input_tabs, self.output_tabs, 
                    self.input_notebook, self.output_notebook
                )
                # Create the widgets
                self.find_replace_widget.create_widgets(parent_frame, tool_settings)
            else:
                # Find & Replace module not available
                ttk.Label(parent_frame, text="Find & Replace module not available").pack()
        elif tool_name == "Generator Tools":
            self.create_generator_tools_widget(parent_frame)
        elif tool_name == "URL Parser":
            if URL_PARSER_MODULE_AVAILABLE and self.url_parser:
                tool_settings = self.settings["tool_settings"].get("URL Parser", {
                    "ascii_decode": True
                })
                self.url_parser_ui = self.url_parser.create_ui(
                    parent_frame, 
                    tool_settings,
                    on_setting_change_callback=self.on_tool_setting_change,
                    apply_tool_callback=self.apply_tool
                )
            else:
                ttk.Label(parent_frame, text="URL Parser module not available").pack()
        elif tool_name == "Diff Viewer":
            if DIFF_VIEWER_MODULE_AVAILABLE:
                # Use the new modular settings widget
                self.diff_settings_widget = DiffViewerSettingsWidget(
                    parent_frame, 
                    self.diff_viewer_widget, 
                    self.on_tool_setting_change
                )
            else:
                # Module not available - show message
                ttk.Label(parent_frame, text="Diff Viewer module not available").pack(side=tk.LEFT, padx=10)
        elif tool_name == "Email Extraction Tool":
            if EMAIL_EXTRACTION_MODULE_AVAILABLE and self.email_extraction_tool:
                tool_settings = self.settings["tool_settings"].get("Email Extraction Tool", {
                    "omit_duplicates": False,
                    "hide_counts": True,
                    "sort_emails": False,
                    "only_domain": False
                })
                self.email_extraction_ui = self.email_extraction_tool.create_ui(
                    parent_frame, 
                    tool_settings,
                    on_setting_change_callback=self.on_tool_setting_change,
                    apply_tool_callback=self.apply_tool
                )
            else:
                ttk.Label(parent_frame, text="Email Extraction Tool module not available").pack()
        elif tool_name == "Email Header Analyzer":
            if EMAIL_HEADER_ANALYZER_MODULE_AVAILABLE and self.email_header_analyzer:
                tool_settings = self.settings["tool_settings"].get("Email Header Analyzer", {
                    "show_timestamps": True,
                    "show_delays": True,
                    "show_authentication": True,
                    "show_spam_score": True
                })
                self.email_header_analyzer_ui = self.email_header_analyzer.create_ui(
                    parent_frame, 
                    tool_settings,
                    on_setting_change_callback=self.on_tool_setting_change,
                    apply_tool_callback=self.apply_tool
                )
            else:
                ttk.Label(parent_frame, text="Email Header Analyzer module not available").pack()
        elif tool_name == "Folder File Reporter":
            if FOLDER_FILE_REPORTER_MODULE_AVAILABLE and self.folder_file_reporter:
                tool_settings = self.settings["tool_settings"].get("Folder File Reporter", {
                    "last_input_folder": "",
                    "last_output_folder": ""
                })
                self.folder_file_reporter.load_settings(tool_settings)
                self.folder_file_reporter_ui = self.folder_file_reporter.create_ui(parent_frame)
            else:
                ttk.Label(parent_frame, text="Folder File Reporter module not available").pack()
        elif tool_name == "Line Tools":
            self.create_line_tools_widget(parent_frame)
        elif tool_name == "Whitespace Tools":
            self.create_whitespace_tools_widget(parent_frame)
        elif tool_name == "Text Statistics":
            self.create_text_statistics_widget(parent_frame)
        elif tool_name == "Markdown Tools":
            self.create_markdown_tools_widget(parent_frame)
        elif tool_name == "String Escape Tool":
            self.create_string_escape_tool_widget(parent_frame)
        elif tool_name == "Number Base Converter":
            self.create_number_base_converter_widget(parent_frame)
        elif tool_name == "Text Wrapper":
            self.create_text_wrapper_widget(parent_frame)
        elif tool_name == "Slug Generator":
            self.create_slug_generator_widget(parent_frame)
        elif tool_name == "Column Tools":
            self.create_column_tools_widget(parent_frame)
        elif tool_name == "Timestamp Converter":
            self.create_timestamp_converter_widget(parent_frame)
        elif tool_name == "Web Search":
            self.create_web_search_options(parent_frame)
        elif tool_name == "URL Reader":
            self.create_url_reader_options(parent_frame)




    def create_ai_tools_widget(self, parent):
        """Creates the AI Tools tabbed interface widget."""
        if not AI_TOOLS_AVAILABLE:
            ttk.Label(parent, text="AI Tools module not available").pack(padx=10, pady=10)
            return
        
        # Create and pack the AI tools widget
        self.ai_tools_widget = AIToolsWidget(parent, self, self.dialog_manager)
        self.ai_tools_widget.pack(fill=tk.BOTH, expand=True)
        
        # Apply current font settings to AI tools
        try:
            text_font_family, text_font_size = self.get_best_font("text")
            self.ai_tools_widget.apply_font_to_widgets((text_font_family, text_font_size))
        except:
            pass  # Continue if font application fails

    def create_sorter_tools_widget(self, parent):
        """Creates the Sorter Tools tabbed interface widget."""
        if not SORTER_TOOLS_MODULE_AVAILABLE:
            ttk.Label(parent, text="Sorter Tools module not available").pack(padx=10, pady=10)
            return
        
        # Create and pack the sorter tools widget
        self.sorter_tools_widget = self.sorter_tools.create_widget(parent, self)
        self.sorter_tools_widget.pack(fill=tk.BOTH, expand=True)

    def create_generator_tools_widget(self, parent):
        """Creates the Generator Tools tabbed interface widget."""
        if not GENERATOR_TOOLS_MODULE_AVAILABLE:
            ttk.Label(parent, text="Generator Tools module not available").pack(padx=10, pady=10)
            return

        # Create and pack the generator tools widget
        self.generator_tools_widget = GeneratorToolsWidget(self.generator_tools)
        self.generator_tools_widget_frame = self.generator_tools_widget.create_widget(parent, self)
        self.generator_tools_widget_frame.pack(fill=tk.BOTH, expand=True)

    def create_extraction_tools_widget(self, parent):
        """Creates the Extraction Tools tabbed interface widget."""
        if not EXTRACTION_TOOLS_MODULE_AVAILABLE:
            ttk.Label(parent, text="Extraction Tools module not available").pack(padx=10, pady=10)
            return

        # Create and pack the extraction tools widget
        self.extraction_tools_widget = self.extraction_tools.create_widget(parent, self)
        self.extraction_tools_widget.pack(fill=tk.BOTH, expand=True)

    def create_translator_tools_widget(self, parent):
        """Creates the Translator Tools tabbed interface widget."""
        if not TRANSLATOR_TOOLS_MODULE_AVAILABLE:
            ttk.Label(parent, text="Translator Tools module not available").pack(padx=10, pady=10)
            return
        
        # Create and pack the translator tools widget
        self.translator_tools_widget = self.translator_tools.create_widget(parent, self, self.dialog_manager)
        self.translator_tools_widget.pack(fill=tk.BOTH, expand=True)

    def create_base64_tools_widget(self, parent):
        """Creates the Base64 Tools interface widget."""
        if not BASE64_TOOLS_MODULE_AVAILABLE:
            ttk.Label(parent, text="Base64 Tools module not available").pack(padx=10, pady=10)
            return
        
        # Create and pack the base64 tools widget
        self.base64_tools_widget = Base64ToolsWidget(self.base64_tools)
        self.base64_tools_widget_frame = self.base64_tools_widget.create_widget(parent, self)
        self.base64_tools_widget_frame.pack(fill=tk.BOTH, expand=True)

    def create_jsonxml_tool_widget(self, parent):
        """Creates the JSON/XML Tool interface widget."""
        if not JSONXML_TOOL_MODULE_AVAILABLE:
            ttk.Label(parent, text="JSON/XML Tool module not available").pack(padx=10, pady=10)
            return
        
        # Create the JSON/XML tool instance
        self.jsonxml_tool = JSONXMLTool(self)
        
        # Get current settings
        settings = self.settings["tool_settings"].get("JSON/XML Tool", {})
        
        # Create and pack the JSON/XML tool widget
        self.jsonxml_tool_frame = self.jsonxml_tool.create_widgets(parent, settings)
        self.jsonxml_tool_frame.pack(fill=tk.BOTH, expand=True)
        
        # Apply current font settings
        try:
            text_font_family, text_font_size = self.get_best_font("text")
            self.jsonxml_tool.apply_font_to_widgets((text_font_family, text_font_size))
        except:
            pass  # Continue if font application fails

    def create_cron_tool_widget(self, parent):
        """Creates the Cron Tool interface widget."""
        if not CRON_TOOL_MODULE_AVAILABLE:
            ttk.Label(parent, text="Cron Tool module not available").pack(padx=10, pady=10)
            return
        
        # Create the Cron tool instance
        self.cron_tool = CronTool(self)
        
        # Get current settings
        settings = self.settings["tool_settings"].get("Cron Tool", {})
        
        # Create and pack the Cron tool widget
        self.cron_tool_frame = self.cron_tool.create_widgets(parent, settings)
        self.cron_tool_frame.pack(fill=tk.BOTH, expand=True)
        
        # Apply current font settings
        try:
            text_font_family, text_font_size = self.get_best_font("text")
            self.cron_tool.apply_font_to_widgets((text_font_family, text_font_size))
        except:
            pass  # Continue if font application fails

    def create_web_search_options(self, parent):
        """Creates the Web Search tool options panel with tabbed interface like AI Tools."""
        # Engine configuration: (display_name, engine_key, api_key_url, needs_api_key, needs_cse_id)
        self.web_search_engines = [
            ("DuckDuckGo", "duckduckgo", None, False, False),  # Free, no API key
            ("Tavily", "tavily", "https://tavily.com/", True, False),
            ("Google", "google", "https://programmablesearchengine.google.com/", True, True),  # Needs CSE ID
            ("Brave", "brave", "https://brave.com/search/api/", True, False),
            ("SerpApi", "serpapi", "https://serpapi.com/", True, False),
            ("Serper", "serper", "https://serper.dev/", True, False),
        ]
        
        # Create notebook for tabs
        self.web_search_notebook = ttk.Notebook(parent)
        self.web_search_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Track API key and settings vars per engine
        self.web_search_api_vars = {}
        self.web_search_cse_vars = {}  # For Google CSE ID
        self.web_search_count_vars = {}
        
        for display_name, engine_key, api_url, needs_api_key, needs_cse_id in self.web_search_engines:
            tab = ttk.Frame(self.web_search_notebook)
            self.web_search_notebook.add(tab, text=display_name)
            
            # API Configuration row
            api_frame = ttk.LabelFrame(tab, text="API Configuration", padding=5)
            api_frame.pack(fill=tk.X, padx=5, pady=5)
            
            if needs_api_key:
                # API Key field
                ttk.Label(api_frame, text="API Key:").pack(side=tk.LEFT, padx=(5, 5))
                api_var = tk.StringVar()
                api_entry = ttk.Entry(api_frame, textvariable=api_var, width=30, show="*")
                api_entry.pack(side=tk.LEFT, padx=5)
                
                # Load existing key
                saved_key = self._load_web_search_api_key(engine_key)
                if saved_key:
                    api_var.set(saved_key)
                
                # Auto-save on focus out
                api_entry.bind("<FocusOut>", lambda e, k=engine_key, v=api_var: self._save_web_search_api_key(k, v.get()))
                self.web_search_api_vars[engine_key] = api_var
                
                # Get API Key button
                get_key_btn = ttk.Button(
                    api_frame, 
                    text="Get API Key",
                    command=lambda url=api_url: webbrowser.open_new(url)
                )
                get_key_btn.pack(side=tk.LEFT, padx=5)
                
                # Google needs CSE ID
                if needs_cse_id:
                    ttk.Label(api_frame, text="CSE ID:").pack(side=tk.LEFT, padx=(15, 5))
                    cse_var = tk.StringVar()
                    cse_entry = ttk.Entry(api_frame, textvariable=cse_var, width=20)
                    cse_entry.pack(side=tk.LEFT, padx=5)
                    
                    # Load saved CSE ID
                    saved_cse = self._get_web_search_setting(engine_key, "cse_id", "")
                    if saved_cse:
                        cse_var.set(saved_cse)
                    
                    cse_entry.bind("<FocusOut>", lambda e, k=engine_key, v=cse_var: self._save_web_search_setting(k, "cse_id", v.get()))
                    self.web_search_cse_vars[engine_key] = cse_var
                    
                    # Get CSE ID button
                    get_cse_btn = ttk.Button(
                        api_frame,
                        text="Get CSE ID",
                        command=lambda: webbrowser.open_new("https://programmablesearchengine.google.com/controlpanel/all")
                    )
                    get_cse_btn.pack(side=tk.LEFT, padx=5)
            else:
                ttk.Label(api_frame, text="No API key required (free)", foreground="green").pack(side=tk.LEFT, padx=10)
            
            # Search Configuration row
            config_frame = ttk.LabelFrame(tab, text="Search Configuration", padding=5)
            config_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Result count
            ttk.Label(config_frame, text="Results:").pack(side=tk.LEFT, padx=(5, 5))
            saved_count = self._get_web_search_setting(engine_key, "count", 5)
            count_var = tk.StringVar(value=str(saved_count))
            count_spinbox = ttk.Spinbox(config_frame, from_=1, to=20, width=5, textvariable=count_var)
            count_spinbox.pack(side=tk.LEFT, padx=5)
            count_spinbox.bind("<FocusOut>", lambda e, k=engine_key, v=count_var: self._save_web_search_setting(k, "count", int(v.get())))
            self.web_search_count_vars[engine_key] = count_var
            
            # Search button
            search_btn = ttk.Button(
                config_frame,
                text="Search",
                command=lambda k=engine_key: self._do_web_search(k)
            )
            search_btn.pack(side=tk.LEFT, padx=20)
        
        # Bind tab change to save current engine
        self.web_search_notebook.bind("<<NotebookTabChanged>>", self._on_web_search_tab_changed)
        
        # Select previously active tab
        active_engine = self.settings["tool_settings"].get("Web Search", {}).get("active_engine", "duckduckgo")
        for i, (_, key, _, _, _) in enumerate(self.web_search_engines):
            if key == active_engine:
                self.web_search_notebook.select(i)
                break
    
    def _load_web_search_api_key(self, engine_key):
        """Load encrypted API key for a search engine."""
        try:
            from tools.ai_tools import decrypt_api_key
            encrypted = self.settings["tool_settings"].get("Web Search", {}).get(f"{engine_key}_api_key", "")
            if encrypted:
                return decrypt_api_key(encrypted)
        except Exception:
            pass
        return ""
    
    def _save_web_search_api_key(self, engine_key, api_key):
        """Save encrypted API key for a search engine."""
        try:
            from tools.ai_tools import encrypt_api_key
            if "Web Search" not in self.settings["tool_settings"]:
                self.settings["tool_settings"]["Web Search"] = {}
            if api_key:
                self.settings["tool_settings"]["Web Search"][f"{engine_key}_api_key"] = encrypt_api_key(api_key)
            else:
                self.settings["tool_settings"]["Web Search"].pop(f"{engine_key}_api_key", None)
            self.save_settings()
        except Exception as e:
            self.logger.error(f"Failed to save API key: {e}")
    
    def _get_web_search_setting(self, engine_key, setting, default):
        """Get a search engine setting."""
        return self.settings["tool_settings"].get("Web Search", {}).get(f"{engine_key}_{setting}", default)
    
    def _save_web_search_setting(self, engine_key, setting, value):
        """Save a search engine setting."""
        if "Web Search" not in self.settings["tool_settings"]:
            self.settings["tool_settings"]["Web Search"] = {}
        self.settings["tool_settings"]["Web Search"][f"{engine_key}_{setting}"] = value
        self.save_settings()
    
    def _on_web_search_tab_changed(self, event=None):
        """Save the currently active search engine tab."""
        if hasattr(self, 'web_search_notebook'):
            idx = self.web_search_notebook.index(self.web_search_notebook.select())
            if idx < len(self.web_search_engines):
                engine_key = self.web_search_engines[idx][1]
                if "Web Search" not in self.settings["tool_settings"]:
                    self.settings["tool_settings"]["Web Search"] = {}
                self.settings["tool_settings"]["Web Search"]["active_engine"] = engine_key
                self.save_settings()
    
    def _do_web_search(self, engine_key):
        """Perform web search using the selected engine with inline implementations."""
        # Get input text
        current_tab_index = self.input_notebook.index(self.input_notebook.select())
        active_input_tab = self.input_tabs[current_tab_index]
        query = active_input_tab.text.get("1.0", tk.END).strip()
        
        if not query:
            self.update_output_text("Please enter a search query in the Input panel.")
            return
        
        # Get settings
        count = int(self.web_search_count_vars.get(engine_key, tk.StringVar(value="5")).get())
        
        try:
            # Inline search based on engine - uses API keys from settings
            if engine_key == "duckduckgo":
                results = self._search_duckduckgo(query, count)
            elif engine_key == "tavily":
                results = self._search_tavily(query, count)
            elif engine_key == "google":
                results = self._search_google(query, count)
            elif engine_key == "brave":
                results = self._search_brave(query, count)
            elif engine_key == "serpapi":
                results = self._search_serpapi(query, count)
            elif engine_key == "serper":
                results = self._search_serper(query, count)
            else:
                self.update_output_text(f"Unknown search engine: {engine_key}")
                return
            
            if not results:
                self.update_output_text(f"No results found for '{query}'")
                return
            
            # Format results
            lines = [f"Search Results ({engine_key.upper()}):", "=" * 50, ""]
            for i, r in enumerate(results, 1):
                lines.append(f"{i}. {r.get('title', 'No title')}")
                snippet = r.get('snippet', '')[:200]
                if len(r.get('snippet', '')) > 200:
                    snippet += "..."
                lines.append(f"   {snippet}")
                lines.append(f"   URL: {r.get('url', 'N/A')}")
                lines.append("")
            
            self.update_output_text("\n".join(lines))
        except Exception as e:
            self.update_output_text(f"Search error: {str(e)}")
    
    def _search_duckduckgo(self, query: str, count: int) -> list:
        """Search DuckDuckGo using ddgs package (free, no API key)."""
        try:
            from ddgs import DDGS
        except ImportError:
            return [{"title": "Error", "snippet": "DuckDuckGo requires: pip install ddgs", "url": ""}]
        
        try:
            with DDGS() as ddgs:
                results = []
                for r in ddgs.text(query, max_results=count):
                    results.append({
                        "title": r.get("title", ""),
                        "snippet": r.get("body", ""),
                        "url": r.get("href", ""),
                    })
                return results
        except Exception as e:
            self.logger.error(f"DuckDuckGo search failed: {e}")
            return []
    
    def _search_tavily(self, query: str, count: int) -> list:
        """Search using Tavily API (AI-optimized search)."""
        api_key = self._load_web_search_api_key("tavily")
        if not api_key:
            return [{"title": "Error", "snippet": "Tavily API key required. Enter in API Configuration.", "url": ""}]
        
        try:
            import urllib.request
            import json
            
            url = "https://api.tavily.com/search"
            data = json.dumps({
                "api_key": api_key,
                "query": query,
                "search_depth": "basic",
                "max_results": count
            }).encode()
            
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode())
            
            results = []
            for item in result.get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("content", ""),
                    "url": item.get("url", ""),
                })
            return results
        except Exception as e:
            self.logger.error(f"Tavily search failed: {e}")
            return [{"title": "Error", "snippet": str(e), "url": ""}]
    
    def _search_google(self, query: str, count: int) -> list:
        """Search using Google Custom Search API."""
        api_key = self._load_web_search_api_key("google")
        cse_id = self._get_web_search_setting("google", "cse_id", "")
        
        if not api_key:
            return [{"title": "Error", "snippet": "Google API key required. Enter in API Configuration.", "url": ""}]
        if not cse_id:
            return [{"title": "Error", "snippet": "Google CSE ID required. Enter in API Configuration.", "url": ""}]
        
        try:
            import urllib.request
            import urllib.parse
            import json
            
            url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={urllib.parse.quote(query)}&num={min(count, 10)}"
            
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())
            
            if "error" in data:
                return [{"title": "Error", "snippet": data["error"]["message"], "url": ""}]
            
            results = []
            for item in data.get("items", []):
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "url": item.get("link", ""),
                })
            return results
        except Exception as e:
            self.logger.error(f"Google search failed: {e}")
            return [{"title": "Error", "snippet": str(e), "url": ""}]
    
    def _search_brave(self, query: str, count: int) -> list:
        """Search using Brave Search API."""
        api_key = self._load_web_search_api_key("brave")
        if not api_key:
            return [{"title": "Error", "snippet": "Brave API key required. Enter in API Configuration.", "url": ""}]
        
        try:
            import urllib.request
            import urllib.parse
            import json
            
            url = f"https://api.search.brave.com/res/v1/web/search?q={urllib.parse.quote(query)}&count={min(count, 20)}"
            
            req = urllib.request.Request(url, headers={
                "Accept": "application/json",
                "X-Subscription-Token": api_key
            })
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())
            
            results = []
            for item in data.get("web", {}).get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("description", ""),
                    "url": item.get("url", ""),
                })
            return results
        except Exception as e:
            self.logger.error(f"Brave search failed: {e}")
            return [{"title": "Error", "snippet": str(e), "url": ""}]
    
    def _search_serpapi(self, query: str, count: int) -> list:
        """Search using SerpApi (Google SERP)."""
        api_key = self._load_web_search_api_key("serpapi")
        if not api_key:
            return [{"title": "Error", "snippet": "SerpApi key required. Enter in API Configuration.", "url": ""}]
        
        try:
            import urllib.request
            import urllib.parse
            import json
            
            url = f"https://serpapi.com/search?q={urllib.parse.quote(query)}&api_key={api_key}&num={min(count, 10)}"
            
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())
            
            results = []
            for item in data.get("organic_results", []):
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "url": item.get("link", ""),
                })
            return results[:count]
        except Exception as e:
            self.logger.error(f"SerpApi search failed: {e}")
            return [{"title": "Error", "snippet": str(e), "url": ""}]
    
    def _search_serper(self, query: str, count: int) -> list:
        """Search using Serper.dev (Google SERP)."""
        api_key = self._load_web_search_api_key("serper")
        if not api_key:
            return [{"title": "Error", "snippet": "Serper API key required. Enter in API Configuration.", "url": ""}]
        
        try:
            import urllib.request
            import json
            
            url = "https://google.serper.dev/search"
            data = json.dumps({"q": query, "num": min(count, 10)}).encode()
            
            req = urllib.request.Request(url, data=data, headers={
                "X-API-KEY": api_key,
                "Content-Type": "application/json"
            })
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode())
            
            results = []
            for item in result.get("organic", []):
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "url": item.get("link", ""),
                })
            return results
        except Exception as e:
            self.logger.error(f"Serper search failed: {e}")
            return [{"title": "Error", "snippet": str(e), "url": ""}]
    
    def create_url_reader_options(self, parent):
        """Creates the URL Reader tool options panel with format options."""
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Options row
        options_frame = ttk.LabelFrame(main_frame, text="Output Format", padding=5)
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Format selection
        self.url_reader_format_var = tk.StringVar(value=self.settings["tool_settings"].get("URL Reader", {}).get("format", "markdown"))
        
        formats = [("Raw HTML", "html"), ("HTML Extraction", "html_extraction"), ("Markdown", "markdown")]
        for text, value in formats:
            rb = ttk.Radiobutton(options_frame, text=text, variable=self.url_reader_format_var, value=value)
            rb.pack(side=tk.LEFT, padx=10)
        
        # Auto-save on change and update UI
        self.url_reader_format_var.trace_add("write", lambda *_: self._on_url_reader_format_change())
        
        # HTML Extraction settings frame (shows when HTML Extraction is selected)
        self.url_reader_html_settings_frame = ttk.LabelFrame(main_frame, text="HTML Extraction Settings", padding=5)
        
        # Get current settings or defaults
        url_reader_settings = self.settings["tool_settings"].get("URL Reader", {})
        
        # Import HTML tool settings configuration
        from tools.html_tool import get_default_settings, get_settings_ui_config
        default_html_settings = get_default_settings()
        
        # Ensure URL Reader has HTML extraction settings
        if "html_extraction" not in url_reader_settings:
            url_reader_settings["html_extraction"] = default_html_settings.copy()
        
        # Get UI configuration
        ui_config = get_settings_ui_config()
        
        # Store setting variables
        self.url_reader_html_vars = {}
        
        # Separate UI elements by type for better layout
        dropdown_configs = []
        checkbox_configs = []
        entry_configs = []
        
        for setting_key, config in ui_config.items():
            if config["type"] == "dropdown":
                dropdown_configs.append((setting_key, config))
            elif config["type"] == "checkbox":
                checkbox_configs.append((setting_key, config))
            elif config["type"] == "entry":
                entry_configs.append((setting_key, config))
        
        # Create a single row for dropdown and entry elements
        if dropdown_configs or entry_configs:
            controls_frame = ttk.Frame(self.url_reader_html_settings_frame)
            controls_frame.pack(fill=tk.X, pady=5)
            
            # Create dropdown elements (left side)
            for setting_key, config in dropdown_configs:
                ttk.Label(controls_frame, text=config["label"]).pack(side=tk.LEFT, padx=(0, 5))
                
                current_value = url_reader_settings["html_extraction"].get(setting_key, config["default"])
                var = tk.StringVar(value=current_value)
                self.url_reader_html_vars[setting_key] = var
                
                combo = ttk.Combobox(controls_frame, textvariable=var, state="readonly", width=20)
                combo['values'] = [option[0] for option in config["options"]]
                
                # Set the display value based on the internal value
                for option_display, option_value in config["options"]:
                    if option_value == current_value:
                        var.set(option_display)
                        break
                
                combo.pack(side=tk.LEFT, padx=(0, 20))
                
                # Set up change callback
                var.trace('w', lambda *args, key=setting_key: self._on_url_reader_html_setting_change(key))
            
            # Create entry elements (right side of same row)
            for setting_key, config in entry_configs:
                ttk.Label(controls_frame, text=config["label"]).pack(side=tk.LEFT, padx=(0, 5))
                
                current_value = url_reader_settings["html_extraction"].get(setting_key, config["default"])
                var = tk.StringVar(value=current_value)
                self.url_reader_html_vars[setting_key] = var
                
                entry = ttk.Entry(controls_frame, textvariable=var, width=15)
                entry.pack(side=tk.LEFT)
                
                # Set up change callback
                var.trace('w', lambda *args, key=setting_key: self._on_url_reader_html_setting_change(key))
        
        # Create checkbox elements in 3 columns
        if checkbox_configs:
            checkbox_frame = ttk.Frame(self.url_reader_html_settings_frame)
            checkbox_frame.pack(fill=tk.X, pady=5)
            
            # Configure 3 columns with equal weight
            checkbox_frame.grid_columnconfigure(0, weight=1)
            checkbox_frame.grid_columnconfigure(1, weight=1)
            checkbox_frame.grid_columnconfigure(2, weight=1)
            
            # Distribute checkboxes across 3 columns
            for i, (setting_key, config) in enumerate(checkbox_configs):
                column = i % 3
                row = i // 3
                
                current_value = url_reader_settings["html_extraction"].get(setting_key, config["default"])
                var = tk.BooleanVar(value=current_value)
                self.url_reader_html_vars[setting_key] = var
                
                check = ttk.Checkbutton(checkbox_frame, text=config["label"], variable=var)
                check.grid(row=row, column=column, sticky="w", padx=5, pady=2)
                
                # Set up change callback
                var.trace('w', lambda *args, key=setting_key: self._on_url_reader_html_setting_change(key))
        
        # Show/hide HTML extraction settings based on current format
        self._update_url_reader_html_settings_visibility()
        
        # Action row
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Fetch button (becomes Cancel while fetching)
        self.url_fetch_btn = ttk.Button(action_frame, text="Fetch Content", command=self._toggle_url_fetch)
        self.url_fetch_btn.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.url_fetch_status = ttk.Label(action_frame, text="Enter URLs in Input panel (one per line)")
        self.url_fetch_status.pack(side=tk.LEFT, padx=10)
        
        # Track fetch state
        self.url_fetch_in_progress = False
        self.url_fetch_thread = None
    
    def _on_url_reader_format_change(self):
        """Handle URL Reader format change."""
        self._save_url_reader_settings()
        self._update_url_reader_html_settings_visibility()
    
    def _update_url_reader_html_settings_visibility(self):
        """Show or hide HTML extraction settings based on selected format."""
        if not hasattr(self, 'url_reader_html_settings_frame'):
            return
        
        format_value = self.url_reader_format_var.get()
        if format_value == "html_extraction":
            self.url_reader_html_settings_frame.pack(fill=tk.X, padx=5, pady=5, before=self.url_fetch_btn.master)
        else:
            self.url_reader_html_settings_frame.pack_forget()
    
    def _on_url_reader_html_setting_change(self, setting_key):
        """Handle URL Reader HTML extraction setting changes."""
        if not hasattr(self, 'url_reader_html_vars'):
            return
        
        # Ensure settings structure exists
        if "URL Reader" not in self.settings["tool_settings"]:
            self.settings["tool_settings"]["URL Reader"] = {}
        if "html_extraction" not in self.settings["tool_settings"]["URL Reader"]:
            self.settings["tool_settings"]["URL Reader"]["html_extraction"] = {}
        
        # Get the actual value based on setting type
        var = self.url_reader_html_vars[setting_key]
        if isinstance(var, tk.BooleanVar):
            value = var.get()
        elif isinstance(var, tk.StringVar):
            # For dropdown, convert display value to internal value
            display_value = var.get()
            from tools.html_tool import get_settings_ui_config
            ui_config = get_settings_ui_config()
            if setting_key in ui_config and ui_config[setting_key]["type"] == "dropdown":
                # Find the internal value for this display value
                for option_display, option_value in ui_config[setting_key]["options"]:
                    if option_display == display_value:
                        value = option_value
                        break
                else:
                    value = display_value
            else:
                value = display_value
        else:
            value = var.get()
        
        self.settings["tool_settings"]["URL Reader"]["html_extraction"][setting_key] = value
        self.save_settings()
    
    def _save_url_reader_settings(self):
        """Save URL Reader settings."""
        if "URL Reader" not in self.settings["tool_settings"]:
            self.settings["tool_settings"]["URL Reader"] = {}
        self.settings["tool_settings"]["URL Reader"]["format"] = self.url_reader_format_var.get()
        self.save_settings()
    
    def _toggle_url_fetch(self):
        """Toggle between Fetch Content and Cancel."""
        if self.url_fetch_in_progress:
            # Cancel the fetch
            self.url_fetch_in_progress = False
            self.url_fetch_btn.configure(text="Fetch Content")
            self.url_fetch_status.configure(text="Cancelled")
        else:
            # Start fetch
            self._start_url_fetch()
    
    def _start_url_fetch(self):
        """Start fetching URL content in background."""
        import threading
        
        # Get URLs from input
        current_tab_index = self.input_notebook.index(self.input_notebook.select())
        active_input_tab = self.input_tabs[current_tab_index]
        text = active_input_tab.text.get("1.0", tk.END).strip()
        urls = [u.strip() for u in text.splitlines() if u.strip()]
        
        if not urls:
            self.url_fetch_status.configure(text="No URLs found in Input panel")
            return
        
        self.url_fetch_in_progress = True
        self.url_fetch_btn.configure(text="Cancel")
        self.url_fetch_status.configure(text=f"Fetching {len(urls)} URL(s)...")
        
        output_format = self.url_reader_format_var.get()
        
        def fetch_worker():
            from tools.url_content_reader import URLContentReader
            reader = URLContentReader()
            results = []
            
            for i, url in enumerate(urls):
                if not self.url_fetch_in_progress:
                    results.append(f"# Cancelled\n\nFetch cancelled by user.")
                    break
                
                self.after(0, lambda i=i, t=len(urls): self.url_fetch_status.configure(text=f"Fetching {i+1}/{t}..."))
                
                try:
                    if output_format == "html":
                        content = reader.fetch_url(url, timeout=30)
                        results.append(f"<!-- URL: {url} -->\n{content}")
                    elif output_format == "html_extraction":
                        # Fetch HTML and process with HTML Extraction Tool
                        from tools.html_tool import HTMLExtractionTool
                        html_content = reader.fetch_url(url, timeout=30)
                        html_tool = HTMLExtractionTool()
                        
                        # Get HTML extraction settings
                        html_settings = self.settings["tool_settings"].get("URL Reader", {}).get("html_extraction", {})
                        extracted_content = html_tool.process_text(html_content, html_settings)
                        results.append(f"# Content from: {url}\n\n{extracted_content}")
                    else:  # markdown
                        content = reader.fetch_and_convert(url, timeout=30)
                        results.append(f"# Content from: {url}\n\n{content}")
                except Exception as e:
                    results.append(f"# Error: {url}\n\nError: {str(e)}")
            
            final_output = "\n\n---\n\n".join(results)
            
            def update_ui():
                self.url_fetch_in_progress = False
                self.url_fetch_btn.configure(text="Fetch Content")
                self.url_fetch_status.configure(text="Complete")
                self.update_output_text(final_output)
            
            self.after(0, update_ui)
        
        self.url_fetch_thread = threading.Thread(target=fetch_worker, daemon=True)
        self.url_fetch_thread.start()

    def create_html_extraction_tool_widget(self, parent):
        """Create and configure the HTML Extraction Tool widget."""
        if not HTML_EXTRACTION_TOOL_MODULE_AVAILABLE:
            return
        
        # Get current settings
        settings = self.settings["tool_settings"].get("HTML Extraction Tool", {})
        
        # Create the HTML Extraction Tool UI
        self.create_html_extraction_tool_ui(parent, settings)

    def create_html_extraction_tool_ui(self, parent, settings):
        """Create the HTML Extraction Tool user interface."""
        from tools.html_tool import get_default_settings, get_settings_ui_config
        
        # Ensure we have default settings
        default_settings = get_default_settings()
        for key, value in default_settings.items():
            if key not in settings:
                settings[key] = value
        
        # Main frame
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="HTML Extraction Settings", padding="5")
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Get UI configuration
        ui_config = get_settings_ui_config()
        
        # Store setting variables
        self.html_tool_vars = {}
        
        # Separate UI elements by type for better layout
        dropdown_configs = []
        checkbox_configs = []
        entry_configs = []
        
        for setting_key, config in ui_config.items():
            if config["type"] == "dropdown":
                dropdown_configs.append((setting_key, config))
            elif config["type"] == "checkbox":
                checkbox_configs.append((setting_key, config))
            elif config["type"] == "entry":
                entry_configs.append((setting_key, config))
        
        # Create a single row for dropdown and entry elements
        if dropdown_configs or entry_configs:
            controls_frame = ttk.Frame(settings_frame)
            controls_frame.pack(fill=tk.X, pady=5)
            
            # Create dropdown elements (left side)
            for setting_key, config in dropdown_configs:
                ttk.Label(controls_frame, text=config["label"]).pack(side=tk.LEFT, padx=(0, 5))
                
                var = tk.StringVar(value=settings.get(setting_key, config["default"]))
                self.html_tool_vars[setting_key] = var
                
                combo = ttk.Combobox(controls_frame, textvariable=var, state="readonly", width=20)
                combo['values'] = [option[0] for option in config["options"]]
                combo.pack(side=tk.LEFT, padx=(0, 20))
                
                # Set up change callback
                var.trace('w', lambda *args, key=setting_key: self.on_html_tool_setting_change(key))
            
            # Create entry elements (right side of same row)
            for setting_key, config in entry_configs:
                ttk.Label(controls_frame, text=config["label"]).pack(side=tk.LEFT, padx=(0, 5))
                
                var = tk.StringVar(value=settings.get(setting_key, config["default"]))
                self.html_tool_vars[setting_key] = var
                
                entry = ttk.Entry(controls_frame, textvariable=var, width=15)
                entry.pack(side=tk.LEFT)
                
                # Set up change callback
                var.trace('w', lambda *args, key=setting_key: self.on_html_tool_setting_change(key))
        
        # Create checkbox elements in 3 columns
        if checkbox_configs:
            checkbox_frame = ttk.Frame(settings_frame)
            checkbox_frame.pack(fill=tk.X, pady=5)
            
            # Configure 3 columns with equal weight
            checkbox_frame.grid_columnconfigure(0, weight=1)
            checkbox_frame.grid_columnconfigure(1, weight=1)
            checkbox_frame.grid_columnconfigure(2, weight=1)
            
            # Distribute checkboxes across 3 columns
            for i, (setting_key, config) in enumerate(checkbox_configs):
                column = i % 3
                row = i // 3
                
                var = tk.BooleanVar(value=settings.get(setting_key, config["default"]))
                self.html_tool_vars[setting_key] = var
                
                check = ttk.Checkbutton(checkbox_frame, text=config["label"], variable=var)
                check.grid(row=row, column=column, sticky="w", padx=5, pady=2)
                
                # Set up change callback
                var.trace('w', lambda *args, key=setting_key: self.on_html_tool_setting_change(key))
        

        
        # Extract button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        extract_button = ttk.Button(
            button_frame, 
            text="Extract", 
            command=self.extract_html_content,
            style="Accent.TButton"
        )
        extract_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Help text
        help_text = ttk.Label(
            button_frame,
            text="Paste HTML content in input tab, select extraction method, then click Extract",
            foreground="gray"
        )
        help_text.pack(side=tk.LEFT)

    def on_html_tool_setting_change(self, setting_key):
        """Handle HTML tool setting changes."""
        if not hasattr(self, 'html_tool_vars'):
            return
        
        # Update settings
        if "HTML Extraction Tool" not in self.settings["tool_settings"]:
            self.settings["tool_settings"]["HTML Extraction Tool"] = {}
        
        # Get the actual value based on setting type
        var = self.html_tool_vars[setting_key]
        if isinstance(var, tk.BooleanVar):
            value = var.get()
        elif isinstance(var, tk.StringVar):
            # For dropdown, convert display value to internal value
            display_value = var.get()
            from tools.html_tool import get_settings_ui_config
            ui_config = get_settings_ui_config()
            if setting_key in ui_config and ui_config[setting_key]["type"] == "dropdown":
                # Find the internal value for this display value
                for option_display, option_value in ui_config[setting_key]["options"]:
                    if option_display == display_value:
                        value = option_value
                        break
                else:
                    value = display_value
            else:
                value = display_value
        else:
            value = var.get()
        
        self.settings["tool_settings"]["HTML Extraction Tool"][setting_key] = value
        self.save_settings()

    def extract_html_content(self):
        """Extract HTML content using the selected method."""
        try:
            # Get input text
            active_input_tab = self.input_tabs[self.input_notebook.index(self.input_notebook.select())]
            input_text = active_input_tab.text.get("1.0", tk.END).strip()
            
            if not input_text:
                if self.dialog_manager:
                    self.dialog_manager.show_warning("No Input", "Please paste HTML content in the input tab first.", "warning")
                else:
                    messagebox.showwarning("No Input", "Please paste HTML content in the input tab first.")
                return
            
            # Process the HTML
            if HTML_EXTRACTION_TOOL_MODULE_AVAILABLE and self.html_extraction_tool:
                settings = self.settings["tool_settings"]["HTML Extraction Tool"]
                result = self.html_extraction_tool.process_text(input_text, settings)
                
                # Update output
                self.update_output_text(result)
                
                # Show success message
                if self.dialog_manager:
                    self.dialog_manager.show_info("Extraction Complete", "HTML content has been processed successfully.", "success")
                else:
                    messagebox.showinfo("Extraction Complete", "HTML content has been processed successfully.")
            else:
                error_msg = "HTML Extraction Tool is not available."
                self.update_output_text(error_msg)
                self._handle_warning(error_msg, "HTML Extraction", "Module", show_dialog=True)
                
        except Exception as e:
            self._handle_error(e, "Extracting HTML content", "HTML Tool")
            self.update_output_text(f"Error extracting HTML content: {str(e)}")

    def create_line_tools_widget(self, parent):
        """Creates the Line Tools widget."""
        if not LINE_TOOLS_MODULE_AVAILABLE:
            ttk.Label(parent, text="Line Tools module not available").pack(padx=10, pady=10)
            return
        self.line_tools_widget = self.line_tools.create_widget(parent, self)
        self.line_tools_widget.pack(fill=tk.BOTH, expand=True)

    def create_whitespace_tools_widget(self, parent):
        """Creates the Whitespace Tools widget."""
        if not WHITESPACE_TOOLS_MODULE_AVAILABLE:
            ttk.Label(parent, text="Whitespace Tools module not available").pack(padx=10, pady=10)
            return
        self.whitespace_tools_widget = self.whitespace_tools.create_widget(parent, self)
        self.whitespace_tools_widget.pack(fill=tk.BOTH, expand=True)

    def create_text_statistics_widget(self, parent):
        """Creates the Text Statistics widget."""
        if not TEXT_STATISTICS_MODULE_AVAILABLE:
            ttk.Label(parent, text="Text Statistics module not available").pack(padx=10, pady=10)
            return
        self.text_statistics_widget = self.text_statistics.create_widget(parent, self)
        self.text_statistics_widget.pack(fill=tk.BOTH, expand=True)

    def create_hash_generator_widget(self, parent):
        """Creates the Hash Generator widget."""
        if not HASH_GENERATOR_MODULE_AVAILABLE:
            ttk.Label(parent, text="Hash Generator module not available").pack(padx=10, pady=10)
            return
        self.hash_generator_widget = self.hash_generator.create_widget(parent, self)
        self.hash_generator_widget.pack(fill=tk.BOTH, expand=True)

    def create_markdown_tools_widget(self, parent):
        """Creates the Markdown Tools widget."""
        if not MARKDOWN_TOOLS_MODULE_AVAILABLE:
            ttk.Label(parent, text="Markdown Tools module not available").pack(padx=10, pady=10)
            return
        self.markdown_tools_widget = self.markdown_tools.create_widget(parent, self)
        self.markdown_tools_widget.pack(fill=tk.BOTH, expand=True)

    def create_string_escape_tool_widget(self, parent):
        """Creates the String Escape Tool widget."""
        if not STRING_ESCAPE_TOOL_MODULE_AVAILABLE:
            ttk.Label(parent, text="String Escape Tool module not available").pack(padx=10, pady=10)
            return
        self.string_escape_tool_widget = self.string_escape_tool.create_widget(parent, self)
        self.string_escape_tool_widget.pack(fill=tk.BOTH, expand=True)

    def create_number_base_converter_widget(self, parent):
        """Creates the Number Base Converter widget."""
        if not NUMBER_BASE_CONVERTER_MODULE_AVAILABLE:
            ttk.Label(parent, text="Number Base Converter module not available").pack(padx=10, pady=10)
            return
        self.number_base_converter_widget = self.number_base_converter.create_widget(parent, self)
        self.number_base_converter_widget.pack(fill=tk.BOTH, expand=True)

    def create_text_wrapper_widget(self, parent):
        """Creates the Text Wrapper widget."""
        if not TEXT_WRAPPER_MODULE_AVAILABLE:
            ttk.Label(parent, text="Text Wrapper module not available").pack(padx=10, pady=10)
            return
        self.text_wrapper_widget = self.text_wrapper.create_widget(parent, self)
        self.text_wrapper_widget.pack(fill=tk.BOTH, expand=True)

    def create_column_tools_widget(self, parent):
        """Creates the Column Tools widget."""
        if not COLUMN_TOOLS_MODULE_AVAILABLE:
            ttk.Label(parent, text="Column Tools module not available").pack(padx=10, pady=10)
            return
        self.column_tools_widget = self.column_tools.create_widget(parent, self)
        self.column_tools_widget.pack(fill=tk.BOTH, expand=True)

    def create_timestamp_converter_widget(self, parent):
        """Creates the Timestamp Converter widget."""
        if not TIMESTAMP_CONVERTER_MODULE_AVAILABLE:
            ttk.Label(parent, text="Timestamp Converter module not available").pack(padx=10, pady=10)
            return
        self.timestamp_converter_widget = self.timestamp_converter.create_widget(parent, self)
        self.timestamp_converter_widget.pack(fill=tk.BOTH, expand=True)

    def on_tool_setting_change(self, *args):
        """
        Handles changes in tool-specific settings.
        Also saves the new settings.
        """
        tool_name = self.tool_var.get()
        if tool_name not in self.settings["tool_settings"]:
            self.settings["tool_settings"][tool_name] = {}
        


        if tool_name == "AI Tools":
            # Settings are handled by the AIToolsWidget itself
            pass
        elif tool_name == "Case Tool":
            if CASE_TOOL_MODULE_AVAILABLE and hasattr(self, 'case_tool_ui'):
                current_settings = self.case_tool_ui.get_current_settings()
                self.settings["tool_settings"][tool_name].update(current_settings)

        elif tool_name == "Base64 Encoder/Decoder":
            # Settings are handled by the Base64ToolsWidget itself
            pass
        elif tool_name == "JSON/XML Tool":
            # Get current settings from the JSON/XML tool widget
            if hasattr(self, 'jsonxml_tool') and self.jsonxml_tool:
                current_settings = self.jsonxml_tool.get_settings()
                self.settings["tool_settings"][tool_name].update(current_settings)
        elif tool_name == "Cron Tool":
            # Get current settings from the Cron tool widget
            if hasattr(self, 'cron_tool') and self.cron_tool:
                current_settings = self.cron_tool.get_settings()
                self.settings["tool_settings"][tool_name].update(current_settings)
        elif tool_name == "Extraction Tools":
            # Settings are handled by the individual extraction tool widgets
            pass
        elif tool_name == "HTML Extraction Tool":
            # Settings are handled by the on_html_tool_setting_change method
            pass
        elif tool_name == "Sorter Tools":
            # Settings are handled by the SorterToolsWidget itself
            pass
        elif tool_name == "Find & Replace Text":
            if FIND_REPLACE_MODULE_AVAILABLE and self.find_replace_widget:
                # Use the new Find & Replace widget's settings
                settings = self.settings["tool_settings"][tool_name]
                widget_settings = self.find_replace_widget.get_settings()
                settings.update(widget_settings)
            

        elif tool_name == "Generator Tools":
            # Settings are handled by the GeneratorToolsWidget itself
            pass
        elif tool_name == "Extraction Tools":
            # Settings are handled by the individual extraction tool widgets
            pass
        elif tool_name == "Email Header Analyzer":
            if EMAIL_HEADER_ANALYZER_MODULE_AVAILABLE and hasattr(self, 'email_header_analyzer_ui'):
                current_settings = self.email_header_analyzer_ui.get_current_settings()
                self.settings["tool_settings"][tool_name].update(current_settings)
        elif tool_name == "Folder File Reporter":
            if FOLDER_FILE_REPORTER_MODULE_AVAILABLE and self.folder_file_reporter:
                current_settings = self.folder_file_reporter.save_settings()
                self.settings["tool_settings"][tool_name].update(current_settings)
        elif tool_name == "URL Parser":
            if URL_PARSER_MODULE_AVAILABLE and hasattr(self, 'url_parser_ui'):
                current_settings = self.url_parser_ui.get_current_settings()
                self.settings["tool_settings"][tool_name].update(current_settings)
        elif tool_name == "Diff Viewer":
            if "Diff Viewer" not in self.settings["tool_settings"]:
                self.settings["tool_settings"]["Diff Viewer"] = {}
            if DIFF_VIEWER_MODULE_AVAILABLE and hasattr(self, 'diff_settings_widget'):
                # Get settings from the new widget
                widget_settings = self.diff_settings_widget.get_settings()
                self.settings["tool_settings"]["Diff Viewer"].update(widget_settings)

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
        self._update_stats_impl(text_widget, status_bar)
    
    def _update_stats_impl(self, text_widget, status_bar):
        """Internal implementation of statistics update with intelligent caching and progressive calculation."""
        text = text_widget.get("1.0", tk.END)
        text_length = len(text)
        
        # Determine widget ID for tracking
        widget_id = self._get_widget_id_for_text_widget(text_widget)
        
        # Check if we should use progressive calculation for large content (>50,000 characters)
        if text_length >= 50000 and hasattr(self, 'progressive_stats_calculator') and self.progressive_stats_calculator:
            try:
                # Cancel any existing calculation for this widget
                if widget_id:
                    cancelled_count = self.progressive_stats_calculator.cancel_calculation_for_widget(widget_id)
                    if cancelled_count > 0:
                        self.logger.debug(f"Cancelled {cancelled_count} existing calculation(s) for {widget_id}")
                
                # Show initial progress indicator
                self._show_progress_indicator(status_bar, "Calculating...")
                
                # Define callbacks
                def on_complete(stats):
                    """Callback when progressive calculation completes."""
                    try:
                        # Update status bar with results
                        if status_bar.winfo_exists():
                            status_bar.config(text=stats.to_status_string())
                            self._hide_progress_indicator(status_bar)
                    except tk.TclError:
                        # Widget may have been destroyed
                        pass
                
                def on_progress(progress_info):
                    """Callback for progress updates."""
                    try:
                        if status_bar.winfo_exists():
                            # Only show indicator if calculation is taking longer than 100ms
                            if progress_info.should_show_indicator:
                                progress_text = f"Calculating... {progress_info.progress_percent:.0f}%"
                                self._show_progress_indicator(status_bar, progress_text)
                    except tk.TclError:
                        # Widget may have been destroyed
                        pass
                
                # Start progressive calculation
                self.progressive_stats_calculator.calculate_progressive(
                    text=text,
                    callback=on_complete,
                    progress_callback=on_progress,
                    widget_id=widget_id
                )
                
                return
                
            except Exception as e:
                self.logger.warning(f"Progressive calculation failed, falling back: {e}")
                self._hide_progress_indicator(status_bar)
                # Fall through to standard calculation
        
        # Use intelligent caching if available (for smaller content or if progressive failed)
        if INTELLIGENT_CACHING_AVAILABLE and hasattr(self, 'smart_stats_calculator'):
            try:
                stats = self.smart_stats_calculator.calculate_stats(text)
                status_bar.config(text=stats.to_status_string())
                return
            except Exception as e:
                self.logger.warning(f"Smart stats calculation failed, falling back to basic: {e}")
        
        # Fallback to optimized basic calculation
        self._update_stats_basic(text, status_bar)
    
    def _update_stats_basic(self, text, status_bar):
        """Optimized basic statistics calculation without regex where possible."""
        # Strip text once and reuse
        stripped_text = text.strip()
        char_count = len(stripped_text)
        
        # Count lines efficiently
        line_count = text.count('\n')
        
        # Optimized word counting - avoid regex for simple cases
        if char_count == 0:
            word_count = 0
        else:
            # Split on whitespace and filter empty strings
            words = [word for word in stripped_text.split() if word]
            word_count = len(words)
        
        # Optimized sentence counting - count sentence endings
        sentence_count = 0
        for char in stripped_text:
            if char in '.!?':
                sentence_count += 1
        
        # Token estimation (rough approximation)
        token_count = max(1, round(char_count / 4))
        
        # Format bytes with K/M suffixes
        byte_count = len(text.encode('utf-8'))
        formatted_bytes = self._format_bytes(byte_count)
        
        status_bar.config(text=f"Bytes: {formatted_bytes} | Word: {word_count} | Sentence: {sentence_count} | Line: {line_count} | Tokens: {token_count}")
    
    def _get_widget_id_for_text_widget(self, text_widget):
        """
        Get a unique identifier for a text widget.
        
        Args:
            text_widget: The text widget to identify
            
        Returns:
            Widget identifier string or None if not found
        """
        # Check input tabs
        for i, tab in enumerate(self.input_tabs):
            if tab.text == text_widget:
                return f"input_tab_{i}"
        
        # Check output tabs
        for i, tab in enumerate(self.output_tabs):
            if tab.text == text_widget:
                return f"output_tab_{i}"
        
        # Check diff tabs if they exist
        if hasattr(self, 'diff_input_tabs'):
            for i, tab in enumerate(self.diff_input_tabs):
                if tab.text == text_widget:
                    return f"diff_input_tab_{i}"
        
        if hasattr(self, 'diff_output_tabs'):
            for i, tab in enumerate(self.diff_output_tabs):
                if tab.text == text_widget:
                    return f"diff_output_tab_{i}"
        
        return None
    
    def _show_progress_indicator(self, status_bar, message="Calculating..."):
        """
        Show a progress indicator in the status bar.
        
        Args:
            status_bar: The status bar label widget
            message: Progress message to display
        """
        try:
            # Store original text if not already stored
            if not hasattr(status_bar, '_original_text'):
                status_bar._original_text = status_bar.cget('text')
            
            # Update with progress message
            status_bar.config(text=message)
            
            # Add visual indicator (change foreground color)
            if not hasattr(status_bar, '_original_fg'):
                status_bar._original_fg = status_bar.cget('foreground')
            status_bar.config(foreground='blue')
            
        except tk.TclError:
            # Widget may have been destroyed
            pass
    
    def _hide_progress_indicator(self, status_bar):
        """
        Hide the progress indicator and restore normal status bar appearance.
        
        Args:
            status_bar: The status bar label widget
        """
        try:
            # Restore original foreground color
            if hasattr(status_bar, '_original_fg'):
                status_bar.config(foreground=status_bar._original_fg)
                delattr(status_bar, '_original_fg')
            
            # Clear stored original text
            if hasattr(status_bar, '_original_text'):
                delattr(status_bar, '_original_text')
            
        except tk.TclError:
            # Widget may have been destroyed
            pass

    def update_tab_labels(self):
        """Updates tab labels to show first 7 non-whitespace characters of content."""
        self._update_tab_labels_impl()
    
    def _update_tab_labels_impl(self):
        """Internal implementation of tab label updates with caching and optimization."""
        # Initialize tab label cache if not exists
        if not hasattr(self, '_tab_label_cache'):
            self._tab_label_cache = {}
        
        # Update input tabs
        self._update_notebook_tab_labels(self.input_tabs, self.input_notebook, 'input')
        
        # Update output tabs
        self._update_notebook_tab_labels(self.output_tabs, self.output_notebook, 'output')
        
        # Update diff tabs if they exist
        if hasattr(self, 'diff_input_tabs'):
            self._update_notebook_tab_labels(self.diff_input_tabs, self.diff_input_notebook, 'diff_input')
            self._update_notebook_tab_labels(self.diff_output_tabs, self.diff_output_notebook, 'diff_output')
    
    def _update_notebook_tab_labels(self, tabs, notebook, cache_key_prefix):
        """Update tab labels for a specific notebook with caching."""
        for i, tab in enumerate(tabs):
            cache_key = f"{cache_key_prefix}_{i}"
            
            # Get content efficiently - only first 50 chars to avoid processing large content
            try:
                # Get only the first few lines to extract first characters efficiently
                content_sample = tab.text.get("1.0", "3.0")  # First 2 lines should be enough
                content_hash = hash(content_sample)
                
                # Check cache
                if cache_key in self._tab_label_cache:
                    cached_hash, cached_label = self._tab_label_cache[cache_key]
                    if cached_hash == content_hash:
                        # Content hasn't changed, skip update
                        continue
                
                # Extract first non-whitespace characters efficiently
                first_chars = self._extract_first_chars(content_sample, 7)
                new_label = f"{i+1}: {first_chars}" if first_chars else f"{i+1}:"
                
                # Update cache
                self._tab_label_cache[cache_key] = (content_hash, new_label)
                
                # Update tab label only if it changed
                current_label = notebook.tab(i, "text")
                if current_label != new_label:
                    notebook.tab(i, text=new_label)
                    
            except tk.TclError:
                # Handle case where tab might not exist
                continue
    
    def _extract_first_chars(self, text, max_chars):
        """Efficiently extract first non-whitespace characters."""
        result = []
        char_count = 0
        
        for char in text:
            if char_count >= max_chars:
                break
            if char not in ' \t\n\r':
                result.append(char)
                char_count += 1
        
        return ''.join(result)

    def _format_bytes(self, byte_count):
        """Format byte count with K/M suffixes for readability."""
        if byte_count >= 1000000:
            value = byte_count / 1000000
            formatted = f"{value:.1f}M"
        elif byte_count >= 1000:
            value = byte_count / 1000
            # Check if rounding to 1 decimal would make it >= 1000K
            if round(value, 1) >= 1000:
                formatted = f"{value / 1000:.1f}M"
            else:
                formatted = f"{value:.1f}K"
        else:
            return str(byte_count)
        
        # Remove trailing zeros and decimal point if not needed
        return formatted.rstrip('0').rstrip('.')

    def update_all_stats(self):
        """
        Updates the status bars for both input and output with visibility awareness.
        
        When StatisticsUpdateManager is available, this method uses visibility-aware
        updates that skip hidden tabs and inactive components. Otherwise, it falls
        back to direct statistics updates.
        """
        # Get active tab indices
        active_input_index = self.input_notebook.index(self.input_notebook.select())
        active_output_index = self.output_notebook.index(self.output_notebook.select())
        
        # Use StatisticsUpdateManager if available
        if hasattr(self, 'statistics_update_manager') and self.statistics_update_manager:
            # Request updates for active tabs with HIGH priority
            input_component_id = f"input_tab_{active_input_index}"
            output_component_id = f"output_tab_{active_output_index}"
            
            # Create update callbacks
            def update_input_stats(widget_id):
                active_input_tab = self.input_tabs[active_input_index]
                self.update_stats(active_input_tab.text, self.input_status_bar)
            
            def update_output_stats(widget_id):
                active_output_tab = self.output_tabs[active_output_index]
                self.update_stats(active_output_tab.text, self.output_status_bar)
            
            # Request updates through the manager
            self.statistics_update_manager.request_update(
                widget_id=input_component_id,
                priority=UpdatePriority.HIGH,
                callback=update_input_stats
            )
            
            self.statistics_update_manager.request_update(
                widget_id=output_component_id,
                priority=UpdatePriority.HIGH,
                callback=update_output_stats
            )
        else:
            # Fallback to direct updates when StatisticsUpdateManager is not available
            active_input_tab = self.input_tabs[active_input_index]
            active_output_tab = self.output_tabs[active_output_index]
            self.update_stats(active_input_tab.text, self.input_status_bar)
            self.update_stats(active_output_tab.text, self.output_status_bar)
        
        # Always update tab labels
        self.update_tab_labels()

    def _consolidated_input_changed(self, widget_id: str, tab_index: int):
        """
        Handles input changes from EventConsolidator with optimized debouncing.
        
        This method is called by the EventConsolidator after intelligent debouncing
        and event deduplication. The EventConsolidator has already:
        - Consolidated multiple event triggers (<<Modified>>, <KeyRelease>, <Button-1>)
        - Applied adaptive debouncing based on content size
        - Prevented duplicate calculations for the same content
        
        Args:
            widget_id: Unique identifier for the widget (e.g., "input_tab_0")
            tab_index: Index of the tab that changed
        """
        # Update statistics immediately since EventConsolidator already handled debouncing
        self.update_all_stats()
        
        # Handle tool processing for non-manual tools
        if self.tool_var.get() not in self.manual_process_tools:
            self.apply_tool()
        
        # Save settings with debouncing to avoid excessive file writes
        if not hasattr(self, '_save_after_id'):
            self._save_after_id = None
        
        if self._save_after_id:
            self.after_cancel(self._save_after_id)
        self._save_after_id = self.after(1000, self.save_settings)
        
        # Store original content for filtering (only if no filter is active)
        try:
            if hasattr(self, 'input_filter_var') and not self.input_filter_var.get():
                if 0 <= tab_index < len(self.input_tabs):
                    active_input_tab = self.input_tabs[tab_index]
                    self.input_original_content[tab_index] = active_input_tab.text.get("1.0", tk.END)
        except (tk.TclError, IndexError) as e:
            # Handle case where tab might not exist or be selected
            self.logger.debug(f"Error storing original content for tab {tab_index}: {e}")

    def on_input_changed(self, event=None):
        """
        Legacy input change handler for backward compatibility.
        
        This method is kept for widgets that don't use EventConsolidator.
        When EventConsolidator is available, it handles all event consolidation,
        debouncing, and deduplication, so this method should rarely be called.
        
        This provides a fallback for:
        - Systems where EventConsolidator is not available
        - Widgets not registered with EventConsolidator
        - Edge cases during initialization
        """
        # If EventConsolidator is available, log that we're using fallback
        if hasattr(self, 'event_consolidator') and self.event_consolidator:
            self.logger.debug("on_input_changed called despite EventConsolidator being available - using fallback")
        
        # Initialize debouncing system if not exists
        if not hasattr(self, '_debounce_manager'):
            self._debounce_manager = {
                'stats_after_id': None,
                'tool_after_id': None,
                'save_after_id': None,
                'last_stats_update': 0,
                'last_tool_update': 0,
                'last_save_update': 0
            }
        
        current_time = time.time() * 1000  # Convert to milliseconds
        
        # Save settings with debouncing to avoid excessive file writes
        if self._debounce_manager['save_after_id']:
            self.after_cancel(self._debounce_manager['save_after_id'])
        self._debounce_manager['save_after_id'] = self.after(1000, self.save_settings)
        
        # Immediate stats update for small changes, debounced for frequent changes
        time_since_last_stats = current_time - self._debounce_manager['last_stats_update']
        
        if time_since_last_stats > 100:  # Update stats immediately if >100ms since last update
            self.update_all_stats()
            self._debounce_manager['last_stats_update'] = current_time
        else:
            # Debounce stats updates for rapid typing
            if self._debounce_manager['stats_after_id']:
                self.after_cancel(self._debounce_manager['stats_after_id'])
            self._debounce_manager['stats_after_id'] = self.after(50, self._debounced_stats_update)
        
        # Tool processing with longer debounce
        if self.tool_var.get() in self.manual_process_tools:
            return

        if self._debounce_manager['tool_after_id']:
            self.after_cancel(self._debounce_manager['tool_after_id'])
        
        # Adaptive debounce delay based on content size (matches EventConsolidator behavior)
        try:
            current_tab_index = self.input_notebook.index(self.input_notebook.select())
            active_input_tab = self.input_tabs[current_tab_index]
            content_length = len(active_input_tab.text.get("1.0", tk.END))
            
            # Store original content for filtering (only if no filter is active)
            if hasattr(self, 'input_filter_var') and not self.input_filter_var.get():
                self.input_original_content[current_tab_index] = active_input_tab.text.get("1.0", tk.END)
            
            # Adaptive delay matching EventConsolidator's DebounceConfig
            if content_length > 100000:  # Very large content
                debounce_delay = 700  # Extra delay for very large content
            elif content_length > 10000:  # Large content
                debounce_delay = 500  # Slow delay
            elif content_length > 1000:  # Medium content
                debounce_delay = 300  # Normal delay
            else:  # Small content
                debounce_delay = 50  # Fast delay
            
            self._debounce_manager['tool_after_id'] = self.after(debounce_delay, self.apply_tool)
            self._debounce_manager['last_tool_update'] = current_time
            
        except (tk.TclError, IndexError) as e:
            self.logger.debug(f"Error in on_input_changed: {e}")
    
    def _debounced_stats_update(self):
        """Debounced statistics update."""
        self.update_all_stats()
        self._debounce_manager['last_stats_update'] = time.time() * 1000
    
    def cancel_pending_operations(self):
        """Cancel all pending debounced operations."""
        # Cancel EventConsolidator pending updates
        if hasattr(self, 'event_consolidator') and self.event_consolidator:
            self.event_consolidator.cancel_all_pending_updates()
        
        # Cancel legacy debouncing operations
        if hasattr(self, '_debounce_manager'):
            if self._debounce_manager['stats_after_id']:
                self.after_cancel(self._debounce_manager['stats_after_id'])
                self._debounce_manager['stats_after_id'] = None
            
            if self._debounce_manager['tool_after_id']:
                self.after_cancel(self._debounce_manager['tool_after_id'])
                self._debounce_manager['tool_after_id'] = None
                
            if self._debounce_manager['save_after_id']:
                self.after_cancel(self._debounce_manager['save_after_id'])
                self._debounce_manager['save_after_id'] = None
        
        # Cancel consolidated save operation
        if hasattr(self, '_save_after_id') and self._save_after_id:
            self.after_cancel(self._save_after_id)
            self._save_after_id = None
        
        # Legacy support for old debouncing
        if hasattr(self, '_after_id') and self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None

    def export_input_file(self, file_format):
        """Exports the input text to the specified file format."""
        active_input_tab = self.input_tabs[self.input_notebook.index(self.input_notebook.select())]
        input_text = active_input_tab.text.get("1.0", tk.END)
        export_path = self.export_path_var.get()
        if not os.path.isdir(export_path):
            self._handle_warning("Invalid export path specified in settings", "Export Input", "File", show_dialog=True)
            return

        filename = filedialog.asksaveasfilename(
            initialdir=export_path,
            title=f"Save Input as {file_format.upper()}",
            defaultextension=f".{file_format}",
            filetypes=[(f"{file_format.upper()} files", f"*.{file_format}"), ("All files", "*.*")]
        )
        if not filename: return

        try:
            if file_format == "txt":
                with open(filename, "w", encoding="utf-8") as f: f.write(input_text)
            elif file_format == "csv":
                with open(filename, "w", encoding="utf-8", newline='') as f:
                    writer = csv.writer(f)
                    for line in input_text.splitlines():
                        writer.writerow([line])
            elif file_format == "pdf": self.export_to_pdf(filename, input_text)
            elif file_format == "docx": self.export_to_docx(filename, input_text)

            self.logger.info(f"Successfully exported input to {filename}")
            if self.dialog_manager:
                self.dialog_manager.show_info("Export Successful", f"Input file saved as {filename}", "success")
            else:
                messagebox.showinfo("Export Successful", f"Input file saved as {filename}")

            if platform.system() == "Windows": 
                os.startfile(filename)
            elif platform.system() == "Darwin": 
                import subprocess
                subprocess.Popen(["open", filename])
            else: 
                import subprocess
                subprocess.Popen(["xdg-open", filename])
        except Exception as e:
            self._handle_error(e, "Exporting input", "Export", 
                               user_message=f"An error occurred while exporting:\n{e}")

    def copy_to_specific_input_tab(self, target_tab_index, dialog):
        """Copies output to a specific input tab and closes the dialog."""
        if hasattr(self, 'diff_frame') and self.diff_frame.winfo_viewable():
            active_output_tab = self.diff_output_tabs[self.diff_output_notebook.index("current")]
            destination_tab = self.diff_input_tabs[target_tab_index]
        else:
            active_output_tab = self.output_tabs[self.output_notebook.index("current")]
            destination_tab = self.input_tabs[target_tab_index]
        
        output_text = active_output_tab.text.get("1.0", tk.END)
        
        destination_tab.text.delete("1.0", tk.END)
        destination_tab.text.insert("1.0", output_text)

        # Save settings after modifying tab content
        self.save_settings()
        self.update_tab_labels()

        self.logger.info(f"Output copied to Input Tab {target_tab_index + 1}.")
        if dialog:
            dialog.destroy()
    
    def send_content_to_input_tab(self, target_tab_index, content):
        """Send custom content to a specific input tab."""
        try:
            if hasattr(self, 'diff_frame') and self.diff_frame.winfo_viewable():
                destination_tab = self.diff_input_tabs[target_tab_index]
            else:
                destination_tab = self.input_tabs[target_tab_index]
            
            destination_tab.text.delete("1.0", tk.END)
            destination_tab.text.insert("1.0", content)
            
            self.logger.info(f"Content sent to Input Tab {target_tab_index + 1}.")
            
            # Apply tool if not manual processing
            if self.tool_var.get() not in self.manual_process_tools:
                self.apply_tool()
            
            # Save settings after modifying tab content
            self.save_settings()
                
        except Exception as e:
            self._handle_error(e, "Sending content to input tab", "UI", show_dialog=False)
            raise
        
        self.after(10, self.update_all_stats)
        self.update_tab_labels()
        
        # Switch to the target tab and apply tool if needed
        if hasattr(self, 'diff_frame') and self.diff_frame.winfo_viewable():
            self.diff_input_notebook.select(target_tab_index)
            if self.tool_var.get() == "Diff Viewer":
                self.run_diff_viewer()
        else:
            self.input_notebook.select(target_tab_index)
            # Don't auto-apply for manual processing tools
            # (first apply_tool call above handles non-manual tools)

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
        self.after(10, self.update_all_stats)

    def on_input_tab_change(self, event):
        """
        Handles logic when the input tab is changed.
        
        Updates visibility states for all input tabs when using visibility-aware updates.
        """
        # Update visibility states if visibility monitor is available
        if hasattr(self, 'visibility_monitor') and self.visibility_monitor:
            active_index = self.input_notebook.index(self.input_notebook.select())
            
            # Update visibility states for all input tabs
            for i in range(len(self.input_tabs)):
                component_id = f"input_tab_{i}"
                tab_id = f"input_notebook_tab_{i}"
                
                # Set active tab as visible and active, others as hidden
                is_active = (i == active_index)
                self.visibility_monitor.set_tab_active(tab_id, is_active)
                
                # Update component visibility state
                new_state = VisibilityState.VISIBLE_ACTIVE if is_active else VisibilityState.HIDDEN
                if hasattr(self, 'statistics_update_manager') and self.statistics_update_manager:
                    self.statistics_update_manager.set_visibility_state(component_id, new_state)
            
            self.logger.debug(f"Input tab changed to {active_index}, updated visibility states")
        
        # Apply tool if needed
        if self.tool_var.get() not in self.manual_process_tools:
            self.apply_tool()
        
        # Request immediate statistics update for the newly active tab
        if hasattr(self, 'statistics_update_manager') and self.statistics_update_manager:
            active_index = self.input_notebook.index(self.input_notebook.select())
            component_id = f"input_tab_{active_index}"
            self.statistics_update_manager.request_update(component_id, UpdatePriority.IMMEDIATE)
        
        self.after(10, self.update_all_stats)

    def on_output_tab_change(self, event):
        """
        Handles logic when the output tab is changed.
        
        Updates visibility states for all output tabs when using visibility-aware updates.
        """
        # Update visibility states if visibility monitor is available
        if hasattr(self, 'visibility_monitor') and self.visibility_monitor:
            active_index = self.output_notebook.index(self.output_notebook.select())
            
            # Update visibility states for all output tabs
            for i in range(len(self.output_tabs)):
                component_id = f"output_tab_{i}"
                tab_id = f"output_notebook_tab_{i}"
                
                # Set active tab as visible and active, others as hidden
                is_active = (i == active_index)
                self.visibility_monitor.set_tab_active(tab_id, is_active)
                
                # Update component visibility state
                new_state = VisibilityState.VISIBLE_ACTIVE if is_active else VisibilityState.HIDDEN
                if hasattr(self, 'statistics_update_manager') and self.statistics_update_manager:
                    self.statistics_update_manager.set_visibility_state(component_id, new_state)
            
            self.logger.debug(f"Output tab changed to {active_index}, updated visibility states")
        
        # Apply tool if output is empty
        active_output_tab = self.output_tabs[self.output_notebook.index(self.output_notebook.select())]
        if not active_output_tab.text.get("1.0", tk.END).strip():
            if self.tool_var.get() not in self.manual_process_tools:
                self.apply_tool()
        
        # Request immediate statistics update for the newly active tab
        if hasattr(self, 'statistics_update_manager') and self.statistics_update_manager:
            active_index = self.output_notebook.index(self.output_notebook.select())
            component_id = f"output_tab_{active_index}"
            self.statistics_update_manager.request_update(component_id, UpdatePriority.IMMEDIATE)
        
        self.after(10, self.update_all_stats)
    
    def _on_window_focus_in(self, event=None):
        """
        Handle window focus in event.
        
        Resumes statistics updates when window regains focus.
        """
        if hasattr(self, 'statistics_update_manager') and self.statistics_update_manager:
            # Resume updates
            self.statistics_update_manager.pause_updates(False)
            
            # Mark user activity
            self.statistics_update_manager.mark_user_activity()
            
            self.logger.debug("Window gained focus - resumed statistics updates")
    
    def _on_window_focus_out(self, event=None):
        """
        Handle window focus out event.
        
        Reduces update frequency when window loses focus.
        """
        if hasattr(self, 'statistics_update_manager') and self.statistics_update_manager:
            # Don't pause completely, just reduce priority
            # The update manager will handle this through visibility states
            self.logger.debug("Window lost focus - reduced update priority")
    
    def _on_window_minimized(self, event=None):
        """
        Handle window minimization event.
        
        Pauses statistics updates when window is minimized.
        """
        if hasattr(self, 'statistics_update_manager') and self.statistics_update_manager:
            # Pause all updates
            self.statistics_update_manager.pause_updates(True)
            
            self.logger.debug("Window minimized - paused statistics updates")
    
    def _on_window_restored(self, event=None):
        """
        Handle window restoration event.
        
        Resumes statistics updates when window is restored from minimization.
        """
        if hasattr(self, 'statistics_update_manager') and self.statistics_update_manager:
            # Resume updates
            self.statistics_update_manager.pause_updates(False)
            
            # Force update of all visible components
            self.statistics_update_manager.force_update_all_visible()
            
            self.logger.debug("Window restored - resumed statistics updates")

    def apply_tool(self):
        """Applies the selected text processing tool to the input text."""
        tool_name = self.tool_var.get()
        
        if tool_name in ["Google AI", "Anthropic AI", "OpenAI", "Cohere AI", "HuggingFace AI", "Groq AI", "OpenRouterAI", "Diff Viewer", "AI Tools"]:
            return

        try:
            active_input_tab = self.input_tabs[self.input_notebook.index(self.input_notebook.select())]
            input_text = active_input_tab.text.get("1.0", tk.END).strip()
            
            if not input_text:
                # Check if we have content in output that might be from Diff Viewer sync
                current_output_tab = self.output_tabs[self.output_notebook.index(self.output_notebook.select())]
                current_output = current_output_tab.text.get("1.0", tk.END).strip()
                
                # Only clear output if it's actually empty
                if not current_output:
                    self.update_output_text("")
                return
            
            # Check if we should use async processing based on settings
            perf_settings = self.settings.get("performance_settings", {})
            async_settings = perf_settings.get("async_processing", {})
            async_enabled = async_settings.get("enabled", True)
            async_threshold = async_settings.get("threshold_kb", 10) * 1024  # Convert KB to bytes
            
            if (ASYNC_PROCESSING_AVAILABLE and self.async_processor and 
                async_enabled and len(input_text) > async_threshold):
                
                self._process_text_async(tool_name, input_text)
            else:
                # Process synchronously for small content
                output_text = self._process_text_with_tool(tool_name, input_text)
                    
                self.update_output_text(output_text)
            
        except Exception as e:
            self._handle_error(
                e, 
                f"Processing text with {tool_name}",
                show_dialog=False  # Show in output instead
            )
            self.update_output_text(f"Error processing text: {e}")
    
    def _process_text_async(self, tool_name: str, input_text: str):
        """Process text asynchronously for large content."""
        try:
            # Cancel any existing async operation for this tab
            tab_index = self.input_notebook.index(self.input_notebook.select())
            existing_task_id = self.pending_async_operations.get(tab_index)
            if existing_task_id:
                self.async_processor.cancel_processing(existing_task_id)
            
            # Create processing context
            context = TextProcessingContext.from_content(
                input_text, 
                tool_name=tool_name,
                callback_id=f"tab_{tab_index}"
            )
            
            # Show processing indicator and cancel button
            self.update_output_text("⏳ Processing large content asynchronously...")
            if hasattr(self, 'cancel_async_button'):
                self.cancel_async_button.pack(side=tk.LEFT, padx=(0, 6))
            
            # Create processor function
            def processor_func(text: str) -> str:
                return self._process_text_with_tool(tool_name, text)
            
            # Create completion callback
            def completion_callback(result: ProcessingResult):
                self.after(0, lambda: self._on_async_processing_complete(result, tab_index))
            
            # Create progress callback
            def progress_callback(current: int, total: int):
                progress_text = f"⏳ Processing chunk {current}/{total}..."
                self.after(0, lambda: self.update_output_text(progress_text))
            
            # Start async processing
            task_id = self.async_processor.process_text_async(
                context=context,
                processor_func=processor_func,
                callback=completion_callback,
                progress_callback=progress_callback if context.processing_mode == ProcessingMode.CHUNKED else None
            )
            
            # Track the operation
            self.pending_async_operations[tab_index] = task_id
            
            self.logger.info(f"Started async processing for {tool_name} "
                           f"({context.size_bytes} bytes, {context.processing_mode.value} mode)")
            
        except Exception as e:
            self._handle_error(e, "Starting async processing", show_dialog=False)
            self.update_output_text(f"Error starting async processing: {e}")
    
    def _on_async_processing_complete(self, result: ProcessingResult, tab_index: int):
        """Handle completion of async text processing."""
        try:
            # Remove from pending operations
            self.pending_async_operations.pop(tab_index, None)
            
            # Hide cancel button if no more pending operations
            if not self.pending_async_operations and hasattr(self, 'cancel_async_button'):
                self.cancel_async_button.pack_forget()
            
            if result.success:
                self.update_output_text(result.result)
                
                # Log performance info
                if result.chunks_processed > 1:
                    self.logger.info(f"Async processing completed: {result.processing_time_ms:.1f}ms, "
                                   f"{result.chunks_processed} chunks")
                else:
                    self.logger.info(f"Async processing completed: {result.processing_time_ms:.1f}ms")
            else:
                error_msg = f"Async processing failed: {result.error_message}"
                self.logger.error(error_msg)
                self.update_output_text(f"Error: {error_msg}")
                
        except Exception as e:
            self._handle_error(e, "Handling async completion", show_dialog=False)
            self.update_output_text(f"Error handling async completion: {e}")
    
    def cancel_async_processing(self, tab_index: Optional[int] = None):
        """Cancel async processing for a specific tab or all tabs."""
        if tab_index is not None:
            task_id = self.pending_async_operations.get(tab_index)
            if task_id and self.async_processor:
                if self.async_processor.cancel_processing(task_id):
                    self.pending_async_operations.pop(tab_index, None)
                    self.update_output_text("Processing cancelled.")
                    self.logger.info(f"Cancelled async processing for tab {tab_index}")
        else:
            # Cancel all pending operations
            if self.async_processor:
                cancelled_count = 0
                for tab_idx, task_id in list(self.pending_async_operations.items()):
                    if self.async_processor.cancel_processing(task_id):
                        cancelled_count += 1
                
                self.pending_async_operations.clear()
                if cancelled_count > 0:
                    self.logger.info(f"Cancelled {cancelled_count} async operations")
    
    def cancel_current_async_processing(self):
        """Cancel async processing for the current active tab."""
        current_tab_index = self.output_notebook.index(self.output_notebook.select())
        self.cancel_async_processing(current_tab_index)
    
    def _process_text_with_tool(self, tool_name, input_text):
        """Processes text with the specified tool using the TextProcessor class."""
        try:
            # Use processing cache if available
            if INTELLIGENT_CACHING_AVAILABLE and self.processing_cache:
                # Get tool settings for cache key
                tool_settings = self.settings.get("tool_settings", {}).get(tool_name, {})
                
                # Define processor function for cache miss
                def processor_func(content):
                    return self._process_text_basic(tool_name, content)
                
                # Process with cache
                result, was_cached = self.processing_cache.process_with_cache(
                    input_text, tool_name, tool_settings, processor_func
                )
                

                
                return result
            else:
                # Fallback to basic processing without cache
                return self._process_text_basic(tool_name, input_text)
                
        except Exception as e:
            self._handle_error(e, f"Processing text with {tool_name}", "Tool", show_dialog=False)
            raise

    
    def _process_text_basic(self, tool_name, input_text):
        """Basic text processing without caching - used as fallback."""
        if tool_name == "Case Tool":
            if CASE_TOOL_MODULE_AVAILABLE and self.case_tool:
                settings = self.settings["tool_settings"]["Case Tool"]
                return self.case_tool.process_text(input_text, settings)
            else:
                return "Case Tool module not available"



        elif tool_name == "Find & Replace Text": 
            if FIND_REPLACE_MODULE_AVAILABLE and self.find_replace_widget:
                return self.find_replace_widget.replace_all()
            else:
                return "Find & Replace module not available"
        elif tool_name == "Extraction Tools":
            # Extraction Tools is a manual tool - processing handled by individual tool widgets
            return "Extraction Tools processing handled by widget interface"
        elif tool_name == "Email Header Analyzer":
            if EMAIL_HEADER_ANALYZER_MODULE_AVAILABLE and self.email_header_analyzer:
                settings = self.settings["tool_settings"]["Email Header Analyzer"]
                return self.email_header_analyzer.process_text(input_text, settings)
            else:
                return "Email Header Analyzer module not available"
        elif tool_name == "URL and Link Extractor":
            if URL_LINK_EXTRACTOR_MODULE_AVAILABLE and self.url_link_extractor:
                settings = self.settings["tool_settings"]["URL and Link Extractor"]
                return self.url_link_extractor.process_text(input_text, settings)
            else:
                return "URL and Link Extractor module not available"
        elif tool_name == "Regex Extractor":
            if REGEX_EXTRACTOR_MODULE_AVAILABLE and self.regex_extractor:
                settings = self.settings["tool_settings"]["Regex Extractor"]
                return self.regex_extractor.process_text(input_text, settings)
            else:
                return "Regex Extractor module not available"
        elif tool_name == "Word Frequency Counter":
            if WORD_FREQUENCY_COUNTER_MODULE_AVAILABLE and self.word_frequency_counter:
                settings = self.settings["tool_settings"].get("Word Frequency Counter", {})
                return self.word_frequency_counter.process_text(input_text, settings)
            else:
                return "Word Frequency Counter module not available"
        elif tool_name == "URL Parser":
            if URL_PARSER_MODULE_AVAILABLE and self.url_parser:
                settings = self.settings["tool_settings"]["URL Parser"]
                return self.url_parser.process_text(input_text, settings)
            else:
                return "URL Parser module not available"
        elif tool_name == "JSON/XML Tool":
            if JSONXML_TOOL_MODULE_AVAILABLE:
                # JSON/XML Tool uses its own processing method, not this basic text processing
                return "JSON/XML Tool processing handled by widget interface"
            else:
                return "JSON/XML Tool module not available"
        elif tool_name == "Cron Tool":
            if CRON_TOOL_MODULE_AVAILABLE:
                # Cron Tool uses its own processing method, not this basic text processing
                return "Cron Tool processing handled by widget interface"
            else:
                return "Cron Tool module not available"
        elif tool_name == "Generator Tools":
            if GENERATOR_TOOLS_MODULE_AVAILABLE:
                # Generator Tools uses its own widget interface for processing
                return "Generator Tools processing handled by widget interface"
            else:
                return "Generator Tools module not available"
        elif tool_name == "Sorter Tools":
            if SORTER_TOOLS_MODULE_AVAILABLE and self.sorter_tools:
                settings = self.settings["tool_settings"].get("Sorter Tools", {})
                return self.sorter_tools.process_text(input_text, settings)
            else:
                return "Sorter Tools module not available"
        elif tool_name == "Folder File Reporter":
            # Folder File Reporter uses its own widget interface
            return "Folder File Reporter processing handled by widget interface"
        elif tool_name == "Translator Tools":
            if TRANSLATOR_TOOLS_MODULE_AVAILABLE and self.translator_tools:
                # Get the active tool type from settings
                tool_type = self.settings["tool_settings"].get("Translator Tools", {}).get("active_tool", "Morse Code Translator")
                settings = self.settings["tool_settings"].get("Translator Tools", {}).get(tool_type, {})
                return self.translator_tools.process_text(input_text, tool_type, settings)
            else:
                return "Translator Tools module not available"
        elif tool_name == "Base64 Encoder/Decoder":
            if BASE64_TOOLS_MODULE_AVAILABLE and self.base64_tools:
                settings = self.settings["tool_settings"].get("Base64 Tools", {})
                return self.base64_tools.process_text(input_text, settings)
            else:
                return "Base64 Tools module not available"
        elif tool_name == "Web Search":
            try:
                from tools.web_search import search
                settings = self.settings["tool_settings"].get("Web Search", {})
                engine = settings.get("engine", "duckduckgo")
                count = settings.get("count", 5)
                query = input_text.strip()
                if not query:
                    return "Please enter a search query in the input panel."
                results = search(query, engine, count)
                if not results:
                    return f"No results found for '{query}'"
                lines = [f"Search Results ({engine}):", "=" * 50, ""]
                for i, r in enumerate(results, 1):
                    lines.append(f"{i}. {r.get('title', 'No title')}")
                    snippet = r.get('snippet', '')[:200]
                    if len(r.get('snippet', '')) > 200:
                        snippet += "..."
                    lines.append(f"   {snippet}")
                    lines.append(f"   URL: {r.get('url', 'N/A')}")
                    lines.append("")
                return "\n".join(lines)
            except ImportError:
                return "Web Search module not available"
            except Exception as e:
                return f"Search error: {str(e)}"
        elif tool_name == "URL Reader":
            try:
                from tools.url_content_reader import URLContentReader
                reader = URLContentReader()
                urls = [u.strip() for u in input_text.strip().splitlines() if u.strip()]
                if not urls:
                    return "Please enter one or more URLs in the input panel (one per line)."
                all_output = []
                for url in urls:
                    try:
                        markdown = reader.fetch_and_convert(url, timeout=30)
                        all_output.append(f"# Content from: {url}\n\n{markdown}\n\n---\n")
                    except Exception as e:
                        all_output.append(f"# Error fetching: {url}\n\nError: {str(e)}\n\n---\n")
                return "\n".join(all_output)
            except ImportError:
                return "URL Content Reader module not available"
            except Exception as e:
                return f"URL Reader error: {str(e)}"
        else: 
            return f"Unknown tool: {tool_name}"

    def update_output_text(self, text):
        """Thread-safe method to update the output text widget."""
        current_tab_index = self.output_notebook.index(self.output_notebook.select())
        active_output_tab = self.output_tabs[current_tab_index]
        
        # Clear any stored filter content since we have new content
        self.output_original_content[current_tab_index] = ""
        
        # Always show the new content directly
        active_output_tab.text.config(state="normal")
        active_output_tab.text.delete("1.0", tk.END)
        active_output_tab.text.insert("1.0", text)
        active_output_tab.text.config(state="disabled")
        
        # If there's an active filter, apply it to the new content
        if hasattr(self, 'output_filter_var') and self.output_filter_var.get():
            self.apply_output_filter()
        
        self.save_settings()
        self.after(10, self.update_all_stats)
        
        if self.tool_var.get() == "Find & Replace Text":
            if FIND_REPLACE_MODULE_AVAILABLE and self.find_replace_widget:
                self.find_replace_widget.highlight_processed_results()
        
        self.update_tab_labels()
    
    # ==================== Streaming Text Methods ====================
    
    def is_streaming_available(self):
        """Check if streaming text handler is available."""
        return STREAMING_TEXT_HANDLER_AVAILABLE and getattr(self, '_streaming_enabled', False)
    
    def get_streaming_manager(self, text_widget=None):
        """
        Get a streaming text manager for a text widget.
        
        Args:
            text_widget: The text widget to stream to. If None, uses current output tab.
            
        Returns:
            StreamingTextManager instance or None if not available
        """
        if not self.is_streaming_available():
            return None
        
        if text_widget is None:
            current_tab_index = self.output_notebook.index(self.output_notebook.select())
            text_widget = self.output_tabs[current_tab_index].text
        
        try:
            return StreamingTextManager(
                text_widget,
                stream_config=self._default_stream_config
            )
        except Exception as e:
            self.logger.error(f"Failed to create streaming manager: {e}")
            return None
    
    def update_output_text_streaming(self, text, chunk_size=100):
        """
        Update output text using streaming display for progressive rendering.
        
        Args:
            text: The text to display
            chunk_size: Size of each chunk to display progressively
        """
        if not self.is_streaming_available() or len(text) < 500:
            # Fall back to regular update for small text or if streaming unavailable
            self.update_output_text(text)
            return
        
        current_tab_index = self.output_notebook.index(self.output_notebook.select())
        active_output_tab = self.output_tabs[current_tab_index]
        text_widget = active_output_tab.text
        
        # Clear stored filter content
        self.output_original_content[current_tab_index] = ""
        
        # Enable widget for editing
        text_widget.config(state="normal")
        text_widget.delete("1.0", tk.END)
        
        try:
            manager = StreamingTextManager(
                text_widget,
                stream_config=self._default_stream_config
            )
            
            def on_complete(metrics):
                self.logger.info(
                    f"Streaming complete: {metrics.total_characters} chars "
                    f"in {metrics.duration:.2f}s"
                )
                # Disable widget after streaming
                self.after(0, lambda: text_widget.config(state="disabled"))
                # Update stats and save
                self.after(10, self.update_all_stats)
                self.after(20, self.save_settings)
                self.after(30, self.update_tab_labels)
            
            manager.start_streaming(
                clear_existing=False,  # Already cleared
                on_complete=on_complete
            )
            
            # Stream text in chunks
            def stream_chunks():
                for i in range(0, len(text), chunk_size):
                    chunk = text[i:i + chunk_size]
                    if not manager.add_stream_chunk(chunk):
                        break
                manager.end_streaming()
            
            # Run in background thread
            import threading
            thread = threading.Thread(target=stream_chunks, daemon=True)
            thread.start()
            
        except Exception as e:
            self.logger.error(f"Streaming failed, falling back to regular update: {e}")
            text_widget.insert("1.0", text)
            text_widget.config(state="disabled")
            self.save_settings()
            self.after(10, self.update_all_stats)
    
    def update_text_incrementally(self, text_widget, new_text, preserve_state=True):
        """
        Update a text widget using incremental diff-based updates.
        
        This is more efficient than full replacement for large texts
        with small changes.
        
        Args:
            text_widget: The text widget to update
            new_text: The new text content
            preserve_state: Whether to preserve cursor and scroll position
            
        Returns:
            Tuple of (insertions, deletions) or None if not available
        """
        if not STREAMING_TEXT_HANDLER_AVAILABLE:
            # Fall back to full replacement
            text_widget.config(state="normal")
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", new_text)
            return None
        
        try:
            updater = IncrementalTextUpdater(text_widget)
            return updater.update_text(
                new_text,
                preserve_cursor=preserve_state,
                preserve_scroll=preserve_state
            )
        except Exception as e:
            self.logger.error(f"Incremental update failed: {e}")
            # Fall back to full replacement
            text_widget.config(state="normal")
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", new_text)
            return None

    def _get_search_pattern(self):
        """Helper to build the regex pattern for Find & Replace."""
        find_str = self.find_text_field.get().strip()
        
        # Determine case sensitivity and base option
        is_case_sensitive = self.match_case_var.get()
        base_option = self.fr_option_var.get()
        

        

        
        # Skip intelligent caching for now as it doesn't support our custom text matching options
        # TODO: Integrate custom text matching with intelligent caching
        # if INTELLIGENT_CACHING_AVAILABLE and self.regex_cache:
        #     try:
        #         flags = 0 if is_case_sensitive else re.IGNORECASE
        #         compiled_pattern = self.regex_cache.get_compiled_pattern(
        #             find_str, flags, self.regex_mode_var.get()
        #         )
        #         return compiled_pattern.pattern
        #     except Exception as e:
        #         self.logger.warning(f"Regex cache failed, falling back to basic: {e}")
        
        # Fallback to basic caching
        cache_key = (find_str, base_option, is_case_sensitive, self.regex_mode_var.get())
        if cache_key in self._regex_cache:
            return self._regex_cache[cache_key]
        
        if self.regex_mode_var.get():
            pattern = find_str
        else:
            search_term = re.escape(find_str)
            if base_option == "whole_words": 
                search_term = r'\b' + search_term + r'\b'
            elif base_option == "match_prefix": 
                search_term = r'\b' + search_term
            elif base_option == "match_suffix": 
                search_term = search_term + r'\b'
            pattern = search_term
        
        self._regex_cache[cache_key] = pattern
        

        
        return pattern

    def preview_find_replace(self):
        """Highlights matches in input and output without replacing using progressive search."""
        self.on_tool_setting_change()
        active_input_tab = self.input_tabs[self.input_notebook.index(self.input_notebook.select())]
        active_output_tab = self.output_tabs[self.output_notebook.index(self.output_notebook.select())]

        # Reset replacement count and skip tracking when starting new search
        self.replaced_count = 0
        self.replaced_count_label.config(text="Replaced matches: 0")
        self.skipped_matches = set()  # Reset skipped matches tracking
        self.all_matches_processed = False
        self.loop_start_position = None

        # Clear existing highlights
        if PROGRESSIVE_SEARCH_AVAILABLE and self.search_highlighter:
            self.search_highlighter.clear_highlights(active_input_tab.text, "yellow_highlight")
            self.search_highlighter.clear_highlights(active_output_tab.text, "pink_highlight")
        else:
            active_input_tab.text.tag_remove("yellow_highlight", "1.0", tk.END)
            active_output_tab.text.tag_remove("pink_highlight", "1.0", tk.END)
        
        active_output_tab.text.config(state="normal")
        input_content = active_input_tab.text.get("1.0", tk.END)
        active_output_tab.text.delete("1.0", tk.END)
        active_output_tab.text.insert("1.0", input_content)

        find_str = self.find_text_field.get()
        if not find_str:
            active_output_tab.text.config(state="disabled")
            self.match_count_label.config(text="Found matches: 0")
            return
        
        # Use progressive search if available
        if PROGRESSIVE_SEARCH_AVAILABLE and self.search_highlighter and self.find_replace_processor:
            self._preview_with_progressive_search(active_input_tab, active_output_tab, find_str)
        else:
            self._preview_with_basic_search(active_input_tab, active_output_tab, find_str)
        
        active_output_tab.text.config(state="disabled")
        self.after(10, self.update_all_stats)








    def load_diff_viewer_content(self):
        """Copies content from the main input/output tabs to the diff viewer tabs."""
        if DIFF_VIEWER_MODULE_AVAILABLE and hasattr(self, 'diff_viewer_widget'):
            try:
                # Use the new modular diff viewer
                input_contents = []
                output_contents = []
                
                for i in range(AppConfig.TAB_COUNT):
                    input_content = self.input_tabs[i].text.get("1.0", tk.END)
                    input_contents.append(input_content)
                    
                    output_content = self.output_tabs[i].text.get("1.0", tk.END)
                    output_contents.append(output_content)
                
                self.logger.info(f"Loading content to diff viewer - {len(input_contents)} input tabs, {len(output_contents)} output tabs")
                self.diff_viewer_widget.load_content(input_contents, output_contents)
                
                # Sync notebook selections
                try:
                    self.diff_viewer_widget.input_notebook.select(self.input_notebook.index("current"))
                    self.diff_viewer_widget.output_notebook.select(self.output_notebook.index("current"))
                except (tk.TclError, AttributeError):
                    # Fallback to first tab if sync fails
                    try:
                        self.diff_viewer_widget.input_notebook.select(0)
                        self.diff_viewer_widget.output_notebook.select(0)
                    except:
                        pass
                
                self.logger.info("Content loaded to diff viewer successfully")
            except Exception as e:
                self.logger.error(f"Error loading content to diff viewer: {e}")
        
        self.update_tab_labels()

    def sync_diff_viewer_to_main_tabs(self):
        """Copies content from the diff viewer tabs back to the main tabs."""
        if DIFF_VIEWER_MODULE_AVAILABLE and hasattr(self, 'diff_viewer_widget'):
            try:
                # Use the new modular diff viewer
                input_contents, output_contents = self.diff_viewer_widget.sync_content_back()
                
                self.logger.info(f"Syncing diff viewer content back to main tabs - {len(input_contents)} input tabs, {len(output_contents)} output tabs")
                
                # Debug: Log what content we're syncing
                for i, content in enumerate(input_contents):
                    if content.strip():
                        self.logger.info(f"Input tab {i+1}: '{content[:50]}...' ({len(content)} chars)")
                for i, content in enumerate(output_contents):
                    if content.strip():
                        self.logger.info(f"Output tab {i+1}: '{content[:50]}...' ({len(content)} chars)")
                
                for i in range(min(len(input_contents), AppConfig.TAB_COUNT)):
                    self.input_tabs[i].text.delete("1.0", tk.END)
                    self.input_tabs[i].text.insert("1.0", input_contents[i])
                    
                    self.output_tabs[i].text.config(state="normal")
                    self.output_tabs[i].text.delete("1.0", tk.END)
                    self.output_tabs[i].text.insert("1.0", output_contents[i])
                    self.output_tabs[i].text.config(state="disabled")
                
                self.logger.info("Diff viewer content synced successfully")
                
                # Verify what's actually in the main tabs after sync
                main_input_contents = [tab.text.get("1.0", tk.END).strip() for tab in self.input_tabs]
                main_output_contents = [tab.text.get("1.0", tk.END).strip() for tab in self.output_tabs]
                non_empty_main_inputs = sum(1 for content in main_input_contents if content)
                non_empty_main_outputs = sum(1 for content in main_output_contents if content)
                self.logger.info(f"After sync - Main tabs have {non_empty_main_inputs} non-empty input tabs, {non_empty_main_outputs} non-empty output tabs")
                
            except Exception as e:
                self.logger.error(f"Error syncing diff viewer content: {e}")
                import traceback
                self.logger.error(f"Traceback: {traceback.format_exc()}")
        
        self.update_tab_labels()
        self.save_settings()



    def on_diff_viewer_content_changed(self):
        """Callback for when diff viewer content changes."""
        # This ensures that changes in diff viewer are reflected in main tabs
        # when the user switches tools or closes the app
        pass

    def run_diff_viewer(self):
        """Compares the active tabs within the Diff Viewer and displays the diff."""
        if DIFF_VIEWER_MODULE_AVAILABLE and hasattr(self, 'diff_viewer_widget'):
            # Use the new modular diff viewer
            option = self.settings.get("tool_settings", {}).get("Diff Viewer", {}).get("option", "ignore_case")
            self.diff_viewer_widget.run_comparison(option)
        else:
            self.logger.warning("Diff Viewer module not available")





    def export_file(self, file_format):
        """Exports the output text to the specified file format."""
        active_output_tab = self.output_tabs[self.output_notebook.index(self.output_notebook.select())]
        output_text = active_output_tab.text.get("1.0", tk.END)
        export_path = self.export_path_var.get()
        if not os.path.isdir(export_path):
            self._handle_warning("Invalid export path specified in settings", "Export Output", "File", show_dialog=True)
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
            elif file_format == "csv":
                with open(filename, "w", encoding="utf-8", newline='') as f:
                    writer = csv.writer(f)
                    for line in output_text.splitlines():
                        writer.writerow([line])
            elif file_format == "pdf": self.export_to_pdf(filename, output_text)
            elif file_format == "docx": self.export_to_docx(filename, output_text)

            self.logger.info(f"Successfully exported to {filename}")
            if self.dialog_manager:
                self.dialog_manager.show_info("Export Successful", f"File saved as {filename}", "success")
            else:
                messagebox.showinfo("Export Successful", f"File saved as {filename}")

            if platform.system() == "Windows": 
                os.startfile(filename)
            elif platform.system() == "Darwin": 
                import subprocess
                subprocess.Popen(["open", filename])
            else: 
                import subprocess
                subprocess.Popen(["xdg-open", filename])
        except Exception as e:
            self._handle_error(e, f"Exporting to {filename}", "File Operations")

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
        
    # Settings Backup and Recovery Methods
    
    def create_manual_backup(self):
        """Create a manual backup of current settings."""
        try:
            if not hasattr(self, 'db_settings_manager') or not self.db_settings_manager:
                self._handle_warning("Database settings manager not available", "Creating backup", "Database", show_dialog=True)
                return
            
            self.logger.info("Creating manual backup from File menu...")
            
            # Check current settings before backup
            current_settings = self.db_settings_manager.load_settings()
            tool_count = len(current_settings.get("tool_settings", {}))
            self.logger.info(f"Backing up {tool_count} tool configurations")
            
            success = self.db_settings_manager.create_backup("manual", "Manual backup created from File menu")
            
            if success:
                # Get backup statistics for user feedback
                try:
                    backup_stats = self.db_settings_manager.get_backup_statistics()
                    total_backups = backup_stats.get('total_backups', 'unknown')
                    
                    success_msg = f"Manual backup created successfully!\n\nTool configurations: {tool_count}\nTotal backups: {total_backups}"
                    self.show_success(success_msg)
                    self.logger.info(f"Manual backup created - {tool_count} tools backed up")
                except Exception as stats_error:
                    self.logger.warning(f"Failed to get backup statistics: {stats_error}")
                    self.show_success("Manual backup created successfully!")
            else:
                error_msg = "Backup operation returned failure status"
                self.logger.error(error_msg)
                
                # Try to get more specific error information
                if not hasattr(self.db_settings_manager, 'backup_recovery_manager') or not self.db_settings_manager.backup_recovery_manager:
                    error_msg += "\n\nBackup recovery manager is not available."
                
                self._handle_warning(f"Failed to create manual backup:\n{error_msg}", "Creating backup", "Database", show_dialog=True)
                
        except Exception as e:
            self._handle_error(e, "Creating manual backup")
    
    def show_backup_history(self):
        """Show backup history in a dialog window."""
        try:
            if not hasattr(self, 'db_settings_manager') or not self.db_settings_manager:
                self._handle_warning("Database settings manager not available", "Showing backup history", "Database", show_dialog=True)
                return
            
            # Create backup history window
            history_window = tk.Toplevel(self)
            history_window.title("Backup History")
            history_window.geometry("800x600")
            history_window.transient(self)
            history_window.grab_set()
            
            # Create main frame
            main_frame = ttk.Frame(history_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            title_label = ttk.Label(main_frame, text="Settings Backup History", font=("Helvetica", 14, "bold"))
            title_label.pack(pady=(0, 10))
            
            # Get backup statistics
            stats = self.db_settings_manager.get_backup_statistics()
            
            # Add statistics info (moved above table)
            stats_frame = ttk.LabelFrame(main_frame, text="Backup Statistics", padding="5")
            stats_frame.pack(fill=tk.X, pady=(0, 10))
            
            stats_text = f"Total Backups: {stats.get('total_backups', 0)} | "
            stats_text += f"Total Size: {stats.get('total_size_mb', 0):.2f} MB | "
            stats_text += f"Recent (7 days): {stats.get('recent_backups_7d', 0)}"
            
            ttk.Label(stats_frame, text=stats_text).pack()
            
            # Button frame (moved above table)
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Create treeview for backup list
            columns = ("Timestamp", "Type", "Size", "Description")
            tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
            
            # Configure columns
            tree.heading("Timestamp", text="Timestamp")
            tree.heading("Type", text="Type")
            tree.heading("Size", text="Size (MB)")
            tree.heading("Description", text="Description")
            
            tree.column("Timestamp", width=150)
            tree.column("Type", width=100)
            tree.column("Size", width=80)
            tree.column("Description", width=300)
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            # Pack treeview and scrollbar
            tree_frame = ttk.Frame(main_frame)
            tree_frame.pack(fill=tk.BOTH, expand=True)
            
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Get backup history and populate tree
            if hasattr(self.db_settings_manager, 'backup_recovery_manager') and self.db_settings_manager.backup_recovery_manager:
                backup_history = self.db_settings_manager.backup_recovery_manager.get_backup_history()
                
                for backup in reversed(backup_history):  # Show most recent first
                    timestamp_str = backup.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    size_mb = round(backup.size_bytes / (1024 * 1024), 2)
                    description = backup.description or "No description"
                    
                    tree.insert("", tk.END, values=(
                        timestamp_str,
                        backup.backup_type.value,
                        size_mb,
                        description
                    ))
            
            # Restore button (define function before button creation)
            def restore_selected():
                selection = tree.selection()
                if not selection:
                    self.show_warning("Please select a backup to restore")
                    return
                
                item = tree.item(selection[0])
                timestamp_str = item['values'][0]
                backup_type = item['values'][1]
                
                # Find the backup info
                backup_history = self.db_settings_manager.backup_recovery_manager.get_backup_history()
                selected_backup = None
                
                for backup in backup_history:
                    if (backup.timestamp.strftime("%Y-%m-%d %H:%M:%S") == timestamp_str and 
                        backup.backup_type.value == backup_type):
                        selected_backup = backup
                        break
                
                if selected_backup:
                    history_window.destroy()
                    self.restore_from_backup_file(selected_backup.filepath)
                else:
                    self._handle_warning("Could not find selected backup", "Restore backup", "Database", show_dialog=True)
            
            # Add buttons to the button frame (now above table)
            ttk.Button(button_frame, text="Restore Selected", command=restore_selected).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="Refresh", command=lambda: self.show_backup_history()).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="Close", command=history_window.destroy).pack(side=tk.RIGHT)
            
        except Exception as e:
            self._handle_error(e, "Backup History", "Settings")
    
    def export_settings_to_json(self):
        """Export current settings to a JSON file."""
        try:
            if not hasattr(self, 'db_settings_manager') or not self.db_settings_manager:
                self._handle_warning("Database settings manager not available", "Export settings", "Database", show_dialog=True)
                return
            
            # Ask user for file location
            filename = filedialog.asksaveasfilename(
                title="Export Settings to JSON",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile="settings_export.json"
            )
            
            if filename:
                self.logger.info(f"Starting export to: {filename}")
                
                # Check current settings before export
                current_settings = self.db_settings_manager.load_settings()
                tool_count = len(current_settings.get("tool_settings", {}))
                self.logger.info(f"Exporting {tool_count} tool configurations")
                
                success = self.db_settings_manager.export_settings_to_file(filename, "json")
                
                if success:
                    # Verify export file was created and has content
                    if os.path.exists(filename):
                        file_size = os.path.getsize(filename)
                        self.logger.info(f"Export successful - file size: {file_size} bytes")
                        
                        # Quick validation of exported content
                        try:
                            with open(filename, 'r') as f:
                                exported_data = json.load(f)
                            exported_tools = len(exported_data.get("tool_settings", {}))
                            
                            success_msg = f"Settings exported successfully!\n\nFile: {filename}\nSize: {file_size:,} bytes\nTools: {exported_tools} configurations"
                            self.show_success(success_msg)
                            self.logger.info(f"Export validation passed - {exported_tools} tools exported")
                        except Exception as validation_error:
                            self.logger.warning(f"Export file validation failed: {validation_error}")
                            self.show_success(f"Settings exported to:\n{filename}\n\nNote: File validation failed, but export completed.")
                    else:
                        self._handle_warning(f"Export reported success but file not found: {filename}", "Export settings", "File", show_dialog=True)
                else:
                    error_msg = "Export operation returned failure status"
                    if hasattr(self.db_settings_manager, 'backup_recovery_manager'):
                        error_msg += "\n\nCheck that the backup recovery manager is properly initialized."
                    self._handle_warning(error_msg, "Export settings", "Database", show_dialog=True)
                    
        except Exception as e:
            self._handle_error(e, "Exporting settings")
    
    def import_settings_from_json(self):
        """Import settings from a JSON file."""
        try:
            if not hasattr(self, 'db_settings_manager') or not self.db_settings_manager:
                self._handle_warning("Database settings manager not available", "Import settings", "Database", show_dialog=True)
                return
            
            # Ask user for file location
            filename = filedialog.askopenfilename(
                title="Import Settings from JSON",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                self.logger.info(f"Starting import from: {filename}")
                
                # Validate import file first
                if not os.path.exists(filename):
                    self._handle_warning(f"Import file not found: {filename}", "Import settings", "File", show_dialog=True)
                    return
                
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        import_data = json.load(f)
                    
                    file_size = os.path.getsize(filename)
                    import_tools = len(import_data.get("tool_settings", {}))
                    self.logger.info(f"Import file validation passed - {file_size} bytes, {import_tools} tools")
                    
                except Exception as validation_error:
                    self._handle_warning(f"Import file is not valid JSON: {validation_error}", "Import settings", "File", show_dialog=True)
                    return
                
                # Confirm import with details
                result = messagebox.askyesno(
                    "Confirm Import",
                    f"Import settings from:\n{os.path.basename(filename)}\n\n"
                    f"File size: {file_size:,} bytes\n"
                    f"Tool configurations: {import_tools}\n\n"
                    "This will replace your current settings.\n"
                    "A backup will be created automatically.\n\n"
                    "Do you want to continue?",
                    icon="warning"
                )
                
                if result:
                    # Create backup before import
                    self.logger.info("Creating pre-import backup...")
                    backup_success = self.db_settings_manager.create_backup("manual", "Pre-import backup")
                    if backup_success:
                        self.logger.info("Pre-import backup created successfully")
                    else:
                        self.logger.warning("Failed to create pre-import backup")
                        
                        # Ask if user wants to continue without backup
                        continue_result = messagebox.askyesno(
                            "Backup Failed",
                            "Failed to create backup before import.\n\n"
                            "Do you want to continue anyway?\n"
                            "(This is not recommended)",
                            icon="warning"
                        )
                        if not continue_result:
                            self.logger.info("Import cancelled by user due to backup failure")
                            return
                    
                    # Import settings
                    self.logger.info("Starting settings import...")
                    success = self.db_settings_manager.import_settings_from_file(filename)
                    
                    if success:
                        # Verify import by checking current settings
                        try:
                            current_settings = self.db_settings_manager.load_settings()
                            current_tools = len(current_settings.get("tool_settings", {}))
                            
                            # Reload settings into UI to apply imported tab content
                            self.settings = current_settings
                            self.load_last_state()
                            self.update_tab_labels()
                            self.logger.info("Imported settings loaded into UI")
                            
                            success_msg = f"Settings imported successfully!\n\nFrom: {os.path.basename(filename)}\nTool configurations: {current_tools}\n\nTab content has been refreshed."
                            self.show_success(success_msg)
                            self.logger.info(f"Import successful - {current_tools} tools now in database")
                        except Exception as verify_error:
                            self.logger.warning(f"Import verification failed: {verify_error}")
                            self.show_success(f"Settings imported from:\n{filename}\n\nNote: Import verification failed, but import completed.\n\nPlease restart the application.")
                    else:
                        error_msg = "Import operation returned failure status"
                        self.logger.error(error_msg)
                        
                        # Try to get more specific error information
                        if hasattr(self.db_settings_manager, 'backup_recovery_manager'):
                            error_msg += "\n\nPossible causes:\n- File format is incompatible\n- Settings validation failed\n- Database write error"
                        
                        self._handle_warning(f"Failed to import settings:\n{error_msg}", "Import settings", "Database", show_dialog=True)
                        
        except Exception as e:
            self._handle_error(e, "Importing settings")
    
    def restore_from_backup_dialog(self):
        """Show dialog to select and restore from a backup file."""
        try:
            if not hasattr(self, 'db_settings_manager') or not self.db_settings_manager:
                self._handle_warning("Database settings manager not available", "Restore from backup", "Database", show_dialog=True)
                return
            
            # Ask user for backup file
            filename = filedialog.askopenfilename(
                title="Select Backup File to Restore",
                filetypes=[
                    ("Database backups", "*.db"),
                    ("Compressed backups", "*.gz"),
                    ("All files", "*.*")
                ]
            )
            
            if filename:
                self.restore_from_backup_file(filename)
                
        except Exception as e:
            self._handle_error(e, "Restore dialog", "Settings")
    
    def restore_from_backup_file(self, filename):
        """Restore settings from a specific backup file."""
        try:
            # Confirm restore
            result = messagebox.askyesno(
                "Confirm Restore",
                f"Restoring from backup will replace your current settings.\n\n"
                f"Backup file: {os.path.basename(filename)}\n\n"
                f"A backup of current settings will be created before restore.\n\n"
                f"Do you want to continue?",
                icon="warning"
            )
            
            if result:
                # Create backup of current state
                backup_success = self.db_settings_manager.create_backup("manual", "Pre-restore backup")
                if not backup_success:
                    self.logger.warning("Failed to create pre-restore backup")
                
                # Restore from backup
                success = self.db_settings_manager.restore_from_backup(filename)
                
                if success:
                    self.show_success(f"Settings restored successfully from backup.\n\nPlease restart the application for all changes to take effect.")
                    self.logger.info(f"Settings restored from backup: {filename}")
                else:
                    self._handle_warning("Failed to restore from backup", "Restore from backup", "Database", show_dialog=True)
                    
        except Exception as e:
            self._handle_error(e, "Restoring from backup", "Settings")
    
    def repair_database_dialog(self):
        """Show dialog to repair database corruption."""
        try:
            if not hasattr(self, 'db_settings_manager') or not self.db_settings_manager:
                self._handle_warning("Database settings manager not available", "Repair database", "Database", show_dialog=True)
                return
            
            # Confirm repair
            result = messagebox.askyesno(
                "Confirm Database Repair",
                "Database repair will attempt to fix corruption issues.\n\n"
                "An emergency backup will be created before repair.\n\n"
                "This operation may take a few moments.\n\n"
                "Do you want to continue?",
                icon="question"
            )
            
            if result:
                # Show progress dialog
                progress_window = tk.Toplevel(self)
                progress_window.title("Repairing Database")
                progress_window.geometry("400x150")
                progress_window.transient(self)
                progress_window.grab_set()
                
                progress_frame = ttk.Frame(progress_window, padding="20")
                progress_frame.pack(fill=tk.BOTH, expand=True)
                
                ttk.Label(progress_frame, text="Repairing database...").pack(pady=(0, 10))
                progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
                progress_bar.pack(fill=tk.X, pady=(0, 10))
                progress_bar.start()
                
                status_label = ttk.Label(progress_frame, text="Creating emergency backup...")
                status_label.pack()
                
                def repair_worker():
                    try:
                        # Update status
                        self.after(0, lambda: status_label.config(text="Analyzing database..."))
                        
                        # Perform repair
                        success = self.db_settings_manager.repair_database()
                        
                        # Close progress window
                        self.after(0, progress_window.destroy)
                        
                        if success:
                            self.after(0, lambda: self.show_success("Database repair completed successfully."))
                            self.logger.info("Database repair completed successfully")
                        else:
                            self.after(0, lambda: self.show_error("Database repair failed. Check logs for details."))
                            
                    except Exception as e:
                        self.after(0, progress_window.destroy)
                        self.after(0, lambda: self.show_error(f"Database repair error: {e}"))
                        self.logger.error(f"Database repair error: {e}")
                
                # Run repair in background thread
                threading.Thread(target=repair_worker, daemon=True).start()
                
        except Exception as e:
            self._handle_error(e, "Database repair dialog", "Database")
    
    def validate_settings_integrity_dialog(self):
        """Show dialog to validate settings integrity."""
        try:
            if not hasattr(self, 'db_settings_manager') or not self.db_settings_manager:
                self._handle_warning("Database settings manager not available", "Validate settings", "Database", show_dialog=True)
                return
            
            # Ask if user wants to apply automatic fixes
            apply_fixes = messagebox.askyesno(
                "Settings Integrity Validation",
                "Do you want to automatically apply fixes for issues that can be repaired?\n\n"
                "Choose 'Yes' to apply fixes automatically, or 'No' to only validate without changes.",
                icon="question"
            )
            
            # Show progress dialog
            progress_window = tk.Toplevel(self)
            progress_window.title("Validating Settings")
            progress_window.geometry("400x150")
            progress_window.transient(self)
            progress_window.grab_set()
            
            progress_frame = ttk.Frame(progress_window, padding="20")
            progress_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(progress_frame, text="Validating settings integrity...").pack(pady=(0, 10))
            progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
            progress_bar.pack(fill=tk.X, pady=(0, 10))
            progress_bar.start()
            
            status_label = ttk.Label(progress_frame, text="Analyzing settings...")
            status_label.pack()
            
            def validation_worker():
                try:
                    # Perform validation
                    report = self.db_settings_manager.validate_settings_integrity(apply_fixes)
                    
                    # Close progress window
                    self.after(0, progress_window.destroy)
                    
                    # Show results
                    self.after(0, lambda: self.show_validation_results(report, apply_fixes))
                    
                except Exception as e:
                    self.after(0, progress_window.destroy)
                    self.after(0, lambda: self.show_error(f"Validation error: {e}"))
                    self.logger.error(f"Settings validation error: {e}")
            
            # Run validation in background thread
            threading.Thread(target=validation_worker, daemon=True).start()
            
        except Exception as e:
            self._handle_error(e, "Settings validation dialog", "Database")
    
    def show_validation_results(self, report, fixes_applied):
        """Show validation results in a dialog."""
        try:
            # Create results window
            results_window = tk.Toplevel(self)
            results_window.title("Settings Validation Results")
            results_window.geometry("700x500")
            results_window.transient(self)
            results_window.grab_set()
            
            # Create main frame
            main_frame = ttk.Frame(results_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            title_text = "Settings Validation Results"
            if fixes_applied:
                title_text += " (with Auto-fixes Applied)"
            
            title_label = ttk.Label(main_frame, text=title_text, font=("Helvetica", 14, "bold"))
            title_label.pack(pady=(0, 10))
            
            # Summary frame
            summary_frame = ttk.LabelFrame(main_frame, text="Summary", padding="10")
            summary_frame.pack(fill=tk.X, pady=(0, 10))
            
            total_issues = report.get('total_issues', 0)
            if total_issues == 0:
                summary_text = "✅ No issues found - settings are valid!"
                summary_color = "green"
            else:
                summary_text = f"Found {total_issues} issues:\n"
                issues_by_severity = report.get('issues_by_severity', {})
                for severity, count in issues_by_severity.items():
                    if count > 0:
                        summary_text += f"  • {severity.title()}: {count}\n"
                
                if fixes_applied:
                    auto_fixable = report.get('auto_fixable_issues', 0)
                    summary_text += f"\n🔧 {auto_fixable} issues were automatically fixed"
                
                summary_color = "red" if issues_by_severity.get('critical', 0) > 0 else "orange"
            
            summary_label = ttk.Label(summary_frame, text=summary_text.strip())
            summary_label.pack(anchor=tk.W)
            
            # Details frame with scrollable text
            if total_issues > 0:
                details_frame = ttk.LabelFrame(main_frame, text="Issue Details", padding="5")
                details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
                
                details_text = scrolledtext.ScrolledText(details_frame, height=15, wrap=tk.WORD)
                details_text.pack(fill=tk.BOTH, expand=True)
                
                # Add all issues by severity
                issues_by_severity = report.get('issues_by_severity', {})
                
                # Display critical issues first
                critical_issues = report.get('critical_issues', [])
                if critical_issues:
                    details_text.insert(tk.END, "🚨 CRITICAL ISSUES:\n")
                    for issue in critical_issues:
                        details_text.insert(tk.END, f"  • {issue['message']}\n")
                        details_text.insert(tk.END, f"    Location: {issue['location']}\n")
                        if issue.get('auto_fixable'):
                            details_text.insert(tk.END, "    Status: Auto-fixable\n")
                        details_text.insert(tk.END, "\n")
                
                # Display other severity levels if we have the full issue list
                # Check if the report contains a full issues list
                all_issues = report.get('all_issues', [])
                if all_issues:
                    # Group issues by severity
                    severity_groups = {
                        'high': [],
                        'medium': [],
                        'low': []
                    }
                    
                    for issue in all_issues:
                        severity = issue.get('severity', 'medium')
                        if severity != 'critical':  # Critical already handled above
                            if severity in severity_groups:
                                severity_groups[severity].append(issue)
                    
                    # Display each severity group
                    severity_icons = {
                        'high': '🔴',
                        'medium': '🟡', 
                        'low': '🟢'
                    }
                    
                    for severity in ['high', 'medium', 'low']:
                        issues = severity_groups[severity]
                        if issues:
                            icon = severity_icons[severity]
                            details_text.insert(tk.END, f"\n{icon} {severity.upper()} ISSUES:\n")
                            for issue in issues:
                                details_text.insert(tk.END, f"  • {issue.get('message', 'Unknown issue')}\n")
                                if issue.get('location'):
                                    details_text.insert(tk.END, f"    Location: {issue['location']}\n")
                                if issue.get('auto_fixable'):
                                    details_text.insert(tk.END, "    Status: Auto-fixable\n")
                                if issue.get('suggestion'):
                                    details_text.insert(tk.END, f"    Suggestion: {issue['suggestion']}\n")
                                details_text.insert(tk.END, "\n")
                
                elif issues_by_severity:
                    # Fallback: show summary by severity if we don't have detailed issues
                    details_text.insert(tk.END, "\n📊 ISSUES BY SEVERITY:\n")
                    for severity, count in issues_by_severity.items():
                        if count > 0 and severity != 'critical':  # Critical already shown
                            details_text.insert(tk.END, f"  • {severity.title()}: {count} issues\n")
                    
                    details_text.insert(tk.END, "\nNote: Run validation again to see detailed issue descriptions.\n")
                
                # Add recommendations
                recommendations = report.get('recommendations', [])
                if recommendations:
                    details_text.insert(tk.END, "\n💡 RECOMMENDATIONS:\n")
                    for rec in recommendations:
                        details_text.insert(tk.END, f"  • {rec}\n")
                
                details_text.config(state=tk.DISABLED)
            
            # Button frame
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X)
            
            ttk.Button(button_frame, text="Close", command=results_window.destroy).pack(side=tk.RIGHT)
            
            if total_issues > 0 and not fixes_applied:
                def apply_fixes():
                    results_window.destroy()
                    self.validate_settings_integrity_dialog()
                
                ttk.Button(button_frame, text="Apply Auto-fixes", command=apply_fixes).pack(side=tk.RIGHT, padx=(0, 5))
            
        except Exception as e:
            self.logger.error(f"Error showing validation results: {e}")
            self.show_error(f"Error showing validation results: {e}")
    
    def cleanup_old_backups_dialog(self):
        """Show dialog to cleanup old backups."""
        try:
            if not hasattr(self, 'db_settings_manager') or not self.db_settings_manager:
                self.show_error("Database settings manager not available")
                return
            
            # Get current backup statistics
            stats = self.db_settings_manager.get_backup_statistics()
            total_backups = stats.get('total_backups', 0)
            total_size_mb = stats.get('total_size_mb', 0)
            
            if total_backups == 0:
                self.show_info("No backups found to cleanup.")
                return
            
            # Confirm cleanup
            result = messagebox.askyesno(
                "Cleanup Old Backups",
                f"Current backup statistics:\n"
                f"  • Total backups: {total_backups}\n"
                f"  • Total size: {total_size_mb:.2f} MB\n\n"
                f"This will remove old backups based on the retention policy.\n"
                f"Recent backups will be preserved.\n\n"
                f"Do you want to continue?",
                icon="question"
            )
            
            if result:
                cleaned_count = self.db_settings_manager.cleanup_old_backups()
                
                if cleaned_count > 0:
                    self.show_success(f"Cleanup completed successfully.\n\n{cleaned_count} old backups were removed.")
                    self.logger.info(f"Cleaned up {cleaned_count} old backups")
                else:
                    self.show_info("No old backups needed cleanup.")
                    
        except Exception as e:
            self.logger.error(f"Error in cleanup dialog: {e}")
            self.show_error(f"Error in cleanup dialog: {e}")
    
    def open_retention_settings(self):
        """Open retention settings configuration dialog."""
        try:
            if not hasattr(self, 'db_settings_manager') or not self.db_settings_manager:
                self.show_error("Database settings manager not available")
                return
            
            # Create retention settings window
            retention_window = tk.Toplevel(self)
            retention_window.title("Backup Retention Settings")
            retention_window.transient(self)
            
            # Hide window initially to prevent flickering
            retention_window.withdraw()
            
            # Set initial size and allow resizing
            retention_window.geometry("550x650")
            retention_window.minsize(500, 600)
            retention_window.resizable(True, True)
            
            # Create scrollable main frame
            canvas = tk.Canvas(retention_window)
            scrollbar = ttk.Scrollbar(retention_window, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Pack canvas and scrollbar
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Create main frame inside scrollable frame
            main_frame = ttk.Frame(scrollable_frame, padding="15")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Bind mousewheel to canvas for scrolling
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            def _bind_to_mousewheel(event):
                canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
            def _unbind_from_mousewheel(event):
                canvas.unbind_all("<MouseWheel>")
            
            canvas.bind('<Enter>', _bind_to_mousewheel)
            canvas.bind('<Leave>', _unbind_from_mousewheel)
            
            # Title
            title_label = ttk.Label(main_frame, text="Backup Retention Policy", font=("Helvetica", 14, "bold"))
            title_label.pack(pady=(0, 15))
            
            # Get current settings
            backup_manager = self.db_settings_manager.backup_recovery_manager
            if not backup_manager:
                self.show_error("Backup manager not available")
                retention_window.destroy()
                return
            
            current_max_backups = backup_manager.max_backups
            current_auto_interval = backup_manager.auto_backup_interval
            current_compression = backup_manager.enable_compression
            
            # Settings frame
            settings_frame = ttk.LabelFrame(main_frame, text="Retention Policy Settings", padding="10")
            settings_frame.pack(fill=tk.X, pady=(0, 15))
            
            # Max backups setting
            max_backups_frame = ttk.Frame(settings_frame)
            max_backups_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(max_backups_frame, text="Maximum number of backups to keep:").pack(side=tk.LEFT)
            max_backups_var = tk.IntVar(value=current_max_backups)
            max_backups_spinbox = ttk.Spinbox(
                max_backups_frame, 
                from_=5, 
                to=200, 
                width=10,
                textvariable=max_backups_var
            )
            max_backups_spinbox.pack(side=tk.RIGHT)
            
            # Auto backup interval setting
            interval_frame = ttk.Frame(settings_frame)
            interval_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(interval_frame, text="Automatic backup interval (minutes):").pack(side=tk.LEFT)
            interval_var = tk.IntVar(value=current_auto_interval // 60)  # Convert seconds to minutes
            interval_spinbox = ttk.Spinbox(
                interval_frame,
                from_=5,
                to=1440,  # 24 hours
                width=10,
                textvariable=interval_var
            )
            interval_spinbox.pack(side=tk.RIGHT)
            
            # Compression setting
            compression_frame = ttk.Frame(settings_frame)
            compression_frame.pack(fill=tk.X, pady=(0, 10))
            
            compression_var = tk.BooleanVar(value=current_compression)
            compression_check = ttk.Checkbutton(
                compression_frame,
                text="Enable backup compression (saves disk space)",
                variable=compression_var
            )
            compression_check.pack(side=tk.LEFT)
            
            # Current statistics frame
            stats_frame = ttk.LabelFrame(main_frame, text="Current Backup Statistics", padding="10")
            stats_frame.pack(fill=tk.X, pady=(0, 15))
            
            # Get and display current statistics
            stats = self.db_settings_manager.get_backup_statistics()
            total_backups = stats.get('total_backups', 0)
            total_size_mb = stats.get('total_size_mb', 0)
            recent_backups = stats.get('recent_backups_7d', 0)
            
            stats_text = f"Total backups: {total_backups}\n"
            stats_text += f"Total size: {total_size_mb:.2f} MB\n"
            stats_text += f"Recent backups (7 days): {recent_backups}\n"
            stats_text += f"Backup directory: {backup_manager.backup_dir}"
            
            stats_label = ttk.Label(stats_frame, text=stats_text, justify=tk.LEFT)
            stats_label.pack(anchor=tk.W)
            
            # Retention policy explanation
            explanation_frame = ttk.LabelFrame(main_frame, text="How Retention Policy Works", padding="10")
            explanation_frame.pack(fill=tk.X, pady=(0, 15))
            
            explanation_text = (
                "• Backups are automatically cleaned up when the maximum count is exceeded\n"
                "• The most recent backups are always preserved\n"
                "• Manual backups and migration backups are treated equally\n"
                "• Compression reduces file size but may slightly increase backup time\n"
                "• Shorter intervals provide better protection but use more disk space"
            )
            
            explanation_label = ttk.Label(explanation_frame, text=explanation_text, justify=tk.LEFT)
            explanation_label.pack(anchor=tk.W)
            
            # Button frame
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(10, 0))
            
            def apply_settings():
                try:
                    # Get new values
                    new_max_backups = max_backups_var.get()
                    new_interval_minutes = interval_var.get()
                    new_compression = compression_var.get()
                    
                    # Validate values
                    if new_max_backups < 5:
                        self.show_warning("Maximum backups must be at least 5")
                        return
                    
                    if new_interval_minutes < 5:
                        self.show_warning("Backup interval must be at least 5 minutes")
                        return
                    
                    # Apply settings using the backup manager's method
                    success = backup_manager.update_retention_settings(
                        max_backups=new_max_backups,
                        auto_backup_interval=new_interval_minutes * 60,  # Convert to seconds
                        enable_compression=new_compression
                    )
                    
                    if success:
                        self.show_success("Retention settings updated and saved successfully!")
                        self.logger.info(f"Updated retention settings: max_backups={new_max_backups}, interval={new_interval_minutes}min, compression={new_compression}")
                        retention_window.destroy()
                    else:
                        self.show_error("Failed to update retention settings")
                    
                except Exception as e:
                    self.logger.error(f"Error applying retention settings: {e}")
                    self.show_error(f"Error applying settings: {e}")
            
            def reset_defaults():
                max_backups_var.set(50)
                interval_var.set(60)  # 1 hour
                compression_var.set(True)
            
            # Buttons
            ttk.Button(button_frame, text="Apply", command=apply_settings).pack(side=tk.RIGHT, padx=(5, 0))
            ttk.Button(button_frame, text="Cancel", command=retention_window.destroy).pack(side=tk.RIGHT)
            ttk.Button(button_frame, text="Reset to Defaults", command=reset_defaults).pack(side=tk.LEFT)
            
            # Update window size after all content is added
            def adjust_window_size():
                retention_window.update_idletasks()
                
                # Get the required size for all content
                required_width = scrollable_frame.winfo_reqwidth() + 50  # Add padding
                required_height = scrollable_frame.winfo_reqheight() + 50  # Add padding
                
                # Get screen dimensions
                screen_width = retention_window.winfo_screenwidth()
                screen_height = retention_window.winfo_screenheight()
                
                # Limit to reasonable maximum sizes (80% of screen)
                max_width = min(required_width, int(screen_width * 0.8))
                max_height = min(required_height, int(screen_height * 0.8))
                
                # Ensure minimum sizes
                final_width = max(max_width, 550)
                final_height = max(max_height, 600)
                
                # Center the window on screen
                x = (screen_width - final_width) // 2
                y = (screen_height - final_height) // 2
                
                retention_window.geometry(f"{final_width}x{final_height}+{x}+{y}")
                
                # If content is larger than window, enable scrolling
                if required_height > final_height:
                    scrollbar.pack(side="right", fill="y")
                else:
                    scrollbar.pack_forget()
                
                # Show the window after positioning (prevents flickering)
                retention_window.deiconify()
                retention_window.grab_set()
            
            # Schedule size adjustment after window is fully rendered
            retention_window.after(100, adjust_window_size)
            
        except Exception as e:
            self.logger.error(f"Error opening retention settings: {e}")
            self.show_error(f"Error opening retention settings: {e}")
    
    def open_mcp_security_settings(self):
        """Open MCP Security settings configuration dialog."""
        try:
            # Create MCP security settings window
            security_window = tk.Toplevel(self)
            security_window.title("MCP Security Settings")
            security_window.transient(self)
            security_window.geometry("550x600")
            security_window.minsize(500, 550)
            security_window.resizable(True, True)
            security_window.grab_set()
            
            # Load current settings
            mcp_settings = self.settings.get("mcp_security", {
                "enabled": False,
                "rate_limit_per_minute": 30,
                "token_limit_per_hour": 100000,
                "cost_limit_per_hour": 1.00,
                "locked": False,
                "lock_reason": ""
            })
            
            # Create main frame with padding
            main_frame = ttk.Frame(security_window, padding="15")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # === HEADER ===
            header_frame = ttk.Frame(main_frame)
            header_frame.pack(fill=tk.X, pady=(0, 15))
            
            ttk.Label(header_frame, text="🛡️ MCP Security Circuit Breaker", 
                     font=("TkDefaultFont", 12, "bold")).pack(anchor=tk.W)
            
            header_text = ("Protects against runaway API costs by automatically locking\n"
                          "protected MCP tools when usage thresholds are exceeded.")
            ttk.Label(header_frame, text=header_text, foreground="gray").pack(anchor=tk.W, pady=(5, 0))
            
            # === STATUS DISPLAY ===
            status_frame = ttk.LabelFrame(main_frame, text="Current Status")
            status_frame.pack(fill=tk.X, pady=(0, 15))
            
            is_locked = mcp_settings.get("locked", False)
            lock_reason = mcp_settings.get("lock_reason", "")
            
            status_inner = ttk.Frame(status_frame)
            status_inner.pack(fill=tk.X, padx=10, pady=10)
            
            if is_locked:
                status_text = f"🔒 LOCKED: {lock_reason}"
                status_color = "red"
            else:
                status_text = "🔓 Unlocked - Protected tools are available"
                status_color = "green"
            
            status_label = ttk.Label(status_inner, text=status_text, foreground=status_color)
            status_label.pack(anchor=tk.W)
            
            # Unlock button (only if locked)
            if is_locked:
                unlock_frame = ttk.Frame(status_inner)
                unlock_frame.pack(fill=tk.X, pady=(10, 0))
                
                ttk.Label(unlock_frame, text="Password:").pack(side=tk.LEFT)
                unlock_password = ttk.Entry(unlock_frame, show="*", width=20)
                unlock_password.pack(side=tk.LEFT, padx=(5, 10))
                
                def do_unlock():
                    from core.mcp_security_manager import get_security_manager
                    security = get_security_manager()
                    if security.unlock(unlock_password.get()):
                        mcp_settings["locked"] = False
                        mcp_settings["lock_reason"] = ""
                        self.settings["mcp_security"] = mcp_settings
                        self.save_settings()
                        self.show_success("MCP tools unlocked successfully!")
                        security_window.destroy()
                        self.open_mcp_security_settings()  # Reopen to show updated status
                    else:
                        self.show_error("Incorrect password")
                
                ttk.Button(unlock_frame, text="Unlock", command=do_unlock).pack(side=tk.LEFT)
            
            # === ENABLE TOGGLE ===
            enable_frame = ttk.LabelFrame(main_frame, text="Security Status")
            enable_frame.pack(fill=tk.X, pady=(0, 15))
            
            enable_inner = ttk.Frame(enable_frame)
            enable_inner.pack(fill=tk.X, padx=10, pady=10)
            
            enabled_var = tk.BooleanVar(value=mcp_settings.get("enabled", False))
            
            enable_check = ttk.Checkbutton(enable_inner, text="Enable MCP Security Monitoring", 
                                           variable=enabled_var)
            enable_check.pack(anchor=tk.W)
            
            ttk.Label(enable_inner, text="When enabled, protected tools are monitored and auto-locked if thresholds exceeded.",
                     foreground="gray", font=("TkDefaultFont", 8)).pack(anchor=tk.W, padx=(20, 0))
            
            ttk.Label(enable_inner, text="Protected: pomera_ai_tools, pomera_web_search, pomera_read_url",
                     foreground="blue", font=("TkDefaultFont", 8)).pack(anchor=tk.W, padx=(20, 0), pady=(2, 0))
            
            # === THRESHOLD SETTINGS ===
            threshold_frame = ttk.LabelFrame(main_frame, text="Threshold Settings")
            threshold_frame.pack(fill=tk.X, pady=(0, 15))
            
            threshold_inner = ttk.Frame(threshold_frame)
            threshold_inner.pack(fill=tk.X, padx=10, pady=10)
            
            # Rate limit
            rate_frame = ttk.Frame(threshold_inner)
            rate_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(rate_frame, text="Rate Limit (calls/minute):").pack(side=tk.LEFT)
            rate_var = tk.IntVar(value=mcp_settings.get("rate_limit_per_minute", 30))
            rate_spinbox = ttk.Spinbox(rate_frame, from_=5, to=100, textvariable=rate_var, width=8)
            rate_spinbox.pack(side=tk.LEFT, padx=(10, 0))
            ttk.Label(rate_frame, text="(Lock if exceeded)", foreground="gray").pack(side=tk.LEFT, padx=(10, 0))
            
            # Token limit
            token_frame = ttk.Frame(threshold_inner)
            token_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(token_frame, text="Token Limit (tokens/hour):").pack(side=tk.LEFT)
            token_var = tk.IntVar(value=mcp_settings.get("token_limit_per_hour", 100000))
            token_entry = ttk.Entry(token_frame, textvariable=token_var, width=10)
            token_entry.pack(side=tk.LEFT, padx=(10, 0))
            ttk.Label(token_frame, text="(Estimated via tiktoken)", foreground="gray").pack(side=tk.LEFT, padx=(10, 0))
            
            # Cost limit
            cost_frame = ttk.Frame(threshold_inner)
            cost_frame.pack(fill=tk.X, pady=(0, 0))
            
            ttk.Label(cost_frame, text="Cost Limit ($/hour):").pack(side=tk.LEFT)
            cost_var = tk.DoubleVar(value=mcp_settings.get("cost_limit_per_hour", 1.00))
            cost_spinbox = ttk.Spinbox(cost_frame, from_=0.10, to=100.0, increment=0.10, textvariable=cost_var, width=8)
            cost_spinbox.pack(side=tk.LEFT, padx=(10, 0))
            ttk.Label(cost_frame, text="(Estimated @ $0.003/1K tokens)", foreground="gray").pack(side=tk.LEFT, padx=(10, 0))
            
            # === PASSWORD SETTINGS ===
            password_frame = ttk.LabelFrame(main_frame, text="Unlock Password")
            password_frame.pack(fill=tk.X, pady=(0, 15))
            
            password_inner = ttk.Frame(password_frame)
            password_inner.pack(fill=tk.X, padx=10, pady=10)
            
            has_password = bool(mcp_settings.get("password_hash", ""))
            
            if has_password:
                ttk.Label(password_inner, text="✅ Password is set", foreground="green").pack(anchor=tk.W)
            else:
                ttk.Label(password_inner, text="⚠️ No password set - set one to enable unlock", foreground="orange").pack(anchor=tk.W)
            
            new_pass_frame = ttk.Frame(password_inner)
            new_pass_frame.pack(fill=tk.X, pady=(10, 0))
            
            ttk.Label(new_pass_frame, text="New Password:").pack(side=tk.LEFT)
            new_password_entry = ttk.Entry(new_pass_frame, show="*", width=20)
            new_password_entry.pack(side=tk.LEFT, padx=(10, 0))
            
            confirm_pass_frame = ttk.Frame(password_inner)
            confirm_pass_frame.pack(fill=tk.X, pady=(5, 0))
            
            ttk.Label(confirm_pass_frame, text="Confirm Password:").pack(side=tk.LEFT)
            confirm_password_entry = ttk.Entry(confirm_pass_frame, show="*", width=20)
            confirm_password_entry.pack(side=tk.LEFT, padx=(10, 0))
            
            # === BUTTONS ===
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(10, 0))
            
            def apply_settings():
                try:
                    # Validate password if entered
                    new_pass = new_password_entry.get()
                    confirm_pass = confirm_password_entry.get()
                    
                    if new_pass or confirm_pass:
                        if new_pass != confirm_pass:
                            self.show_error("Passwords do not match")
                            return
                        if len(new_pass) < 4:
                            self.show_error("Password must be at least 4 characters")
                            return
                    
                    # Update settings
                    mcp_settings["enabled"] = enabled_var.get()
                    mcp_settings["rate_limit_per_minute"] = rate_var.get()
                    mcp_settings["token_limit_per_hour"] = token_var.get()
                    mcp_settings["cost_limit_per_hour"] = cost_var.get()
                    
                    self.settings["mcp_security"] = mcp_settings
                    self.save_settings()
                    
                    # Update security manager
                    from core.mcp_security_manager import get_security_manager
                    security = get_security_manager()
                    security._config.enabled = enabled_var.get()
                    security._config.rate_limit_per_minute = rate_var.get()
                    security._config.token_limit_per_hour = token_var.get()
                    security._config.cost_limit_per_hour_usd = cost_var.get()
                    
                    # Set password if provided
                    if new_pass:
                        security.set_password(new_pass)
                        mcp_settings["password_hash"] = security._config.password_hash
                        self.settings["mcp_security"] = mcp_settings
                        self.save_settings()
                    
                    self.show_success("MCP Security settings saved!")
                    security_window.destroy()
                    
                except Exception as e:
                    self.logger.error(f"Error applying MCP security settings: {e}")
                    self.show_error(f"Error applying settings: {e}")
            
            def manual_lock():
                from core.mcp_security_manager import get_security_manager
                security = get_security_manager()
                security._config.enabled = True
                security.manual_lock("Manual lock via UI")
                mcp_settings["locked"] = True
                mcp_settings["lock_reason"] = "Manual lock via UI"
                mcp_settings["enabled"] = True
                self.settings["mcp_security"] = mcp_settings
                self.save_settings()
                self.show_success("MCP tools locked manually!")
                security_window.destroy()
                self.open_mcp_security_settings()
            
            ttk.Button(button_frame, text="Apply", command=apply_settings).pack(side=tk.RIGHT, padx=(5, 0))
            ttk.Button(button_frame, text="Cancel", command=security_window.destroy).pack(side=tk.RIGHT)
            if not is_locked:
                ttk.Button(button_frame, text="🔒 Lock Now", command=manual_lock).pack(side=tk.LEFT)
            
        except Exception as e:
            self.logger.error(f"Error opening MCP security settings: {e}")
            self.show_error(f"Error opening MCP security settings: {e}")
    
    # Helper methods for dialogs
    
    def show_success(self, message):
        """Show success message dialog."""
        if hasattr(self, 'dialog_manager') and self.dialog_manager:
            self.dialog_manager.show_info("Success", message)
        else:
            messagebox.showinfo("Success", message)
    
    def show_error(self, message):
        """Show error message dialog."""
        if hasattr(self, 'dialog_manager') and self.dialog_manager:
            self.dialog_manager.show_error("Error", message)
        else:
            messagebox.showerror("Error", message)
    
    def show_warning(self, message):
        """Show warning message dialog."""
        if hasattr(self, 'dialog_manager') and self.dialog_manager:
            self.dialog_manager.show_warning("Warning", message)
        else:
            messagebox.showwarning("Warning", message)
    
    def show_info(self, message):
        """Show info message dialog."""
        if hasattr(self, 'dialog_manager') and self.dialog_manager:
            self.dialog_manager.show_info("Information", message)
        else:
            messagebox.showinfo("Information", message)

    def on_closing(self):
        """Handles cleanup when the application window is closed."""
        # Sync diff viewer content if it's currently active
        if (self.tool_var.get() == "Diff Viewer" and 
            DIFF_VIEWER_MODULE_AVAILABLE and hasattr(self, 'diff_viewer_widget')):
            self.sync_diff_viewer_to_main_tabs()
        
        self.save_settings()
        self.clear_regex_cache()
        
        # Cancel pending debounced operations
        self.cancel_pending_operations()
        
        # Cancel and cleanup progressive search operations
        if PROGRESSIVE_SEARCH_AVAILABLE:
            if self.operation_manager:
                self.operation_manager.cancel_all_operations()
                self.operation_manager.shutdown()
            if self.search_highlighter:
                self.search_highlighter.shutdown()
            if self.find_replace_processor:
                self.find_replace_processor.shutdown()
            self.logger.info("Progressive search components shut down")
        
        # Cancel and cleanup async operations
        if ASYNC_PROCESSING_AVAILABLE and self.async_processor:
            self.cancel_async_processing()  # Cancel all pending operations
            self.async_processor.shutdown(wait=False, timeout=2.0)
            self.logger.info("Async processor shut down")
        
        # Shutdown Task Scheduler
        if TASK_SCHEDULER_AVAILABLE and self.task_scheduler:
            shutdown_task_scheduler(wait=False)
            self.logger.info("Task Scheduler shut down")
        
        # Shutdown Widget Cache
        if WIDGET_CACHE_AVAILABLE and hasattr(self, 'widget_cache') and self.widget_cache:
            shutdown_widget_cache()
            self.logger.info("Widget Cache shut down")
        
        # Advanced memory management cleanup not needed (modules not available)
        
        # Cleanup intelligent caching
        if INTELLIGENT_CACHING_AVAILABLE:
            if self.smart_stats_calculator:
                self.smart_stats_calculator.clear_cache()
            if self.regex_cache:
                self.regex_cache.clear_cache()
            if self.content_cache:
                self.content_cache.clear_cache()
            # Note: processing_cache doesn't have clear_cache method, it uses content_cache
            self.logger.info("Intelligent caching cleared")
        
        # Cleanup Event Consolidator
        if EVENT_CONSOLIDATOR_AVAILABLE and hasattr(self, 'event_consolidator') and self.event_consolidator:
            # Unregister all widgets and cancel pending updates
            for i in range(AppConfig.TAB_COUNT):
                widget_id = f"input_tab_{i}"
                self.event_consolidator.unregister_text_widget(widget_id)
            self.logger.info("Event Consolidator cleaned up")
        
        # Cleanup Database Settings Manager
        if DATABASE_SETTINGS_AVAILABLE and hasattr(self, 'db_settings_manager') and self.db_settings_manager:
            try:
                self.db_settings_manager.close()
                self.logger.info("Database settings manager closed")
            except Exception as e:
                self.logger.error(f"Error closing database settings manager: {e}")
        
        if self.audio_stream:
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

def run_mcp_server():
    """Run the MCP server (called when --mcp-server flag is passed)."""
    import argparse
    import logging
    
    # Configure logging to stderr (stdout is used for MCP communication)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )
    logger = logging.getLogger(__name__)
    
    parser = argparse.ArgumentParser(
        description="Pomera MCP Server - Expose text tools via Model Context Protocol"
    )
    parser.add_argument("--mcp-server", action="store_true", help="Run as MCP server")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--list-tools", action="store_true", help="List available tools and exit")
    
    args, _ = parser.parse_known_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Import MCP modules
    try:
        from core.mcp.tool_registry import ToolRegistry
        from core.mcp.server_stdio import StdioMCPServer
    except ImportError as e:
        logger.error(f"Failed to import MCP modules: {e}")
        sys.exit(1)
    
    # Create tool registry
    try:
        registry = ToolRegistry()
        logger.info(f"Loaded {len(registry)} tools")
    except Exception as e:
        logger.error(f"Failed to create tool registry: {e}")
        sys.exit(1)
    
    # List tools mode
    if args.list_tools:
        print("Available Pomera MCP Tools:")
        print("-" * 60)
        for tool in registry.list_tools():
            print(f"\n{tool.name}")
            print(f"  {tool.description}")
            if "properties" in tool.inputSchema:
                print("  Parameters:")
                for prop_name, prop_def in tool.inputSchema["properties"].items():
                    prop_type = prop_def.get("type", "any")
                    prop_desc = prop_def.get("description", "")
                    required = prop_name in tool.inputSchema.get("required", [])
                    req_marker = "*" if required else ""
                    print(f"    - {prop_name}{req_marker} ({prop_type}): {prop_desc}")
        return
    
    # Create and run server
    server = StdioMCPServer(
        tool_registry=registry,
        server_name="pomera-mcp-server",
        server_version="0.1.0"
    )
    
    logger.info("Starting Pomera MCP Server...")
    logger.info(f"Available tools: {', '.join(registry.get_tool_names())}")
    
    try:
        server.run_sync()
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.exception(f"Server error: {e}")
        sys.exit(1)
    
    logger.info("Server shutdown complete")


if __name__ == "__main__":
    # Check for --mcp-server flag first
    if "--mcp-server" in sys.argv:
        run_mcp_server()
    else:
        # Normal GUI mode
        if not PYAUDIO_AVAILABLE:
            print("Warning: 'PyAudio' or 'numpy' not found. Morse audio playback will be disabled.")
            print("Please install them using: pip install pyaudio numpy")
        app = PromeraAIApp()
        app.mainloop()