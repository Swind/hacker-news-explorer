# tools/finish.py
"""Finish exploration tool."""
from .base import BaseTool

class FinishExplorationTool(BaseTool):
    """Tool for stopping exploration and providing summary."""

    @classmethod
    def get_name(cls) -> str:
        return "finish_exploration"

    @classmethod
    def get_schema(cls) -> dict:
        return {
            "name": "finish_exploration",
            "description": "Stop exploration and provide summary. Call when you've found enough interesting content.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "interesting_stories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Paths to story analysis files"
                    }
                },
                "required": ["summary"]
            }
        }

    def _execute(self, summary: str, interesting_stories: list = None) -> str:
        """Mark exploration as finished."""
        # Set flag in context for agent to check
        self.context["is_finished"] = True
        self.context["final_summary"] = summary

        output = f"**EXPLORATION FINISHED**\\n\\nSummary: {summary}"
        if interesting_stories:
            output += f"\\n\\nInteresting stories:\\n" + "\\n".join(f"- {s}" for s in interesting_stories)
        return output
