# tools/hn_stories.py
"""Get Hacker News stories tool."""
from .base import BaseTool

class GetHNStoriesTool(BaseTool):
    """Tool for fetching HN stories."""

    @classmethod
    def get_name(cls) -> str:
        return "get_hn_stories"

    @classmethod
    def get_schema(cls) -> dict:
        return {
            "name": "get_hn_stories",
            "description": "Fetch Hacker News stories. Returns list with id, title, url, score, author, time, comment count.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "story_type": {
                        "type": "string",
                        "enum": ["top", "new", "best", "ask", "show", "job"]
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 30
                    }
                },
                "required": ["story_type"]
            }
        }

    def _execute(self, story_type: str, limit: int = 10) -> str:
        """Fetch HN stories."""
        hn_adapter = self.context.get("hn_adapter")
        if not hn_adapter:
            return "Error: hn_adapter not available in context"

        result = hn_adapter.get_stories(story_type=story_type, limit=limit)
        return self._format_stories(result)

    def _format_stories(self, stories: list) -> str:
        """Format stories list for display."""
        if not stories:
            return "No stories found."
        lines = []
        for s in stories:
            line = f"[{s['id']}] {s['title']}"
            if s.get("url"):
                line += f" ({s['url']})"
            line += f" | score: {s['score']} | comments: {s['descendants']} | by: {s['by']}"
            lines.append(line)
        return "\\n".join(lines)
