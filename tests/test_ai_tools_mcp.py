"""
MCP integration tests for AI Tools (pomera_ai_tools)

Tests the pomera_ai_tools MCP tool registration and execution.
"""

import pytest
import json
from core.mcp.tool_registry import get_registry


def get_result(result):
    """Extract result dict from MCP result."""
    if hasattr(result, 'content') and result.content:
        text = result.content[0].get('text', '{}')
        return json.loads(text)
    return {}


@pytest.fixture(scope="module")
def tool_registry():
    """Get shared ToolRegistry for testing."""
    return get_registry()


class TestAIToolsMCP:
    """MCP integration tests for pomera_ai_tools."""
    
    # =========================================================================
    # Registration Tests
    # =========================================================================
    
    def test_tool_registration(self, tool_registry):
        """Verify pomera_ai_tools is registered in MCP."""
        tools = {tool.name for tool in tool_registry.list_tools()}
        assert 'pomera_ai_tools' in tools
    
    def test_tool_schema(self, tool_registry):
        """Verify tool has correct input schema."""
        tools = {tool.name: tool for tool in tool_registry.list_tools()}
        tool = tools.get('pomera_ai_tools')
        
        assert tool is not None
        assert 'action' in tool.inputSchema['properties']
        assert 'prompt' in tool.inputSchema['properties']
        assert 'provider' in tool.inputSchema['properties']
        assert 'model' in tool.inputSchema['properties']
        assert 'system_prompt' in tool.inputSchema['properties']
        assert 'temperature' in tool.inputSchema['properties']
        assert 'top_p' in tool.inputSchema['properties']
        assert 'top_k' in tool.inputSchema['properties']
        assert 'max_tokens' in tool.inputSchema['properties']
        assert 'stop_sequences' in tool.inputSchema['properties']
        
        # Verify action enum
        action_schema = tool.inputSchema['properties']['action']
        assert 'enum' in action_schema
        assert set(action_schema['enum']) == {'generate', 'list_providers', 'list_models'}
    
    # =========================================================================
    # list_providers Action Tests
    # =========================================================================
    
    def test_list_providers(self, tool_registry):
        """Test list_providers action returns all supported providers."""
        result = tool_registry.execute('pomera_ai_tools', {
            "action": "list_providers"
        })
        
        data = get_result(result)
        assert data['success'] is True
        assert 'providers' in data
        assert len(data['providers']) == 11
        
        # Check expected providers are present
        providers = set(data['providers'])
        assert 'OpenAI' in providers
        assert 'Anthropic AI' in providers
        assert 'Google AI' in providers
        assert 'Groq AI' in providers
        assert 'Azure AI' in providers
        assert 'AWS Bedrock' in providers
    
    def test_list_providers_default_action(self, tool_registry):
        """Test that list_providers works with explicit action."""
        result = tool_registry.execute('pomera_ai_tools', {
            "action": "list_providers"
        })
        
        data = get_result(result)
        assert data['success'] is True
        assert data['count'] == 11
    
    # =========================================================================
    # list_models Action Tests
    # =========================================================================
    
    def test_list_models_requires_provider(self, tool_registry):
        """Test list_models requires provider parameter."""
        result = tool_registry.execute('pomera_ai_tools', {
            "action": "list_models"
        })
        
        data = get_result(result)
        assert data['success'] is False
        assert 'error' in data
        assert 'provider' in data['error'].lower()
    
    def test_list_models_unknown_provider(self, tool_registry):
        """Test list_models with unknown provider returns empty list."""
        result = tool_registry.execute('pomera_ai_tools', {
            "action": "list_models",
            "provider": "Unknown Provider"
        })
        
        data = get_result(result)
        assert data['success'] is True
        assert data['models'] == []
        assert data['count'] == 0
    
    # =========================================================================
    # generate Action Tests
    # =========================================================================
    
    def test_generate_requires_provider(self, tool_registry):
        """Test generate action requires provider."""
        result = tool_registry.execute('pomera_ai_tools', {
            "action": "generate",
            "prompt": "Hello"
        })
        
        data = get_result(result)
        assert data['success'] is False
        assert 'provider' in data['error'].lower()
    
    def test_generate_requires_prompt(self, tool_registry):
        """Test generate action requires prompt."""
        result = tool_registry.execute('pomera_ai_tools', {
            "action": "generate",
            "provider": "OpenAI"
        })
        
        data = get_result(result)
        assert data['success'] is False
        assert 'prompt' in data['error'].lower()
    
    def test_generate_no_api_key_error(self, tool_registry):
        """Test generate without API key returns helpful error."""
        result = tool_registry.execute('pomera_ai_tools', {
            "action": "generate",
            "provider": "OpenAI",
            "prompt": "Hello, world!"
        })
        
        data = get_result(result)
        # Without a configured API key, should fail gracefully
        assert data['success'] is False
        assert 'provider' in data and data['provider'] == 'OpenAI'
    
    def test_generate_standalone_database_access(self, tool_registry):
        """Test AI Tools can access database in standalone mode (no GUI context).
        
        This test verifies the fix for the app context bug where AI Tools
        couldn't access the database when running standalone (outside GUI).
        
        The test confirms database access is working by checking:
        - If no API key configured: Gets "API key not configured" error (proves DB was queried)
        - If API key IS configured: Should either succeed or fail with API error (proves DB was queried)
        - Should NOT fail with "NoneType" or "database not accessible" errors
        """
        result = tool_registry.execute('pomera_ai_tools', {
            "action": "generate",
            "provider": "Google AI",
            "model": "gemini-2.5-flash",
            "prompt": "Hello, world!",
            "max_tokens": 50
        })
        
        data = get_result(result)
        
        # Test passes if:
        # 1. Database was accessed (no NoneType errors)
        # 2. Provider and model were read from args
        assert 'provider' in data
        assert data['provider'] == 'Google AI'
        assert 'model' in data
        assert data['model'] == 'gemini-2.5-flash'
        
        # Should not have database access errors
        if not data['success']:
            error_msg = data.get('error', '').lower()
            # These would indicate database access failure:
            assert 'nonetype' not in error_msg, "Database manager was None (app context bug)"
            assert 'database not accessible' not in error_msg
            assert 'failed to load' not in error_msg or 'api key' in error_msg

    
    # =========================================================================
    # Unknown Action Tests
    # =========================================================================
    
    def test_unknown_action(self, tool_registry):
        """Test unknown action returns error."""
        result = tool_registry.execute('pomera_ai_tools', {
            "action": "unknown_action"
        })
        
        data = get_result(result)
        assert data['success'] is False
        assert 'unknown' in data['error'].lower()
    
    # =========================================================================
    # Parameter Validation Tests
    # =========================================================================
    
    def test_temperature_parameter_type(self, tool_registry):
        """Verify temperature parameter accepts float."""
        tools = {tool.name: tool for tool in tool_registry.list_tools()}
        tool = tools.get('pomera_ai_tools')
        
        temp_schema = tool.inputSchema['properties']['temperature']
        assert temp_schema['type'] == 'number'
    
    def test_max_tokens_parameter_type(self, tool_registry):
        """Verify max_tokens parameter accepts integer."""
        tools = {tool.name: tool for tool in tool_registry.list_tools()}
        tool = tools.get('pomera_ai_tools')
        
        tokens_schema = tool.inputSchema['properties']['max_tokens']
        assert tokens_schema['type'] == 'integer'
    
    def test_top_k_parameter_type(self, tool_registry):
        """Verify top_k parameter accepts integer."""
        tools = {tool.name: tool for tool in tool_registry.list_tools()}
        tool = tools.get('pomera_ai_tools')
        
        topk_schema = tool.inputSchema['properties']['top_k']
        assert topk_schema['type'] == 'integer'


