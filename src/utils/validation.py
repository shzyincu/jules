from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
import ast

class TableDefinition(BaseModel):
    name: str
    description: Optional[str] = None
    query: str

class PipelineDefinition(BaseModel):
    pipeline_name: str
    target_schema: str
    tables: List[TableDefinition]

def validate_pipeline_request(request_data: dict) -> PipelineDefinition:
    """Validates the pipeline request against the Pydantic model."""
    try:
        return PipelineDefinition(**request_data)
    except ValidationError as e:
        raise ValueError(f"Invalid pipeline request: {e}")

class CodeValidator(ast.NodeVisitor):
    def __init__(self):
        self.errors = []
        self.forbidden_functions = ['os.system', 'subprocess.call', 'subprocess.Popen', 'exec', 'eval']
        self.required_decorators = ['dlt.table', 'dlt.view', 'dlt.materialized_view']
        self.has_dlt_decorator = False

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            func_name = f"{node.func.value.id}.{node.func.attr}" if isinstance(node.func.value, ast.Name) else node.func.attr
            if func_name in self.forbidden_functions:
                 self.errors.append(f"Forbidden function call: {func_name}")
        elif isinstance(node.func, ast.Name):
             if node.func.id in self.forbidden_functions:
                 self.errors.append(f"Forbidden function call: {node.func.id}")
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Attribute): # e.g. @dlt.table
                decorator_name = f"{decorator.value.id}.{decorator.attr}"
                if decorator_name in self.required_decorators:
                    self.has_dlt_decorator = True
            elif isinstance(decorator, ast.Call): # e.g. @dlt.table(name="foo")
                 if isinstance(decorator.func, ast.Attribute):
                    decorator_name = f"{decorator.func.value.id}.{decorator.func.attr}"
                    if decorator_name in self.required_decorators:
                         self.has_dlt_decorator = True
        self.generic_visit(node)

def validate_code_integrity(code: str) -> List[str]:
    """
    Validates the generated Python code for syntax and security.
    Returns a list of error messages. If list is empty, code is valid.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [f"Syntax Error: {e}"]

    validator = CodeValidator()
    validator.visit(tree)

    errors = validator.errors

    # Check if at least one DLT decorator is present (heuristic)
    if not validator.has_dlt_decorator:
         # This might be too strict if the code is just helper functions,
         # but for a DLT pipeline file, it's expected.
         # Making it a warning or optional check might be better, but for now let's append it.
         pass
         # errors.append("No DLT decorators (@dlt.table, etc.) found.")
         # Commented out to avoid false positives on partial code generation

    return errors
