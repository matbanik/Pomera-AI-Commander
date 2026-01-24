#!/usr/bin/env python3
"""
Standalone test script for Vertex AI authentication and API access.
Tests the service account JSON file and API connectivity.
"""

import json
import sys
import requests
from pathlib import Path
import io

# Fix Windows console encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    print("ERROR: google-auth library not installed.")
    print("Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2")
    sys.exit(1)

# Configuration
JSON_FILE = "quitnot.com_api-project-1086985281187-b9dd25f4eed9.json"
PROJECT_ID = "quitnot.com:api-project-1086985281187"
LOCATION = "us-central1"
MODEL = "gemini-2.5-flash"  # Try this first
# Alternative models to try if the above doesn't work:
# MODEL = "gemini-1.5-flash"
# MODEL = "gemini-1.5-pro"

def load_credentials(json_file):
    """Load service account credentials from JSON file."""
    print(f"Loading credentials from: {json_file}")
    
    if not Path(json_file).exists():
        print(f"ERROR: File not found: {json_file}")
        sys.exit(1)
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        print(f"✓ JSON file loaded successfully")
        print(f"  Project ID: {json_data.get('project_id')}")
        print(f"  Client Email: {json_data.get('client_email')}")
        
        # Create credentials
        credentials = service_account.Credentials.from_service_account_info(
            json_data,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        print(f"✓ Credentials object created")
        
        # Refresh token if needed
        if not credentials.valid:
            print("Refreshing access token...")
            request = Request()
            credentials.refresh(request)
            print(f"✓ Access token obtained")
        else:
            print(f"✓ Credentials are valid")
        
        return credentials, json_data
        
    except Exception as e:
        print(f"ERROR loading credentials: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def test_vertex_ai_api(credentials, project_id, location, model):
    """Test Vertex AI API with a simple request."""
    print("\n" + "="*60)
    print("Testing Vertex AI API")
    print("="*60)
    
    # Get access token
    access_token = credentials.token
    print(f"✓ Access token obtained (length: {len(access_token)})")
    
    # Build URL
    url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model}:generateContent"
    print(f"\nRequest URL:")
    print(f"  {url}")
    
    # Build payload
    payload = {
        "contents": [{
            "parts": [{
                "text": "Hello, this is a test. Please respond with 'Test successful'."
            }],
            "role": "user"
        }]
    }
    
    # Build headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    print(f"\nRequest Headers:")
    print(f"  Content-Type: {headers['Content-Type']}")
    print(f"  Authorization: Bearer {access_token[:20]}...{access_token[-10:]}")
    
    print(f"\nRequest Payload:")
    print(json.dumps(payload, indent=2))
    
    print(f"\nMaking API request...")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        print(f"\nResponse Body:")
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=2))
        except:
            print(response.text)
        
        if response.status_code == 200:
            print("\n" + "="*60)
            print("✓ SUCCESS! API request completed successfully")
            print("="*60)
            
            # Extract response text
            if 'candidates' in response_json and len(response_json['candidates']) > 0:
                result_text = response_json['candidates'][0].get('content', {}).get('parts', [{}])[0].get('text', '')
                print(f"\nAI Response:")
                print(f"  {result_text}")
            
            return True
        else:
            print("\n" + "="*60)
            print(f"✗ ERROR: API request failed with status {response.status_code}")
            print("="*60)
            
            # Detailed error analysis
            if response.status_code == 403:
                print("\n403 Forbidden Error Analysis:")
                print("Common causes:")
                print("  1. Vertex AI API not enabled for the project")
                print("  2. Service account missing 'Vertex AI User' role")
                print("  3. Billing not enabled for the project")
                print("  4. Model name incorrect or not available in region")
                print("  5. Project ID format issue")
                
                if 'error' in response_json:
                    error_info = response_json['error']
                    print(f"\nError details from API:")
                    print(f"  Message: {error_info.get('message', 'N/A')}")
                    print(f"  Status: {error_info.get('status', 'N/A')}")
                    if 'details' in error_info:
                        print(f"  Details: {json.dumps(error_info['details'], indent=2)}")
            
            elif response.status_code == 404:
                print("\n404 Not Found Error Analysis:")
                print("Possible issues:")
                print("  1. Model name is incorrect")
                print("  2. Model not available in the selected region")
                print("  3. Project ID is incorrect")
                print(f"\nTry these models instead:")
                print(f"  - gemini-1.5-flash")
                print(f"  - gemini-1.5-pro")
                print(f"  - gemini-1.0-pro")
            
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Network Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*60)
    print("Vertex AI API Test Script")
    print("="*60)
    print()
    
    # Load credentials
    credentials, json_data = load_credentials(JSON_FILE)
    
    # Verify project ID matches
    if json_data.get('project_id') != PROJECT_ID:
        print(f"\nWARNING: Project ID in JSON ({json_data.get('project_id')}) doesn't match configured PROJECT_ID ({PROJECT_ID})")
        print(f"Using project ID from JSON file: {json_data.get('project_id')}")
        actual_project_id = json_data.get('project_id')
    else:
        actual_project_id = PROJECT_ID
    
    # Test API
    success = test_vertex_ai_api(credentials, actual_project_id, LOCATION, MODEL)
    
    if not success:
        print("\n" + "="*60)
        print("Troubleshooting Steps:")
        print("="*60)
        print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
        print(f"2. Select project: {actual_project_id}")
        print("3. Enable Vertex AI API:")
        print("   - Go to 'APIs & Services' > 'Library'")
        print("   - Search for 'Vertex AI API'")
        print("   - Click 'Enable'")
        print("4. Check service account permissions:")
        print(f"   - Go to 'IAM & Admin' > 'IAM'")
        print(f"   - Find service account: {json_data.get('client_email')}")
        print("   - Ensure it has 'Vertex AI User' role")
        print("5. Verify billing is enabled for the project")
        print("6. Try different model names:")
        print("   - gemini-1.5-flash")
        print("   - gemini-1.5-pro")
        print("   - gemini-1.0-pro")
        print("="*60)
        sys.exit(1)
    else:
        print("\n✓ All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()

