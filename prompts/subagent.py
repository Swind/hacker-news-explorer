"""Subagent system prompts."""
from datetime import datetime
from tools.schemas import AGENT_TYPES

def get_subagent_prompt(agent_type: str, workdir: str) -> str:
    """Generate system prompt for specific subagent type."""
    config = AGENT_TYPES.get(agent_type, {})
    today = datetime.now().strftime("%Y-%m-%d")

    template = f"""You are a {agent_type} subagent at {workdir}.

Today's date: {today}

{config.get('description', '')}

Complete the task and return a clear, concise summary."""

    return template
