"""
Tests for MCP Security Manager (Circuit Breaker)

Tests the auto-lock mechanism, rate limiting, token limits,
and password unlock functionality.
"""

import pytest
import time
from unittest.mock import Mock, patch
from core.mcp_security_manager import (
    MCPSecurityManager,
    SecurityConfig,
    LockState,
    UsageRecord,
    get_security_manager,
    reset_security_manager
)


@pytest.fixture
def security_manager():
    """Create fresh security manager for each test."""
    reset_security_manager()
    manager = MCPSecurityManager()
    # Enable security for testing
    manager._config.enabled = True
    manager._config.rate_limit_per_minute = 5  # Low limit for testing
    manager._config.token_limit_per_hour = 1000
    manager._config.cost_limit_per_hour_usd = 0.10
    return manager


class TestSecurityConfig:
    """Tests for SecurityConfig dataclass."""
    
    def test_default_disabled(self):
        """Verify security is disabled by default."""
        config = SecurityConfig()
        assert config.enabled is False
    
    def test_default_rate_limit(self):
        """Verify default rate limit is 30/min."""
        config = SecurityConfig()
        assert config.rate_limit_per_minute == 30
    
    def test_from_dict(self):
        """Test config creation from dictionary."""
        data = {
            'mcp_security_enabled': True,
            'mcp_rate_limit_per_minute': 50,
            'mcp_token_limit_per_hour': 200000
        }
        config = SecurityConfig.from_dict(data)
        assert config.enabled is True
        assert config.rate_limit_per_minute == 50
        assert config.token_limit_per_hour == 200000


class TestMCPSecurityManager:
    """Tests for MCPSecurityManager class."""
    
    # =========================================================================
    # Basic State Tests
    # =========================================================================
    
    def test_disabled_by_default(self):
        """Verify manager is disabled by default."""
        reset_security_manager()
        manager = MCPSecurityManager()
        assert manager.is_enabled() is False
        assert manager.is_locked() is False
    
    def test_protected_tools_list(self):
        """Verify protected tools list."""
        manager = MCPSecurityManager()
        assert manager.is_protected("pomera_ai_tools") is True
        assert manager.is_protected("pomera_web_search") is True
        assert manager.is_protected("pomera_read_url") is True
        assert manager.is_protected("pomera_case_transform") is False
    
    # =========================================================================
    # Rate Limit Tests
    # =========================================================================
    
    def test_rate_limit_allows_under_threshold(self, security_manager):
        """Verify calls allowed when under rate limit."""
        for i in range(4):  # Under limit of 5
            allowed, error = security_manager.check_and_record("pomera_ai_tools")
            assert allowed is True
            assert error == ""
        
        assert security_manager.is_locked() is False
    
    def test_rate_limit_triggers_lock(self, security_manager):
        """Verify lock triggers when rate limit exceeded."""
        # Make calls up to the limit
        for i in range(5):
            security_manager.check_and_record("pomera_ai_tools")
        
        # Next call should trigger lock
        allowed, error = security_manager.check_and_record("pomera_ai_tools")
        
        assert allowed is False
        assert security_manager.is_locked() is True
        assert "Rate limit" in security_manager.get_lock_state().reason
    
    def test_rate_limit_resets_after_window(self, security_manager):
        """Verify rate limit resets after time window."""
        # Fill up rate limit
        for i in range(4):
            security_manager.check_and_record("pomera_ai_tools")
        
        # Simulate time passing (modify timestamps)
        for record in security_manager._usage_history:
            record.timestamp -= 65  # Move to more than 1 minute ago
        
        # Should be allowed now
        allowed, error = security_manager.check_and_record("pomera_ai_tools")
        assert allowed is True
    
    # =========================================================================
    # Token Limit Tests
    # =========================================================================
    
    def test_token_limit_allows_under_threshold(self, security_manager):
        """Verify calls allowed when under token limit."""
        allowed, error = security_manager.check_and_record("pomera_ai_tools", 500)
        assert allowed is True
        assert security_manager.is_locked() is False
    
    def test_token_limit_triggers_lock(self, security_manager):
        """Verify lock triggers when token limit exceeded."""
        # First call uses most of the budget
        security_manager.check_and_record("pomera_ai_tools", 800)
        
        # Second call should exceed limit (800 + 500 > 1000)
        allowed, error = security_manager.check_and_record("pomera_ai_tools", 500)
        
        assert allowed is False
        assert security_manager.is_locked() is True
        assert "Token limit" in security_manager.get_lock_state().reason
    
    # =========================================================================
    # Cost Limit Tests
    # =========================================================================
    
    def test_cost_limit_triggers_lock(self, security_manager):
        """Verify lock triggers when cost limit exceeded."""
        # Raise token limit high so we only test cost limit
        security_manager._config.token_limit_per_hour = 1_000_000
        
        # 10000 tokens at $0.003/1K = $0.03 per call
        # 4 calls = $0.12 > limit of $0.10
        
        # First few calls should be fine
        security_manager.check_and_record("pomera_ai_tools", 10000)
        security_manager.check_and_record("pomera_ai_tools", 10000)
        security_manager.check_and_record("pomera_ai_tools", 10000)
        
        # This should trigger cost limit
        allowed, error = security_manager.check_and_record("pomera_ai_tools", 10000)
        
        assert allowed is False
        assert security_manager.is_locked() is True
        assert "Cost limit" in security_manager.get_lock_state().reason
    
    # =========================================================================
    # Lock/Unlock Tests
    # =========================================================================
    
    def test_manual_lock(self, security_manager):
        """Test manual lock (panic button)."""
        security_manager.manual_lock("Testing panic button")
        
        assert security_manager.is_locked() is True
        assert "panic button" in security_manager.get_lock_state().reason
    
    def test_blocked_when_locked(self, security_manager):
        """Verify all calls blocked when locked."""
        security_manager.manual_lock("Test lock")
        
        allowed, error = security_manager.check_and_record("pomera_ai_tools")
        
        assert allowed is False
        assert "locked" in error.lower()
    
    def test_password_set_and_verify(self, security_manager):
        """Test password setting and verification."""
        security_manager.set_password("test123")
        security_manager.manual_lock("Test")
        
        # Wrong password should fail
        assert security_manager.unlock("wrong") is False
        assert security_manager.is_locked() is True
        
        # Correct password should work
        assert security_manager.unlock("test123") is True
        assert security_manager.is_locked() is False
    
    def test_unlock_clears_reason(self, security_manager):
        """Verify unlock clears lock reason."""
        security_manager.set_password("test123")
        security_manager.manual_lock("Test reason")
        security_manager.unlock("test123")
        
        state = security_manager.get_lock_state()
        assert state.locked is False
        assert state.reason == ""
    
    # =========================================================================
    # Token Estimation Tests
    # =========================================================================
    
    def test_estimate_tokens_short_text(self, security_manager):
        """Test token estimation for short text."""
        tokens = security_manager.estimate_tokens("Hello, world!")
        assert tokens > 0
        assert tokens < 20  # Short text should be few tokens
    
    def test_estimate_tokens_long_text(self, security_manager):
        """Test token estimation for longer text."""
        long_text = "This is a test sentence. " * 100
        tokens = security_manager.estimate_tokens(long_text)
        assert tokens > 100  # Long text should have many tokens
    
    # =========================================================================
    # Stats Tests
    # =========================================================================
    
    def test_get_stats(self, security_manager):
        """Test stats retrieval."""
        security_manager.check_and_record("pomera_ai_tools", 100)
        
        stats = security_manager.get_stats()
        
        assert 'enabled' in stats
        assert 'locked' in stats
        assert 'rate' in stats
        assert 'tokens' in stats
        assert 'cost' in stats
        assert stats['rate']['current'] == 1
        assert stats['tokens']['current'] == 100
    
    # =========================================================================
    # Disabled Security Tests
    # =========================================================================
    
    def test_disabled_allows_all(self):
        """Verify disabled security allows all calls."""
        reset_security_manager()
        manager = MCPSecurityManager()
        # Security disabled by default
        
        # Many calls should all be allowed
        for i in range(100):
            allowed, error = manager.check_and_record("pomera_ai_tools", 100000)
            assert allowed is True
        
        assert manager.is_locked() is False


