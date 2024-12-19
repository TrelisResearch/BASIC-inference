import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

def test_openai_connection():
    """Test OpenAI connection and model availability."""
    try:
        print("Testing OpenAI connection...")
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello!"}
            ],
            temperature=0.7
        )
        
        print("\nConnection successful!")
        print("\nModel Response:")
        print(f"Content: {response.choices[0].message.content}")
        print(f"\nResponse metadata:")
        print(f"Model: {response.model}")
        print(f"Created: {response.created}")
        print(f"Response ID: {response.id}")
        
    except Exception as e:
        print(f"\nError occurred:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")

if __name__ == "__main__":
    test_openai_connection() 