class TestAIToolsEngine:
    """Direct tests for AIToolsEngine class."""
    
    def test_engine_import(self):
        """Test AIToolsEngine can be imported."""
        from core.ai_tools_engine import AIToolsEngine
        engine = AIToolsEngine()
        assert engine is not None
    
    def test_engine_list_providers(self):
        """Test engine list_providers method."""
        from core.ai_tools_engine import AIToolsEngine
        engine = AIToolsEngine()
        
        providers = engine.list_providers()
        assert len(providers) == 11
        assert 'OpenAI' in providers
        assert 'Google AI' in providers
    
    def test_engine_estimate_complexity(self):
        """Test engine complexity estimation."""
        from core.ai_tools_engine import AIToolsEngine
        engine = AIToolsEngine()
        
        estimation = engine.estimate_complexity("Hello, world!")
        assert 'estimated_seconds' in estimation
        assert 'should_show_progress' in estimation
        assert estimation['should_show_progress'] is True
    
    def test_result_dataclass(self):
        """Test AIToolsResult dataclass."""
        from core.ai_tools_engine import AIToolsResult
        
        result = AIToolsResult(
            success=True,
            response="Test response",
            provider="OpenAI",
            model="gpt-4"
        )
        
        result_dict = result.to_dict()
        assert result_dict['success'] is True
        assert result_dict['response'] == "Test response"
        assert result_dict['provider'] == "OpenAI"
        assert result_dict['model'] == "gpt-4"
