# tools/task.py
"""Task tool for spawning subagents."""
from .base import BaseTool

class TaskTool(BaseTool):
    """Tool for spawning subagents."""

    @classmethod
    def get_name(cls) -> str:
        return "Task"

    @classmethod
    def get_schema(cls) -> dict:
        from tools.schemas import TASK_TOOL
        return TASK_TOOL

    def _execute(self, agent_type: str, description: str, prompt: str) -> str:
        """This is handled specially by the agent, not executed directly."""
        return "Task execution is handled by the agent's execute_tool method."
