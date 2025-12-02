from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class ModelConfig(BaseModel):
    name: str
    temperature: float = 0.1
    max_tokens: int = 4096

class PipelineTemplate(BaseModel):
    target_schema: str
    cluster_id: str
    edition: str

class EnvironmentConfig(BaseModel):
    catalog_name: str
    volume_path: str

class AppConfig(BaseModel):
    model: ModelConfig
    tools: List[Dict[str, str]]
    pipeline_templates: Dict[str, PipelineTemplate]
    environments: Dict[str, EnvironmentConfig]

def load_config(path: str) -> AppConfig:
    import yaml
    with open(path, 'r') as f:
        config_data = yaml.safe_load(f)
    return AppConfig(**config_data)
