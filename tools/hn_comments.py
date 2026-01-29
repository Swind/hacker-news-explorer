# tools/hn_comments.py
"""Get Hacker News comments tool."""
from .base import BaseTool

class GetHNCommentsTool(BaseTool):
    """Tool for fetching HN story comments."""

    @classmethod
    def get_name(cls) -> str:
        return "get_hn_comments"

    @classmethod
    def get_schema(cls) -> dict:
        return {
            "name": "get_hn_comments",
            "description": "Fetch comments for a HN story. Returns top-level comments with preview.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "story_id": {"type": "integer"},
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 50
                    }
                },
                "required": ["story_id"]
            }
        }

    def _execute(self, story_id: int, limit: int = 20) -> str:
        """Fetch HN comments."""
        hn_adapter = self.context.get("hn_adapter")
        if not hn_adapter:
            return "Error: hn_adapter not available in context"

        result = hn_adapter.get_comments(story_id=story_id, limit=limit)
        return self._format_comments(result)

    def _format_comments(self, comments: list) -> str:
        """Format comments for display."""
        if not comments:
            return "No comments found."
        lines = []
        for c in comments:
            text_preview = c.get("text", "")[:200].replace("\\n", " ")
            lines.append(f"[{c['id']}] by {c['by']}: {text_preview}...")
        return "\\n".join(lines)
