# Configuration & Setup

> Dialog configuration system, application settings, themes, performance tuning, and deployment options.

---

## Dialog Configuration System

### Overview

The Pomera AI Commander includes a sophisticated dialog management system that allows users to customize which notification and confirmation dialogs are displayed throughout the application. This system provides a better user experience by reducing interruptions while maintaining important system communications.

### Dialog Categories

#### Success Notifications (`success`)
- **Purpose**: Inform users of successful operations and completions
- **Examples**: "File saved successfully", "Settings applied", "Export complete"
- **Default**: Enabled
- **When Disabled**: Messages are logged but no dialog is shown
- **Use Cases**: Reduce interruptions for routine operations

#### Warning Messages (`warning`)  
- **Purpose**: Alert users to potential issues or invalid inputs
- **Examples**: "No data specified", "Invalid input detected", "Feature unavailable"
- **Default**: Enabled
- **When Disabled**: Warnings are logged but no dialog is shown
- **Use Cases**: Streamline workflows while maintaining error visibility in logs

#### Confirmation Dialogs (`confirmation`)
- **Purpose**: Request user confirmation for destructive or important actions
- **Examples**: "Clear all tabs?", "Delete entry?", "Reset settings?"
- **Default**: Enabled
- **When Disabled**: Default action is taken automatically (usually "Yes")
- **Use Cases**: Speed up workflows for experienced users

#### Error Messages (`error`)
- **Purpose**: Display critical error information that requires user attention
- **Examples**: "File not found", "Network error", "Invalid configuration"
- **Default**: Always enabled (cannot be disabled)
- **Safety Feature**: Ensures users are always informed of critical issues

### Configuration Interface

#### Accessing Dialog Settings
1. Open the main application settings
2. Click "Dialog Settings" button
3. Configure categories using checkboxes
4. Changes apply immediately without restart

#### Settings Window Features
- **Categorized Controls**: Grouped checkboxes for each dialog type
- **Descriptions**: Clear explanations of what each category controls
- **Examples**: Sample messages to help users understand categories
- **Reset Option**: "Reset to Defaults" button to restore original settings
- **Real-time Application**: Changes take effect immediately

#### Settings Persistence
- Dialog preferences are saved in `settings.json`
- Settings persist across application sessions
- Backward compatibility with existing installations
- Automatic migration for new dialog categories

### Technical Implementation

#### DialogManager Class
The core `DialogManager` class provides:
- Centralized dialog decision making
- Settings-driven dialog suppression
- Logging fallback when dialogs are suppressed
- Real-time settings updates
- Extensible category registration system

#### Integration Points
- **Main Application**: All core dialogs use DialogManager
- **Tool Modules**: Consistent dialog behavior across tools
- **Settings System**: Integrated with existing settings persistence
- **Logging System**: Fallback logging when dialogs are suppressed

#### Error Handling
- **Graceful Degradation**: System continues if dialog display fails
- **Settings Corruption**: Invalid settings handled with safe defaults
- **Missing Categories**: Unknown categories default to enabled
- **Display Failures**: Automatic fallback to logging

### Usage Examples

#### Power User Configuration
```
✓ Success Notifications: Disabled
✓ Warning Messages: Enabled  
✓ Confirmation Dialogs: Disabled
✓ Error Messages: Enabled (locked)
```
**Result**: Minimal interruptions, only warnings and errors shown

#### Safety-First Configuration
```
✓ Success Notifications: Enabled
✓ Warning Messages: Enabled
✓ Confirmation Dialogs: Enabled  
✓ Error Messages: Enabled (locked)
```
**Result**: All dialogs shown for maximum safety and feedback

#### Balanced Configuration
```
✓ Success Notifications: Disabled
✓ Warning Messages: Enabled
✓ Confirmation Dialogs: Enabled
✓ Error Messages: Enabled (locked)
```
**Result**: Important dialogs shown, routine confirmations suppressed

### Best Practices

#### Recommended Settings
- **New Users**: Keep all dialogs enabled initially
- **Experienced Users**: Disable success notifications for efficiency
- **Batch Operations**: Temporarily disable confirmations for bulk tasks
- **Development/Testing**: Enable all dialogs for comprehensive feedback

#### Safety Considerations
- Error dialogs cannot be disabled for safety reasons
- Confirmation dialogs should be carefully considered before disabling
- Warning dialogs provide valuable feedback for data validation
- Settings can always be reset to defaults if needed

---



## Configuration & Setup

### Application Dependencies and Requirements

#### System Requirements

##### Operating System Support
- **Windows**: Windows 10 or later (primary platform)
- **macOS**: macOS 10.14 or later (compatible)
- **Linux**: Ubuntu 18.04+ or equivalent (compatible)

##### Python Requirements
- **Python Version**: Python 3.7 or later
- **Recommended**: Python 3.9+ for optimal performance
- **Architecture**: 64-bit recommended for large text processing

#### Required Dependencies

##### Core Dependencies (Always Required)
```python
# Standard Library Modules (included with Python)
import tkinter as tk          # GUI framework
import re                     # Regular expressions
import json                   # JSON handling
import os                     # Operating system interface
import logging                # Logging functionality
import base64                 # Base64 encoding/decoding
import csv                    # CSV file handling
import io                     # Input/output operations
import platform               # Platform identification
import requests               # HTTP requests
import threading              # Threading support
import time                   # Time operations
import string                 # String operations
import random                 # Random number generation
import webbrowser             # Web browser control
from collections import Counter  # Counting utilities
from email.utils import parsedate_to_datetime  # Email parsing
import urllib.parse           # URL parsing
import hashlib               # Hash functions
```

##### Document Processing Dependencies
```python
# Required for document export features
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from docx import Document

# Installation:
pip install reportlab python-docx
```

#### Optional Dependencies

##### AI Tools Support
```python
# For AI Tools functionality
pip install requests  # HTTP requests for AI APIs

# For HuggingFace AI support
pip install huggingface_hub

# For Vertex AI support (service account authentication)
pip install google-auth google-auth-oauthlib google-auth-httplib2
```

##### Audio Support (Morse Code)
```python
# For Morse code audio playback
pip install pyaudio numpy

# Note: PyAudio may require additional system dependencies
# Windows: Usually works with pip install
# macOS: May need: brew install portaudio
# Linux: May need: sudo apt-get install portaudio19-dev
```

##### Performance Optimization
```python
# For enhanced performance monitoring
pip install psutil

# For advanced memory management
pip install memory_profiler
```

#### Installation Guide

##### Basic Installation
1. **Install Python**: Download Python 3.9+ from python.org
2. **Download Application**: Get Pomera AI Commander files
3. **Install Core Dependencies**:
   ```bash
   pip install reportlab python-docx requests
   ```
4. **Run Application**:
   ```bash
   python pomera_ai.py
   ```

##### Full Installation (All Features)
```bash
# Install all optional dependencies
pip install reportlab python-docx requests huggingface_hub pyaudio numpy psutil memory_profiler
```

##### Troubleshooting Installation

**PyAudio Installation Issues:**
- **Windows**: Use `pip install pyaudio` or download wheel from unofficial binaries
- **macOS**: Install portaudio first: `brew install portaudio`
- **Linux**: Install development headers: `sudo apt-get install portaudio19-dev python3-dev`

**HuggingFace Hub Issues:**
- Ensure internet connection for model downloads
- Some models may require authentication tokens
- Check HuggingFace documentation for specific model requirements

### Settings and Configuration Management

#### Settings File Structure

The application uses `settings.json` for persistent configuration storage:

```json
{
  "export_path": "/path/to/exports",
  "debug_level": "INFO",
  "selected_tool": "Case Tool",
  "input_tabs": ["", "", "", ""],
  "output_tabs": ["", "", "", ""],
  "active_input_tab": 0,
  "active_output_tab": 0,
  "tool_settings": {
    "Case Tool": {
      "mode": "Sentence",
      "exclusions": "a\nan\nand\nas\nat\nbut\nby\nen\nfor\nif\nin\nis\nof\non\nor\nthe\nto\nvia\nvs"
    },
    "Find & Replace Text": {
      "find": "",
      "replace": "",
      "mode": "Text",
      "option": "ignore_case",
      "find_history": [],
      "replace_history": []
    },
    "AI Tools": {
      "Google AI": {
        "API_KEY": "your_api_key_here",
        "MODEL": "gemini-1.5-pro-latest",
        "MODELS_LIST": ["gemini-1.5-pro-latest", "gemini-1.5-flash-latest"],
        "system_prompt": "You are a helpful assistant.",
        "temperature": 0.7,
        "maxOutputTokens": 8192
      }
    }
  },
  "performance_settings": {
    "enable_async_processing": true,
    "enable_caching": true,
    "cache_size_mb": 100,
    "async_threshold_kb": 10
  }
}
```

#### Settings Operations and Management

The application provides comprehensive settings management capabilities through the File menu's "Settings Backup & Recovery" submenu. These operations allow users to backup, restore, export, import, and maintain their application settings with full data integrity and recovery options.

##### Settings Backup Operations

**Create Manual Backup**
- **Purpose**: Create an immediate backup of current settings
- **Location**: File → Settings Backup & Recovery → Create Manual Backup
- **Functionality**: 
  - Creates compressed backup file with timestamp
  - Stores in application's backup directory
  - Includes all tool settings, preferences, and configuration
  - Automatic backup description with creation timestamp
- **File Format**: Compressed database backup (.db.gz)
- **Use Cases**: Before major changes, testing new configurations, milestone preservation

