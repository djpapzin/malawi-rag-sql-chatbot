import os
import together
import sys

# Set the API key directly
api_key = "f7119711abb83c4ec5e9b2339eb06c66c87d4958f4ce6cc348ed3ad0c6cb7101"
together.api_key = api_key

print(f"Testing Together API with key: {api_key[:8]}...{api_key[-8:]}")

try:
    # Test the API by listing available models
    print("Listing available models...")
    models = together.Models().list()
    print(f"Successfully retrieved models")
    print("API key is valid!")
    
    # Test a simple completion
    print("\nTesting chat completion...")
    response = together.Complete.create(
        prompt="Hello, how are you?",
        model="meta-llama/Meta-Llama-3-8B-Instruct-Turbo",
        max_tokens=100,
        temperature=0.7,
    )
    print("\nCompletion response:")
    print(response)
    
    sys.exit(0)  # Success
    
except Exception as e:
    print(f"Error: {str(e)}")
    sys.exit(1)  # Failure
