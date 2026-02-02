# skills/loader.py
"""Skill loader for managing agent skills from .skills/ directory."""

import re
from pathlib import Path
from config import WORKDIR

# Skills directory (separate from code)
SKILLS_DIR = WORKDIR / ".skills"


class SkillLoader:
    """
    Loads and manages skills from SKILL.md files.

    A skill is a FOLDER containing:
    - SKILL.md (required): YAML frontmatter + markdown instructions

    SKILL.md Format:
    ----------------
        ---
        name: chinese-writing
        description: 中文報告寫作。使用時機：寫報告前、格式化輸出時。
        ---

        # 中文報告寫作指南

        ## 輸出格式
        ...

    The YAML frontmatter provides metadata (name, description).
    The markdown body provides detailed instructions.
    """

    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self.skills = {}
        self.load_skills()

    def parse_skill_md(self, path: Path) -> dict:
        """
        Parse a SKILL.md file into metadata and body.

        Returns dict with: name, description, body, path, dir
        Returns None if file doesn't match format.
        """
        try:
            content = path.read_text()
        except Exception:
            return None

        # Match YAML frontmatter between --- markers
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        if not match:
            return None

        frontmatter, body = match.groups()

        # Parse YAML-like frontmatter (simple key: value)
        metadata = {}
        for line in frontmatter.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip().strip("\"'")

        # Require name and description
        if "name" not in metadata or "description" not in metadata:
            return None

        return {
            "name": metadata["name"],
            "description": metadata["description"],
            "body": body.strip(),
            "path": path,
            "dir": path.parent,
        }

    def load_skills(self):
        """
        Scan skills directory and load all valid SKILL.md files.

        Only loads metadata at startup - body is loaded on-demand.
        This keeps the initial context lean.
        """
        if not self.skills_dir.exists():
            self.skills_dir.mkdir(parents=True, exist_ok=True)
            return

        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue

            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue

            skill = self.parse_skill_md(skill_md)
            if skill:
                self.skills[skill["name"]] = skill

    def get_descriptions(self) -> str:
        """
        Generate skill descriptions for system prompt.

        This is Layer 1 - only name and description, ~100 tokens per skill.
        Full content (Layer 2) is loaded only when Skill tool is called.
        """
        if not self.skills:
            return "(no skills available)"

        return "\n".join(
            f"- {name}: {skill['description']}"
            for name, skill in sorted(self.skills.items())
        )

    def get_skill_content(self, name: str) -> str:
        """
        Get full skill content for injection.

        This is Layer 2 - the complete SKILL.md body.

        Returns None if skill not found.
        """
        if name not in self.skills:
            return None

        skill = self.skills[name]
        return f"# Skill: {skill['name']}\n\n{skill['body']}"

    def list_skills(self) -> list:
        """Return list of available skill names."""
        return sorted(self.skills.keys())


# Global skill loader instance
SKILLS = SkillLoader(SKILLS_DIR)
