# tools/schemas.py
"""Tool JSON schemas for Claude's function calling."""

from typing import List
from agents.config import AGENT_TYPES

# =============================================================================
# Base Tools
# =============================================================================

BASE_TOOLS = [
    {
        "name": "read_webpage",
        "description": "Read the full content of a webpage. Returns main article text.",
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
        },
    },
    {
        "name": "finish_exploration",
        "description": "Stop exploration and provide summary. Call when you've found enough interesting content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "interesting_stories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Paths to story analysis files",
                },
            },
            "required": ["summary"],
        },
    },
]


# =============================================================================
# Report Tools
# =============================================================================

REPORT_TOOLS = [
    {
        "name": "create_report",
        "description": "Create a new story analysis report with frontmatter metadata.",
        "input_schema": {
            "type": "object",
            "properties": {
                "story_id": {
                    "type": "integer",
                    "description": "Hacker News story ID",
                },
                "hn_url": {
                    "type": "string",
                    "description": "URL to the HN story",
                },
                "title": {
                    "type": "string",
                    "description": "Story title",
                },
                "verdict": {
                    "type": "string",
                    "enum": ["interesting", "not_interesting", "controversial", "technical"],
                    "description": "Analysis verdict",
                },
                "content": {
                    "type": "string",
                    "description": "Markdown content of the analysis",
                },
            },
            "required": ["story_id", "hn_url", "title", "verdict", "content"],
        },
    },
    {
        "name": "read_report",
        "description": "Read a story analysis report by story_id. Returns metadata and content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "story_id": {
                    "type": "integer",
                    "description": "Hacker News story ID",
                },
                "metadata_only": {
                    "type": "boolean",
                    "description": "If true, only return frontmatter metadata",
                },
            },
            "required": ["story_id"],
        },
    },
    {
        "name": "list_reports",
        "description": "List all reports with optional filters by verdict or date.",
        "input_schema": {
            "type": "object",
            "properties": {
                "verdict": {
                    "type": "string",
                    "enum": ["interesting", "not_interesting", "controversial", "technical"],
                    "description": "Filter by verdict",
                },
                "date": {
                    "type": "string",
                    "description": "Filter by date (YYYY-MM-DD format)",
                },
            },
        },
    },
    {
        "name": "search_report_by_id",
        "description": "Check if a report exists for a given story_id. Returns the file path if found.",
        "input_schema": {
            "type": "object",
            "properties": {
                "story_id": {
                    "type": "integer",
                    "description": "Hacker News story ID",
                },
            },
            "required": ["story_id"],
        },
    },
]


# =============================================================================
# Task Tool - Spawn Subagents
# =============================================================================

def get_agent_descriptions() -> str:
    """Generate agent type descriptions."""
    return "\\n".join(
        f"- {name}: {cfg['description']}" for name, cfg in AGENT_TYPES.items()
    )

TASK_TOOL = {
    "name": "Task",
    "description": f"""Spawn a subagent for focused analysis.

Available subagent types:
{get_agent_descriptions()}

Use this to delegate analysis of individual HN stories. Each subagent works independently,
avoiding bias from previous articles. They can read the article, check comments, and write
their analysis to a file.""",
    "input_schema": {
        "type": "object",
        "properties": {
            "description": {
                "type": "string",
                "description": "Short task description (3-5 words)",
            },
            "prompt": {
                "type": "string",
                "description": "Detailed instructions for the subagent",
            },
            "agent_type": {
                "type": "string",
                "enum": list(AGENT_TYPES.keys()),
                "description": "Type of subagent to spawn",
            },
        },
        "required": ["description", "prompt", "agent_type"],
    },
}

# =============================================================================
# Hacker News Tools
# =============================================================================

HN_TOOLS = [
    {
        "name": "get_hn_stories",
        "description": "Fetch Hacker News stories. Returns list with id, title, url, score, author, time, comment count.",
        "input_schema": {
            "type": "object",
            "properties": {
                "story_type": {
                    "type": "string",
                    "enum": ["top", "new", "best", "ask", "show", "job"],
                },
                "limit": {"type": "integer", "minimum": 1, "maximum": 30},
            },
            "required": ["story_type"],
        },
    },
    {
        "name": "get_hn_item",
        "description": "Fetch a specific HN item (story, comment, job) by ID.",
        "input_schema": {
            "type": "object",
            "properties": {"item_id": {"type": "integer"}},
            "required": ["item_id"],
        },
    },
    {
        "name": "get_hn_comments",
        "description": "Fetch comments for a HN story. Returns top-level comments with preview.",
        "input_schema": {
            "type": "object",
            "properties": {
                "story_id": {"type": "integer"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 50},
            },
            "required": ["story_id"],
        },
    },
]

# =============================================================================
# All Tools Combined
# =============================================================================

ALL_TOOLS = BASE_TOOLS + REPORT_TOOLS + [TASK_TOOL] + HN_TOOLS
