# tools/file_write.py
"""Write file tool."""
from pathlib import Path
from .base import BaseTool

class WriteFileTool(BaseTool):
    """Tool for writing content to files."""

    @classmethod
    def get_name(cls) -> str:
        return "write_file"

    @classmethod
    def get_schema(cls) -> dict:
        return {
            "name": "write_file",
            "description": "Write content to a file. Creates directories if needed.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path relative to workspace"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write"
                    }
                },
                "required": ["path", "content"]
            }
        }

    def _execute(self, path: str, content: str) -> str:
        """Write content to file."""
        workdir = self.context.get("workdir", Path.cwd())
        file_path = (workdir / path).resolve()

        if not file_path.is_relative_to(workdir):
            return "Error: Path escapes workspace"

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            return f"Wrote {len(content)} bytes to {path}"
        except Exception as e:
            return f"Error writing file: {e}"