**View Backup History**
- **Purpose**: Browse and manage all created backups
- **Location**: File → Settings Backup & Recovery → View Backup History
- **Features**:
  - **Sortable Table**: Timestamp, Type, Size, Description columns
  - **Backup Statistics**: Total backups, total size, recent backups count
  - **Action Buttons**: Restore Selected, Refresh, Close
  - **Backup Types**: Manual, Automatic, Migration, Pre-import
  - **Size Information**: File sizes displayed in MB with precision
- **Functionality**:
  - Select any backup from history to restore
  - View backup metadata and creation details
  - Refresh list to show latest backups
  - Automatic backup cleanup based on retention policy

##### Settings Import/Export Operations

**Export Settings to JSON**
- **Purpose**: Export current settings to a portable JSON file
- **Location**: File → Settings Backup & Recovery → Export Settings to JSON...
- **Features**:
  - **File Dialog**: Choose export location and filename
  - **JSON Format**: Human-readable, editable format
  - **Complete Export**: All settings, tool configurations, and preferences
  - **Cross-Platform**: JSON files work across different operating systems
- **Use Cases**: 
  - Sharing configurations between installations
  - Creating configuration templates
  - Manual settings editing
  - Cross-platform migration
- **File Format**: Pretty-printed JSON with 2-space indentation

**Import Settings from JSON**
- **Purpose**: Import settings from a previously exported JSON file
- **Location**: File → Settings Backup & Recovery → Import Settings from JSON...
- **Safety Features**:
  - **Automatic Backup**: Creates pre-import backup automatically
  - **Confirmation Dialog**: User confirmation before replacing settings
  - **Validation**: Validates JSON structure before import
  - **Error Handling**: Clear error messages for invalid files
- **Process**:
  1. Select JSON file to import
  2. Confirm import operation (with warning about replacement)
  3. Automatic backup creation
  4. Settings validation and import
  5. Application restart prompt if needed
- **Recovery**: Pre-import backup allows rollback if needed

##### Settings Recovery Operations

**Restore from Backup**
- **Purpose**: Restore settings from any available backup
- **Location**: File → Settings Backup & Recovery → Restore from Backup...
- **Features**:
  - **Backup Selection**: Choose from available backup files
  - **Metadata Display**: Show backup creation time and description
  - **Safety Confirmation**: Confirm before overwriting current settings
  - **Automatic Restart**: Application restart after successful restore
- **Process**:
  1. Browse and select backup file
  2. View backup information and confirm restore
  3. Current settings backed up automatically
  4. Backup restored and validated
  5. Application restart to apply changes

**Repair Database**
- **Purpose**: Repair corrupted settings database
- **Location**: File → Settings Backup & Recovery → Repair Database
- **Features**:
  - **Corruption Detection**: Automatic detection of database issues
  - **Repair Process**: Attempts to repair database structure
  - **Backup Creation**: Creates backup before repair attempt
  - **Fallback Options**: JSON fallback if repair fails
- **Use Cases**: Database corruption, file system errors, unexpected shutdowns

##### Settings Validation and Maintenance

**Validate Settings Integrity**
- **Purpose**: Check settings for corruption, missing values, and inconsistencies
- **Location**: File → Settings Backup & Recovery → Validate Settings Integrity
- **Features**:
  - **Comprehensive Validation**: Checks all settings categories
  - **Issue Detection**: Identifies missing, invalid, or corrupted settings
  - **Auto-Fix Options**: Automatic repair of common issues
  - **Detailed Report**: Shows validation results with issue descriptions
- **Validation Categories**:
  - Tool settings completeness and validity
  - Performance settings ranges and types
  - File paths and directory existence
  - API key format validation
  - Database integrity checks

**Cleanup Old Backups**
- **Purpose**: Remove old backup files based on retention policy
- **Location**: File → Settings Backup & Recovery → Cleanup Old Backups
- **Features**:
  - **Retention Policy**: Configurable backup retention rules
  - **Size Management**: Remove oldest backups when size limits exceeded
  - **Selective Cleanup**: Preserve important backups (manual, migration)
  - **Confirmation Dialog**: Show files to be deleted before cleanup
- **Configuration**: Managed through Retention Settings dialog

##### Backup Retention Settings

**Retention Policy Configuration**
- **Purpose**: Configure automatic backup cleanup and retention rules
- **Location**: Settings → Retention Settings...
- **Features**:
  - **Maximum Backups**: Set maximum number of backups to keep (default: 50)
  - **Automatic Interval**: Configure automatic backup frequency (default: 1 hour)
  - **Compression**: Enable/disable backup compression to save disk space
  - **Statistics Display**: Current backup statistics and disk usage
- **Policy Explanation**: Built-in help explaining how retention policy works
- **Dynamic Sizing**: Window automatically adjusts to show all content

#### Settings Menu Configuration

The Settings menu provides access to various application configuration dialogs and system settings. These settings control the overall behavior, appearance, and functionality of the application.

##### Font Settings
- **Purpose**: Configure application fonts and text display
- **Location**: Settings → Font Settings...
- **Features**:
  - **Font Family**: Choose from system-available fonts
  - **Font Size**: Adjust text size for better readability
  - **Font Style**: Bold, italic, and other style options
  - **Preview**: Real-time preview of font changes
  - **Apply to All**: Apply font settings to all text areas
- **Scope**: Affects all text widgets, input/output tabs, and tool interfaces

##### Dialog Settings
- **Purpose**: Configure which notification and confirmation dialogs are displayed
- **Location**: Settings → Dialog Settings...
- **Categories**:
  - **Success Notifications**: Completion messages for successful operations
  - **Warning Messages**: Alerts for potential issues or invalid inputs
  - **Confirmation Dialogs**: User prompts for destructive or important actions
  - **Error Messages**: Critical error notifications (cannot be disabled)
- **Features**:
  - **Category-based Control**: Enable/disable entire categories of dialogs
  - **Real-time Application**: Changes take effect immediately
  - **Safety Design**: Error dialogs always shown for critical issues
  - **Logging Fallback**: Suppressed dialogs are logged for reference

##### Performance Settings
- **Purpose**: Configure performance optimization and system resource usage
- **Location**: Settings → Performance Settings...
- **Categories**:
  - **Async Processing**: Background processing configuration
  - **Caching Strategy**: Intelligent caching mechanisms
  - **Memory Management**: Memory optimization and leak detection
  - **UI Optimizations**: User interface performance settings
- **Features**:
  - **Performance Modes**: Automatic, Performance, Memory-Optimized, Compatibility
  - **Real-time Monitoring**: Performance metrics and resource usage
  - **Adaptive Settings**: Automatic adjustment based on system capabilities
  - **Expert Configuration**: Advanced settings for power users

##### Console Log
- **Purpose**: View application logs and debugging information
- **Location**: Settings → Console Log
- **Features**:
  - **Real-time Logging**: Live view of application events and errors
  - **Log Levels**: Filter by DEBUG, INFO, WARNING, ERROR levels
  - **Search and Filter**: Find specific log entries
  - **Export Logs**: Save logs to file for troubleshooting
  - **Clear Logs**: Clear current log display
- **Use Cases**: Troubleshooting, debugging, monitoring application behavior

#### Configuration Categories

##### Tool-Specific Settings
Each tool maintains its own configuration section:
- **Persistent State**: Settings saved automatically
- **Default Values**: Sensible defaults for first-time users
- **Validation**: Settings validated on load
- **Migration**: Automatic migration for setting changes

##### Performance Settings
```json
"performance_settings": {
  "enable_async_processing": true,    // Enable background processing
  "enable_caching": true,             // Enable result caching
  "cache_size_mb": 100,              // Maximum cache size
  "async_threshold_kb": 10,          // Size threshold for async processing
  "max_workers": 2,                  // Background worker threads
  "chunk_size_kb": 50,               // Chunk size for large texts
  "enable_optimizations": "auto"     // Optimization level
}
```

##### Performance Settings

The application includes a comprehensive performance optimization system that allows users to configure various aspects of text processing, memory management, and UI responsiveness. These settings enable fine-tuning of the application's behavior to match system capabilities and user preferences, ensuring optimal performance across different hardware configurations and usage patterns.

#### Overview

The Performance Settings system provides granular control over four main categories of optimizations, each designed to improve different aspects of the application's performance. Users can configure these settings to balance performance, memory usage, and responsiveness based on their specific needs and system capabilities.

#### Performance Categories

##### 1. Async Processing Configuration (`async_processing`)
- **Purpose**: Configure background processing for large text operations to prevent UI freezing
- **Default State**: Enabled with automatic thresholds
- **Behavior**: Text operations exceeding the threshold are processed in background threads
- **Use Cases**:
  - Prevent UI blocking during large text processing
  - Enable cancellable long-running operations
  - Provide progress indicators for lengthy tasks
  - Maintain application responsiveness during heavy operations
- **Configuration Options**:
  - **enabled** (boolean): Enable/disable async processing (default: true)
  - **threshold_kb** (integer): Size threshold in KB for async processing (default: 10)
  - **max_workers** (integer): Maximum background worker threads (default: 2)
  - **chunk_size_kb** (integer): Chunk size for processing large texts (default: 50)
- **Performance Impact**: Significantly improves UI responsiveness for large texts (>10KB)
- **Memory Impact**: Minimal additional memory usage for thread management

##### 2. Caching Strategy Options (`caching`)
- **Purpose**: Configure intelligent caching mechanisms to avoid redundant processing
- **Default State**: Enabled with optimized cache sizes
- **Behavior**: Processed results are cached based on content hash and tool settings
- **Use Cases**:
  - Speed up repeated operations on same content
  - Reduce processing time for frequently accessed data
  - Optimize memory usage through intelligent cache management
  - Improve performance for iterative text editing workflows
