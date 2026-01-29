# agents/config.py
"""Agent type configurations."""

AGENT_TYPES = {
    "analyze_story": {
        "description": "Analyze a single HN story for interest, controversy, technical significance. Read the article, check comments, and provide verdict. Write the final analysis report in Chinese.",
        "tools": ["read_file", "write_file", "read_webpage"],
    },
}
