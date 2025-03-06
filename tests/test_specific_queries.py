import requests
import re
import json
import time
from colorama import Fore, Style, init

# Initialize colorama
init()

class SpecificProjectTester:
    def __init__(self, server_url="http://154.0.164.254:5000"):
        self.server_url = server_url
        self.api_endpoint = f"{server_url}/api/rag-sql-chatbot/chat"
        self.total_tests = 0
        self.passed_tests = 0
        self.test_results = []
        
    def test_query(self, query, expected_pattern, test_name):
        """Test a specific query and check for expected patterns and Python code"""
        print(f"\n{Fore.YELLOW}Test: {test_name}{Style.RESET_ALL}")
        print(f"Query: \"{query}\"")
        
        # Make the API request
        try:
            response = requests.post(
                self.api_endpoint,
                headers={"Content-Type": "application/json"},
                json={"message": query},
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"{Fore.RED}ERROR: API returned status code {response.status_code}{Style.RESET_ALL}")
                self.test_results.append({
                    "name": test_name,
                    "query": query,
                    "status": "FAILED",
                    "error": f"API returned status code {response.status_code}"
                })
                return False
                
            response_text = response.text
            
            # Check if the response contains Python code
            python_code_patterns = [
                r"```python", r"def\s+\w+\(", r"return\s+", r"import\s+", r"class\s+\w+:"
            ]
            
            has_python_code = False
            for pattern in python_code_patterns:
                if re.search(pattern, response_text):
                    has_python_code = True
                    print(f"{Fore.RED}ERROR: Response contains Python code:{Style.RESET_ALL}")
                    print(re.search(pattern, response_text).group())
                    break
            
            # Check if the response contains the expected pattern
            if re.search(expected_pattern, response_text, re.IGNORECASE):
                if not has_python_code:
                    print(f"{Fore.GREEN}SUCCESS: Response contains expected information{Style.RESET_ALL}")
                    matches = re.findall(expected_pattern, response_text, re.IGNORECASE)
                    print(f"Found patterns: {', '.join(matches[:3])}")
                    self.passed_tests += 1
                    self.test_results.append({
                        "name": test_name,
                        "query": query,
                        "status": "PASSED" if not has_python_code else "PARTIALLY PASSED",
                        "notes": "Contains expected information but also has Python code" if has_python_code else ""
                    })
                    return True
                else:
                    print(f"{Fore.YELLOW}PARTIAL SUCCESS: Contains expected information but also has Python code{Style.RESET_ALL}")
                    self.test_results.append({
                        "name": test_name,
                        "query": query,
                        "status": "PARTIALLY PASSED",
                        "notes": "Contains expected information but also has Python code"
                    })
                    return False
            else:
                print(f"{Fore.RED}FAILURE: Response does not contain expected information{Style.RESET_ALL}")
                print(f"Expected pattern: {expected_pattern}")
                print(f"First 200 chars of response:")
                print(response_text[:200])
                self.test_results.append({
                    "name": test_name,
                    "query": query,
                    "status": "FAILED",
                    "notes": "Does not contain expected information"
                })
                return False
                
        except Exception as e:
            print(f"{Fore.RED}ERROR: {str(e)}{Style.RESET_ALL}")
            self.test_results.append({
                "name": test_name,
                "query": query,
                "status": "ERROR",
                "error": str(e)
            })
            return False
    
    def run_test(self, query, expected_pattern, test_name):
        """Run a test and track results"""
        self.total_tests += 1
        return self.test_query(query, expected_pattern, test_name)
    
    def run_all_tests(self):
        """Run all test categories"""
        print(f"\n{Fore.YELLOW}1. Testing Direct Project Name Queries{Style.RESET_ALL}")
        print("----------------------------------------")
        
        self.run_test("Show me details for Lilongwe Water Supply Construction", r"budget|contractor|completion_percentage", "Direct project name query")
        self.run_test("Tell me about the Kasungu School Construction project", r"budget|contractor|completion_percentage", "Project with 'Tell me about'")
        self.run_test("What is the status of Salima School Construction?", r"completion_percentage|status", "Status query")
        
        print(f"\n{Fore.YELLOW}2. Testing Project Attribute Queries{Style.RESET_ALL}")
        print("----------------------------------------")
        
        self.run_test("Which project in Lilongwe has the highest budget?", r"budget|Lilongwe", "Highest budget query")
        self.run_test("Show me water sector projects", r"water|project", "Projects by sector")
        self.run_test("Find school construction projects that are 100% complete", r"School|100%|complete", "Projects by completion status")
        
        print(f"\n{Fore.YELLOW}3. Testing Contextual Follow-up Queries{Style.RESET_ALL}")
        print("----------------------------------------")
        
        self.run_test("What projects are in Machinga?", r"Machinga|projects", "List projects in district")
        time.sleep(3)  # Give the API time to process context
        self.run_test("Tell me more about projects in Machinga", r"Machinga|project", "Follow-up query about district")
        
        print(f"\n{Fore.YELLOW}4. Testing Specific Detail Queries{Style.RESET_ALL}")
        print("----------------------------------------")
        
        self.run_test("Who is the contractor for Solar powered water reticulation System in Lilongwe?", r"contractor|Lilongwe", "Contractor query")
        self.run_test("What is the completion percentage of the Kasungu School project?", r"completion_percentage|%", "Completion percentage query")
        self.run_test("When did the construction of health centers in Salima start?", r"start_date|Salima|health", "Start date query")
        
        print(f"\n{Fore.YELLOW}5. Testing Negative Cases{Style.RESET_ALL}")
        print("----------------------------------------")
        
        self.run_test("Show me details for Non-Existent Project XYZ", r"No matching projects found", "Non-existent project query")
        self.run_test("Tell me about projects on Mars", r"no such table|No matching projects found", "Invalid location query")
    
    def print_summary(self):
        """Print a summary of test results"""
        print(f"\n{Fore.YELLOW}Results Summary{Style.RESET_ALL}")
        print("----------------------------------------")
        print(f"Total tests: {self.total_tests}")
        print(f"Passed tests: {Fore.GREEN}{self.passed_tests}{Style.RESET_ALL}")
        print(f"Failed tests: {Fore.RED}{self.total_tests - self.passed_tests}{Style.RESET_ALL}")
        
        if self.passed_tests == self.total_tests:
            print(f"{Fore.GREEN}All tests passed!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Some tests failed. Review the output above for details.{Style.RESET_ALL}")
            print(f"\nCommon issues to check:")
            print("1. Is the specific project query handler working?")
            print("2. Is the SQL generation working correctly for specific projects?")
            print("3. Are responses containing Python code instead of user-friendly answers?")
        
        # Detailed results
        print(f"\n{Fore.YELLOW}Detailed Test Results{Style.RESET_ALL}")
        print("----------------------------------------")
        for i, result in enumerate(self.test_results):
            status_color = Fore.GREEN if result["status"] == "PASSED" else Fore.YELLOW if result["status"] == "PARTIALLY PASSED" else Fore.RED
            print(f"{i+1}. {result['name']}: {status_color}{result['status']}{Style.RESET_ALL}")
            if "notes" in result and result["notes"]:
                print(f"   Notes: {result['notes']}")
            if "error" in result and result["error"]:
                print(f"   Error: {Fore.RED}{result['error']}{Style.RESET_ALL}")

def main():
    print(f"{Fore.YELLOW}Starting Specific Project Query Tests{Style.RESET_ALL}")
    print("========================================")
    
    tester = SpecificProjectTester()
    print(f"Testing against: {tester.api_endpoint}")
    print("========================================")
    
    tester.run_all_tests()
    tester.print_summary()
    
    print(f"\n{Fore.YELLOW}Test Script Completed{Style.RESET_ALL}")
    print("========================================")

if __name__ == "__main__":
    main() 