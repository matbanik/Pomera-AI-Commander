"""
cURL Tool History Management Module

This module provides request history management for the cURL GUI Tool.
It handles history storage, persistence, and organization functionality.

Author: Pomera AI Commander
"""

import json
import os
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict


@dataclass
class RequestHistoryItem:
    """Individual request history entry."""
    timestamp: str
    method: str
    url: str
    status_code: Optional[int]
    response_time: Optional[float]
    success: bool
    headers: Dict[str, str]
    body: Optional[str]
    auth_type: str
    response_preview: str  # First 200 chars of response
    response_size: Optional[int]
    content_type: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RequestHistoryItem':
        """Create from dictionary."""
        return cls(**data)


class CurlHistoryManager:
    """
    Manages request history persistence and organization for the cURL Tool.
    
    Handles:
    - History file storage and loading (JSON or database backend)
    - History item management (add, remove, search)
    - History cleanup and organization
    - Collections support
    """
    
    def __init__(self, history_file: str = "settings.json", 
                 max_items: int = 100, logger=None, db_settings_manager=None):
        """
        Initialize the history manager.
        
        Args:
            history_file: Path to the main settings file (used if no db_settings_manager)
            max_items: Maximum number of history items to keep
            logger: Logger instance for debugging
            db_settings_manager: DatabaseSettingsManager instance for database backend (optional)
        """
        self.history_file = history_file
        self.max_items = max_items
        self.logger = logger or logging.getLogger(__name__)
        self.tool_key = "cURL Tool"  # Key in tool_settings section
        
        # Database backend support
        self.db_settings_manager = db_settings_manager
        self.use_database = db_settings_manager is not None
        
        # History storage
        self.history: List[RequestHistoryItem] = []
        self.collections: Dict[str, List[str]] = {}  # Collection name -> list of history item IDs
        
        # Load history on initialization
        self.load_history()

    
    def add_request(self, method: str, url: str, headers: Dict[str, str] = None,
                   body: str = None, auth_type: str = "None", 
                   status_code: int = None, response_time: float = None,
                   success: bool = True, response_body: str = "",
                   response_size: int = None, content_type: str = None) -> str:
        """
        Add a request to history.
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            body: Request body
            auth_type: Authentication type used
            status_code: Response status code
            response_time: Response time in seconds
            success: Whether request was successful
            response_body: Response body content
            response_size: Response size in bytes
            content_type: Response content type
            
        Returns:
            History item ID (timestamp)
        """
        timestamp = datetime.now().isoformat()
        
        # Create response preview (first 200 chars)
        response_preview = ""
        if response_body:
            response_preview = response_body[:200]
            if len(response_body) > 200:
                response_preview += "..."
        
        # Create history item
        history_item = RequestHistoryItem(
            timestamp=timestamp,
            method=method,
            url=url,
            status_code=status_code,
            response_time=response_time,
            success=success,
            headers=headers or {},
            body=body,
            auth_type=auth_type,
            response_preview=response_preview,
            response_size=response_size,
            content_type=content_type
        )
        
        # Add to history
        self.history.append(history_item)
        
        # Maintain max items limit
        if len(self.history) > self.max_items:
            removed_item = self.history.pop(0)
            # Remove from collections if present
            self._remove_from_collections(removed_item.timestamp)
        
        # Save history
        self.save_history()
        
        self.logger.debug(f"Added request to history: {method} {url}")
        return timestamp
    
    def get_history(self, limit: int = None) -> List[RequestHistoryItem]:
        """
        Get history items.
        
        Args:
            limit: Maximum number of items to return
            
        Returns:
            List of history items (newest first)
        """
        history = sorted(self.history, key=lambda x: x.timestamp, reverse=True)
        if limit:
            return history[:limit]
        return history
    
    def get_history_item(self, timestamp: str) -> Optional[RequestHistoryItem]:
        """
        Get a specific history item by timestamp.
        
        Args:
            timestamp: Item timestamp ID
            
        Returns:
            History item or None if not found
        """
        for item in self.history:
            if item.timestamp == timestamp:
                return item
        return None
    
    def remove_history_item(self, timestamp: str) -> bool:
        """
        Remove a history item.
        
        Args:
            timestamp: Item timestamp ID
            
        Returns:
            True if removed, False if not found
        """
        for i, item in enumerate(self.history):
            if item.timestamp == timestamp:
                self.history.pop(i)
                self._remove_from_collections(timestamp)
                self.save_history()
                self.logger.debug(f"Removed history item: {timestamp}")
                return True
        return False
    
    def clear_history(self) -> bool:
        """
        Clear all history.
        
        Returns:
            True if successful
        """
        try:
            self.history.clear()
            self.collections.clear()
            self.save_history()
            self.logger.info("History cleared")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing history: {e}")
            return False
    
    def search_history(self, query: str, field: str = "all") -> List[RequestHistoryItem]:
        """
        Search history items.
        
        Args:
            query: Search query
            field: Field to search in ("all", "url", "method", "status")
            
        Returns:
            List of matching history items
        """
        query = query.lower()
        results = []
        
        for item in self.history:
            match = False
            
            if field == "all":
                # Search in multiple fields
                search_text = f"{item.method} {item.url} {item.status_code or ''} {item.response_preview}".lower()
                match = query in search_text
            elif field == "url":
                match = query in item.url.lower()
            elif field == "method":
                match = query in item.method.lower()
            elif field == "status":
                match = query in str(item.status_code or "")
            
            if match:
                results.append(item)
        
        return sorted(results, key=lambda x: x.timestamp, reverse=True)
    
    def cleanup_old_history(self, retention_days: int = 30) -> int:
        """
        Clean up old history items.
        
        Args:
            retention_days: Number of days to retain history
            
        Returns:
            Number of items removed
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            initial_count = len(self.history)
            
            # Filter out old items
            self.history = [
                item for item in self.history
                if datetime.fromisoformat(item.timestamp) > cutoff_date
            ]
            
            removed_count = initial_count - len(self.history)
            
            if removed_count > 0:
                # Clean up collections
                self._cleanup_collections()
                self.save_history()
                self.logger.info(f"Cleaned up {removed_count} old history items")
            
            return removed_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up history: {e}")
            return 0
    
    def create_collection(self, name: str, item_timestamps: List[str] = None) -> bool:
        """
        Create a new collection.
        
        Args:
            name: Collection name
            item_timestamps: List of history item timestamps to include
            
        Returns:
            True if successful
        """
        try:
            if name in self.collections:
                self.logger.warning(f"Collection '{name}' already exists")
                return False
            
            self.collections[name] = item_timestamps or []
            self.save_history()
            self.logger.info(f"Created collection: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating collection: {e}")
            return False
    
    def add_to_collection(self, collection_name: str, timestamp: str) -> bool:
        """
        Add a history item to a collection.
        
        Args:
            collection_name: Name of the collection
            timestamp: History item timestamp
            
        Returns:
            True if successful
        """
        try:
            if collection_name not in self.collections:
                self.collections[collection_name] = []
            
            if timestamp not in self.collections[collection_name]:
                # Verify the history item exists
                if self.get_history_item(timestamp):
                    self.collections[collection_name].append(timestamp)
                    self.save_history()
                    self.logger.debug(f"Added item {timestamp} to collection {collection_name}")
                    return True
                else:
                    self.logger.warning(f"History item {timestamp} not found")
                    return False
            else:
                self.logger.debug(f"Item {timestamp} already in collection {collection_name}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error adding to collection: {e}")
            return False
    
    def remove_from_collection(self, collection_name: str, timestamp: str) -> bool:
        """
        Remove a history item from a collection.
        
        Args:
            collection_name: Name of the collection
            timestamp: History item timestamp
            
        Returns:
            True if successful
        """
        try:
            if collection_name in self.collections:
                if timestamp in self.collections[collection_name]:
                    self.collections[collection_name].remove(timestamp)
                    self.save_history()
                    self.logger.debug(f"Removed item {timestamp} from collection {collection_name}")
                    return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error removing from collection: {e}")
            return False
    
    def get_collection(self, name: str) -> List[RequestHistoryItem]:
        """
        Get items in a collection.
        
        Args:
            name: Collection name
            
        Returns:
            List of history items in the collection
        """
        if name not in self.collections:
            return []
        
        items = []
        for timestamp in self.collections[name]:
            item = self.get_history_item(timestamp)
            if item:
                items.append(item)
        
        return sorted(items, key=lambda x: x.timestamp, reverse=True)
    
    def get_collections(self) -> Dict[str, int]:
        """
        Get all collections with item counts.
        
        Returns:
            Dictionary of collection name -> item count
        """
        result = {}
        for name, timestamps in self.collections.items():
            # Count only existing items
            count = sum(1 for ts in timestamps if self.get_history_item(ts))
            result[name] = count
        return result
    
    def delete_collection(self, name: str) -> bool:
        """
        Delete a collection.
        
        Args:
            name: Collection name
            
        Returns:
            True if successful
        """
        try:
            if name in self.collections:
                del self.collections[name]
                self.save_history()
                self.logger.info(f"Deleted collection: {name}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error deleting collection: {e}")
            return False
    
    def export_history(self, filepath: str, collection_name: str = None) -> bool:
        """
        Export history to a file.
        
        Args:
            filepath: Export file path
            collection_name: Optional collection name to export
            
        Returns:
            True if successful
        """
        try:
            if collection_name:
                items = self.get_collection(collection_name)
                export_data = {
                    "type": "collection",
                    "name": collection_name,
                    "items": [item.to_dict() for item in items]
                }
            else:
                export_data = {
                    "type": "full_history",
                    "items": [item.to_dict() for item in self.history],
                    "collections": self.collections
                }
            
            export_data["export_date"] = datetime.now().isoformat()
            export_data["version"] = "1.0"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"History exported to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting history: {e}")
            return False
    
    def import_history(self, filepath: str, merge: bool = True) -> bool:
        """
        Import history from a file.
        
        Args:
            filepath: Import file path
            merge: Whether to merge with existing history
            
        Returns:
            True if successful
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if not merge:
                self.history.clear()
                self.collections.clear()
            
            # Import items
            items_data = import_data.get("items", [])
            for item_data in items_data:
                try:
                    item = RequestHistoryItem.from_dict(item_data)
                    # Check if item already exists (by timestamp)
                    if not any(h.timestamp == item.timestamp for h in self.history):
                        self.history.append(item)
                except Exception as e:
                    self.logger.warning(f"Error importing history item: {e}")
            
            # Import collections if present
            if "collections" in import_data:
                for name, timestamps in import_data["collections"].items():
                    if name not in self.collections:
                        self.collections[name] = []
                    # Add timestamps that don't already exist
                    for ts in timestamps:
                        if ts not in self.collections[name]:
                            self.collections[name].append(ts)
            
            # Maintain max items limit
            if len(self.history) > self.max_items:
                # Sort by timestamp and keep newest
                self.history.sort(key=lambda x: x.timestamp, reverse=True)
                self.history = self.history[:self.max_items]
            
            self.save_history()
            self.logger.info(f"History imported from {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error importing history: {e}")
            return False
    
    def load_history(self) -> bool:
        """
        Load history from database or settings.json file.
        
        Returns:
            True if successful
        """
        try:
            if self.use_database and self.db_settings_manager:
                # Load from database backend
                curl_settings = self.db_settings_manager.get_tool_settings(self.tool_key)
                if curl_settings:
                    # Load history items
                    self.history = []
                    for item_data in curl_settings.get("history", []):
                        try:
                            item = RequestHistoryItem.from_dict(item_data)
                            self.history.append(item)
                        except Exception as e:
                            self.logger.warning(f"Error loading history item: {e}")
                    
                    # Load collections
                    self.collections = curl_settings.get("collections", {})
                    
                    self.logger.info(f"Loaded {len(self.history)} history items from database")
                else:
                    self.logger.info("No history found in database, starting with empty history")
                return True
            
            # Fallback to JSON file
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    all_settings = json.load(f)
                
                # Get tool settings from tool_settings section
                tool_settings = all_settings.get("tool_settings", {})
                curl_settings = tool_settings.get(self.tool_key, {})
                
                # Load history items
                self.history = []
                for item_data in curl_settings.get("history", []):
                    try:
                        item = RequestHistoryItem.from_dict(item_data)
                        self.history.append(item)
                    except Exception as e:
                        self.logger.warning(f"Error loading history item: {e}")
                
                # Load collections
                self.collections = curl_settings.get("collections", {})
                
                self.logger.info(f"Loaded {len(self.history)} history items from {self.history_file}")
                return True
            else:
                self.logger.info("No history file found, starting with empty history")
                return True
                
        except Exception as e:
            self.logger.error(f"Error loading history: {e}")
            return False
    
    def save_history(self) -> bool:
        """
        Save history to database or settings.json file.
        
        Returns:
            True if successful
        """
        try:
            if self.use_database and self.db_settings_manager:
                # Save to database backend
                history_data = [item.to_dict() for item in self.history]
                self.db_settings_manager.set_tool_setting(self.tool_key, "history", history_data)
                self.db_settings_manager.set_tool_setting(self.tool_key, "collections", self.collections)
                self.db_settings_manager.set_tool_setting(self.tool_key, "history_last_updated", datetime.now().isoformat())
                self.db_settings_manager.set_tool_setting(self.tool_key, "history_version", "1.0")
                
                self.logger.debug("History saved to database")
                return True
            
            # Fallback to JSON file
            # Load existing settings file
            all_settings = {}
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    all_settings = json.load(f)
            
            # Ensure tool_settings section exists
            if "tool_settings" not in all_settings:
                all_settings["tool_settings"] = {}
            
            # Ensure cURL Tool section exists
            if self.tool_key not in all_settings["tool_settings"]:
                all_settings["tool_settings"][self.tool_key] = {}
            
            # Update history and collections in cURL Tool settings
            all_settings["tool_settings"][self.tool_key]["history"] = [item.to_dict() for item in self.history]
            all_settings["tool_settings"][self.tool_key]["collections"] = self.collections
            all_settings["tool_settings"][self.tool_key]["history_last_updated"] = datetime.now().isoformat()
            all_settings["tool_settings"][self.tool_key]["history_version"] = "1.0"
            
            # Write settings to file
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(all_settings, f, indent=4, ensure_ascii=False)
            
            self.logger.debug(f"History saved to {self.history_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving history: {e}")
            return False
    
    def _remove_from_collections(self, timestamp: str):
        """Remove a timestamp from all collections."""
        for collection_name in list(self.collections.keys()):
            if timestamp in self.collections[collection_name]:
                self.collections[collection_name].remove(timestamp)
    
    def _cleanup_collections(self):
        """Clean up collections by removing references to non-existent items."""
        for collection_name in list(self.collections.keys()):
            # Filter out timestamps that don't exist in history
            valid_timestamps = [
                ts for ts in self.collections[collection_name]
                if self.get_history_item(ts) is not None
            ]
            self.collections[collection_name] = valid_timestamps
            
            # Remove empty collections
            if not self.collections[collection_name]:
                del self.collections[collection_name]