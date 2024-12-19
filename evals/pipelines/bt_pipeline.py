import os
from typing import List, Dict, Optional
import openai
from dotenv import load_dotenv
from braintrust import init_logger, wrap_openai

# Load environment variables and configure OpenAI
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize Braintrust logger
init_logger(
    api_key=os.getenv('BRAINTRUST_API_KEY'),
    project="touch-rugby-bot"
)

# Wrap OpenAI client with Braintrust
openai = wrap_openai(openai)

class TouchRugbyAssistant:
    def __init__(self):
        self.system_message = {
            "role": "system",
            "content": "You are a knowledgeable touch rugby expert. You provide accurate, \
                helpful information about touch rugby rules, techniques, strategies, and training. \
                Keep your responses clear, concise, and focused on touch rugby."
        }
        self.messages: List[Dict[str, str]] = [self.system_message]
    
    def get_response(self, user_input: str) -> str:
        """Get a response from the assistant for a given user input."""
        try:
            # Add user message to conversation history
            self.messages.append({"role": "user", "content": user_input})
            
            # Get completion from OpenAI
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.messages,
                temperature=0.7
            )
            
            # Extract and store response
            assistant_message = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
            
        except Exception as e:
            return f"An error occurred: {str(e)}"
    
    def reset_conversation(self) -> None:
        """Reset the conversation history to just the system message."""
        self.messages = [self.system_message] 