"""
Quick test script for api_server.py
Tests health check, list tools, and execute endpoints
"""

import requests
import json
import time
import sys

API_URL = "http://localhost:8002"

def test_health():
    """Test health check endpoint"""
    print("\n[TEST] Health Check...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"[OK] Health check passed")
        print(f"   Status: {data.get('status')}")
        print(f"   Service: {data.get('service')}")
        return True
    except Exception as e:
        print(f"[ERROR] Health check failed: {e}")
        return False

def test_list_tools():
    """Test list tools endpoint"""
    print("\n[TEST] List Tools...")
    try:
        response = requests.get(f"{API_URL}/api/tools/google-suite/list", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"[OK] List tools passed")
        print(f"   Total tools: {data.get('total')}")
        print(f"   Sample tools: {list(data.get('tools', []))[:5]}")
        return True
    except Exception as e:
        print(f"[ERROR] List tools failed: {e}")
        return False

def test_execute_gmail_read():
    """Test Gmail read tool execution"""
    print("\n[TEST] Execute Gmail Read Tool...")
    try:
        payload = {
            "toolId": "gmail_read",
            "params": {
                "hours": 24,
                "unread_only": True,
                "maxResults": 5
            }
        }
        response = requests.post(
            f"{API_URL}/api/tools/google-suite/execute",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        print(f"[OK] Execute tool passed")
        print(f"   Success: {data.get('success')}")
        if data.get('output'):
            output = data.get('output', {})
            message = output.get('message', 'N/A')[:200]
            print(f"   Response: {message}...")
        if data.get('metadata'):
            print(f"   Execution time: {data.get('metadata', {}).get('execution_time_seconds', 'N/A')}s")
        return True
    except Exception as e:
        print(f"[ERROR] Execute tool failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Response: {e.response.text[:200]}")
        return False

def test_execute_calendar_list():
    """Test Calendar list tool execution"""
    print("\n[TEST] Execute Calendar List Tool...")
    try:
        payload = {
            "toolId": "google_calendar_list",
            "params": {
                "timeMin": "now",
                "maxResults": 5
            }
        }
        response = requests.post(
            f"{API_URL}/api/tools/google-suite/execute",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        print(f"[OK] Execute tool passed")
        print(f"   Success: {data.get('success')}")
        if data.get('output'):
            output = data.get('output', {})
            message = output.get('message', 'N/A')[:200]
            print(f"   Response: {message}...")
        return True
    except Exception as e:
        print(f"[ERROR] Execute tool failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Response: {e.response.text[:200]}")
        return False

def wait_for_server(max_wait=30):
    """Wait for server to be ready"""
    print(f"\n[INFO] Waiting for server at {API_URL}...")
    for i in range(max_wait):
        try:
            response = requests.get(f"{API_URL}/health", timeout=2)
            if response.status_code == 200:
                print(f"[OK] Server is ready!")
                return True
        except:
            pass
        time.sleep(1)
        if (i + 1) % 5 == 0:
            print(f"   Still waiting... ({i+1}/{max_wait}s)")
    print(f"[ERROR] Server did not start within {max_wait} seconds")
    return False

def main():
    """Run all tests"""
    print("="*60)
    print("API Server Test Suite")
    print("="*60)
    
    # Wait for server
    if not wait_for_server():
        print("\n[ERROR] Server is not running. Please start it first:")
        print("   uv run python api_server.py")
        sys.exit(1)
    
    # Run tests
    results = []
    results.append(("Health Check", test_health()))
    results.append(("List Tools", test_list_tools()))
    results.append(("Gmail Read", test_execute_gmail_read()))
    results.append(("Calendar List", test_execute_calendar_list()))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    for name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {name}")
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60)

if __name__ == "__main__":
    main()

