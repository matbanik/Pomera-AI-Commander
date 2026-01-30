"""
MCP Security Manager - Circuit Breaker for Protected Tools

This module provides proactive security for MCP tools that access
paid APIs (AI providers, web search). It monitors usage patterns
and automatically locks protected tools when thresholds are exceeded.

**DISABLED BY DEFAULT** - Opt-in for security-conscious users.

Features:
- Rate limiting (calls per minute)
- Token/cost estimation (for AI calls)
- Automatic lock on threshold breach
- Password-protected unlock

Protected tools:
- pomera_ai_tools (AI providers - incurs API costs)
- pomera_web_search (Web search - may incur costs)
- pomera_read_url (URL reading - may be abused)
"""

import logging
import time
import hashlib
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List, Deque

logger = logging.getLogger(__name__)


@dataclass
class UsageRecord:
    """Record of a single MCP tool call."""
    tool_name: str
    timestamp: float
    estimated_tokens: int = 0
    estimated_cost_usd: float = 0.0


@dataclass
class SecurityConfig:
    """Configuration for MCP security circuit breaker."""
    enabled: bool = False  # DISABLED by default
    rate_limit_per_minute: int = 30
    token_limit_per_hour: int = 100_000
    cost_limit_per_hour_usd: float = 1.00
    password_hash: str = ""  # bcrypt hash
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SecurityConfig':
        # Handle nested mcp_security dict from settings registry
        mcp_data = data.get('mcp_security', data)
        return cls(
            enabled=mcp_data.get('enabled', data.get('mcp_security_enabled', False)),
            rate_limit_per_minute=mcp_data.get('rate_limit_per_minute', data.get('mcp_rate_limit_per_minute', 30)),
            token_limit_per_hour=mcp_data.get('token_limit_per_hour', data.get('mcp_token_limit_per_hour', 100_000)),
            cost_limit_per_hour_usd=mcp_data.get('cost_limit_per_hour', data.get('mcp_cost_limit_per_hour', 1.00)),
            password_hash=mcp_data.get('password_hash', data.get('mcp_security_password_hash', ''))
        )


@dataclass
class LockState:
    """Current lock state."""
    locked: bool = False
    reason: str = ""
    locked_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'locked': self.locked,
            'reason': self.reason,
            'locked_at': self.locked_at.isoformat() if self.locked_at else None
        }


