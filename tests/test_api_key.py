import os
from together import Together
import sys

# Set the API key
api_key = "f7119711abb83c4ec5e9b2339eb06c66c87d4958f4ce6cc348ed3ad0c6cb7101"
os.environ["TOGETHER_API_KEY"] = api_key

print(f"Testing Together API with key: {api_key[:8]}...{api_key[-8:]}")

try:
    # Initialize the Together client
    client = Together()
    print("Client initialized successfully")
    
    # Test the API by listing available models
    print("Listing available models...")
    models = client.models.list()
    print(f"Successfully retrieved {len(models)} models")
    print("API key is valid!")
    
    # Test a simple completion
    print("\nTesting chat completion...")
    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-8B-Instruct-Turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"}
        ],
        max_tokens=100,
        temperature=0.7,
    )
    print("\nChat completion response:")
    print(f"Role: {response.choices[0].message.role}")
    print(f"Content: {response.choices[0].message.content}")
    
    sys.exit(0)  # Success
    
except Exception as e:
    print(f"Error: {str(e)}")
    sys.exit(1)  # Failure
