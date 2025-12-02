# Agentic AI Delivery Plan Implementation

This repository contains the implementation of the Agentic AI system for generating Delta Live Tables (DLT) pipelines.

## Project Structure

- `src/agent`: Core agent logic, tools, and prompts.
- `src/config`: Configuration management and schemas.
- `src/utils`: Utility functions (validation, LLM client).
- `tests`: Unit and integration tests.
- `notebooks`: Example scripts and drivers.

## Setup

1. **Install Dependencies:**
   Ensure you have Python 3.9+ installed.
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables:**
   If connecting to real Databricks or OpenAI APIs, set the necessary environment variables (e.g., `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `OPENAI_API_KEY`).
   *Note: The current implementation uses a mock LLM client for demonstration purposes.*

## Running the Code

### Interactive Driver
To run a sample generation flow locally:

```bash
python notebooks/driver.py
```

This script will:
1. Initialize the Agent.
2. Load the configuration.
3. Send a sample request ("Create a DLT pipeline...") to the agent.
4. Print the generated Python code and Pipeline JSON configuration.

### Running Tests
To run the unit tests:

```bash
python -m pytest tests/unit
```

## Configuration
The agent is configured via `src/config/config.yaml`. You can modify model parameters, enabled tools, and environment settings there.
