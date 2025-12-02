import os
import sys
import pandas as pd
import json

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.agent import Agent

def main():
    print("Initializing Agent...")
    # Initialize the agent
    # In a real Databricks environment, config paths might need to be absolute or relative to the repo root
    config_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'config', 'config.yaml')
    agent = Agent(config_path=config_path)

    # Load context (mocking the MLflow context)
    agent.load_context(None)

    print("Agent initialized.")

    # Define a user request
    user_request = "Create a DLT pipeline that ingests JSON data from S3 into a silver table named 'transactions'."
    print(f"\nSending Request: {user_request}")

    # Create input DataFrame
    input_df = pd.DataFrame({"request": [user_request]})

    # Run prediction
    try:
        response_df = agent.predict(None, input_df)
        response_json = response_df.iloc[0]["response"]
        response_data = json.loads(response_json)

        if "error" in response_data:
            print(f"\nError: {response_data['error']}")
        else:
            print("\n--- Generated Code ---")
            print(response_data["code"])
            print("\n--- Pipeline Config ---")
            print(json.dumps(response_data["pipeline_config"], indent=2))

    except Exception as e:
        print(f"\nExecution failed: {e}")

if __name__ == "__main__":
    main()
