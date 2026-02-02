# tools/skill.py
"""Skill loading tool."""
from .base import BaseTool
from agents.base import SKILL_TOOL, run_skill


class SkillTool(BaseTool):
    """Tool for loading skills to gain specialized knowledge."""

    @classmethod
    def get_name(cls) -> str:
        return "Skill"

    @classmethod
    def get_schema(cls) -> dict:
        return SKILL_TOOL

    def _execute(self, skill: str) -> str:
        """Load and inject a skill into the conversation."""
        return run_skill(skill)