- **Configuration Options**:
  - **enabled** (boolean): Enable/disable all caching mechanisms (default: true)
  - **stats_cache_size** (integer): Maximum cached statistics entries (default: 1000)
  - **regex_cache_size** (integer): Maximum cached regex patterns (default: 100)
  - **content_cache_size_mb** (integer): Maximum content cache size in MB (default: 50)
  - **processing_cache_size** (integer): Maximum processing result cache entries (default: 500)
- **Performance Impact**: Up to 90% reduction in processing time for cached operations
- **Memory Impact**: Configurable memory usage based on cache size limits

##### 3. Memory Management Settings (`memory_management`)
- **Purpose**: Configure memory optimization strategies and leak detection
- **Default State**: Enabled with conservative settings
- **Behavior**: Automatic memory cleanup, garbage collection optimization, and leak detection
- **Use Cases**:
  - Prevent memory leaks during long application sessions
  - Optimize memory usage for large text processing
  - Enable memory monitoring and alerting
  - Improve stability for resource-constrained systems
- **Configuration Options**:
  - **enabled** (boolean): Enable/disable memory management optimizations (default: true)
  - **gc_optimization** (boolean): Enable garbage collection optimization (default: true)
  - **memory_pool** (boolean): Enable memory pooling for frequent allocations (default: true)
  - **leak_detection** (boolean): Enable memory leak detection and reporting (default: true)
  - **memory_threshold_mb** (integer): Memory usage threshold for cleanup triggers (default: 500)
- **Performance Impact**: Reduces memory fragmentation and improves long-term stability
- **Memory Impact**: Lower overall memory usage and more predictable memory patterns

##### 4. UI Optimizations (`ui_optimizations`)
- **Purpose**: Configure user interface performance optimizations
- **Default State**: Enabled with balanced settings
- **Behavior**: Optimizes text rendering, search highlighting, and UI responsiveness
- **Use Cases**:
  - Improve text editor performance for large documents
  - Optimize search and highlighting operations
  - Reduce UI lag during text manipulation
  - Enable progressive loading for better user experience
- **Configuration Options**:
  - **enabled** (boolean): Enable/disable UI optimizations (default: true)
  - **efficient_line_numbers** (boolean): Use optimized line number rendering (default: true)
  - **progressive_search** (boolean): Enable progressive search with chunking (default: true)
  - **debounce_delay_ms** (integer): Delay for debouncing rapid UI updates (default: 300)
  - **lazy_updates** (boolean): Enable lazy loading for UI components (default: true)
- **Performance Impact**: Smoother UI interactions and faster text rendering
- **Memory Impact**: Reduced memory usage for UI components and text rendering

#### Performance Modes

The application supports different performance modes that automatically configure optimal settings:

##### Automatic Mode (`mode: "automatic"`)
- **Description**: Automatically adjusts settings based on system capabilities and content size
- **Behavior**: Dynamic optimization based on available memory, CPU cores, and text size
- **Best For**: Most users who want optimal performance without manual configuration
- **Settings**: All categories enabled with adaptive thresholds

##### Performance Mode (`mode: "performance"`)
- **Description**: Maximizes performance at the cost of higher memory usage
- **Behavior**: Aggressive caching, larger chunk sizes, more worker threads
- **Best For**: High-performance systems with abundant memory
- **Settings**: Maximum cache sizes, increased worker threads, optimized thresholds

##### Memory Mode (`mode: "memory"`)
- **Description**: Minimizes memory usage while maintaining acceptable performance
- **Behavior**: Smaller caches, conservative thresholds, frequent cleanup
- **Best For**: Resource-constrained systems or when running multiple applications
- **Settings**: Reduced cache sizes, lower thresholds, aggressive memory management

##### Balanced Mode (`mode: "balanced"`)
- **Description**: Balances performance and memory usage for general use
- **Behavior**: Moderate settings that work well for most scenarios
- **Best For**: General users with typical system configurations
- **Settings**: Default values optimized for common usage patterns

#### Configuration Interface

##### Accessing Performance Settings
1. **From Main Menu**: Settings → Performance Settings...
2. **From Settings Button**: Click main "Settings" button, then "Performance Settings"
3. **Keyboard Shortcut**: Alt+S, P (Settings menu, Performance Settings)

##### Settings Window Features

**Window Layout:**
- **Title**: "Performance Settings"
- **Size**: 700×600 pixels (resizable, minimum 650×550)
- **Tabs**: Organized by performance category with clear visual separation

**Category Controls:**
- **Mode Selection**: Radio buttons for Automatic, Performance, Memory, Balanced modes
- **Category Sections**: Expandable sections for each performance category
- **Advanced Options**: Collapsible advanced settings for power users
- **Real-time Monitoring**: Live performance metrics and memory usage display
- **Preset Buttons**: Quick preset configurations for common scenarios

**Action Buttons:**
- **Apply**: Save changes and apply immediately
- **Reset to Defaults**: Restore all settings to default values
- **Import/Export**: Save and load performance profiles
- **Test Configuration**: Run performance tests with current settings
- **Help**: Open detailed performance optimization guide

##### Real-Time Settings Updates

**Immediate Application:**
- Most changes take effect immediately upon clicking "Apply"
- Some settings (like worker thread count) may require tool restart
- Performance monitoring updates in real-time
- Settings are validated and optimized automatically

**Settings Validation:**
- Invalid settings are automatically corrected with warnings
- Conflicting settings are resolved with user notification
- System capability checks ensure settings are appropriate for hardware
- Performance impact estimates are provided for major changes

#### Configuration Structure

The performance settings are stored in `settings.json` under the `performance_settings` key:

```json
{
  "performance_settings": {
    "mode": "automatic",
    "async_processing": {
      "enabled": true,
      "threshold_kb": 10,
      "max_workers": 2,
      "chunk_size_kb": 50
    },
    "caching": {
      "enabled": true,
      "stats_cache_size": 1000,
      "regex_cache_size": 100,
      "content_cache_size_mb": 50,
      "processing_cache_size": 500
    },
    "memory_management": {
      "enabled": true,
      "gc_optimization": true,
      "memory_pool": true,
      "leak_detection": true,
      "memory_threshold_mb": 500
    },
    "ui_optimizations": {
      "enabled": true,
      "efficient_line_numbers": true,
      "progressive_search": true,
      "debounce_delay_ms": 300,
      "lazy_updates": true
    }
  }
}
```

#### Performance Monitoring Features

##### Real-Time Metrics
- **Memory Usage**: Current and peak memory consumption
- **Cache Performance**: Hit rates and cache efficiency statistics
- **Processing Times**: Average and peak processing times for different operations
- **Thread Utilization**: Background thread usage and queue status
- **UI Responsiveness**: Frame rates and UI update latencies

##### Performance Dashboard
- **System Overview**: CPU, memory, and disk usage relevant to the application
- **Cache Statistics**: Detailed cache performance across all categories
- **Processing Analytics**: Breakdown of time spent in different processing stages
- **Memory Analysis**: Memory allocation patterns and cleanup effectiveness
- **Historical Trends**: Performance trends over time with configurable time windows

##### Diagnostic Tools
- **Performance Profiler**: Built-in profiling for identifying bottlenecks
- **Memory Analyzer**: Tools for detecting memory leaks and optimization opportunities
- **Cache Inspector**: Detailed view of cache contents and effectiveness
- **Thread Monitor**: Real-time view of background thread activity
- **Export Reports**: Generate detailed performance reports for analysis

#### Performance Optimization Scenarios

##### Scenario 1: Large Document Processing
**Problem**: Application becomes unresponsive when processing documents >1MB
**Solution**: 
- Enable async processing with lower threshold (5KB)
- Increase chunk size to 100KB for better throughput
- Enable memory management with 1GB threshold
- Use Performance mode for maximum speed

**Configuration:**
```json
{
  "mode": "performance",
  "async_processing": {
    "enabled": true,
    "threshold_kb": 5,
    "max_workers": 4,
    "chunk_size_kb": 100
  },
  "memory_management": {
    "memory_threshold_mb": 1000
  }
}
```

##### Scenario 2: Memory-Constrained System
**Problem**: Application uses too much memory on systems with limited RAM
**Solution**:
- Use Memory mode with aggressive cleanup
- Reduce all cache sizes significantly
- Enable frequent garbage collection
- Lower async processing thresholds

**Configuration:**
```json
{
  "mode": "memory",
  "caching": {
    "stats_cache_size": 100,
    "content_cache_size_mb": 10,
    "processing_cache_size": 50
  },
  "memory_management": {
    "memory_threshold_mb": 100,
    "gc_optimization": true
  }
}
```

##### Scenario 3: Repetitive Text Processing
**Problem**: Frequently processing similar content with poor performance
**Solution**:
- Maximize caching for all categories
- Enable content hash caching
- Use larger cache sizes
- Enable processing result caching

**Configuration:**
```json
{
  "caching": {
    "enabled": true,
    "stats_cache_size": 2000,
    "regex_cache_size": 500,
    "content_cache_size_mb": 100,
    "processing_cache_size": 1000
  }
}
```

##### Scenario 4: Real-Time Text Analysis
**Problem**: Need immediate feedback during text editing
**Solution**:
- Reduce debounce delays
- Enable progressive search
- Use smaller async thresholds
- Optimize UI updates

**Configuration:**
```json
{
  "async_processing": {
    "threshold_kb": 1,
    "max_workers": 3
  },
  "ui_optimizations": {
    "debounce_delay_ms": 100,
    "progressive_search": true,
    "lazy_updates": true
  }
}
```

