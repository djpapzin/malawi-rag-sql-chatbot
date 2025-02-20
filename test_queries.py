from src.llm_chain import initialize_chain

def test_queries():
    chain = initialize_chain()
    
    # Test queries
    queries = [
        "How many education projects are there in the Southern Region?",
        "What is the total budget for all projects in Lilongwe District?",
        "Show me details about the CHILIPA CDSS GIRLS HOSTEL project."
    ]
    
    for query in queries:
        print("\nTesting query:", query)
        print("=" * 80)
        result = chain.invoke(query)
        print(result)
        print("=" * 80)

if __name__ == "__main__":
    test_queries() 