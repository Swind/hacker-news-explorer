# agents/base.py
"""Base agent with shared loop logic."""
from abc import ABC, abstractmethod
from anthropic import Anthropic
from config import MODEL, MAX_TOKENS

class BaseAgent(ABC):
    """Shared agent logic for main and sub agents."""

    def __init__(self, client: Anthropic, tools: list, max_tokens: int = MAX_TOKENS):
        self.client = client
        self.tools = tools
        self.max_tokens = max_tokens
        self.tool_call_count = 0

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return system prompt for this agent type."""
        pass

    @abstractmethod
    def should_stop(self, response, is_finished: bool = False) -> bool:
        """Determine if agent should stop."""
        pass

    @abstractmethod
    def execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """Execute a tool - implemented differently by main vs subagent."""
        pass
