# test_smart_diff_realworld.py
# Real-world Smart Diff testing with direct Python API calls

import json
import os
from pathlib import Path
from core.semantic_diff import SemanticDiffEngine

# Setup paths
fixtures_dir = Path("tests/fixtures/realworld")
results = {}

print("=== Real-World Smart Diff Testing ===\n")

# Initialize engine
engine = SemanticDiffEngine()

# Test 1: JSON Comparison (package.json)
print("Test 1: JSON - package.json comparison")
with open(fixtures_dir / "package-before.json", "r", encoding="utf-8") as f:
    before_json = f.read()
with open(fixtures_dir / "package-after.json", "r", encoding="utf-8") as f:
    after_json = f.read()

result_json = engine.compare_2way(before_json, after_json, "json", {"include_stats": True})
results["json"] = result_json
with open(fixtures_dir / "result-json.json", "w", encoding="utf-8") as f:
    json.dump(result_json.__dict__, f, indent=2, default=str)
print(f"✓ Changes: {result_json.summary}\n")

# Test 2: YAML Comparison (docker-compose.yml)
print("Test 2: YAML - docker-compose comparison")
with open(fixtures_dir / "docker-compose-before.yml", "r", encoding="utf-8") as f:
    before_yaml = f.read()
with open(fixtures_dir / "docker-compose-after.yml", "r", encoding="utf-8") as f:
    after_yaml = f.read()

result_yaml = engine.compare_2way(before_yaml, after_yaml, "yaml", {"include_stats": True})
results["yaml"] = result_yaml
with open(fixtures_dir / "result-yaml.json", "w", encoding="utf-8") as f:
    json.dump(result_yaml.__dict__, f, indent=2, default=str)
print(f"✓ Changes: {result_yaml.summary}\n")

# Test 3: TOML Comparison (pyproject.toml)
print("Test 3: TOML - pyproject.toml comparison")
with open(fixtures_dir / "pyproject-before.toml", "r", encoding="utf-8") as f:
    before_toml = f.read()
with open(fixtures_dir / "pyproject-after.toml", "r", encoding="utf-8") as f:
    after_toml = f.read()

result_toml = engine.compare_2way(before_toml, after_toml, "toml", {"include_stats": True})
results["toml"] = result_toml
with open(fixtures_dir / "result-toml.json", "w", encoding="utf-8") as f:
    json.dump(result_toml.__dict__, f, indent=2, default=str)
print(f"✓ Changes: {result_toml.summary}\n")

# Test 4: ENV Comparison (.env)
print("Test 4: ENV - .env file comparison")
with open(fixtures_dir / "env-before.env", "r", encoding="utf-8") as f:
    before_env = f.read()
with open(fixtures_dir / "env-after.env", "r", encoding="utf-8") as f:
    after_env = f.read()

result_env = engine.compare_2way(before_env, after_env, "env", {"include_stats": True})
results["env"] = result_env
with open(fixtures_dir / "result-env.json", "w", encoding="utf-8") as f:
    json.dump(result_env.__dict__, f, indent=2, default=str)
print(f"✓ Changes: {result_env.summary}\n")

# Test 5: JSON5 Comparison (ts config.json with comments)
print("Test 5: JSON5 - tsconfig.json with comments")
with open(fixtures_dir / "tsconfig-before.json", "r", encoding="utf-8") as f:
    before_json5 = f.read()
with open(fixtures_dir / "tsconfig-after.json", "r", encoding="utf-8") as f:
    after_json5 = f.read()

result_json5 = engine.compare_2way(before_json5, after_json5, "json5", {"include_stats": True})
results["json5"] = result_json5
with open(fixtures_dir / "result-json5.json", "w", encoding="utf-8") as f:
    json.dump(result_json5.__dict__, f, indent=2, default=str)
print(f"✓ Changes: {result_json5.summary}\n")

# Test 6: Malformed JSON (error handling)
print("Test 6: Error Handling - Malformed JSON")
with open(fixtures_dir / "malformed.json", "r", encoding="utf-8") as f:
    malformed_json = f.read()

result_error = engine.compare_2way(malformed_json, after_json, "json", {})
results["error_json"] = result_error
with open(fixtures_dir / "result-error-json.json", "w", encoding="utf-8") as f:
    json.dump(result_error.__dict__, f, indent=2, default=str)
print(f"✓ Error captured: {result_error.error is not None}\n")

# Test 7: Malformed yaml (error handling)
print("Test 7: Error Handling - Malformed YAML")
with open(fixtures_dir / "malformed.yml", "r", encoding="utf-8") as f:
    malformed_yaml = f.read()

result_error_yaml = engine.compare_2way(malformed_yaml, after_yaml, "yaml", {})
results["error_yaml"] = result_error_yaml
with open(fixtures_dir / "result-error-yaml.json", "w", encoding="utf-8") as f:
    json.dump(result_error_yaml.__dict__, f, indent=2, default=str)
print(f"✓ Error captured: {result_error_yaml.error is not None}\n")

# Test 8: Auto Format Detection
print("Test 8: Auto Format Detection")
result_auto = engine.compare_2way(before_json, after_json, "auto", {"include_stats": True})
results["auto_detect"] = result_auto
with open(fixtures_dir / "result-auto-detect.json", "w", encoding="utf-8") as f:
    json.dump(result_auto.__dict__, f, indent=2, default=str)
print(f"✓ Detected format: {result_auto.format}\n")

print("=== All Tests Complete ===")
print(f"Results saved in: {fixtures_dir}")
print(f"\nSummary:")
print(f"- JSON: {len(results['json'].changes)} changes")
print(f"- YAML: {len(results['yaml'].changes)} changes")
print(f"- TOML: {len(results['toml'].changes)} changes")
print(f"- ENV: {len(results['env'].changes)} changes")
print(f"- JSON5: {len(results['json5'].changes)} changes")
print(f"- Error Handling: {'✓ Working' if results['error_json'].error else '✗ Failed'}")
print(f"- Auto Detection: {'✓ Detected as ' + results['auto_detect'].format if results['auto_detect'].format else '✗ Failed'}")
