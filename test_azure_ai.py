#!/usr/bin/env python3
"""
Standalone test script for Azure AI Foundry/Azure OpenAI connectivity.
Tests API key authentication and API access.
"""

import json
import sys
import requests
import re
import io
import argparse

# Fix Windows console encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Default configuration
DEFAULT_API_VERSION = "2024-10-21"
DEFAULT_MODEL = "gpt-4.1"

def normalize_endpoint(endpoint):
    """
    Normalize endpoint URL and auto-detect if it's Azure AI Foundry or Azure OpenAI.
    Returns: (normalized_endpoint, endpoint_type, resource_name)
    """
    endpoint = endpoint.strip().rstrip('/')
    
    # Azure AI Foundry: https://[resource].services.ai.azure.com
    # Or project endpoint: https://[resource].services.ai.azure.com/api/projects/[project-name]
    if ".services.ai.azure.com" in endpoint:
        match = re.search(r'https://([^.]+)\.services\.ai\.azure\.com', endpoint)
        if match:
            resource_name = match.group(1)
            # Extract base resource endpoint
            if "/api/projects/" in endpoint:
                # Project endpoint - extract base resource
                normalized = f"https://{resource_name}.services.ai.azure.com"
                return normalized, "Azure AI Foundry (Project)", resource_name
            else:
                return endpoint, "Azure AI Foundry", resource_name
    
    # Azure OpenAI: https://[resource].openai.azure.com or https://[resource].cognitiveservices.azure.com
    elif ".openai.azure.com" in endpoint or ".cognitiveservices.azure.com" in endpoint:
        # Try openai.azure.com first
        match = re.search(r'https://([^.]+)\.openai\.azure\.com', endpoint)
        if match:
            resource_name = match.group(1)
            return endpoint, "Azure OpenAI", resource_name
        # Try cognitiveservices.azure.com
        match = re.search(r'https://([^.]+)\.cognitiveservices\.azure\.com', endpoint)
        if match:
            resource_name = match.group(1)
            return endpoint, "Azure OpenAI", resource_name
    
    # Unknown format, return as-is
    return endpoint, "Unknown", ""

def build_api_url(endpoint, model, api_version):
    """
    Build the API URL based on endpoint type.
    """
    endpoint_normalized, endpoint_type, _ = normalize_endpoint(endpoint)
    
    # Azure AI Foundry uses: /models/chat/completions (model in request body)
    # Azure OpenAI uses: /openai/deployments/{model}/chat/completions (model in URL)
    if endpoint_type == "Azure AI Foundry" or endpoint_type == "Azure AI Foundry (Project)":
        # Foundry format: model goes in request body, not URL
        url = f"{endpoint_normalized}/models/chat/completions?api-version={api_version}"
    elif endpoint_type == "Azure OpenAI":
        # Azure OpenAI format: model in URL path
        url = f"{endpoint_normalized}/openai/deployments/{model}/chat/completions?api-version={api_version}"
    else:
        # Unknown format - assume Foundry format by default
        url = f"{endpoint_normalized}/models/chat/completions?api-version={api_version}"
    return url

