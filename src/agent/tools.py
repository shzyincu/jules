from typing import List, Dict, Any

class ToolManager:
    def __init__(self, tools_config: List[Dict[str, str]]):
        self.available_tools = {}
        for tool_conf in tools_config:
            name = tool_conf.get("name")
            if name:
                self.available_tools[name] = self._get_tool_implementation(name)

    def _get_tool_implementation(self, tool_name: str):
        # In a real implementation, this would look up the actual function/tool
        # For now, we return a mock.
        if tool_name == "system.ai.python_exec":
            return self._mock_python_exec
        elif tool_name == "system.ai.sql_exec":
            return self._mock_sql_exec
        return None

    def _mock_python_exec(self, code: str):
        return "Python execution result (mock)"

    def _mock_sql_exec(self, query: str):
        return "SQL execution result (mock)"

    def get_tool(self, name: str):
        return self.available_tools.get(name)

    def list_tools(self):
        return list(self.available_tools.keys())
