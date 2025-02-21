from src.llm_chain import ProjectQueryChain
import json
import os

def test_query():
    print("Starting test...")
    print(f"TOGETHER_API_KEY present: {'TOGETHER_API_KEY' in os.environ}")
    
    # Initialize the chain
    print("Initializing chain...")
    chain = ProjectQueryChain()
    print("Chain initialized successfully")
    
    # Test questions
    test_questions = [
        "How many education projects are there in the Southern Region?",
        "What is the total budget for all projects in Lilongwe District?",
        "Show me details about the CHILIPA CDSS GIRLS HOSTEL project"
    ]
    
    # Test each question
    for question in test_questions:
        print("\n" + "="*80)
        print(f"Question: {question}")
        print("="*80)
        
        try:
            print(f"\nProcessing question: {question}")
            response = chain.query(question)
            print("Response received")
            
            print("\nSQL Query:")
            print(response.get("sql_query", "No query available"))
            
            print("\nSQL Result:")
            if isinstance(response.get("sql_result"), (list, dict)):
                print(json.dumps(response["sql_result"], indent=2))
            else:
                print(response.get("sql_result", "No result available"))
            
            print("\nAnswer:")
            print(response.get("answer", "No answer available"))
            
            if "files" in response:
                print("\nResults saved to:")
                print(f"Markdown: {response['files']['markdown_file']}")
                print(f"CSV: {response['files']['csv_file']}")
            
            if "error" in response:
                print("\nError encountered:")
                print(response["error"])
            
        except Exception as e:
            print(f"\nError during execution: {str(e)}")
            import traceback
            print(traceback.format_exc())
        
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    test_query() 