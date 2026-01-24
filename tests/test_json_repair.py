"""
Tests for JSON repair functionality in semantic_diff.py
Tests automatic repair of common LLM-generated JSON issues.
"""

import unittest
from core.semantic_diff import FormatParser


class TestJSONRepair(unittest.TestCase):
    """Test suite for FormatParser.repair_json method"""
    
    def test_remove_markdown_fences(self):
        """Test removal of markdown code fences"""
        text = """```json
{"name": "Alice", "age": 30}
```"""
        repaired, repairs = FormatParser.repair_json(text)
        
        self.assertIn("Removed opening markdown fence", repairs)
        self.assertIn("Removed closing markdown fence", repairs)
        self.assertNotIn('```', repaired)
        self.assertIn('"name"', repaired)
    
    def test_remove_only_opening_fence(self):
        """Test removal when only opening fence present"""
        text = """```json
{"name": "Bob"}"""
        repaired, repairs = FormatParser.repair_json(text)
        
        self.assertEqual(len(repairs), 1)
        self.assertIn("opening", repairs[0].lower())
        self.assertNotIn('```', repaired)
    
    def test_extract_json_from_prose(self):
        """Test extraction of JSON from surrounding text"""
        text = """Here is the config:
{"api_key": "secret123", "enabled": true}
That's all!"""
        repaired, repairs = FormatParser.repair_json(text)
        
        self.assertIn("Extracted JSON from prose", repairs)
        self.assertTrue(repaired.startswith('{'))
        # Prose before JSON should be removed
        self.assertNotIn("Here is", repaired)
    
    def test_remove_trailing_commas(self):
        """Test removal of trailing commas (common LLM mistake)"""
        text = """
{
  "items": [1, 2, 3,],
  "name": "test",
}
"""
        repaired, repairs = FormatParser.repair_json(text)
        
        self.assertIn("Removed trailing commas", repairs)
        # Trailing commas should be removed
        self.assertNotIn(',]', repaired)
        self.assertNotIn(',}', repaired)
    
    def test_multiple_repairs(self):
        """Test applying multiple repairs at once"""
        text = """```
Here's the JSON: {"key": "value",}
```"""
        repaired, repairs = FormatParser.repair_json(text)
        
        # Should have all three repairs
        self.assertGreaterEqual(len(repairs), 2)
        repair_text = ' '.join(repairs)
        self.assertIn("markdown", repair_text.lower())
    
    def test_no_repairs_needed(self):
        """Test when JSON is already valid"""
        text = '{"name": "Alice", "age": 30}'
        repaired, repairs = FormatParser.repair_json(text)
        
        self.assertEqual(len(repairs), 0)
        self.assertEqual(text, repaired)
    
    def test_parse_with_auto_repair(self):
        """Test that parse method uses auto-repair"""
        # Malformed JSON with markdown fences
        text = """```json
{"status": "ok", "count": 42,}
```"""
        # parse() should automatically repair and succeed
        result = FormatParser.parse(text, 'json')
        
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['count'], 42)
    
    def test_repair_llm_style_output(self):
        """Test repairing typical LLM JSON output with explanation"""
        text = """Based on your request, here's the configuration:
```json
{
  "server": {
    "host": "localhost",
    "port": 8080,
  },
}
```
This should work for your needs."""
        
        repaired, repairs = FormatParser.repair_json(text)
        
        # Should have multiple repairs
        self.assertGreater(len(repairs), 0)
        # Should be able to parse after repair
        import json
        try:
            json.loads(repaired)
            parsed_successfully = True
        except:
            parsed_successfully = False
        
        self.assertTrue(parsed_successfully)
    
    def test_nested_arrays_with_trailing_commas(self):
        """Test trailing comma removal in nested structures"""
        text = """
{
  "data": [
    {"id": 1,},
    {"id": 2,},
  ],
}
"""
        repaired, repairs = FormatParser.repair_json(text)
        
        self.assertIn("Removed trailing commas", repairs)
        # All trailing commas should be removed
        import re
        self.assertIsNone(re.search(r',\s*[}\]]', repaired))
    
    def test_json_with_array_start(self):
        """Test extracting JSON array from prose"""
        text = """The results are:
[
  {"name": "Alice"},
  {"name": "Bob"}
]
End of results."""
        
        repaired, repairs = FormatParser.repair_json(text)
        
        if repairs:
            self.assertIn("prose", repairs[0].lower())
        self.assertTrue(repaired.strip().startswith('['))


if __name__ == '__main__':
    unittest.main()