#### Best Practices

##### Recommended Settings by System Type

**High-Performance Desktop (16GB+ RAM, 8+ cores):**
- Mode: Performance
- Max workers: 4-6
- Cache sizes: Maximum
- Memory threshold: 1GB+

**Standard Laptop (8GB RAM, 4 cores):**
- Mode: Automatic or Balanced
- Max workers: 2-3
- Cache sizes: Default
- Memory threshold: 500MB

**Resource-Constrained System (4GB RAM, 2 cores):**
- Mode: Memory
- Max workers: 1-2
- Cache sizes: Minimal
- Memory threshold: 200MB

##### Performance Tuning Tips
1. **Monitor Memory Usage**: Regularly check memory consumption and adjust thresholds
2. **Test with Real Data**: Use actual documents and workflows for performance testing
3. **Gradual Adjustments**: Make incremental changes and measure impact
4. **Profile Bottlenecks**: Use built-in profiling to identify specific performance issues
5. **Consider Usage Patterns**: Optimize for your most common operations

##### Common Pitfalls
- **Over-Caching**: Too large caches can actually hurt performance due to memory pressure
- **Too Many Workers**: More threads don't always mean better performance
- **Ignoring System Limits**: Settings should match system capabilities
- **Disabling Optimizations**: Some optimizations have minimal overhead but significant benefits

#### Technical Implementation

The performance system is implemented through several core modules:

##### AsyncTextProcessor (`core/async_text_processor.py`)
- Handles background text processing with configurable worker pools
- Implements chunking strategies for large content
- Provides progress tracking and cancellation support
- Manages thread lifecycle and resource cleanup

##### ContentHashCache (`core/content_hash_cache.py`)
- Implements intelligent content-based caching
- Provides LRU eviction with frequency-based optimization
- Supports configurable cache sizes and TTL policies
- Includes cache performance monitoring and statistics

##### SmartStatsCalculator (`core/smart_stats_calculator.py`)
- Provides cached statistics calculation with incremental updates
- Implements memory-efficient text analysis
- Supports widget-specific cache management
- Includes automatic cache optimization and cleanup

##### ProgressiveStatsCalculator (`core/progressive_stats_calculator.py`)
- Handles progressive statistics calculation for large texts
- Implements cancellable calculations with progress indicators
- Provides chunked processing with UI yield points
- Supports threshold-based processing mode selection

#### Integration Points
- **Settings Manager**: Persists performance settings in `settings.json`
- **UI Framework**: Integrates with tkinter-based performance monitoring
- **Tool System**: All tools respect performance settings automatically
- **Memory Monitor**: Real-time memory usage tracking and alerting
- **Background Services**: Automatic cleanup and optimization services

##### Dialog Settings

The application includes a sophisticated dialog management system that allows users to control which notification and confirmation dialogs are displayed throughout the application. This system provides a better user experience by reducing interruptions while maintaining important system communications and ensuring critical information is never missed.

#### Overview

The Dialog Settings system provides granular control over four distinct categories of dialogs, each serving different purposes in the user experience. Users can customize which types of dialogs are shown while maintaining safety through mandatory error notifications and comprehensive logging fallback for suppressed messages.

#### Dialog Categories

##### 1. Success Notifications (`success`)
- **Purpose**: Inform users of successful operations and completions
- **Default State**: Enabled (can be disabled by user)
- **Behavior When Disabled**: Messages are logged to application log but no dialog is shown
- **Use Cases**: 
  - Reduce interruptions for routine operations
  - Streamline workflows for experienced users
  - Minimize dialog fatigue during batch operations
- **Common Examples**:
  - "File saved successfully"
  - "Settings applied and saved"
  - "Export completed successfully"
  - "Data processed successfully"
  - "Configuration updated"
- **Logging Fallback**: All suppressed success messages are logged at INFO level

##### 2. Warning Messages (`warning`)
- **Purpose**: Alert users to potential issues, invalid inputs, or non-critical problems
- **Default State**: Enabled (can be disabled by user)
- **Behavior When Disabled**: Warnings are logged to application log but no dialog is shown
- **Use Cases**:
  - Streamline workflows while maintaining error visibility in logs
  - Reduce interruptions for known issues that don't require immediate action
  - Allow automated processing to continue without user intervention
- **Common Examples**:
  - "No data specified for processing"
  - "Invalid input detected, using defaults"
  - "Feature unavailable with current settings"
  - "Some files could not be processed"
  - "Network timeout, retrying automatically"
- **Logging Fallback**: All suppressed warning messages are logged at WARNING level

##### 3. Confirmation Dialogs (`confirmation`)
- **Purpose**: Request user confirmation for destructive, irreversible, or important actions
- **Default State**: Enabled (can be disabled by user)
- **Behavior When Disabled**: Default action is taken automatically (typically "Yes" or "OK")
- **Default Action**: Configurable per dialog, usually the affirmative action
- **Use Cases**:
  - Speed up workflows for experienced users who understand the consequences
  - Enable automated batch processing without user intervention
  - Reduce clicks for repetitive operations
- **Common Examples**:
  - "Clear all tabs? This action cannot be undone."
  - "Delete selected entries? This will permanently remove them."
  - "Reset settings to defaults? Current settings will be lost."
  - "Overwrite existing file?"
  - "Exit without saving changes?"
- **Safety Considerations**: Users should carefully consider disabling confirmations for destructive actions
- **Logging Fallback**: All automatic confirmations are logged at INFO level with the action taken

##### 4. Error Messages (`error`)
- **Purpose**: Display critical error information that requires immediate user attention
- **Default State**: Always enabled (cannot be disabled)
- **Behavior**: Always shown regardless of user settings
- **Safety Feature**: Ensures users are always informed of critical issues that could affect data integrity or application functionality
- **Common Examples**:
  - "File not found or access denied"
  - "Network connection error"
  - "Invalid configuration detected"
  - "Critical system error occurred"
  - "Data corruption detected"
- **No Logging Fallback**: Error dialogs are always shown and also logged at ERROR level

#### Configuration Interface

##### Accessing Dialog Settings
1. **From Main Menu**: Settings → Dialog Settings...
2. **From Settings Button**: Click main "Settings" button, then "Dialog Settings"
3. **Keyboard Shortcut**: Alt+S, D (Settings menu, Dialog Settings)

##### Settings Window Features

**Window Layout:**
- **Title**: "Dialog Settings"
- **Size**: 650×550 pixels (resizable, minimum 600×500)
- **Sections**: Organized by dialog category with clear visual separation

**Category Controls:**
- **Checkboxes**: One per category (Success, Warning, Confirmation)
- **Error Category**: Displayed but disabled (always checked) with explanation
- **Descriptions**: Detailed explanations of what each category controls
- **Examples**: Sample messages to help users understand the impact
- **Visual Indicators**: Icons or colors to distinguish category types

**Action Buttons:**
- **Apply**: Save changes and apply immediately
- **Reset to Defaults**: Restore all categories to default enabled state
- **Cancel**: Close without saving changes
- **Help**: Open detailed help documentation

##### Real-Time Settings Updates

**Immediate Application:**
- Changes take effect immediately upon clicking "Apply"
- No application restart required
- All tools and components respect new settings instantly
- Settings are persisted to `settings.json` automatically

**Settings Validation:**
- Invalid settings are automatically corrected
- Missing categories default to enabled for safety
- Corrupted settings trigger automatic reset to defaults
- All changes are validated before application

#### Configuration Structure

The dialog settings are stored in `settings.json` under the `dialog_settings` key:

```json
{
  "dialog_settings": {
    "success": {
      "enabled": true,
      "description": "Success notifications for completed operations",
      "examples": [
        "File saved successfully",
        "Settings applied and saved", 
        "Export completed successfully",
        "Data processed successfully"
      ]
    },
    "confirmation": {
      "enabled": true,
      "description": "Confirmation dialogs for destructive or important actions",
      "examples": [
        "Clear all tabs? This action cannot be undone.",
        "Delete selected entries? This will permanently remove them.",
        "Reset settings to defaults? Current settings will be lost.",
        "Overwrite existing file?"
      ],
      "default_action": "yes"
    },
    "warning": {
      "enabled": true,
      "description": "Warning messages for potential issues or invalid inputs",
      "examples": [
        "No data specified for processing",
        "Invalid input detected, using defaults",
        "Feature unavailable with current settings",
        "Some files could not be processed"
      ]
    },
    "error": {
      "enabled": true,
      "locked": true,
      "description": "Critical error messages (cannot be disabled for safety)",
      "examples": [
        "File not found or access denied",
        "Network connection error",
        "Invalid configuration detected",
        "Critical system error occurred"
      ]
    }
  }
}
```

#### Logging Fallback System

When dialogs are suppressed, the application maintains a comprehensive logging system to ensure no information is lost:

##### Log Levels and Categories
- **SUCCESS dialogs** → INFO level logs
- **WARNING dialogs** → WARNING level logs  
- **CONFIRMATION dialogs** → INFO level logs (with action taken)
- **ERROR dialogs** → ERROR level logs (always shown + logged)

##### Log Format
```
[TIMESTAMP] [LEVEL] [DIALOG_SUPPRESSED] Category: Message
[2024-01-15 14:30:25] [INFO] [DIALOG_SUPPRESSED] Success: File saved successfully
[2024-01-15 14:30:26] [WARNING] [DIALOG_SUPPRESSED] Warning: Invalid input detected, using defaults
[2024-01-15 14:30:27] [INFO] [DIALOG_SUPPRESSED] Confirmation: Clear all tabs - Action taken: YES
```

