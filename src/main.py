"""
Main entry point for the EFund Analysis project.
"""
import os
from dotenv import load_dotenv
from core.agent import Agent
from data_provider.fund import get_fund_individual_detail_info, get_fund_info, get_fund_performance
from data_provider.common_util import get_date
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
    prompt = "000001基金过去三年的业绩如何？"
    response = agent.run(prompt)
    print(f"Response: {response}")

if __name__ == "__main__":
    main() 