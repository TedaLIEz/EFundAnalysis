"""
Main entry point for the EFund Analysis project.
"""
import os
from dotenv import load_dotenv
from core.agent import Agent
from data_provider import get_fund_individual_detail_info, get_fund_info

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Create an agent
    agent = Agent()
    
    # Add some functions that the agent can use
    agent.add_function(get_fund_individual_detail_info)
    agent.add_function(get_fund_info)
    
    # Run the agent with a prompt
    prompt = "000001基金的业绩比较标准是啥"
    response = agent.run(prompt)
    print(f"Response: {response}")

if __name__ == "__main__":
    main() 