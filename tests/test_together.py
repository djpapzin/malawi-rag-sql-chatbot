from together import Together
import os

def test_together():
    # Get API key and create client
    api_key = os.getenv('TOGETHER_API_KEY')
    if not api_key:
        raise ValueError("TOGETHER_API_KEY environment variable not set")
    print(f"API Key found: {'*' * 8}{api_key[-4:]}")
    
    # Initialize client
    client = Together()
    print("Client created successfully")
    
    # Test chat completion
    try:
        print("\nTesting chat completion...")
        response = client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",  # Using Mixtral model
            messages=[
                {"role": "system", "content": "You are a helpful assistant that helps generate SQL queries."},
                {"role": "user", "content": "What infrastructure projects are currently ongoing in Lilongwe?"}
            ],
            max_tokens=1000,
            temperature=0.7,
        )
        print("\nChat completion response:")
        print(f"Role: {response.choices[0].message.role}")
        print(f"Content: {response.choices[0].message.content}")
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"\nError during chat completion test: {str(e)}")
        raise

if __name__ == "__main__":
    test_together() 