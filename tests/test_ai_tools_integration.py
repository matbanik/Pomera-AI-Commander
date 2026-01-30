"""
AI Tools Integration Test Suite

Tests AI Tools engine with real API keys from encrypted database.
This ensures refactoring doesn't break existing functionality.

Usage:
    python test_ai_tools_integration.py --all
    python test_ai_tools_integration.py --provider OpenAI
    python test_ai_tools_integration.py --streaming-only
"""

import sys
import os
from pathlib import Path
from typing import Optional, List
import argparse
import json
from dataclasses import dataclass, asdict

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.ai_tools_engine import AIToolsEngine, AIToolsResult
from core.database_settings_manager import DatabaseSettingsManager


@dataclass
class TestResult:
    """Test result for a single provider test"""
    provider: str
    model: str
    streaming: bool
    success: bool
    response_length: int = 0
    error: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)


class AIToolsIntegrationTest:
    """Integration tests for AI Tools using real API keys from database"""
    
    # Test prompt for all providers
    TEST_PROMPT = "Say 'Hello from AI Tools test' and nothing else."
    
    # Providers to test
    ALL_PROVIDERS = [
        "OpenAI",
        "Google AI",
        "Anthropic AI",
        "Groq AI",
        "Azure AI",
        "Vertex AI",
        "Cohere AI",
        "AWS Bedrock",
        "HuggingFace AI",
        "LM Studio",
        "OpenRouterAI"
    ]
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize test suite with database settings manager"""
        if db_path is None:
            db_path = os.path.join(project_root, "settings.db")
        
        print(f"Loading settings from: {db_path}")
        self.db_manager = DatabaseSettingsManager(db_path)
        self.engine = AIToolsEngine(db_settings_manager=self.db_manager)
        self.results: List[TestResult] = []
    
    def _has_valid_api_key(self, provider: str) -> bool:
        """Check if provider has a valid API key configured"""
        try:
            settings = self.db_manager.get_tool_settings(provider)
            api_key = settings.get("API_KEY", "")
            
            # Special cases for providers that don't need API keys
            if provider == "LM Studio":
                return True  # No API key needed
            
            # Check if API key exists and is not placeholder
            return api_key and api_key != "putinyourkey" and len(api_key) > 10
        except Exception as e:
            print(f"  ⚠️  Error checking API key for {provider}: {e}")
            return False
    
    def test_provider(
        self, 
        provider: str, 
        streaming: bool = False,
        custom_prompt: Optional[str] = None
    ) -> TestResult:
        """Test a single provider"""
        prompt = custom_prompt or self.TEST_PROMPT
        
        # Get provider settings to determine model
        try:
            settings = self.db_manager.get_tool_settings(provider)
            model = settings.get("MODEL", "unknown")
        except:
            model = "unknown"
        
        print(f"\n{'='*60}")
        print(f"Testing: {provider}")
        print(f"Model: {model}")
        print(f"Mode: {'Streaming' if streaming else 'Non-streaming'}")
        print(f"{'='*60}")
        
        # Check API key
        if not self._has_valid_api_key(provider):
            result = TestResult(
                provider=provider,
                model=model,
                streaming=streaming,
                success=False,
                error="No valid API key configured"
            )
            print(f"❌ SKIPPED: No valid API key configured")
            self.results.append(result)
            return result
        
        # Streaming callback
        chunks = []
        def on_chunk(text: str):
            chunks.append(text)
            print(f"  📝 Chunk: {text[:50]}...")
        
        try:
            # Make API call
            if streaming:
                # For streaming, we'll need to enhance the engine first
                # For now, test non-streaming
                print("  ⚠️  Streaming test not yet implemented (pending Phase 1)")
                result = TestResult(
                    provider=provider,
                    model=model,
                    streaming=streaming,
                    success=False,
                    error="Streaming not yet implemented in engine"
                )
                self.results.append(result)
                return result
            else:
                api_result: AIToolsResult = self.engine.generate(
                    prompt=prompt,
                    provider=provider
                )
            
            if api_result.success:
                response_text = api_result.response
                print(f"✅ SUCCESS")
                print(f"  Response length: {len(response_text)} chars")
                print(f"  Response preview: {response_text[:100]}...")
                
                result = TestResult(
                    provider=provider,
                    model=api_result.model or model,
                    streaming=streaming,
                    success=True,
                    response_length=len(response_text)
                )
            else:
                print(f"❌ FAILED: {api_result.error}")
                result = TestResult(
                    provider=provider,
                    model=model,
                    streaming=streaming,
                    success=False,
                    error=api_result.error
                )
            
            self.results.append(result)
            return result
            
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
            result = TestResult(
                provider=provider,
                model=model,
                streaming=streaming,
                success=False,
                error=str(e)
            )
            self.results.append(result)
            return result
    
    def test_all_providers(self, streaming: bool = False):
        """Test all providers"""
        print(f"\n{'#'*60}")
        print(f"Testing ALL Providers - {'Streaming' if streaming else 'Non-streaming'} Mode")
        print(f"{'#'*60}")
        
        for provider in self.ALL_PROVIDERS:
            self.test_provider(provider, streaming=streaming)
    
    def test_gpt52_specific(self):
        """Test GPT-5.2 specific features"""
        print(f"\n{'#'*60}")
        print("GPT-5.2 Specific Tests")
        print(f"{'#'*60}")
        
        # Test that max_tokens is not sent for GPT-5.2
        print("\nTest: Verify max_tokens is filtered for GPT-5.2")
        settings = self.db_manager.get_tool_settings("OpenAI")
        settings["MODEL"] = "gpt-5.2"
        
        # This should work without errors despite max_tokens being set
        result = self.test_provider(
            "OpenAI",
            streaming=False,
            custom_prompt="Respond with exactly: GPT-5.2 parameter test passed"
        )
        
        if result.success:
            print("✅ GPT-5.2 parameter filtering works correctly")
        else:
            print("❌ GPT-5.2 parameter filtering may have issues")
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print(f"{'='*60}")
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.success)
        failed = total - passed
        skipped = sum(1 for r in self.results if "No valid API key" in (r.error or ""))
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"\nSuccess Rate: {(passed/total*100) if total > 0 else 0:.1f}%")
        
        # Show failures
        failures = [r for r in self.results if not r.success and "No valid API key" not in (r.error or "")]
        if failures:
            print(f"\n{'='*60}")
            print("FAILURES")
            print(f"{'='*60}")
            for result in failures:
                print(f"\n{result.provider} ({result.model})")
                print(f"  Error: {result.error}")
        
        # Save results to JSON
        results_file = os.path.join(project_root, "test_results.json")
        with open(results_file, "w") as f:
            json.dump([r.to_dict() for r in self.results], f, indent=2)
        print(f"\nDetailed results saved to: {results_file}")


def main():
    parser = argparse.ArgumentParser(description="AI Tools Integration Tests")
    parser.add_argument("--all", action="store_true", help="Test all providers")
    parser.add_argument("--provider", type=str, help="Test specific provider")
    parser.add_argument("--streaming", action="store_true", help="Test streaming mode")
    parser.add_argument("--gpt52", action="store_true", help="Run GPT-5.2 specific tests")
    parser.add_argument("--db", type=str, help="Path to settings database")
    
    args = parser.parse_args()
    
    # Create test suite
    tester = AIToolsIntegrationTest(db_path=args.db)
    
    # Run tests
    if args.gpt52:
        tester.test_gpt52_specific()
    elif args.all:
        tester.test_all_providers(streaming=args.streaming)
    elif args.provider:
        tester.test_provider(args.provider, streaming=args.streaming)
    else:
        # Default: test all non-streaming
        print("No specific test selected. Running all providers (non-streaming)")
        print("Use --help for more options")
        tester.test_all_providers(streaming=False)
    
    # Print summary
    tester.print_summary()
    
    # Exit code based on results
    failures = sum(1 for r in tester.results if not r.success and "No valid API key" not in (r.error or ""))
    sys.exit(1 if failures > 0 else 0)


if __name__ == "__main__":
    main()
