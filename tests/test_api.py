#!/usr/bin/env python3
import requests
import json
import time
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_URL = "http://154.0.164.254:5000/api/rag-sql-chatbot/chat"
HEADERS = {"Content-Type": "application/json"}

# Test queries from UI tiles
TEST_QUERIES = [
    {"name": "Total Budget Query (Tile 1)", "message": "What is the total budget for infrastructure projects?"},
    {"name": "District Query (Tile 2)", "message": "Show me all projects in Zomba district"},
    {"name": "Completion Status Query (Tile 3)", "message": "List all completed projects"}
]

def test_query(query_name, message):
    """Test a single query and print the response"""
    print(f"\n\n{'=' * 50}")
    print(f"Testing: {query_name}")
    print(f"Query: {message}")
    print(f"{'-' * 50}")
    
    try:
        # Make the request
        start_time = time.time()
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json={"message": message},
            timeout=30
        )
        elapsed = time.time() - start_time
        
        # Print response status
        print(f"Status Code: {response.status_code} (in {elapsed:.2f}s)")
        
        # Print formatted response
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                
                # Extract and print just the message for readability
                if "response" in data and "results" in data["response"] and len(data["response"]["results"]) > 0:
                    message = data["response"]["results"][0].get("message", "")
                    print(f"\nExtracted Message: {message}")
                    
                    # Print SQL query if available
                    if "metadata" in data["response"] and "sql_query" in data["response"]["metadata"]:
                        sql = data["response"]["metadata"]["sql_query"]
                        if sql:
                            print(f"\nSQL Query: {sql}")
                
            except json.JSONDecodeError:
                print(f"Response (not JSON): {response.text}")
        else:
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print(f"{'=' * 50}")

def main():
    """Run all tests"""
    print(f"Testing API at: {API_URL}")
    
    # Run all tests
    for test in TEST_QUERIES:
        test_query(test["name"], test["message"])
        time.sleep(1)  # Small delay between requests

if __name__ == "__main__":
    main()
