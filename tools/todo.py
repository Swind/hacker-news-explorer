# tools/todo.py
"""Todo list management tool."""
from .base import BaseTool


class TodoWriteTool(BaseTool):
    """Tool for managing task lists during analysis."""

    @classmethod
    def get_name(cls) -> str:
        return "TodoWrite"

    @classmethod
    def get_schema(cls) -> dict:
        return {
            "name": "TodoWrite",
            "description": "Update the task list to track multi-step work.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "content": {
                                    "type": "string",
                                    "description": "Task description"
                                },
                                "status": {
                                    "type": "string",
                                    "enum": ["pending", "in_progress", "completed"],
                                    "description": "Task status"
                                },
                                "activeForm": {
                                    "type": "string",
                                    "description": "Active form (e.g., 'Analyzing story')"
                                }
                            },
                            "required": ["content", "status", "activeForm"]
                        }
                    }
                },
                "required": ["items"]
            }
        }

    def _execute(self, items: list) -> str:
        """Update the task list."""
        # Get TodoManager from context
        todo_manager = self.context.get("todo_manager")
        if not todo_manager:
            return "Error: TodoManager not available in context"

        try:
            return todo_manager.update(items)
        except ValueError as e:
            return f"Error: {e}"