def test_azure_ai_api(api_key, endpoint, deployment_name, api_version=DEFAULT_API_VERSION):
    """Test Azure AI API with a simple request."""
    print("\n" + "="*60)
    print("Testing Azure AI API")
    print("="*60)
    
    # Validate inputs
    if not api_key or api_key.strip() == "":
        print("ERROR: API Key is required")
        return False
    
    if not endpoint or endpoint.strip() == "":
        print("ERROR: Resource Endpoint is required")
        return False
    
    if not deployment_name or deployment_name.strip() == "":
        print("ERROR: Deployment Name is required")
        return False
    
    # Normalize endpoint - remove trailing slashes to avoid double slashes
    endpoint = endpoint.strip().rstrip('/')
    endpoint_normalized, endpoint_type, resource_name = normalize_endpoint(endpoint)
    endpoint_normalized = endpoint_normalized.rstrip('/')  # Ensure no trailing slash
    
    print(f"\nEndpoint Information:")
    print(f"  Original: {endpoint}")
    print(f"  Normalized: {endpoint_normalized}")
    print(f"  Type: {endpoint_type}")
    if resource_name:
        print(f"  Resource: {resource_name}")
    
    # Build URL
    url = build_api_url(endpoint_normalized, deployment_name, api_version)
    # Ensure URL doesn't have double slashes
    url = url.replace('://', '://temp').replace('//', '/').replace('://temp', '://')
    print(f"\nRequest URL:")
    print(f"  {url}")
    
    # Build headers
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    print(f"\nRequest Headers:")
    print(f"  Content-Type: {headers['Content-Type']}")
    print(f"  api-key: {api_key[:10]}...{api_key[-5:] if len(api_key) > 15 else ''}")
    
    print(f"\nAPI Version: {api_version}")
    print(f"Deployment/Model: {deployment_name}")
    print(f"\n⚠️  IMPORTANT: Deployment names are CASE-SENSITIVE!")
    print(f"   Make sure '{deployment_name}' matches exactly (case) as in Azure Portal")
    
    # Build payload - strategy depends on endpoint type
    # For Azure OpenAI: model is in URL, but some API versions accept it in payload too
    # For Azure AI Foundry: model MUST be in payload
    base_payload = {
        "messages": [
            {
                "role": "user",
                "content": "Hello, this is a test. Please respond with 'Test successful'."
            }
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    # Strategy: For Azure OpenAI, try without model in payload first (recommended)
    # For Azure AI Foundry, model must be in payload
    payloads_to_try = []
    
    if endpoint_type == "Azure AI Foundry" or endpoint_type == "Azure AI Foundry (Project)":
        # Foundry: model MUST be in payload
        payload = base_payload.copy()
        payload["model"] = deployment_name
        payloads_to_try = [("With model in payload (required for Foundry)", payload)]
    elif endpoint_type == "Azure OpenAI":
        # Azure OpenAI: model is in URL, try without model first (recommended), then with model
        payload_no_model = base_payload.copy()
        payload_with_model = base_payload.copy()
        payload_with_model["model"] = deployment_name
        payloads_to_try = [
            ("Without model in payload (recommended for Azure OpenAI)", payload_no_model),
            ("With model in payload (fallback)", payload_with_model)
        ]
    else:
        # Unknown: try both strategies
        payload_no_model = base_payload.copy()
        payload_with_model = base_payload.copy()
        payload_with_model["model"] = deployment_name
        payloads_to_try = [
            ("Without model in payload", payload_no_model),
            ("With model in payload", payload_with_model)
        ]
    
    print(f"\nMaking API request(s)...")
    
    last_error = None
    for attempt_name, payload in payloads_to_try:
        print(f"\n{'='*60}")
        print(f"Attempt: {attempt_name}")
        print(f"{'='*60}")
        print(f"Request Payload:")
        print(json.dumps(payload, indent=2))
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            print(f"\nResponse Status Code: {response.status_code}")
            print(f"Response Headers:")
            for key, value in response.headers.items():
                if key.lower() in ['content-type', 'content-length', 'x-request-id', 'apim-request-id']:
                    print(f"  {key}: {value}")
            
            print(f"\nResponse Body:")
            try:
                response_json = response.json()
                print(json.dumps(response_json, indent=2))
            except:
                print(response.text[:1000])  # First 1000 chars if not JSON
            
            if response.status_code == 200:
                print("\n" + "="*60)
                print("✓ SUCCESS! API request completed successfully")
                print("="*60)
                
                # Extract response text
                if 'choices' in response_json and len(response_json['choices']) > 0:
                    result_text = response_json['choices'][0].get('message', {}).get('content', '')
                    print(f"\nAI Response:")
                    print(f"  {result_text}")
                    
                    # Show usage info if available
                    if 'usage' in response_json:
                        usage = response_json['usage']
                        print(f"\nToken Usage:")
                        print(f"  Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
                        print(f"  Completion tokens: {usage.get('completion_tokens', 'N/A')}")
                        print(f"  Total tokens: {usage.get('total_tokens', 'N/A')}")
                
                return True
            else:
                last_error = (response.status_code, response)
                # Continue to next attempt if available
                if len(payloads_to_try) > 1 and payloads_to_try.index((attempt_name, payload)) < len(payloads_to_try) - 1:
                    print(f"\n⚠️  Attempt failed with status {response.status_code}, trying next strategy...")
                    continue
                else:
                    # Last attempt failed, show detailed error
                    break
                
        except requests.exceptions.Timeout:
            last_error = ("timeout", None)
            print(f"\n✗ Network Error: Request timed out after 30 seconds")
            if len(payloads_to_try) > 1 and payloads_to_try.index((attempt_name, payload)) < len(payloads_to_try) - 1:
                print("  Trying next strategy...")
                continue
            break
        except requests.exceptions.ConnectionError as e:
            last_error = ("connection", str(e))
            print(f"\n✗ Network Error: Could not connect to endpoint")
            print(f"  Error: {e}")
            if len(payloads_to_try) > 1 and payloads_to_try.index((attempt_name, payload)) < len(payloads_to_try) - 1:
                print("  Trying next strategy...")
                continue
            break
        except requests.exceptions.RequestException as e:
            last_error = ("request", str(e))
            print(f"\n✗ Network Error: {e}")
            if len(payloads_to_try) > 1 and payloads_to_try.index((attempt_name, payload)) < len(payloads_to_try) - 1:
                print("  Trying next strategy...")
                continue
            break
        except Exception as e:
            last_error = ("exception", str(e))
            print(f"\n✗ Unexpected Error: {e}")
            import traceback
            traceback.print_exc()
            if len(payloads_to_try) > 1 and payloads_to_try.index((attempt_name, payload)) < len(payloads_to_try) - 1:
                print("  Trying next strategy...")
                continue
            break
    
    # All attempts failed
    print("\n" + "="*60)
    print("✗ ERROR: All API request attempts failed")
    print("="*60)
    
    # Handle last error
    if isinstance(last_error, tuple) and len(last_error) == 2:
        status_code, response = last_error
        if isinstance(status_code, int):
            # HTTP error
            error_details = {}
            try:
                error_details = response.json()
            except:
                error_details = {"error": response.text[:500] if response else "No response"}
            
            if status_code == 401:
                print("\n401 Unauthorized Error Analysis:")
                print("Common causes:")
                print("  1. Invalid API Key")
                print("  2. API Key expired or revoked")
                print("  3. Wrong API Key for this resource")
                print("\nSolution:")
                print("  - Verify your API key in Azure Portal")
                print("  - Ensure you're using the correct key for this resource")
                if 'error' in error_details:
                    print(f"\nError details from API:")
                    print(f"  {json.dumps(error_details.get('error', {}), indent=2)}")
            
            elif status_code == 404:
                print("\n404 Not Found Error Analysis:")
                print("="*60)
                print("Based on common issues found in Azure OpenAI documentation:")
                print("\nMost Common Causes (in order of likelihood):")
                print("  1. ✗ Deployment name mismatch (CASE-SENSITIVE!)")
                print(f"     Current deployment name: '{deployment_name}'")
                print("     → Check Azure Portal and ensure EXACT match (case matters!)")
                print("     → Common mistake: 'gpt-4.1' vs 'GPT-4.1' vs 'gpt-41'")
                print("\n  2. ✗ Deployment doesn't exist in this resource/region")
                print(f"     Resource: {resource_name if resource_name else endpoint_normalized}")
                print("     → Verify deployment exists in Azure Portal > Your Resource > Deployments")
                print("     → Ensure deployment is in the same resource/region as your endpoint")
                print("\n  3. ✗ API version incompatible with deployment/model")
                print(f"     Current API version: {api_version}")
                print("     → Try these API versions (newest first):")
                print("        • 2025-01-01-preview (latest)")
                print("        • 2024-10-21")
                print("        • 2024-02-15-preview")
                print("        • 2023-12-01-preview")
                print("     → For GPT-4.1 and GPT-4o, use: 2024-02-15-preview or later")
                print("\n  4. ✗ URL format issue")
                print(f"     Current URL: {url}")
                if endpoint_type == "Azure OpenAI":
                    print("     → Should be: .../openai/deployments/{deployment-name}/chat/completions?api-version=...")
                    print("     → Check: No double slashes, deployment name matches exactly")
                else:
                    print("     → Should be: .../models/chat/completions?api-version=...")
                    print("     → Model should be in request body, not URL")
                print("\n  5. ✗ Missing /chat in URL path")
                print("     → URL must include '/chat/completions', not just '/completions'")
                print("     → This is a common mistake from documentation examples")
                
                if 'error' in error_details:
                    error_info = error_details.get('error', {})
                    print(f"\nError details from API:")
                    print(f"  Message: {error_info.get('message', 'N/A')}")
                    print(f"  Code: {error_info.get('code', 'N/A')}")
                    
                    # Check for specific error messages
                    error_msg = str(error_info.get('message', '')).lower()
                    if 'deployment' in error_msg and 'not found' in error_msg:
                        print("\n⚠️  SPECIFIC ISSUE: Deployment not found")
                        print("   → Double-check deployment name spelling and case in Azure Portal")
                        print("   → Verify the deployment exists and is active")
                    elif 'api deployment' in error_msg:
                        print("\n⚠️  SPECIFIC ISSUE: API deployment issue")
                        print("   → The deployment may not be active or may be in a different region")
                    elif 'resource' in error_msg and 'not found' in error_msg:
                        print("\n⚠️  SPECIFIC ISSUE: Resource not found")
                        print("   → Verify your endpoint URL is correct")
                        print("   → Check that the resource exists in Azure Portal")
                
                print("\n" + "="*60)
                print("Recommended Fixes (try in this order):")
                print("="*60)
                print("1. Verify deployment name in Azure Portal:")
                print("   - Go to Azure Portal > Your Resource > Deployments")
                print("   - Copy the EXACT deployment name (including case)")
                print("   - Common issue: Case sensitivity - 'gpt-4.1' ≠ 'GPT-4.1'")
                print()
                print("2. Verify deployment exists in the same resource:")
                print(f"   - Resource: {resource_name if resource_name else endpoint_normalized}")
                print("   - Deployments are resource/region specific")
                print()
                print("3. Try a different API version:")
                print("   python test_azure_ai.py --api-key YOUR_KEY --endpoint YOUR_ENDPOINT \\")
                print("     --deployment YOUR_DEPLOYMENT --api-version 2025-01-01-preview")
                print()
                print("4. Verify URL format:")
                print(f"   Current: {url}")
                print("   - No trailing slashes before path")
                print("   - No double slashes")
                print("   - Includes '/chat/completions'")
                print("="*60)
            
            elif status_code == 400:
                print("\n400 Bad Request Error Analysis:")
                print("Possible issues:")
                print("  1. API version is not supported")
                print(f"  2. Model/deployment name format issue")
                print("  3. Request payload format issue")
                if 'error' in error_details:
                    error_info = error_details.get('error', {})
                    print(f"\nError details from API:")
                    print(f"  Message: {error_info.get('message', 'N/A')}")
                    print(f"  Code: {error_info.get('code', 'N/A')}")
            
            elif status_code == 429:
                print("\n429 Too Many Requests Error Analysis:")
                print("You've exceeded the rate limit for this resource.")
                print("Solution:")
                print("  - Wait a few moments and try again")
                print("  - Check your rate limits in Azure Portal")
            
            else:
                print(f"\n{status_code} Error:")
                if 'error' in error_details:
                    error_info = error_details.get('error', {})
                    print(f"  Message: {error_info.get('message', 'N/A')}")
                    print(f"  Code: {error_info.get('code', 'N/A')}")
        elif status_code == "timeout":
            print("\n✗ Network Error: Request timed out after 30 seconds")
            print("  - Check your internet connection")
            print("  - Verify the endpoint URL is accessible")
        elif status_code == "connection":
            print("\n✗ Network Error: Could not connect to endpoint")
            print(f"  Error: {last_error[1]}")
            print("  - Verify the endpoint URL is correct")
            print("  - Check your network connection")
            print("  - Ensure the endpoint is accessible from your network")
        elif status_code == "request":
            print(f"\n✗ Network Error: {last_error[1]}")
        elif status_code == "exception":
            print(f"\n✗ Unexpected Error: {last_error[1]}")
    
    return False

def get_user_input(prompt, default=None, password=False):
    """Get user input with optional default value."""
    if default:
        prompt_text = f"{prompt} [{default}]: "
    else:
        prompt_text = f"{prompt}: "
    
    if password:
        import getpass
        value = getpass.getpass(prompt_text)
    else:
        value = input(prompt_text).strip()
    
    return value if value else default

def main():
    parser = argparse.ArgumentParser(
        description="Test Azure AI Foundry/Azure OpenAI connectivity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python test_azure_ai.py
  
  # Command line arguments
  python test_azure_ai.py --api-key YOUR_KEY --endpoint https://your-resource.services.ai.azure.com --deployment gpt-4.1
  
  # Azure OpenAI
  python test_azure_ai.py --api-key YOUR_KEY --endpoint https://your-resource.openai.azure.com --deployment gpt-4
  
  # Azure OpenAI (cognitiveservices.azure.com)
  python test_azure_ai.py --api-key YOUR_KEY --endpoint https://your-resource.cognitiveservices.azure.com --deployment gpt-4.1
  
  # Custom API version
  python test_azure_ai.py --api-key YOUR_KEY --endpoint https://your-resource.services.ai.azure.com --deployment gpt-4.1 --api-version 2024-02-15-preview
        """
    )
    
    parser.add_argument('--api-key', '-k', help='API Key')
    parser.add_argument('--endpoint', '-e', help='Resource Endpoint URL')
    parser.add_argument('--deployment', '-d', help='Deployment Name (Model)')
    parser.add_argument('--api-version', '-v', default=DEFAULT_API_VERSION, help=f'API Version (default: {DEFAULT_API_VERSION})')
    
    args = parser.parse_args()
    
    print("="*60)
    print("Azure AI API Test Script")
    print("="*60)
    print()
    
    # Get inputs (command line args or interactive)
    api_key = args.api_key or get_user_input("Enter API Key", password=True)
    endpoint = args.endpoint or get_user_input("Enter Resource Endpoint", default="https://your-resource.services.ai.azure.com")
    deployment_name = args.deployment or get_user_input("Enter Deployment Name (Model)", default=DEFAULT_MODEL)
    api_version = args.api_version
    
    # Test API
    success = test_azure_ai_api(api_key, endpoint, deployment_name, api_version)
    
    if not success:
        print("\n" + "="*60)
        print("Troubleshooting Steps:")
        print("="*60)
        print("1. Verify your API Key:")
        print("   - Azure AI Foundry: https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-models/how-to/quickstart-ai-project")
        print("   - Azure OpenAI: https://portal.azure.com > Your Resource > Keys and Endpoint")
        print()
        print("2. Verify your Resource Endpoint:")
        print("   - Should be: https://[resource-name].services.ai.azure.com (Foundry)")
        print("   - Or: https://[resource-name].openai.azure.com (Azure OpenAI)")
        print("   - Or: https://[resource-name].cognitiveservices.azure.com (Azure OpenAI)")
        print("   - Or: https://[resource-name].services.ai.azure.com/api/projects/[project-name] (Foundry Project)")
        print()
        print("3. Verify your Deployment Name:")
        print("   - Check in Azure Portal that the deployment exists")
        print("   - Ensure the deployment name matches exactly (case-sensitive)")
        print()
        print("4. Check API Version:")
        print(f"   - Current: {api_version}")
        print("   - Try: 2024-10-21, 2024-02-15-preview, or 2023-12-01-preview")
        print()
        print("5. Verify Network Access:")
        print("   - Ensure you can reach the endpoint from your network")
        print("   - Check firewall/proxy settings if applicable")
        print("="*60)
        sys.exit(1)
    else:
        print("\n✓ All tests passed! Azure AI is properly configured.")
        print("\nYou can now use these settings in Pomera AI Commander:")
        print(f"  API Key: {api_key[:10]}...{api_key[-5:] if len(api_key) > 15 else ''}")
        print(f"  Resource Endpoint: {endpoint}")
        print(f"  Deployment/Model: {deployment_name}")
        print(f"  API Version: {api_version}")
        sys.exit(0)

if __name__ == "__main__":
    main()
