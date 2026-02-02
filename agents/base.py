# agents/base.py
"""Base agent with shared loop logic."""
import time
from abc import ABC, abstractmethod
from anthropic import Anthropic
from config import MODEL, MAX_TOKENS

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # seconds
BACKOFF_FACTOR = 2.0


def retry_api_call(func, *args, max_retries=MAX_RETRIES, initial_delay=RETRY_DELAY, **kwargs):
    """Retry an API call with exponential backoff.

    Args:
        func: The function to call (e.g., client.messages.create)
        *args: Positional arguments to pass to func
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
        **kwargs: Keyword arguments to pass to func

    Returns:
        The result of the function call

    Raises:
        Exception: If all retries are exhausted
    """
    last_error = None
    delay = initial_delay

    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_error = e
            # Check if error is retryable (network errors, rate limits, server errors)
            error_str = str(e).lower()
            is_retryable = any(keyword in error_str for keyword in [
                'timeout', 'connection', 'network', 'rate limit',
                '429', '500', '502', '503', '504', 'temporarily'
            ])

            if not is_retryable:
                # Don't retry non-retryable errors (auth, invalid params, etc.)
                raise

            if attempt < max_retries - 1:
                print(f"  ⚠️  API call failed (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"  🔄 Retrying in {delay:.1f}s...")
                time.sleep(delay)
                delay *= BACKOFF_FACTOR
            else:
                print(f"  ❌ API call failed after {max_retries} attempts")

    # All retries exhausted
    raise last_error


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
