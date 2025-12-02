import pytest
from src.utils.validation import validate_pipeline_request, validate_code_integrity, PipelineDefinition

def test_validate_pipeline_request_valid():
    data = {
        "pipeline_name": "test_pipeline",
        "target_schema": "test_schema",
        "tables": [
            {"name": "table1", "query": "SELECT * FROM source"}
        ]
    }
    result = validate_pipeline_request(data)
    assert isinstance(result, PipelineDefinition)
    assert result.pipeline_name == "test_pipeline"

def test_validate_pipeline_request_invalid():
    data = {
        "pipeline_name": "test_pipeline",
        # Missing target_schema
        "tables": []
    }
    with pytest.raises(ValueError):
        validate_pipeline_request(data)

def test_validate_code_integrity_valid():
    code = """
import dlt

@dlt.table
def my_table():
    return spark.table("source")
"""
    errors = validate_code_integrity(code)
    assert not errors

def test_validate_code_integrity_syntax_error():
    code = """
def my_table()
    return spark.table("source")
"""
    errors = validate_code_integrity(code)
    assert len(errors) == 1
    assert "Syntax Error" in errors[0]

def test_validate_code_integrity_forbidden_function():
    code = """
import os
def my_table():
    os.system("rm -rf /")
"""
    errors = validate_code_integrity(code)
    assert len(errors) > 0
    assert "Forbidden function call" in errors[0]
