#!/usr/bin/env python3

import requests
import json

# Server Testing Configuration
BACKEND_URL = "http://154.0.164.254:8000"    # Backend service on server
FRONTEND_URL = "http://154.0.164.254:3000"    # Frontend on server
API_PREFIX = "/api/rag-sql-chatbot"

def test_server_setup():
    """Test server endpoints during internal testing phase"""
    headers = {
        'Content-Type': 'application/json',
        'Origin': FRONTEND_URL,
        'Access-Control-Request-Method': 'POST'
    }

    print("\n=== Testing Server Environment ===")
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Backend URL: {BACKEND_URL}")

    # 1. Test Frontend Accessibility
    print("\n1. Checking Frontend...")
    try:
        frontend_response = requests.get(FRONTEND_URL)
        print(f"Frontend Status: {frontend_response.status_code}")
    except Exception as e:
        print(f"Frontend check failed: {e}")

    # 2. Test Backend Status
    print("\n2. Checking Backend Status...")
    try:
        status_url = f"{BACKEND_URL}{API_PREFIX}/status"
        print(f"Calling: {status_url}")
        status_response = requests.get(status_url, headers=headers)
        print(f"Status Code: {status_response.status_code}")
        print("Response:", json.dumps(status_response.json(), indent=2))
    except Exception as e:
        print(f"Backend status check failed: {e}")

    # 3. Test Query Endpoint
    print("\n3. Testing Query Endpoint...")
    try:
        query_url = f"{BACKEND_URL}{API_PREFIX}/query"
        payload = {
            "message": "Show me projects in Zomba district",
            "language": "en"
        }
        print(f"Calling: {query_url}")
        print("Payload:", json.dumps(payload, indent=2))
        query_response = requests.post(query_url, json=payload, headers=headers)
        print(f"Status Code: {query_response.status_code}")
        print("Response:", json.dumps(query_response.json(), indent=2))
    except Exception as e:
        print(f"Query test failed: {e}")

if __name__ == "__main__":
    test_server_setup() 