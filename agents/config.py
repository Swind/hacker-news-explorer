# agents/config.py
"""Agent type configurations."""

from tools import (GetHNCommentsTool, GetHNItemTool, GetHNStoriesTool,
                   ReadFileTool, ReadWebpageTool, WriteFileTool)

AGENT_TYPES = {
    "analyze_story": {
        "description": "Analyze a single HN story for interest, controversy, technical significance. Read the article, check comments, and provide verdict. Write the final analysis report in Chinese.",
        "tools": [
            ReadFileTool.get_name(),
            WriteFileTool.get_name(),
            ReadWebpageTool.get_name(),
            GetHNItemTool.get_name(),
            GetHNCommentsTool.get_name(),
            GetHNStoriesTool.get_name(),
        ],
    },
}
