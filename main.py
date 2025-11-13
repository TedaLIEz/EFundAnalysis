"""Main entry point for the EFund Analysis project."""

from dotenv import load_dotenv

from core.agent import Agent
from data_provider.common_util import get_date
from data_provider.fund import get_fund_individual_detail_info, get_fund_info, get_fund_performance


def main():
    # Load environment variables from .env file
    load_dotenv()

    # Create an agent
    agent = Agent()

    # Add some functions that the agent can use
    agent.add_function(get_fund_individual_detail_info)
    agent.add_function(get_fund_info)
    agent.add_function(get_fund_performance)
    agent.add_function(get_date)
    # Run the agent with a prompt
    prompt = "000001基金的基金经理是谁？000001过去三年的业绩如何"
    response = agent.run(prompt)
    print(f"Response: {response}")


if __name__ == "__main__":
    main()
