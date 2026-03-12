from agent import run_agent


def main():
    """Main chat loop."""
    print("=" * 60)
    print("Baby Code Phase 1: Minimum Viable Coding Agent")
    print("=" * 60)
    print("Commands: 'quit' to exit, 'clear' to reset conversation")
    print("=" * 60)
    print()

    conversation_history = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() == 'quit':
            print("Goodbye!")
            break

        if user_input.lower() == 'clear':
            conversation_history = []
            print("Conversation cleared.\n")
            continue

        print("\nAgent: ", end="", flush=True)
        run_agent(user_input, conversation_history)
        print()

if __name__ == "__main__":
    main()