"""Tool JSON schemas for Claude's function calling."""

from typing import List

# =============================================================================
# Base Tools
# =============================================================================

BASE_TOOLS = [
    {
        "name": "read_file",
        "description": "Read file contents from the workspace.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path relative to workspace"},
                "limit": {"type": "integer", "description": "Max lines to read"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file. Creates directories if needed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path relative to workspace"},
                "content": {"type": "string", "description": "Content to write"}
            },
            "required": ["path", "content"]
        }
    },
]

# =============================================================================
# Subagent Types
# =============================================================================

AGENT_TYPES = {
    "analyze_story": {
        "description": "Analyze a single HN story for interest, controversy, technical significance. Read the article, check comments, and provide verdict.",
        "tools": ["read_file", "write_file"],
    },
}

def get_agent_descriptions() -> str:
    """Generate agent type descriptions for system prompt."""
    return "\n".join(
        f"- {name}: {cfg['description']}" for name, cfg in AGENT_TYPES.items()
    )

# =============================================================================
# Task Tool - Spawn Subagents
# =============================================================================

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
                "description": "Short task description (3-5 words)"
            },
            "prompt": {
                "type": "string",
                "description": "Detailed instructions for the subagent"
            },
            "agent_type": {
                "type": "string",
                "enum": list(AGENT_TYPES.keys()),
                "description": "Type of subagent to spawn"
            }
        },
        "required": ["description", "prompt", "agent_type"]
    }
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
                    "enum": ["top", "new", "best", "ask", "show", "job"]
                },
                "limit": {"type": "integer", "minimum": 1, "maximum": 30}
            },
            "required": ["story_type"]
        }
    },
    {
        "name": "get_hn_item",
        "description": "Fetch a specific HN item (story, comment, job) by ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "item_id": {"type": "integer"}
            },
            "required": ["item_id"]
        }
    },
    {
        "name": "get_hn_comments",
        "description": "Fetch comments for a HN story. Returns top-level comments with preview.",
        "input_schema": {
            "type": "object",
            "properties": {
                "story_id": {"type": "integer"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 50}
            },
            "required": ["story_id"]
        }
    },
    {
        "name": "read_webpage",
        "description": "Read the full content of a webpage. Returns main article text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string"}
            },
            "required": ["url"]
        }
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
                    "description": "Paths to story analysis files"
                }
            },
            "required": ["summary"]
        }
    }
]

# =============================================================================
# All Tools Combined
# =============================================================================

ALL_TOOLS = BASE_TOOLS + [TASK_TOOL] + HN_TOOLS
