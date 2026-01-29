# tools/base.py
"""Base class for all tools."""
from abc import ABC, abstractmethod

class BaseTool(ABC):
    """Base class for all tools."""

    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        """Return the tool name."""
        pass

    @classmethod
    @abstractmethod
    def get_schema(cls) -> dict:
        """Return the JSON schema for this tool."""
        pass

    def __init__(self, context: dict):
        """Initialize with execution context (adapters, workdir, etc.)."""
        self.context = context

    def execute(self, **kwargs) -> str:
        """Execute the tool with error handling wrapper."""
        try:
            return self._execute(**kwargs)
        except Exception as e:
            return f"Error executing {self.get_name()}: {str(e)}"

    @abstractmethod
    def _execute(self, **kwargs) -> str:
        """Actual implementation - subclasses override this."""
        pass


class ToolExecutionError(Exception):
    """Base exception for tool execution errors."""
    pass
