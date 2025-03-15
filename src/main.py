"""
Main entry point for the EFund Analysis project.
"""
import os
from dotenv import load_dotenv

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    print("EFund Analysis Project")
    print("Environment:", os.getenv("ENVIRONMENT", "development"))

if __name__ == "__main__":
    main() 