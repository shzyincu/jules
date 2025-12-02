import pytest
import pandas as pd
import json
from src.agent.agent import Agent
from unittest.mock import MagicMock

def test_agent_initialization():
    agent = Agent(config_path="src/config/config.yaml")
    agent.load_context(None)
    assert agent.config is not None
    assert agent.llm_client is not None
    assert agent.prompt_manager is not None

def test_agent_predict_mock_flow():
    agent = Agent(config_path="src/config/config.yaml")
    agent.load_context(None)

    input_data = pd.DataFrame({"request": ["Create a pipeline for sales data"]})

    # The LLM Client is mocked in src/utils/llm_client.py to return a valid JSON for pipeline generation
    response_df = agent.predict(None, input_data)

    assert not response_df.empty
    response_json = response_df.iloc[0]["response"]
    response_data = json.loads(response_json)

    assert "code" in response_data
    assert "pipeline_config" in response_data

    # Check generated code
    code = response_data["code"]
    assert "import dlt" in code
    assert "@dlt.table" in code

    # Check generated config
    config = response_data["pipeline_config"]
    assert config["name"] == "mock_pipeline"
    assert config["target"] == "mock_schema"

def test_agent_predict_invalid_request():
    agent = Agent(config_path="src/config/config.yaml")
    agent.load_context(None)

    # Mock LLM to return invalid JSON
    agent.llm_client.generate = MagicMock(return_value="Not JSON")

    input_data = pd.DataFrame({"request": ["Bad request"]})
    response_df = agent.predict(None, input_data)

    response_json = response_df.iloc[0]["response"]
    response_data = json.loads(response_json)

    assert "error" in response_data
    assert "LLM did not return valid JSON" in response_data["error"]
