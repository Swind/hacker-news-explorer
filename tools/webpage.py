# tools/webpage.py
"""Read webpage tool."""
from .base import BaseTool

class ReadWebpageTool(BaseTool):
    """Tool for reading webpage content."""

    @classmethod
    def get_name(cls) -> str:
        return "read_webpage"

    @classmethod
    def get_schema(cls) -> dict:
        return {
            "name": "read_webpage",
            "description": "Read the full content of a webpage. Returns main article text.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"}
                },
                "required": ["url"]
            }
        }

    def _execute(self, url: str) -> str:
        """Read webpage content."""
        web_reader = self.context.get("web_reader")
        if not web_reader:
            return "Error: web_reader not available in context"

        result = web_reader.read(url)
        if result["success"]:
            content = result["content"]
            title = result.get("title", "")
            output = f"Title: {title}\n\n{content[:10000]}"
            if len(content) > 10000:
                output += f"\n\n... (content truncated, was {len(content)} chars)"
            return output
        else:
            return f"Failed to read webpage: {result['error']}"
