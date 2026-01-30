# agents/config.py
"""Agent type configurations."""

from tools import (GetHNCommentsTool, GetHNItemTool, GetHNStoriesTool,
                   ReadWebpageTool, CreateReportTool, ReadReportTool,
                   ListReportsTool, SearchReportByIdTool)

AGENT_TYPES = {
    "analyze_story": {
        "description": "Analyze a single HN story for interest, controversy, technical significance. Read the article, check comments, and provide verdict. Write the final analysis report in Chinese.",
        "tools": [
            CreateReportTool.get_name(),
            ReadReportTool.get_name(),
            ReadWebpageTool.get_name(),
            ListReportsTool.get_name(),
            SearchReportByIdTool.get_name(),
            GetHNItemTool.get_name(),
            GetHNCommentsTool.get_name(),
            GetHNStoriesTool.get_name(),
        ],
    },
}