##### Log Access
- **Log File**: `pomera_ai.log` in application directory
- **Console Output**: Available when running in debug mode
- **Settings Panel**: View recent logs through Settings → View Logs

#### Usage Scenarios and Best Practices

##### Scenario 1: New User (Recommended Default)
```
✓ Success Notifications: Enabled
✓ Warning Messages: Enabled  
✓ Confirmation Dialogs: Enabled
✓ Error Messages: Enabled (locked)
```
**Benefits:**
- Maximum feedback and safety
- Learn application behavior and consequences
- Understand all system messages and warnings
- Safe for learning and exploration

**Recommended For:**
- First-time users
- Users learning the application
- Critical data processing scenarios
- Shared computer environments

##### Scenario 2: Power User (Efficiency Focused)
```
✗ Success Notifications: Disabled
✓ Warning Messages: Enabled  
✗ Confirmation Dialogs: Disabled
✓ Error Messages: Enabled (locked)
```
**Benefits:**
- Minimal interruptions for routine operations
- Faster workflow execution
- Still alerted to warnings and errors
- Automatic confirmation of familiar actions

**Recommended For:**
- Experienced users who understand consequences
- Batch processing operations
- Repetitive workflow scenarios
- Time-sensitive tasks

**Cautions:**
- Destructive actions happen without confirmation
- Success feedback only available in logs
- Requires understanding of default actions

##### Scenario 3: Automated Processing
```
✗ Success Notifications: Disabled
✗ Warning Messages: Disabled
✗ Confirmation Dialogs: Disabled
✓ Error Messages: Enabled (locked)
```
**Benefits:**
- Completely unattended operation
- No user intervention required
- Only critical errors interrupt processing
- Maximum automation capability

**Recommended For:**
- Scripted or automated workflows
- Batch processing large datasets
- Background processing tasks
- Server or headless environments

**Cautions:**
- No feedback except for critical errors
- Warnings and issues may go unnoticed
- Requires careful monitoring of log files
- Not recommended for interactive use

##### Scenario 4: Balanced Approach (Recommended for Most Users)
```
✗ Success Notifications: Disabled
✓ Warning Messages: Enabled
✓ Confirmation Dialogs: Enabled
✓ Error Messages: Enabled (locked)
```
**Benefits:**
- Reduced routine interruptions
- Important warnings still shown
- Safety confirmations for destructive actions
- Good balance of efficiency and safety

**Recommended For:**
- Regular users with some experience
- Mixed interactive and batch workflows
- Shared environments with multiple users
- General-purpose usage

#### Technical Implementation

##### DialogManager Class
The core `DialogManager` class (`core/dialog_manager.py`) provides centralized dialog decision-making:

```python
class DialogManager:
    """
    Centralized dialog management with settings-driven suppression.
    
    Features:
    - Category-based dialog filtering
    - Logging fallback for suppressed dialogs
    - Real-time settings updates
    - Graceful error handling
    """
    
    def show_info(self, title, message, category="info"):
        """Show info dialog if category is enabled, otherwise log."""
        
    def show_warning(self, title, message, category="warning"):
        """Show warning dialog if category is enabled, otherwise log."""
        
    def ask_yes_no(self, title, message, category="confirmation"):
        """Show confirmation dialog if enabled, otherwise return default."""
        
    def show_error(self, title, message):
        """Always show error dialogs (cannot be suppressed)."""
```

##### Settings Integration
- **Settings Manager**: Integrated with existing `settings.json` persistence
- **Validation**: Automatic validation and correction of invalid settings
- **Migration**: Backward compatibility for installations without dialog settings
- **Real-time Updates**: Settings changes apply immediately without restart

##### Error Handling and Safety
- **Graceful Degradation**: System continues if dialog display fails
- **Safe Defaults**: Unknown or corrupted settings default to enabled
- **Fallback Logging**: All suppressed dialogs are logged appropriately
- **Error Safety**: Error dialogs cannot be disabled under any circumstances

##### Integration Points
- **Main Application**: All core dialogs use DialogManager
- **Tool Modules**: Consistent dialog behavior across all tools
- **Settings System**: Seamless integration with existing settings persistence
- **Logging Framework**: Automatic fallback logging when dialogs are suppressed

#### Troubleshooting

##### Common Issues

**Settings Not Persisting:**
- Check file permissions on `settings.json`
- Ensure application has write access to settings directory
- Verify settings file is not corrupted (will auto-reset if needed)

**Dialogs Still Showing When Disabled:**
- Check if dialog is categorized as "error" (cannot be disabled)
- Verify settings have been applied (click "Apply" button)
- Restart application if settings seem corrupted

**Missing Dialog Categories:**
- Update to latest version (new categories added over time)
- Reset settings to defaults to add missing categories
- Check application logs for settings validation messages

**Logging Not Working:**
- Verify log file permissions and disk space
- Check if logging is enabled in application settings
- Ensure log directory exists and is writable

##### Advanced Configuration

**Custom Default Actions:**
Some confirmation dialogs support custom default actions when disabled. These can be configured in the settings file:

```json
"confirmation": {
  "enabled": false,
  "custom_defaults": {
    "clear_tabs": "no",
    "delete_entries": "cancel",
    "reset_settings": "no"
  }
}
```

**Category-Specific Logging:**
Enable detailed logging for specific dialog categories:

```json
"dialog_settings": {
  "logging": {
    "success": true,
    "warning": true,
    "confirmation": true,
    "include_timestamps": true,
    "include_stack_trace": false
  }
}
```

