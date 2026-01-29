# tools/file_read.py
"""Read file tool."""
from pathlib import Path
from .base import BaseTool

class ReadFileTool(BaseTool):
    """Tool for reading file contents from workspace."""

    @classmethod
    def get_name(cls) -> str:
        return "read_file"

    @classmethod
    def get_schema(cls) -> dict:
        return {
            "name": "read_file",
            "description": "Read file contents from the workspace.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path relative to workspace"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max lines to read"
                    }
                },
                "required": ["path"]
            }
        }

    def _execute(self, path: str, limit: int = None) -> str:
        """Read file contents."""
        workdir = self.context.get("workdir", Path.cwd())
        file_path = (workdir / path).resolve()

        if not file_path.is_relative_to(workdir):
            return "Error: Path escapes workspace"

        try:
            lines = file_path.read_text().splitlines()
            if limit:
                lines = lines[:limit]
            return "\n".join(lines)
        except Exception as e:
            return f"Error reading file: {e}"
