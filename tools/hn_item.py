# tools/hn_item.py
"""Get Hacker News item tool."""
from .base import BaseTool

class GetHNItemTool(BaseTool):
    """Tool for fetching a specific HN item."""

    @classmethod
    def get_name(cls) -> str:
        return "get_hn_item"

    @classmethod
    def get_schema(cls) -> dict:
        return {
            "name": "get_hn_item",
            "description": "Fetch a specific HN item (story, comment, job) by ID.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "item_id": {"type": "integer"}
                },
                "required": ["item_id"]
            }
        }

    def _execute(self, item_id: int) -> str:
        """Fetch HN item."""
        hn_adapter = self.context.get("hn_adapter")
        if not hn_adapter:
            return "Error: hn_adapter not available in context"

        result = hn_adapter.get_item(item_id)
        return self._format_item(result)

    def _format_item(self, item: dict) -> str:
        """Format single item for display."""
        if not item:
            return "Item not found."
        lines = [
            f"ID: {item.get('id')}",
            f"Type: {item.get('type')}",
            f"Title: {item.get('title')}",
            f"URL: {item.get('url')}",
            f"Score: {item.get('score')}",
            f"By: {item.get('by')}",
            f"Time: {item.get('time_iso')}"
        ]
        if item.get("text"):
            lines.append(f"\\nText: {item['text'][:500]}...")
        return "\\n".join(lines)
