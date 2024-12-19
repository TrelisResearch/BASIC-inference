from pipelines.bt_pipeline import TouchRugbyAssistant as BraintrustAssistant
from pipelines.hl_pipeline import TouchRugbyAssistant as HumanloopAssistant
from pipelines.hl_gemini_pipeline import TouchRugbyAssistant as GeminiAssistant

def get_pipeline_choice():
    while True:
        print("\nWhich pipeline would you like to use?")
        print("1. Braintrust")
        print("2. Humanloop")
        print("3. Gemini with Humanloop logging")
        choice = input("Enter your choice (1, 2, or 3): ").strip()
        
        if choice == "1":
            return BraintrustAssistant()
        elif choice == "2":
            return HumanloopAssistant()
        elif choice == "3":
            return GeminiAssistant()
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def main():
    # Get user's choice of pipeline
    assistant = get_pipeline_choice()
    
    print("\nWelcome to the Touch Rugby Chat Bot!")
    print("Ask any questions about touch rugby (type 'quit' to exit)")
    print("-" * 50)

    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'quit':
            if hasattr(assistant, 'end_conversation'):
                assistant.end_conversation()
            print("\nThanks for chatting! Goodbye!")
            break
        
        if user_input:
            response = assistant.get_response(user_input)
            print("\nAssistant:", response)

if __name__ == "__main__":
    main() 