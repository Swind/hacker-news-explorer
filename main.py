#!/usr/bin/env python3
"""
News Explorer Agent - Browse Hacker News intelligently with Claude.

Modular architecture with tools/, agents/, and prompts/ packages.
"""
from anthropic import Anthropic

from agents.main import NewsExplorerAgent
from config import ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL


def main():
    """Entry point."""
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set in environment")

    client = Anthropic(api_key=ANTHROPIC_API_KEY, base_url=ANTHROPIC_BASE_URL)
    agent = NewsExplorerAgent(client)
    agent.run()


if __name__ == "__main__":
    main()
