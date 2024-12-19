import datetime
from typing import List, Dict
import google.generativeai as genai
from config import humanloop, genai

class TouchRugbyAssistant:
    def __init__(self):
        self.system_message = "You are a knowledgeable touch rugby expert. You provide accurate, \
            helpful information about touch rugby rules, techniques, strategies, and training. \
            Keep your responses clear, concise, and focused on touch rugby."
        
        # Configure Gemini model
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        # Initialize Gemini model and chat
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config=generation_config,
        )
        
        # Start chat session with system message
        self.chat = self.model.start_chat(
            history=[
                {"role": "user", "parts": ["Please act as the following: " + self.system_message]},
                {"role": "model", "parts": ["I understand. I am now a knowledgeable touch rugby expert ready to help with rules, techniques, strategies, and training."]}
            ]
        )
        
        # Initialize trace
        self.trace_id = humanloop.flows.log(
            path="Touch Rugby Bot/Gemini Flow",
            flow={
                "attributes": {}  # Empty attributes object is required
            }
        ).id
    
    def get_response(self, user_input: str) -> str:
        """Get a response from the assistant for a given user input."""
        try:
            # Record start time
            start_time = datetime.datetime.now()
            
            # Get response from Gemini
            response = self.chat.send_message(user_input)
            assistant_message = response.text
            
            # Log the prompt
            prompt_log_id = humanloop.prompts.log(
                path="Touch Rugby Bot/Gemini Prompt",
                prompt={
                    "model": "gemini-2.0-flash-exp",
                    "messages": [{"role": "user", "content": user_input}],
                    "temperature": 0.7
                },
                output=assistant_message,
                trace_parent_id=self.trace_id,
                start_time=start_time,
                end_time=datetime.datetime.now()
            ).id
            
            return assistant_message
            
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            print(error_message)
            return error_message
    
    def reset_conversation(self) -> None:
        """Reset the conversation history and create a new trace."""
        # Complete current trace
        humanloop.flows.update_log(
            log_id=self.trace_id,
            output="Conversation reset",
            trace_status="complete"
        )
        
        # Start new trace
        self.trace_id = humanloop.flows.log(
            path="Touch Rugby Bot/Gemini Flow",
            flow={
                "attributes": {}
            }
        ).id
        
        # Reset chat session
        self.chat = self.model.start_chat(
            history=[
                {"role": "user", "parts": ["Please act as the following: " + self.system_message]},
                {"role": "model", "parts": ["I understand. I am now a knowledgeable touch rugby expert ready to help with rules, techniques, strategies, and training."]}
            ]
        )
    
    def end_conversation(self) -> None:
        """Complete the trace when conversation ends."""
        humanloop.flows.update_log(
            log_id=self.trace_id,
            output="Conversation ended",
            trace_status="complete"
        )