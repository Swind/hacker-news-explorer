"""Subagent system prompts."""
from datetime import datetime
from agents.config import AGENT_TYPES
from skills.loader import SKILLS

def get_subagent_prompt(agent_type: str, workdir: str) -> str:
    """Generate system prompt for specific subagent type."""
    config = AGENT_TYPES.get(agent_type, {})
    today = datetime.now().strftime("%Y-%m-%d")

    template = f"""You are a {agent_type} subagent at {workdir}.

Today's date: {today}

**Skills available** (invoke with Skill tool when task matches):
{SKILLS.get_descriptions()}

**TodoWrite available** (use to update main agent's task list):
You can update the main agent's todo list to mark your task as completed.

{config.get('description', '')}

Complete the task and return a clear, concise summary."""

    return template
