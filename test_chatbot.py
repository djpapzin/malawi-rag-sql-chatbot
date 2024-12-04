## test_chatbot.py
import sqlite3
import pandas as pd
from app.core.config import settings
from app.core.logger import logger
from app.utils.helpers import analyze_question, format_currency

def test_database_connection():
    print("\n=== Testing Database Connection ===")
    try:
        conn = sqlite3.connect(settings.DATABASE_URL)
        query = """
        SELECT DISTINCT
            PROJECTNAME,
            PROJECTCODE,
            PROJECTSTATUS,
            PROJECTSECTOR,
            REGION,
            DISTRICT,
            COALESCE(BUDGET, 0) as BUDGET,
            COALESCE(COMPLETIONPERCENTAGE, 0) as COMPLETIONPERCENTAGE
        FROM proj_dashboard
        LIMIT 5
        """
        df = pd.read_sql_query(query, conn)
        print(f"Successfully connected to database")
        print(f"Found {len(df)} sample records")
        print("\nSample data:")
        print(df.head())
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False

def test_question_analysis():
    print("\n=== Testing Question Analysis ===")
    test_questions = [
        "How many schools are being built in Central Region?",
        "What is the total budget for healthcare projects?",
        "Show me road construction projects in Lilongwe",
        "Which projects are completed?",
        "What is the most expensive project?"
    ]
    
    for question in test_questions:
        intent = analyze_question(question)  # Changed from analyze_question_intent
        print(f"\nQuestion: {question}")
        print(f"Analysis:")
        for key, value in intent.items():
            print(f"  {key}: {value}")

def test_data_formatting():
    print("\n=== Testing Data Formatting ===")
    # Test currency formatting
    test_amounts = [
        1000000,
        1234567.89,
        500.50,
        0,
        None
    ]
    
    print("Currency Formatting:")
    for amount in test_amounts:
        try:
            formatted = format_currency(amount)
            print(f"  {amount} -> {formatted}")
        except Exception as e:
            print(f"  Error formatting {amount}: {str(e)}")

def main():
    print("Starting Chatbot Component Tests...")
    
    # Test database
    if not test_database_connection():
        print("Database tests failed - stopping further tests")
        return
    
    # Test question analysis
    test_question_analysis()
    
    # Test formatting
    test_data_formatting()

if __name__ == "__main__":
    main()