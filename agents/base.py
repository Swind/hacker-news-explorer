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


# =============================================================================
# Skill Tool
# =============================================================================

from skills.loader import SKILLS


SKILL_TOOL = {
    "name": "Skill",
    "description": f"""Load a skill to gain specialized knowledge for a task.

Available skills:
{SKILLS.get_descriptions()}

When to use:
- IMMEDIATELY when user task matches a skill description
- Before attempting domain-specific work

The skill content will be injected into the conversation, giving you
detailed instructions.""",
    "input_schema": {
        "type": "object",
        "properties": {
            "skill": {"type": "string", "description": "Name of the skill to load"}
        },
        "required": ["skill"],
    },
}


def run_skill(skill_name: str) -> str:
    """
    Load a skill and inject it into the conversation.

    This is the key mechanism:
    1. Get skill content (SKILL.md body)
    2. Return it wrapped in <skill-loaded> tags
    3. Model receives this as tool_result (user message)
    4. Model now "knows" how to do the task

    Why tool_result instead of system prompt?
    - System prompt changes invalidate cache (20-50x cost increase)
    - Tool results append to end (prefix unchanged, cache hit)
    """
    content = SKILLS.get_skill_content(skill_name)

    if content is None:
        available = ", ".join(SKILLS.list_skills()) or "none"
        return f"Error: Unknown skill '{skill_name}'. Available: {available}"

    # Wrap in tags so model knows it's skill content
    return f"""<skill-loaded name="{skill_name}">
{content}
</skill-loaded>

Follow the instructions in the skill above to complete the user's task."""
