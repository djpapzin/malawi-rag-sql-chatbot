# test_components.py
from app.core.config import settings
from app.core.logger import logger
from app.core.error_handler import handle_error, ChatbotError
from app.utils.helpers import analyze_question, format_currency
from src.llm_chain import ProjectQueryChain
from src.rag_components import RAGComponents
from src.result_handler import ResultHandler
import requests
import json

def test_server_health():
    """Test if the FastAPI server is running"""
    try:
        response = requests.get("http://localhost:8000/health")
        print("\n1. Server Health Check:")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("\n1. Server Health Check: Failed - Server not running")
        return False

def test_chain_components():
    """Test the main chain components"""
    print("\n2. Testing Chain Components:")
    
    try:
        # Initialize chain
        chain = ProjectQueryChain()
        print("✓ Chain initialization successful")
        
        # Test RAG components
        rag = RAGComponents()
        print("✓ RAG components initialization successful")
        
        # Test result handler
        result_handler = ResultHandler()
        print("✓ Result handler initialization successful")
        
        return True
    except Exception as e:
        print(f"Chain components test failed: {str(e)}")
        return False

def test_query_processing():
    """Test query processing with sample questions"""
    print("\n3. Testing Query Processing:")
    
    test_questions = [
        "How many education projects are there in Central Region?",
        "What is the total budget for healthcare projects?",
        "Show me completed road construction projects"
    ]
    
    try:
        chain = ProjectQueryChain()
        for question in test_questions:
            print(f"\nProcessing question: {question}")
            # Test question analysis
            intent = analyze_question_intent(question)
            print(f"Intent Analysis: {intent}")
            
            # If server is running, test actual query processing
            try:
                response = requests.post(
                    "http://localhost:8000/chat",
                    json={"message": question}
                )
                if response.status_code == 200:
                    print(f"Server Response: {json.dumps(response.json(), indent=2)}")
            except requests.exceptions.ConnectionError:
                print("Note: Server endpoint test skipped - server not running")
        
        return True
    except Exception as e:
        print(f"Query processing test failed: {str(e)}")
        return False

def test_error_handling():
    """Test error handling mechanisms"""
    print("\n4. Testing Error Handling:")
    
    test_cases = [
        ("Invalid SQL", ChatbotError("Invalid SQL syntax")),
        ("Database Error", ChatbotError("Database connection failed")),
        ("General Error", Exception("Unexpected error"))
    ]
    
    for case_name, error in test_cases:
        print(f"\nTesting {case_name}:")
        try:
            raise error
        except Exception as e:
            error_response = handle_error(e)
            print(f"Error Response: {error_response}")
    
    return True

def run_all_tests():
    """Run all component tests"""
    print("=== Starting Component Tests ===\n")
    
    results = {
        "Server Health": test_server_health(),
        "Chain Components": test_chain_components(),
        "Query Processing": test_query_processing(),
        "Error Handling": test_error_handling()
    }
    
    print("\n=== Test Summary ===")
    for test_name, passed in results.items():
        status = "✓ Passed" if passed else "✗ Failed"
        print(f"{test_name}: {status}")

if __name__ == "__main__":
    run_all_tests()