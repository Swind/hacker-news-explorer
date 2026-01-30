# config.py
"""Centralized configuration."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL")
MODEL = os.getenv("MODEL_ID", "claude-sonnet-4-5-20250929")

# Agent Configuration
MAX_TOOL_CALLS = 60
MAX_TOKENS = 8192
WORKDIR = Path.cwd()

# Debug
DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

# Output Paths
REPORT_BASE_DIR = WORKDIR / "report"
REPORT_DATE_FORMAT = "%Y-%m-%d"
