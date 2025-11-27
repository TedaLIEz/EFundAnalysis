"""Main entry point for the project."""

from dotenv import load_dotenv

from core.llm.agent import Agent


def main():
    load_dotenv()
    agent = Agent()

    while True:
        text_input = input("User: ")
        if text_input == "exit":
            break
        response = agent.run(text_input)
        print(f"Agent: {response}")


if __name__ == "__main__":
    main()