*For complete technical details and implementation examples, see the [Dialog Configuration System](#dialog-configuration-system) section.*

##### Font Settings

The application provides comprehensive font customization capabilities across all text areas and interface elements. Font settings are automatically applied to all tools and persist across application sessions.

**Configuration Structure:**
```json
"font_settings": {
  "text_font": {
    "family": "Source Code Pro",
    "size": 11,
    "fallback_family": "Consolas",
    "fallback_family_mac": "Monaco",
    "fallback_family_linux": "DejaVu Sans Mono"
  },
  "interface_font": {
    "family": "Segoe UI",
    "size": 9,
    "fallback_family": "Arial",
    "fallback_family_mac": "Helvetica",
    "fallback_family_linux": "Ubuntu"
  }
}
```

**Font Categories:**

1. **Text Font** (`text_font`):
   - **Purpose**: Used for all text input/output areas, code display, and content processing
   - **Recommended**: Monospace fonts for better alignment and readability
   - **Default**: Source Code Pro (fallback: Consolas)
   - **Size Range**: 8-24 points (recommended: 10-12)
   - **Applied To**: Main text areas, tool outputs, diff viewers, code displays

2. **Interface Font** (`interface_font`):
   - **Purpose**: Used for UI elements, buttons, labels, and menus
   - **Recommended**: Sans-serif fonts for better UI readability
   - **Default**: Segoe UI (fallback: Arial)
   - **Size Range**: 8-16 points (recommended: 9-11)
   - **Applied To**: Buttons, labels, menus, status bars, dialog boxes

**Platform-Specific Fallbacks:**
- **Windows**: Consolas (text), Segoe UI (interface)
- **macOS**: Monaco (text), Helvetica (interface)
- **Linux**: DejaVu Sans Mono (text), Ubuntu (interface)

**Font Selection Guidelines:**

*For Text Areas (Monospace Recommended):*
- **Source Code Pro**: Excellent for code and text processing
- **Consolas**: Windows default, good readability
- **Monaco**: macOS default, clean appearance
- **DejaVu Sans Mono**: Linux default, Unicode support
- **Fira Code**: Modern with ligature support
- **JetBrains Mono**: Designed for developers

*For Interface Elements (Sans-serif Recommended):*
- **Segoe UI**: Windows modern interface font
- **Helvetica**: macOS standard, clean design
- **Ubuntu**: Linux default, good readability
- **Arial**: Universal fallback
- **Roboto**: Modern, Google design

**Configuration Access:**
1. Font settings are automatically loaded on application startup
2. Changes require application restart to take full effect
3. Invalid font names automatically fall back to platform defaults
4. Font availability is checked at runtime

**Advanced Configuration:**

*Custom Font Installation:*
```json
"font_settings": {
  "text_font": {
    "family": "Your Custom Font",
    "size": 12,
    "style": "normal",  // normal, bold, italic
    "weight": "normal"  // normal, bold, light
  }
}
```

*Font Validation:*
- Application validates font availability at startup
- Missing fonts automatically use fallback options
- Font metrics are cached for performance
- Cross-platform compatibility is maintained

**Performance Considerations:**
- Font rendering is optimized for large text processing
- Monospace fonts provide better performance for text alignment
- Font caching reduces rendering overhead
- Platform-native fonts are preferred for best performance

**Troubleshooting Font Issues:**

*Font Not Displaying:*
1. Verify font is installed on the system
2. Check font name spelling in settings.json
3. Restart application after font changes
4. Use fallback fonts if custom fonts fail

*Performance Issues:*
1. Use system fonts when possible
2. Avoid very large font sizes (>20pt) for large texts
3. Monospace fonts perform better for text processing
4. Clear font cache if rendering issues occur

##### Performance Settings

The application includes comprehensive performance optimization features designed to handle large text processing tasks efficiently. Performance settings allow fine-tuning of async processing, caching strategies, memory management, and UI optimizations.

**Configuration Structure:**
```json
"performance_settings": {
  "mode": "automatic",
  "async_processing": {
    "enabled": true,
    "threshold_kb": 10,
    "max_workers": 2,
    "chunk_size_kb": 50
  },
  "caching": {
    "enabled": true,
    "stats_cache_size": 1000,
    "regex_cache_size": 100,
    "content_cache_size_mb": 50,
    "processing_cache_size": 500
  },
  "memory_management": {
    "enabled": true,
    "gc_optimization": true,
    "memory_pool": true,
    "leak_detection": true,
    "memory_threshold_mb": 500
  },
  "ui_optimizations": {
    "enabled": true,
    "efficient_line_numbers": true,
    "progressive_search": true,
    "debounce_delay_ms": 300,
    "lazy_updates": true
  }
}
```

**Performance Categories:**

1. **Async Processing** (`async_processing`):
   - **Purpose**: Handle large text operations without blocking the UI
   - **Threshold**: Automatically triggers for texts larger than specified size
   - **Worker Threads**: Configurable number of background processing threads
   - **Chunking**: Splits large texts into manageable chunks for processing
   - **Benefits**: Responsive UI, cancellable operations, progress tracking

   **Configuration Options:**
   - `enabled` (boolean): Enable/disable async processing
   - `threshold_kb` (integer): Size threshold in KB to trigger async processing (default: 10)
   - `max_workers` (integer): Maximum number of worker threads (default: 2)
   - `chunk_size_kb` (integer): Size of text chunks in KB (default: 50)

2. **Caching** (`caching`):
   - **Purpose**: Store frequently used results to improve performance
   - **Types**: Statistics cache, regex pattern cache, content hash cache, processing results cache
   - **Memory Management**: Configurable cache sizes with automatic cleanup
   - **Benefits**: Faster repeated operations, reduced CPU usage, improved responsiveness

   **Configuration Options:**
   - `enabled` (boolean): Enable/disable all caching mechanisms
   - `stats_cache_size` (integer): Number of statistical results to cache (default: 1000)
   - `regex_cache_size` (integer): Number of compiled regex patterns to cache (default: 100)
   - `content_cache_size_mb` (integer): Content hash cache size in MB (default: 50)
   - `processing_cache_size` (integer): Number of processing results to cache (default: 500)

3. **Memory Management** (`memory_management`):
   - **Purpose**: Optimize memory usage for large text processing
   - **Features**: Garbage collection optimization, memory pooling, leak detection
   - **Monitoring**: Automatic memory threshold monitoring and cleanup
   - **Benefits**: Reduced memory footprint, prevention of memory leaks, stable performance

   **Configuration Options:**
   - `enabled` (boolean): Enable/disable memory management optimizations
   - `gc_optimization` (boolean): Enable garbage collection optimizations
   - `memory_pool` (boolean): Use memory pooling for text operations
   - `leak_detection` (boolean): Enable memory leak detection and reporting
   - `memory_threshold_mb` (integer): Memory usage threshold for cleanup (default: 500)

4. **UI Optimizations** (`ui_optimizations`):
   - **Purpose**: Optimize user interface responsiveness and rendering
   - **Features**: Efficient line numbering, progressive search, debounced updates, lazy rendering
   - **Benefits**: Smoother scrolling, faster text updates, reduced UI lag

   **Configuration Options:**
   - `enabled` (boolean): Enable/disable UI optimizations
   - `efficient_line_numbers` (boolean): Use optimized line number rendering
   - `progressive_search` (boolean): Enable progressive search highlighting
   - `debounce_delay_ms` (integer): Delay in milliseconds for debounced updates (default: 300)
   - `lazy_updates` (boolean): Enable lazy UI updates for better performance

**Performance Modes:**

1. **Automatic Mode** (`mode: "automatic"`):
   - Automatically adjusts settings based on system capabilities
   - Monitors system resources and adapts performance settings
   - Recommended for most users
   - Balances performance with resource usage

2. **High Performance Mode** (`mode: "high_performance"`):
   - Maximizes performance for large text processing
   - Uses more system resources for better speed
   - Recommended for powerful systems and heavy usage
   - May increase memory and CPU usage

3. **Conservative Mode** (`mode: "conservative"`):
   - Minimizes resource usage
   - Suitable for older systems or limited resources
   - May reduce performance for large operations
   - Prioritizes system stability over speed

4. **Custom Mode** (`mode: "custom"`):
   - Allows manual configuration of all settings
   - Full control over performance parameters
   - Recommended for advanced users
   - Requires understanding of performance implications

**Performance Monitoring:**

The application includes built-in performance monitoring capabilities:

- **Real-time Metrics**: CPU usage, memory consumption, processing times
- **Operation Tracking**: Track performance of individual operations
- **Cache Statistics**: Hit rates, cache sizes, cleanup frequency
- **Memory Monitoring**: Memory usage patterns, leak detection, cleanup events
- **Performance Logs**: Detailed logging of performance-related events

**Optimization Guidelines:**

*For Large Text Processing (>1MB):*
- Enable async processing with appropriate chunk sizes
- Increase cache sizes for repeated operations
- Use memory management optimizations
- Consider high performance mode

*For System with Limited Resources:*
- Use conservative mode
- Reduce cache sizes
- Disable memory-intensive optimizations
- Increase debounce delays

*For Development/Testing:*
- Enable all monitoring features
- Use custom mode for fine-tuning
- Enable leak detection
- Monitor performance logs

**Advanced Configuration:**

*Custom Async Processing:*
```json
"async_processing": {
  "enabled": true,
  "threshold_kb": 5,        // Lower threshold for more async operations
  "max_workers": 4,         // More workers for multi-core systems
  "chunk_size_kb": 25,      // Smaller chunks for better progress tracking
  "timeout_seconds": 300,   // Operation timeout
  "priority": "normal"      // Thread priority: low, normal, high
}
```

*Advanced Caching:*
```json
"caching": {
  "enabled": true,
  "cache_strategy": "lru",  // lru, lfu, fifo
  "cache_compression": true,
  "cache_persistence": true,
  "cleanup_interval_minutes": 30
}
```

**Performance Troubleshooting:**

*Slow Performance:*
1. Check if async processing is enabled
2. Increase cache sizes for repeated operations
3. Enable memory management optimizations
4. Consider switching to high performance mode

*High Memory Usage:*
1. Reduce cache sizes
2. Enable memory management and garbage collection
3. Lower memory threshold for cleanup
4. Use conservative mode

*UI Lag/Freezing:*
1. Lower async processing threshold
2. Increase debounce delays
3. Enable UI optimizations
4. Reduce chunk sizes for better progress updates

*Cache Issues:*
1. Clear caches by restarting application
2. Adjust cache sizes based on available memory
3. Monitor cache hit rates in performance logs
4. Consider cache compression for large datasets

##### Context Menu Functionality

The application provides comprehensive right-click context menu functionality across all text areas and input fields throughout Pomera AI Commander. This feature implements standard text editing operations with intelligent behavior, cross-platform support, and seamless integration across all tools, following best practices from professional text editors and development environments.

**Overview and Purpose:**

Context menus enhance user productivity by providing familiar interaction patterns and reducing reliance on keyboard shortcuts. The implementation follows industry standards from applications like VS Code, Sublime Text, Windows Notepad, and macOS TextEdit, ensuring users feel comfortable with the interface regardless of their background.

**Visual Menu Layout:**

```
┌─────────────────────────────┐
│ Cut           Ctrl+X        │
│ Copy          Ctrl+C        │
│ Paste         Ctrl+V        │
├─────────────────────────────┤
│ Select All    Ctrl+A        │
│ Delete                      │
└─────────────────────────────┘
```

**Standard Operations:**

The context menu provides five core text operations with platform-appropriate keyboard shortcuts:

1. **Cut** (Ctrl+X / Cmd+X on macOS):
   - Removes selected text and copies it to the system clipboard
   - Only enabled when text is selected and the widget is editable
   - Uses Tkinter's virtual event `<<Cut>>` for consistency with built-in undo/redo

2. **Copy** (Ctrl+C / Cmd+C on macOS):
   - Copies selected text to the system clipboard without removing it
   - Only enabled when text is selected (works on both editable and read-only widgets)
   - Uses Tkinter's virtual event `<<Copy>>` for system integration

3. **Paste** (Ctrl+V / Cmd+V on macOS):
   - Inserts clipboard content at the current cursor position
   - Only enabled when clipboard contains text and the widget is editable
   - Uses Tkinter's virtual event `<<Paste>>` for proper formatting

4. **Select All** (Ctrl+A / Cmd+A on macOS):
   - Selects all text in the current widget
   - Only enabled when the widget contains text
   - Works on both single-line and multi-line text widgets

5. **Delete** (Delete key):
   - Removes selected text without copying to clipboard
   - Only enabled when text is selected and the widget is editable
   - Provides quick deletion without affecting clipboard contents

**Smart Context-Sensitive Behavior:**

The context menu implements intelligent state detection to provide optimal user experience:

**Scenario 1: No Text Selected**
```
┌─────────────────────────────┐
│ Cut           Ctrl+X        │  ← DISABLED (nothing to cut)
│ Copy          Ctrl+C        │  ← DISABLED (nothing to copy)
│ Paste         Ctrl+V        │  ← ENABLED (if clipboard has content)
├─────────────────────────────┤
│ Select All    Ctrl+A        │  ← ENABLED (if text exists)
│ Delete                      │  ← DISABLED (nothing to delete)
└─────────────────────────────┘
```

**Scenario 2: Text Selected**
```
┌─────────────────────────────┐
│ Cut           Ctrl+X        │  ← ENABLED
│ Copy          Ctrl+C        │  ← ENABLED
│ Paste         Ctrl+V        │  ← ENABLED (replaces selection)
├─────────────────────────────┤
│ Select All    Ctrl+A        │  ← ENABLED
│ Delete                      │  ← ENABLED
└─────────────────────────────┘
```

**Scenario 3: Read-Only Text**
```
┌─────────────────────────────┐
│ Cut           Ctrl+X        │  ← DISABLED (can't edit)
│ Copy          Ctrl+C        │  ← ENABLED (can still copy)
│ Paste         Ctrl+V        │  ← DISABLED (can't edit)
├─────────────────────────────┤
│ Select All    Ctrl+A        │  ← ENABLED
│ Delete                      │  ← DISABLED (can't edit)
└─────────────────────────────┘
```

**Selection Detection:**
- **Text Widgets**: Uses `widget.tag_ranges("sel")` to detect selected text
- **Entry Widgets**: Uses `widget.selection_present()` for single-line fields
- **Visual Feedback**: Disabled menu items appear grayed out

**Read-Only Widget Detection:**
- Automatically detects widget state using `widget.cget("state")`
- Disables editing operations (Cut, Paste, Delete) for read-only widgets
- Maintains Copy and Select All functionality for read-only content

**Clipboard Content Detection:**
- Checks clipboard availability using `widget.clipboard_get()`
- Handles clipboard errors gracefully (empty clipboard, access issues)
- Updates Paste availability in real-time

**Cross-Platform Support:**

**Event Binding:**
- **Windows/Linux**: Right mouse button (`<Button-3>`)
- **macOS**: Both `<Button-2>` and `<Control-Button-1>` for compatibility
- **Universal**: Supports both trackpad and mouse right-click

**Keyboard Shortcuts:**
- **Windows/Linux**: Standard Ctrl+ combinations (Ctrl+C, Ctrl+V, Ctrl+X, Ctrl+A)
- **macOS**: Command key combinations (Cmd+C, Cmd+V, Cmd+X, Cmd+A)
- **Visual Display**: Shortcuts shown in context menu for user reference

**Platform-Specific Appearance:**
- **Windows**: Native Windows context menu styling with system theme
- **Linux**: GTK-style menus consistent with desktop environment
- **macOS**: Native macOS context menu appearance with proper styling

**Comprehensive Tool Integration:**

**Main Application Areas:**
- **Input Tabs**: All 7 input tabs with full context menu support
- **Output Tabs**: All 7 output tabs with copy and select operations
- **Tool Settings**: Context menus in tool-specific configuration fields

**Find & Replace Text Tool:**
- Context menus in find and replace input fields
- Smart enabling based on selection state and clipboard content
- Keyboard shortcuts work alongside context menu operations
- Enhanced workflow for pattern entry and replacement text

**Diff Viewer Tool:**
- Context menus in both comparison text areas (left and right panels)
- Context menus in filter entry fields for line filtering
- Copy functionality for extracting specific diff results
- Select All for entire text selection in large comparisons
- Read-only result areas support copy operations

**List Comparator Widget:**
- Context menus in input lists (List A and List B text areas)
- Context menus in all result panes (Only in A, Only in B, In Both)
- Integration with stats bars showing real-time line and character counts
- Read-only result panes support copy operations for data extraction
- Enhanced workflow for list data manipulation

**cURL Tool:**
- Context menus in request body text area for API payload editing
- Context menus in headers section for header value manipulation
- Context menus in response areas for API response data extraction
- Copy functionality for API responses and error messages
- Paste support for building complex requests from templates

**Folder File Reporter:**
- Context menus in input tabs for folder path entry
- Context menus in output tabs for report result manipulation
- Copy functionality for extracting specific report sections
- Paste support for folder paths and configuration data

**All Text Processing Tools:**
- Universal context menu support across Case Tool, Sorter Tools, Translator Tools
- Generator Tools with context menu support in all text areas
- JSON/XML Tool with context menus for data manipulation
- HTML Extraction Tool with context menu support
- Consistent behavior across all encoding/decoding tools

**Technical Implementation:**

**Core Module Structure:**

The context menu functionality is implemented in `core/context_menu.py` with the following architecture:

```python
class TextContextMenu:
    """Main context menu manager for text widgets."""
    
    def __init__(self, widget):
        self.widget = widget
        self.menu = tk.Menu(widget, tearoff=0)
        self._setup_menu()
        self._bind_events()
    
    def _setup_menu(self):
        """Create menu items with keyboard shortcuts."""
        self.menu.add_command(label="Cut    Ctrl+X", command=self._cut)
        self.menu.add_command(label="Copy   Ctrl+C", command=self._copy)
        self.menu.add_command(label="Paste  Ctrl+V", command=self._paste)
        self.menu.add_separator()
        self.menu.add_command(label="Select All    Ctrl+A", command=self._select_all)
        self.menu.add_command(label="Delete", command=self._delete)
```

**Integration Functions:**

```python
def add_context_menu(widget):
    """Add context menu to a single text widget."""
    if not hasattr(widget, '_context_menu'):
        widget._context_menu = TextContextMenu(widget)

def add_context_menu_to_children(parent):
    """Recursively add context menus to all text widgets in a container."""
    for child in parent.winfo_children():
        if isinstance(child, (tk.Text, tk.Entry)):
            add_context_menu(child)
        else:
            add_context_menu_to_children(child)
```

**State Detection Methods:**

```python
def _has_selection(self) -> bool:
    """Check if widget has selected text."""
    if isinstance(self.widget, tk.Text):
        return bool(self.widget.tag_ranges("sel"))
    elif isinstance(self.widget, tk.Entry):
        return self.widget.selection_present()
    return False

def _is_readonly(self) -> bool:
    """Check if widget is read-only."""
    state = str(self.widget.cget("state"))
    return state in ("disabled", "readonly")

def _has_clipboard_content(self) -> bool:
    """Check if clipboard has content."""
    try:
        self.widget.clipboard_get()
        return True
    except tk.TclError:
        return False
```

**Supported Widget Types:**

- **tk.Text**: Multi-line text widgets (primary text areas)
- **tk.Entry**: Single-line entry fields (settings, filters)
- **scrolledtext.ScrolledText**: Scrollable text widgets
- **Custom Text Widgets**: Any widgets inheriting from Text or Entry
- **Optimized Widgets**: OptimizedTextWithLineNumbers and similar custom implementations

**Safety and Error Handling:**

**Graceful Degradation:**
- Context menu feature gracefully disabled if `core.context_menu` module unavailable
- Keyboard shortcuts remain fully functional as fallback
- No impact on core tool functionality
- Error messages logged but don't affect application stability

**Error Handling:**
- Try-catch blocks around all clipboard operations
- Graceful handling of clipboard access errors
- State validation before performing operations
- Memory management prevents duplicate menu creation

**Memory Management:**
- Context menu stored as widget attribute `_context_menu`
- Prevents duplicate menu creation on same widget
- Automatic cleanup when widget is destroyed
- Lightweight implementation (~1KB per widget)

**Performance Characteristics:**

**Minimal Overhead:**
- Context menu created once per widget during initialization
- No continuous polling or background monitoring
- Event-driven activation (only processes on right-click)
- Negligible impact on application startup time

**Memory Usage:**
- Approximately 50 widgets × 1KB = ~50KB total memory usage
- No performance degradation observed during testing
- Scales efficiently with number of text widgets

**Compatibility and Requirements:**

**Tkinter Versions:**
- Compatible with Python 3.6+ and all Tkinter versions
- No external dependencies beyond standard library
- Works with both tk and ttk widgets

**Operating System Support:**
- **Windows 10/11**: Full native support with standard right-click behavior
- **macOS 10.14+**: Native styling with Command key shortcuts
- **Linux**: Ubuntu, Fedora, and other distributions with GTK support

**Usage Examples and Workflows:**

**Basic Text Operations:**
1. **Copy Text**: Select text → Right-click → Choose "Copy" → Text copied to clipboard
2. **Move Text**: Select text → Right-click → Choose "Cut" → Position cursor → Right-click → Choose "Paste"
3. **Quick Delete**: Select unwanted text → Right-click → Choose "Delete" (doesn't affect clipboard)

**Common Workflows:**

**Workflow 1: Copy Text from Input to Output**
1. Select text in Input tab
2. Right-click → Copy (or Ctrl+C)
3. Click in Output tab
4. Right-click → Paste (or Ctrl+V)

**Workflow 2: Move Text Between Tabs**
1. Select text in Tab 1
2. Right-click → Cut (or Ctrl+X)
3. Switch to Tab 2
4. Right-click → Paste (or Ctrl+V)

**Workflow 3: Duplicate All Text**
1. Right-click → Select All (or Ctrl+A)
2. Right-click → Copy (or Ctrl+C)
3. Click where you want to paste
4. Right-click → Paste (or Ctrl+V)

**Workflow 4: Clear and Replace**
1. Right-click → Select All (or Ctrl+A)
2. Right-click → Delete (or just type new text)

**Workflow 5: Quick Copy from Filter**
1. Right-click in filter field
2. Select All → Copy
3. Use elsewhere

**Advanced Workflows:**
1. **Cross-Tool Data Transfer**: Copy from Diff Viewer → Paste into Find & Replace → Process with Case Tool
2. **API Testing**: Copy response from cURL Tool → Paste into JSON/XML Tool for formatting
3. **List Processing**: Copy from List Comparator results → Paste into Sorter Tools for organization

**Tips & Tricks:**

💡 **TIP 1**: Keyboard shortcuts are faster than menu for frequent operations

💡 **TIP 2**: Right-click works even if you don't see a cursor

💡 **TIP 3**: Menu shows keyboard shortcuts as reminders

💡 **TIP 4**: Gray menu items indicate why operation isn't available

💡 **TIP 5**: Select All + Copy is quick way to duplicate content

💡 **TIP 6**: Cut is safer than Delete (can undo with Paste)

💡 **TIP 7**: Right-click on filter fields to copy filter text

💡 **TIP 8**: Works in all popup windows (cURL tool, etc.)

**Platform Differences:**

**Windows:**
- Right mouse button = Context menu
- Ctrl+X/C/V/A = Shortcuts

**macOS:**
- Right mouse button = Context menu
- Control+Click = Also works
- Cmd+X/C/V/A = Shortcuts (not Ctrl)

**Linux:**
- Right mouse button = Context menu
- Ctrl+X/C/V/A = Shortcuts
- May need to configure mouse in system settings

**Troubleshooting Guide:**

**Problem: Menu doesn't appear**
**Solution:** 
- Try clicking directly on text (not margin)
- On Mac, try Control+Click
- Check if widget is actually a text field

**Problem: All menu items are gray**
**Solution:**
- Widget might be read-only
- Try selecting text first
- Check if clipboard has content (for paste)

**Problem: Paste doesn't work**
**Solution:**
- Make sure clipboard has content
- Copy something first
- Widget might be read-only

**Problem: Can't cut or delete**
**Solution:**
- Select text first
- Widget might be read-only
- Check if text is actually selected

**Context Menu Not Appearing:**
1. Verify `core.context_menu` module is available in the application
2. Check console for import errors or module loading issues
3. Ensure right-click is properly detected (try different mouse buttons on macOS)
4. Use keyboard shortcuts as alternative (Ctrl+C, Ctrl+V, etc.)

**Menu Items Disabled (Grayed Out):**
1. **Cut/Copy/Delete**: Ensure text is selected before right-clicking
2. **Paste**: Verify clipboard contains text content (copy something first)
3. **Select All**: Check that the text widget contains content
4. **All Operations**: Ensure widget is not in read-only or disabled state

**Platform-Specific Issues:**
1. **macOS**: Try both right-click and Ctrl+Click if trackpad right-click isn't working
2. **Linux**: Configure mouse settings if right-click doesn't register properly
3. **Windows**: Should work with standard right-click; check mouse driver settings

**Performance Issues:**
1. Context menus are lightweight; performance issues likely unrelated
2. Check for memory leaks if application becomes slow over time
3. Restart application if context menus stop responding

**Best Practices and Recommendations:**

**For End Users:**
1. **Efficiency**: Combine context menus with keyboard shortcuts for optimal workflow
2. **Cross-Platform**: Learn both right-click and keyboard shortcuts for portability
3. **Tool Integration**: Use context menus to move data between different tools
4. **Read-Only Areas**: Remember that copy operations work in read-only result areas

**For Developers:**
1. **New Tools**: Context menu support is automatically added to new text widgets
2. **Custom Widgets**: Ensure custom text widgets inherit from tk.Text or tk.Entry
3. **Error Handling**: Context menu failures don't affect core functionality
4. **Testing**: Test context menu functionality across all supported platforms

**Future Enhancement Possibilities:**

While the current implementation is complete and production-ready, potential future enhancements could include:

1. **Extended Operations**: Undo/Redo, Find/Replace quick access
2. **Tool-Specific Actions**: Custom menu items for specific tools
3. **Clipboard History**: Access to recent clipboard entries
4. **Text Transformations**: Quick case conversion, formatting options
5. **Configuration Options**: User customization of menu items and shortcuts

**Integration Status:**

✅ **Complete Integration**: All major tools and text areas support context menus
✅ **Cross-Platform Tested**: Verified on Windows, macOS, and Linux
✅ **Production Ready**: Stable implementation with comprehensive error handling
✅ **User Experience**: Follows industry standards and user expectations
✅ **Performance Optimized**: Minimal overhead with efficient implementation

##### UI Settings
```json
"ui_settings": {
  "window_geometry": "1200x800+100+100",
  "theme": "default",
  "show_line_numbers": true,
  "word_wrap": true,
  "debounce_delay_ms": 300
}
```

#### AI Provider Configuration

##### API Key Setup
Each AI provider requires proper API key configuration:

```json
"Google AI": {
  "API_KEY": "your_google_ai_key",
  "MODEL": "gemini-1.5-pro-latest",
  "system_prompt": "You are a helpful assistant.",
  "temperature": 0.7,
  "maxOutputTokens": 8192
},
"Vertex AI": {
  "PROJECT_ID": "your-project-id",
  "LOCATION": "us-central1",
  "MODEL": "gemini-2.5-flash",
  "system_prompt": "You are a helpful assistant.",
  "temperature": 0.7,
  "maxOutputTokens": 8192
},
"Azure AI": {
  "API_KEY": "your_azure_ai_key",
  "ENDPOINT": "https://your-resource.services.ai.azure.com",
  "API_VERSION": "2024-10-21",
  "MODEL": "gpt-4.1",
  "system_prompt": "You are a helpful assistant.",
  "temperature": 0.7,
  "max_tokens": 4096
}
```

##### Provider-Specific Settings
- **Google AI**: temperature, topK, topP, candidateCount, maxOutputTokens
- **Vertex AI**: temperature, topK, topP, candidateCount, maxOutputTokens (same as Google AI)
- **Azure AI**: temperature, max_tokens, top_p, frequency_penalty, presence_penalty, seed, stop
- **Anthropic AI**: max_tokens, temperature, top_p, top_k
- **OpenAI**: temperature, max_tokens, top_p, frequency_penalty, presence_penalty
- **Cohere AI**: temperature, max_tokens, k, p, frequency_penalty
- **HuggingFace AI**: max_tokens, temperature, top_p
- **Groq AI**: temperature, max_tokens, top_p, frequency_penalty
- **OpenRouter AI**: temperature, max_tokens, top_p, top_k

#### Pattern Library Configuration

The application includes a comprehensive regex pattern library:

```json
"pattern_library": [
  {
    "name": "Email Address",
    "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
    "description": "Validates email addresses",
    "category": "validation",
    "example": "user@example.com"
  },
  {
    "name": "Phone Number (US)",
    "pattern": "^\\(?([0-9]{3})\\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$",
    "description": "US phone number format",
    "category": "validation",
    "example": "(555) 123-4567"
  }
]
```

### Troubleshooting & FAQ

#### Common Issues and Solutions

##### Application Won't Start
**Problem**: Application fails to launch
**Solutions**:
1. Check Python version: `python --version` (requires 3.7+)
2. Install missing dependencies: `pip install -r requirements.txt`
3. Check for import errors in console output
4. Verify all required files are present

##### AI Tools Not Working
**Problem**: AI providers return errors
**Solutions**:
1. Verify API keys are correctly entered
2. Check internet connection
3. Verify API key permissions and quotas
4. Check provider-specific documentation
5. Test with simple prompts first

##### Performance Issues
**Problem**: Application runs slowly with large texts
**Solutions**:
1. Enable async processing in settings
2. Increase cache size if memory allows
3. Reduce chunk size for better responsiveness
4. Close unnecessary applications to free memory
5. Use performance monitoring to identify bottlenecks

##### Memory Issues
**Problem**: Application uses too much memory
**Solutions**:
1. Reduce cache size in settings
2. Process smaller text chunks
3. Clear cache periodically
4. Close unused tabs
5. Restart application for memory cleanup

##### Audio Not Working (Morse Code)
**Problem**: Morse code audio playback fails
**Solutions**:
1. Install PyAudio: `pip install pyaudio`
2. Check system audio settings
3. Verify audio device is working
4. Try different audio output devices
5. Check for audio driver updates

#### Frequently Asked Questions

##### Q: How do I add custom AI providers?
**A**: Currently, the application supports 11 built-in providers. Custom providers would require code modifications to the `ai_tools.py` module.

##### Q: Can I use the application offline?
**A**: Yes, all tools except AI Tools work offline. AI Tools require internet connection for API calls.

##### Q: How do I backup my settings?
**A**: Copy the `settings.json` file to a safe location. This contains all your configurations and preferences.

##### Q: What's the maximum file size I can process?
**A**: There's no hard limit, but performance depends on available memory. Files over 10MB may benefit from chunked processing.

##### Q: How do I update the pattern library?
**A**: The pattern library is stored in `settings.json`. You can edit it directly or use the pattern library interface in the Find & Replace tool.

##### Q: Can I run multiple instances?
**A**: Yes, but each instance will have its own settings file. Be careful not to overwrite settings when closing instances.

#### Performance Optimization Tips

##### For Large Documents
1. **Enable Async Processing**: Prevents UI freezing
2. **Increase Cache Size**: Improves performance for repeated operations
3. **Use Chunked Processing**: Better for very large files
4. **Monitor Memory Usage**: Adjust settings based on available RAM

##### For Better Responsiveness
1. **Reduce Debounce Delay**: Faster response to input changes
2. **Optimize Regex Patterns**: Use efficient patterns in Find & Replace
3. **Clear Cache Periodically**: Prevents memory buildup
4. **Close Unused Features**: Disable features you don't use

##### For AI Tools
1. **Choose Appropriate Models**: Smaller models respond faster
2. **Optimize Prompts**: Shorter prompts process faster
3. **Use Caching**: Repeated queries return instantly
4. **Monitor API Quotas**: Avoid rate limiting

This comprehensive configuration and troubleshooting guide provides users with all the information needed to properly set up, configure, and maintain the Pomera AI Commander application.---




