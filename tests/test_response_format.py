import requests
import json
from typing import List, Dict

def check_database():
    """Check if the database is accessible"""
    base_url = "http://localhost:8000"
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            result = response.json()
            db_status = result.get("services", {}).get("database", "error")
            if db_status == "ok":
                print("✓ Database connection successful")
                return True
            else:
                print("✗ Database connection error")
                return False
    except Exception as e:
        print(f"✗ Error checking database: {str(e)}")
        return False

def test_response_format():
    """Test RAG SQL response formatting"""
    
    # First check database connection
    print("Checking database connection...")
    print("-" * 50)
    if not check_database():
        print("Cannot proceed with tests - database connection required")
        return
    
    # Test cases with different types of queries
    test_cases = [
        {
            "message": "List all road construction projects",
            "language": "english",
            "expected_categories": ["Project", "Location"]
        },
        {
            "message": "Show projects in Lilongwe district",
            "language": "english",
            "expected_categories": ["Project", "Location"]
        },
        {
            "message": "Details about 'Nachuma Market Shed phase 3'",
            "language": "english",
            "expected_categories": ["Project", "Location", "Financial Details", "Timeline", "Contractor Details"]
        },
        {
            "message": "Show me project code MW-CR-DO",
            "language": "english",
            "expected_categories": ["Project", "Location", "Financial Details", "Timeline", "Contractor Details"]
        },
        {
            "message": "What is the status of 'Rehabilitation of Mzimba Hospital'",
            "language": "english",
            "expected_categories": ["Project", "Location", "Financial Details", "Timeline", "Contractor Details"]
        },
        {
            "message": "Expenditure for 'Construction of Mchinji District Hospital'",
            "language": "english",
            "expected_categories": ["Project", "Location", "Financial Details", "Timeline", "Contractor Details"]
        },
        {
            "message": "Покажите проекты в районе Лилонгве",  # Show projects in Lilongwe district
            "language": "russian",
            "expected_categories": ["Project", "Location"]
        },
        {
            "message": "Lilongwe tumani loyihalari",  # Lilongwe district projects
            "language": "uzbek",
            "expected_categories": ["Project", "Location"]
        }
    ]
    
    base_url = "http://localhost:8000"
    
    print("\nStarting response format verification tests...")
    print("-" * 50)
    
    success_count = 0
    total_tests = len(test_cases)
    
    for test_case in test_cases:
        print(f"\nTesting query in {test_case['language'].upper()}:")
        print(f"Query: {test_case['message']}")
        
        try:
            response = requests.post(
                f"{base_url}/query",
                json={
                    "message": test_case["message"],
                    "language": test_case["language"],
                    "session_id": "test_session",
                    "llm_config": {"enabled": True}
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                
                print("\nResponse Analysis:")
                print("-" * 20)
                print(f"Response: {response_text[:200]}...")
                
                # Initialize test scores
                test_score = 0
                max_score = 4  # Categories (2) + No unwanted (1) + Structure (1)
                
                # Check for expected categories
                categories_found = []
                unwanted_categories = ["budget", "status", "statistics", "completion"]
                
                # Check for expected categories
                for category in test_case["expected_categories"]:
                    if category.lower() in response_text.lower():
                        categories_found.append(category)
                        print(f"✓ Found expected category: {category}")
                        test_score += 1
                    else:
                        print(f"✗ Missing expected category: {category}")
                
                # Check for unwanted categories
                unwanted_found = []
                for category in unwanted_categories:
                    if category.lower() in response_text.lower():
                        unwanted_found.append(category)
                
                if unwanted_found:
                    print(f"✗ Found unwanted categories: {', '.join(unwanted_found)}")
                else:
                    print("✓ No unwanted categories found")
                    test_score += 1
                
                # Check response structure
                lines = response_text.split('\n')
                structured = any("1." in response_text) and any("2." in response_text)
                if structured:
                    print("✓ Response is properly structured")
                    test_score += 1
                else:
                    print("✗ Response lacks proper structure")
                
                # Calculate test success
                test_percentage = (test_score / max_score) * 100
                print(f"\nTest Score: {test_score}/{max_score} ({test_percentage:.1f}%)")
                success_count += test_score / max_score
                
            else:
                print(f"✗ Error: Status code {response.status_code}")
                print(f"Error details: {response.text}")
                
        except Exception as e:
            print(f"✗ Error during test: {str(e)}")
        
        print("-" * 50)
    
    # Final summary
    overall_success = (success_count / total_tests) * 100
    print(f"\nOverall Test Results:")
    print(f"Success Rate: {overall_success:.1f}%")
    print(f"Passed: {success_count:.1f}/{total_tests} tests")
    
    if overall_success < 100:
        print("\nRecommendations:")
        print("- Check if the LLM prompt is being followed correctly")
        print("- Verify that responses are properly structured with numbered points")
        print("- Ensure Project and Location categories are explicitly labeled")
        print("- Check that unwanted categories are being filtered out")

if __name__ == "__main__":
    test_response_format() 