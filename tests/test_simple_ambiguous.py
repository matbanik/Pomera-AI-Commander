#!/usr/bin/env python3
"""Simple test to verify ambiguous detection is working"""
import pytest
from core.semantic_diff import SemanticDiffEngine, FormatParser

def test_ambigu Barabous_detection():
    """Test that ambiguous format raises ValueError"""
    confused = '{"name": "value"\nkey: value}'
    
    # First check what detect_format_with_confidence returns
    detected_format, confidence, candidates = FormatParser.detect_format_with_confidence(confused)
    print(f"\\nDetected: {detected_format}, Confidence: {confidence}")
    print(f"Candidates: {candidates}")
    
    # Now test if detect_format raises ValueError
    with pytest.raises(ValueError) as exc_info:
        FormatParser.detect_format(confused)
    
    assert "ambiguous" in str(exc_info.value).lower()
    print(f"\\n✓ ValueError raised: {exc_info.value}")

if __name__ == "__main__":
    test_ambiguous_detection()