class TestMCPSecurityIntegration:
    """Integration tests with MCP tool registry."""
    
    def test_ai_tools_security_import(self):
        """Verify security manager can be imported in tool registry."""
        from core.mcp_security_manager import get_security_manager
        security = get_security_manager()
        assert security is not None
    
    def test_ai_tools_returns_locked_error(self):
        """Verify AI tools returns locked error when security triggered."""
        from core.mcp.tool_registry import get_registry
        from core.mcp_security_manager import get_security_manager, reset_security_manager
        import json
        
        reset_security_manager()
        registry = get_registry()
        security = get_security_manager()
        
        # Enable and lock
        security._config.enabled = True
        security.manual_lock("Test lock for integration")
        
        # Call AI tools
        result = registry.execute('pomera_ai_tools', {
            "action": "generate",
            "provider": "OpenAI",
            "prompt": "Hello"
        })
        
        text = result.content[0].get('text', '{}')
        data = json.loads(text)
        
        assert data['success'] is False
        assert data.get('locked') is True
        assert "locked" in data['error'].lower()
        
        # Cleanup
        reset_security_manager()


class TestSecurityPassword:
    """Tests for password hashing."""
    
    def test_bcrypt_hashing(self):
        """Test bcrypt password hashing if available."""
        reset_security_manager()
        manager = MCPSecurityManager()
        manager._config.enabled = True
        
        manager.set_password("secure_password_123")
        
        # Hash should be stored
        assert manager._config.password_hash != ""
        assert manager._config.password_hash != "secure_password_123"
        
        # Verify works
        manager.manual_lock("test")
        assert manager.unlock("secure_password_123") is True
    
    def test_wrong_password_rejected(self):
        """Test wrong password is rejected."""
        reset_security_manager()
        manager = MCPSecurityManager()
        manager._config.enabled = True
        manager.set_password("correct_password")
        manager.manual_lock("test")
        
        assert manager.unlock("wrong_password") is False
        assert manager.is_locked() is True
