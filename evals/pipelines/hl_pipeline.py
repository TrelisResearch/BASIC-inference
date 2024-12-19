from typing import List, Dict
import datetime
import openai
from config import humanloop  # Remove the dot

class TouchRugbyAssistant:
    def __init__(self):
        self.system_message = {
            "role": "system",
            "content": "You are a knowledgeable touch rugby expert. You provide accurate, \
                helpful information about touch rugby rules, techniques, strategies, and training. \
                Keep your responses clear, concise, and focused on touch rugby."
        }
        self.messages: List[Dict[str, str]] = [self.system_message]
        # Initialize trace for the conversation
        self.trace_id = humanloop.flows.log(
            path="Touch Rugby Bot/Conversation",
            flow={
                "attributes": {},
            },
        ).id
    
    def get_response(self, user_input: str) -> str:
        """Get a response from the assistant for a given user input."""
        try:
            # Add user message to conversation history
            self.messages.append({"role": "user", "content": user_input})
            
            # Record start time for prompt logging
            prompt_start_time = datetime.datetime.now()
            
            # Get completion from OpenAI
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.messages,
                temperature=0.7,
                timeout=30.0
            )
            
            # Extract response content
            assistant_message = response.choices[0].message.content
            
            # Log the prompt and response to Humanloop
            humanloop.prompts.log(
                path="Touch Rugby Bot/QA Prompt",
                prompt={
                    "model": "gpt-4o-mini",
                    "messages": self.messages.copy(),
                    "temperature": 0.7,
                },
                output=assistant_message,
                trace_parent_id=self.trace_id,
                start_time=prompt_start_time,
                end_time=datetime.datetime.now(),
                metadata={
                    "conversation_turn": len(self.messages) // 2
                }
            )
            
            # Add assistant response to conversation history
            self.messages.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
            
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            # Log error to Humanloop with correct parameters
            try:
                humanloop.prompts.log(
                    path="Touch Rugby Bot/QA Prompt",
                    prompt={
                        "model": "gpt-4o-minio-mini",
                        "messages": self.messages,
                        "temperature": 0.7,
                    },
                    output=error_message,
                    trace_parent_id=self.trace_id,
                    start_time=prompt_start_time,
                    end_time=datetime.datetime.now(),
                    metadata={
                        "error": str(e),
                        "conversation_turn": len(self.messages) // 2
                    }
                )
            except Exception as log_error:
                print(f"Failed to log error to Humanloop: {str(log_error)}")
            
            return error_message
    
    def reset_conversation(self) -> None:
        """Reset the conversation history and create a new trace."""
        try:
            # Complete the previous trace
            humanloop.flows.update_log(
                log_id=self.trace_id,
                output="Conversation reset",
                metadata={
                    "total_turns": len(self.messages) // 2
                }
            )
            
            # Start a new trace
            self.trace_id = humanloop.flows.log(
                path="Touch Rugby Bot/Conversation",
                flow={
                    "attributes": {},
                },
            ).id
            
            # Reset messages
            self.messages = [self.system_message]
        except Exception as e:
            print(f"Failed to reset conversation: {str(e)}")
    
    def end_conversation(self) -> None:
        """Complete the trace when conversation ends."""
        try:
            humanloop.flows.update_log(
                log_id=self.trace_id,
                output="Conversation ended",
                metadata={
                    "total_turns": len(self.messages) // 2
                }
            )
        except Exception as e:
            print(f"Failed to end conversation: {str(e)}") 