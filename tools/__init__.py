# tools/__init__.py
"""Tool collection and registration."""
from .base import BaseTool
from .webpage import ReadWebpageTool
from .hn_stories import GetHNStoriesTool
from .hn_item import GetHNItemTool
from .hn_comments import GetHNCommentsTool
from .finish import FinishExplorationTool
from .task import TaskTool
from .report import (CreateReportTool, ReadReportTool, ListReportsTool,
                     SearchReportByIdTool, AppendReportTool)

# All tool classes
ALL_TOOL_CLASSES = [
    ReadWebpageTool,
    GetHNStoriesTool,
    GetHNItemTool,
    GetHNCommentsTool,
    FinishExplorationTool,
    TaskTool,
    CreateReportTool,
    ReadReportTool,
    ListReportsTool,
    SearchReportByIdTool,
    AppendReportTool,
]

def get_tool_schemas() -> list:
    """Get JSON schemas for all tools."""
    return [tool.get_schema() for tool in ALL_TOOL_CLASSES]

def get_tool_class(name: str) -> type:
    """Get tool class by name."""
    for tool_class in ALL_TOOL_CLASSES:
        if tool_class.get_name() == name:
            return tool_class
    raise ValueError(f"Unknown tool: {name}")
