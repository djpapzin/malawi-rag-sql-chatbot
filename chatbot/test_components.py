# test_components.py
from app.core.config import settings
from app.core.logger import logger
from app.core.error_handler import handle_error, ChatbotError
from app.utils.helpers import analyze_question_intent, format_currency

def test_all_components():
    print("\n=== Testing All Components ===\n")
    
    # 1. Test Config
    print("1. Testing Configuration:")
    print(f"App Name: {settings.APP_NAME}")
    print(f"Database URL: {settings.DATABASE_URL}")
    
    # 2. Test Logger
    print("\n2. Testing Logger:")
    logger.info("Test info message")
    logger.error("Test error message")
    
    # 3. Test Error Handler
    print("\n3. Testing Error Handler:")
    try:
        raise ChatbotError("Test error message")
    except Exception as e:
        error_response = handle_error(e)
        print(f"Error Response: {error_response}")
    
    # 4. Test Helpers
    print("\n4. Testing Question Analysis:")
    test_questions = [
        "How many education projects are there in Central Region?",
        "What is the total budget for healthcare projects?",
        "Show me completed road construction projects"
    ]
    
    for question in test_questions:
        intent = analyze_question_intent(question)
        print(f"\nQuestion: {question}")
        print(f"Intent Analysis: {intent}")
    
    # 5. Test Currency Formatting
    print("\n5. Testing Currency Formatting:")
    amounts = [1000000, 500.50, 0]
    for amount in amounts:
        formatted = format_currency(amount)
        print(f"Amount: {amount} -> Formatted: {formatted}")

if __name__ == "__main__":
    test_all_components()