class MCPSecurityManager:
    """
    Proactive security manager for MCP tools.
    
    Monitors usage of protected MCP tools and automatically locks them
    when suspicious activity is detected (rate/cost thresholds exceeded).
    
    **DISABLED BY DEFAULT** - Must be explicitly enabled via UI settings.
    
    Usage:
        security = get_security_manager()
        
        # Check if tools are locked
        if security.is_locked():
            return "Tools locked - unlock via UI"
        
        # Record a call and check thresholds
        allowed, error = security.check_and_record("pomera_ai_tools", estimated_tokens=1000)
        if not allowed:
            return error  # Auto-locked due to threshold breach
        
        # Unlock with password
        if security.unlock("user_password"):
            print("Unlocked!")
    """
    
    # Tools that require security monitoring
    PROTECTED_TOOLS = frozenset([
        "pomera_ai_tools",
        "pomera_web_search", 
        "pomera_read_url"
    ])
    
    # Approximate cost per 1K tokens (conservative estimate)
    # Used for rough cost estimation when tiktoken not available
    COST_PER_1K_TOKENS = 0.003  # $0.003 per 1K tokens (GPT-4o-mini rate)
    
    def __init__(self, db_settings_manager=None):
        """
        Initialize security manager.
        
        Args:
            db_settings_manager: Database settings manager for persistence
        """
        self.db = db_settings_manager
        self._config = SecurityConfig()
        self._lock_state = LockState()
        self._usage_history: Deque[UsageRecord] = deque(maxlen=1000)
        self._logger = logging.getLogger(__name__)
        
        # Load config and state from database
        self._load_state()
    
    def _load_state(self) -> None:
        """Load configuration and lock state from database."""
        if not self.db:
            return
        
        try:
            # Load config
            settings = {}
            for key in ['mcp_security_enabled', 'mcp_rate_limit_per_minute',
                       'mcp_token_limit_per_hour', 'mcp_cost_limit_per_hour',
                       'mcp_security_password_hash']:
                value = self.db.get_setting(key)
                if value is not None:
                    settings[key] = value
            
            self._config = SecurityConfig.from_dict(settings)
            
            # Load lock state
            locked = self.db.get_setting('mcp_security_locked')
            if locked:
                self._lock_state.locked = bool(locked)
                self._lock_state.reason = self.db.get_setting('mcp_lock_reason') or ""
                lock_time = self.db.get_setting('mcp_lock_timestamp')
                if lock_time:
                    self._lock_state.locked_at = datetime.fromisoformat(lock_time)
                    
        except Exception as e:
            self._logger.warning(f"Failed to load security state: {e}")
    
    def _save_lock_state(self) -> None:
        """Persist lock state to database."""
        if not self.db:
            return
        
        try:
            self.db.set_setting('mcp_security_locked', self._lock_state.locked)
            self.db.set_setting('mcp_lock_reason', self._lock_state.reason)
            if self._lock_state.locked_at:
                self.db.set_setting('mcp_lock_timestamp', 
                                   self._lock_state.locked_at.isoformat())
        except Exception as e:
            self._logger.error(f"Failed to save lock state: {e}")
    
    def is_enabled(self) -> bool:
        """Check if security monitoring is enabled."""
        return self._config.enabled
    
    def is_locked(self) -> bool:
        """Check if protected tools are currently locked."""
        return self._config.enabled and self._lock_state.locked
    
    def is_protected(self, tool_name: str) -> bool:
        """Check if a tool is in the protected list."""
        return tool_name in self.PROTECTED_TOOLS
    
    def get_lock_state(self) -> LockState:
        """Get current lock state."""
        return self._lock_state
    
    def check_and_record(
        self, 
        tool_name: str, 
        estimated_tokens: int = 0
    ) -> Tuple[bool, str]:
        """
        Check thresholds and record a tool call.
        
        This is called BEFORE executing a protected tool. It:
        1. Checks if security is enabled
        2. Checks if currently locked
        3. Checks rate/token/cost thresholds
        4. Auto-locks if thresholds exceeded
        5. Records the call for future monitoring
        
        Args:
            tool_name: Name of the MCP tool being called
            estimated_tokens: Estimated input+output tokens (0 if unknown)
        
        Returns:
            (allowed, error_message) - allowed=True if call can proceed
        """
        # Security disabled - always allow
        if not self._config.enabled:
            return True, ""
        
        # Already locked
        if self._lock_state.locked:
            return False, self._format_locked_error()
        
        # Not a protected tool - allow
        if tool_name not in self.PROTECTED_TOOLS:
            return True, ""
        
        now = time.time()
        
        # Check rate limit (calls in last minute)
        one_minute_ago = now - 60
        recent_calls = sum(1 for r in self._usage_history 
                         if r.timestamp > one_minute_ago and 
                            r.tool_name in self.PROTECTED_TOOLS)
        
        if recent_calls >= self._config.rate_limit_per_minute:
            self._trigger_lock(f"Rate limit exceeded: {recent_calls} calls in last minute "
                              f"(limit: {self._config.rate_limit_per_minute})")
            return False, self._format_locked_error()
        
        # Check token limit (tokens in last hour)
        one_hour_ago = now - 3600
        recent_tokens = sum(r.estimated_tokens for r in self._usage_history
                          if r.timestamp > one_hour_ago)
        
        if recent_tokens + estimated_tokens > self._config.token_limit_per_hour:
            self._trigger_lock(f"Token limit exceeded: {recent_tokens + estimated_tokens} tokens "
                              f"in last hour (limit: {self._config.token_limit_per_hour})")
            return False, self._format_locked_error()
        
        # Check cost limit (estimated cost in last hour)
        recent_cost = sum(r.estimated_cost_usd for r in self._usage_history
                         if r.timestamp > one_hour_ago)
        estimated_cost = estimated_tokens * self.COST_PER_1K_TOKENS / 1000
        
        if recent_cost + estimated_cost > self._config.cost_limit_per_hour_usd:
            self._trigger_lock(f"Cost limit exceeded: ${recent_cost + estimated_cost:.4f} "
                              f"in last hour (limit: ${self._config.cost_limit_per_hour_usd:.2f})")
            return False, self._format_locked_error()
        
        # Record this call
        record = UsageRecord(
            tool_name=tool_name,
            timestamp=now,
            estimated_tokens=estimated_tokens,
            estimated_cost_usd=estimated_cost
        )
        self._usage_history.append(record)
        
        return True, ""
    
    def _trigger_lock(self, reason: str) -> None:
        """Lock protected tools with reason."""
        self._lock_state.locked = True
        self._lock_state.reason = reason
        self._lock_state.locked_at = datetime.now()
        self._save_lock_state()
        
        self._logger.warning(f"🔒 MCP Security: Auto-locked - {reason}")
    
    def _format_locked_error(self) -> str:
        """Format user-friendly locked error message."""
        return (
            f"🔒 MCP tools locked due to unusual activity.\n\n"
            f"Reason: {self._lock_state.reason}\n"
            f"Locked at: {self._lock_state.locked_at}\n\n"
            f"To unlock: Open Pomera UI → Settings → MCP Security → Enter password"
        )
    
    def unlock(self, password: str) -> bool:
        """
        Attempt to unlock protected tools.
        
        Args:
            password: User-provided password
            
        Returns:
            True if unlocked successfully
        """
        if not self._config.password_hash:
            self._logger.warning("No password set - cannot unlock")
            return False
        
        # Verify password using bcrypt
        try:
            import bcrypt
            password_bytes = password.encode('utf-8')
            hash_bytes = self._config.password_hash.encode('utf-8')
            
            if bcrypt.checkpw(password_bytes, hash_bytes):
                self._lock_state.locked = False
                self._lock_state.reason = ""
                self._lock_state.locked_at = None
                self._save_lock_state()
                self._logger.info("🔓 MCP Security: Unlocked by user")
                return True
            else:
                self._logger.warning("🔒 MCP Security: Incorrect password attempt")
                return False
                
        except ImportError:
            # Fallback to SHA-256 if bcrypt not available
            self._logger.warning("bcrypt not available, using SHA-256 fallback")
            hash_attempt = hashlib.sha256(password.encode()).hexdigest()
            if hash_attempt == self._config.password_hash:
                self._lock_state.locked = False
                self._lock_state.reason = ""
                self._lock_state.locked_at = None
                self._save_lock_state()
                return True
            return False
    
    def set_password(self, password: str) -> bool:
        """
        Set or update the unlock password.
        
        Args:
            password: New password (will be hashed)
            
        Returns:
            True if password was set
        """
        if not password:
            return False
        
        try:
            import bcrypt
            password_bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()
            hash_bytes = bcrypt.hashpw(password_bytes, salt)
            self._config.password_hash = hash_bytes.decode('utf-8')
        except ImportError:
            # Fallback to SHA-256 if bcrypt not available
            self._logger.warning("bcrypt not available, using SHA-256 fallback")
            self._config.password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Save to database
        if self.db:
            self.db.set_setting('mcp_security_password_hash', self._config.password_hash)
        
        return True
    
    def manual_lock(self, reason: str = "Manual lock by user") -> None:
        """Manually lock protected tools (panic button)."""
        self._trigger_lock(reason)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get current usage statistics.
        
        Returns:
            Dictionary with usage stats for UI display
        """
        now = time.time()
        one_minute_ago = now - 60
        one_hour_ago = now - 3600
        
        # Calculate current usage
        recent_calls = sum(1 for r in self._usage_history 
                         if r.timestamp > one_minute_ago and 
                            r.tool_name in self.PROTECTED_TOOLS)
        
        recent_tokens = sum(r.estimated_tokens for r in self._usage_history
                          if r.timestamp > one_hour_ago)
        
        recent_cost = sum(r.estimated_cost_usd for r in self._usage_history
                         if r.timestamp > one_hour_ago)
        
        return {
            'enabled': self._config.enabled,
            'locked': self._lock_state.locked,
            'lock_reason': self._lock_state.reason,
            'lock_time': self._lock_state.locked_at.isoformat() if self._lock_state.locked_at else None,
            'rate': {
                'current': recent_calls,
                'limit': self._config.rate_limit_per_minute,
                'percent': int((recent_calls / self._config.rate_limit_per_minute) * 100)
            },
            'tokens': {
                'current': recent_tokens,
                'limit': self._config.token_limit_per_hour,
                'percent': int((recent_tokens / self._config.token_limit_per_hour) * 100)
            },
            'cost': {
                'current_usd': round(recent_cost, 4),
                'limit_usd': self._config.cost_limit_per_hour_usd,
                'percent': int((recent_cost / self._config.cost_limit_per_hour_usd) * 100)
            },
            'history_count': len(self._usage_history)
        }
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Uses tiktoken if available, otherwise rough estimate.
        
        Args:
            text: Input text to estimate
            
        Returns:
            Estimated token count
        """
        try:
            import tiktoken
            enc = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
            return len(enc.encode(text))
        except ImportError:
            # Rough estimate: ~4 chars per token
            return len(text) // 4


# Singleton instance
_security_manager: Optional[MCPSecurityManager] = None


def get_security_manager(db_settings_manager=None) -> MCPSecurityManager:
    """
    Get the singleton MCPSecurityManager instance.
    
    Args:
        db_settings_manager: Optional database manager (used on first call)
        
    Returns:
        MCPSecurityManager singleton
    """
    global _security_manager
    
    if _security_manager is None:
        _security_manager = MCPSecurityManager(db_settings_manager)
    
    return _security_manager


def reset_security_manager() -> None:
    """Reset singleton for testing."""
    global _security_manager
    _security_manager = None
