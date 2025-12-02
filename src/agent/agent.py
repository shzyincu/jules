import mlflow
import json
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
from src.utils.llm_client import LLMClient
from src.utils.validation import validate_pipeline_request, validate_code_integrity, PipelineDefinition
from src.agent.prompts import PromptManager
from src.agent.tools import ToolManager
from src.utils.logging import setup_logger

# Configure logging
logger = setup_logger(__name__)

class Agent(mlflow.pyfunc.PythonModel):
    def __init__(self, config_path: str = "src/config/config.yaml"):
        self.config_path = config_path
        self.llm_client = None
        self.prompt_manager = None
        self.tool_manager = None

    def load_context(self, context):
        """
        Loads the agent context. This is called when the model is loaded.
        """
        logger.info("Loading agent context...")
        from src.config.schemas import load_config
        self.config = load_config(self.config_path)

        self.llm_client = LLMClient(self.config.model)
        self.prompt_manager = PromptManager()
        self.tool_manager = ToolManager(self.config.tools)
        logger.info("Agent context loaded.")

    def predict(self, context, model_input: pd.DataFrame) -> pd.DataFrame:
        """
        Main entry point for the agent.
        Expected input: A DataFrame with a 'request' column.
        Returns: A DataFrame with the agent's response (code and config).
        """
        responses = []
        for index, row in model_input.iterrows():
            user_request = row.get("request")
            if not user_request:
                 responses.append({"error": "No request provided."})
                 continue

            try:
                response = self._handle_request(user_request)
                responses.append(response)
            except Exception as e:
                logger.error(f"Error handling request: {e}")
                responses.append({"error": str(e)})

        # Helper to format response into strings for pandas dataframe if needed,
        # or just return dicts if the signature allows.
        # MLflow typically expects consistent types. Let's serialize to JSON string.
        return pd.DataFrame({"response": [json.dumps(r) for r in responses]})

    def _handle_request(self, user_request: str) -> Dict[str, Any]:
        """
        Orchestrates the agent's logic.
        Returns a dictionary containing 'code' and 'config'.
        """
        # 1. Construct Prompt
        prompt = self.prompt_manager.render_prompt("generate_pipeline", user_request=user_request)

        # 2. Call LLM
        llm_response = self.llm_client.generate(prompt)

        # 3. Parse LLM Response (expecting JSON)
        try:
             pipeline_data = json.loads(llm_response)
        except json.JSONDecodeError:
             raise ValueError(f"LLM did not return valid JSON. Response: {llm_response}")

        # 4. Validate Structured Output
        try:
            pipeline_def = validate_pipeline_request(pipeline_data)
        except ValueError as e:
             raise ValueError(f"Validation Error: {e}")

        # 5. Generate Code (using Template)
        generated_code = self.prompt_manager.render_template("dlt_pipeline.py.jinja", pipeline=pipeline_def)

        # 6. Validate Code Integrity
        validation_errors = validate_code_integrity(generated_code)
        if validation_errors:
             raise ValueError(f"Generated code failed validation: {validation_errors}")

        # 7. Generate Pipeline Config (using Template)
        # We need to pass some context, e.g. current user, which might come from environment
        pipeline_config_json = self.prompt_manager.render_template(
            "pipeline_config.json.jinja",
            pipeline=pipeline_def,
            current_user="agent" # Placeholder
        )

        return {
            "code": generated_code,
            "pipeline_config": json.loads(pipeline_config_json)
        }
