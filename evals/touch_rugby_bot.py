import os
import openai
from dotenv import load_dotenv
from braintrust import init_logger, wrap_openai

# Load environment variables
load_dotenv()

# Configure OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize Braintrust logger
init_logger(
    api_key=os.getenv('BRAINTRUST_API_KEY'),
    project="touch-rugby-bot"
)

# Wrap OpenAI client with Braintrust
openai = wrap_openai(openai)

def get_chat_response(messages):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {str(e)}"

def main():
    # Initial system message to set the context
    messages = [
        {
            "role": "system",
            "content": "You are a knowledgeable touch rugby expert. You provide accurate, \
                helpful information about touch rugby rules, techniques, strategies, and training. \
                Keep your responses clear, concise, and focused on touch rugby."
        }
    ]
    
    print("Welcome to the Touch Rugby Chat Bot!")
    print("Ask any questions about touch rugby (type 'quit' to exit)")
    # print("After each response, you can rate it (1-5) or press Enter to skip")
    print("-" * 50)

    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'quit':
            print("\nThanks for chatting! Goodbye!")
            break
        
        if user_input:
            # Add user message to conversation history
            messages.append({"role": "user", "content": user_input})
            
            # Get response from API
            response = get_chat_response(messages)
            
            # Add assistant's response to conversation history
            messages.append({"role": "assistant", "content": response})
            
            # Print response
            print("\nAssistant:", response)

if __name__ == "__main__":
    main() 