from pipeline import TouchRugbyAssistant

def main():
    assistant = TouchRugbyAssistant()
    
    print("Welcome to the Touch Rugby Chat Bot!")
    print("Ask any questions about touch rugby (type 'quit' to exit)")
    print("-" * 50)

    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'quit':
            print("\nThanks for chatting! Goodbye!")
            break
        
        if user_input:
            response = assistant.get_response(user_input)
            print("\nAssistant:", response)

if __name__ == "__main__":
    main() 