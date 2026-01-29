# Hacker News Explorer Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an autonomous agent that uses Claude to explore Hacker News, delegate story analysis to independent subagents, and save findings as markdown files.

**Architecture:** Main agent orchestrates exploration (scans stories, spawns subagents), subagents analyze individual stories in isolation (read article, check comments, write analysis file). Follows v4_skills_agent.py pattern for explicit tool-use control.

**Tech Stack:** Python 3.10+, Anthropic SDK, httpx, trafilatura, python-dotenv

---

## Task 1: Update Dependencies

**Files:**
- Modify: `pyproject.toml`

**Step 1: Add project dependencies**

Edit `pyproject.toml` to add required dependencies:

```toml
[project]
name = "reddit-explorer"
version = "0.1.0"
description = "AI-powered news explorer for Hacker News"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "anthropic>=0.40.0",
    "httpx>=0.27.0",
    "trafilatura>=1.12.0",
    "python-dotenv>=1.0.0",
]
```

**Step 2: Install dependencies**

Run: `pip install -e .`
Expected: Packages installed successfully

**Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "deps: add anthropic, httpx, trafilatura, python-dotenv"
```

---

## Task 2: Create Environment Template

**Files:**
- Create: `.env.example`

**Step 1: Create .env.example**

```bash
# Anthropic API Configuration
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_BASE_URL=https://api.anthropic.com  # Optional: override if using proxy

# Model Configuration
MODEL_ID=claude-sonnet-4-5-20250929
```

**Step 2: Update .gitignore**

```bash
# Environment files
.env
.env.local
```

**Step 3: Commit**

```bash
git add .env.example .gitignore
git commit -m "chore: add environment template and update gitignore"
```

---

## Task 3: Create Adapters Package

**Files:**
- Create: `adapters/__init__.py`
- Create: `adapters/hackernews.py`

**Step 1: Create adapters package**

```python
# adapters/__init__.py
"""Adapters for external data sources."""
```

**Step 2: Implement HackerNewsAdapter**

Create `adapters/hackernews.py`:

```python
"""
Hacker News API Adapter.

Uses the official HN Firebase API:
https://github.com/HackerNews/API
"""
import httpx
from datetime import datetime
from typing import List, Dict, Any, Optional


class HackerNewsAdapter:
    """Adapter for fetching data from Hacker News API."""

    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self, timeout: float = 10.0):
        self.client = httpx.Client(timeout=timeout)

    def _fetch(self, endpoint: str) -> Any:
        """Make a GET request to the HN API."""
        response = self.client.get(f"{self.BASE_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()

    def get_story_ids(self, story_type: str, limit: int = 10) -> List[int]:
        """Get list of story IDs for the given type."""
        type_to_endpoint = {
            "top": "topstories",
            "new": "newstories",
            "best": "beststories",
            "ask": "askstories",
            "show": "showstories",
            "job": "jobstories",
        }

        if story_type not in type_to_endpoint:
            raise ValueError(f"Unknown story_type: {story_type}")

        endpoint = type_to_endpoint[story_type]
        all_ids = self._fetch(f"{endpoint}.json")
        return all_ids[:limit]

    def get_item(self, item_id: int) -> Dict[str, Any]:
        """Fetch a single item (story, comment, job, poll)."""
        return self._fetch(f"item/{item_id}.json")

    def get_stories(self, story_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch multiple stories with their full details."""
        story_ids = self.get_story_ids(story_type, limit)
        stories = []

        for story_id in story_ids:
            item = self.get_item(story_id)
            if item and item.get("type") in ("story", "job"):
                stories.append(self._format_story(item))

        return stories

    def get_comments(self, story_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch top-level comments for a story."""
        story = self.get_item(story_id)
        if not story or "kids" not in story:
            return []

        comment_ids = story["kids"][:limit]
        comments = []

        for comment_id in comment_ids:
            item = self.get_item(comment_id)
            if item and item.get("type") == "comment" and not item.get("deleted"):
                comments.append(self._format_comment(item))

        return comments

    def _format_story(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Format a story item for consistent output."""
        return {
            "id": item.get("id"),
            "title": item.get("title"),
            "url": item.get("url"),
            "score": item.get("score", 0),
            "by": item.get("by"),
            "time": item.get("time"),
            "time_iso": datetime.fromtimestamp(item.get("time", 0)).isoformat() if item.get("time") else None,
            "descendants": item.get("descendants", 0),
            "type": item.get("type"),
            "text": item.get("text"),
        }

    def _format_comment(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Format a comment item for consistent output."""
        return {
            "id": item.get("id"),
            "by": item.get("by"),
            "text": item.get("text"),
            "time": item.get("time"),
            "time_iso": datetime.fromtimestamp(item.get("time", 0)).isoformat() if item.get("time") else None,
            "parent": item.get("parent"),
            "kids_count": len(item.get("kids", [])),
        }

    def close(self):
        """Close the HTTP client."""
        self.client.close()
```

**Step 3: Commit**

```bash
git add adapters/
git commit -m "feat: add HackerNewsAdapter for HN Firebase API"
```

---

## Task 4: Create Web Reader Adapter

**Files:**
- Create: `adapters/web_reader.py`

**Step 1: Implement WebReaderAdapter**

```python
"""
Web Reader Adapter using Trafilatura.

Trafilatura combines fetching and extraction:
https://trafilatura.readthedocs.io/
"""
from trafilatura import fetch_url, extract
from trafilatura.metadata import extract_metadata
from typing import Dict


class WebReaderAdapter:
    """Adapter for reading web page content using Trafilatura."""

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout

    def read(self, url: str) -> Dict:
        """
        Fetch and extract main content from a URL.

        Returns dict with: success, content, title, error
        """
        try:
            downloaded = fetch_url(url, timeout=self.timeout)

            if not downloaded:
                return {
                    "success": False,
                    "error": "Failed to download page",
                    "content": None,
                    "title": None
                }

            content = extract(
                downloaded,
                include_comments=False,
                include_tables=True,
                no_fallback=False
            )

            if not content:
                return {
                    "success": False,
                    "error": "Could not extract content from page",
                    "content": None,
                    "title": None
                }

            metadata = extract_metadata(downloaded)
            title = metadata.get("title") if metadata else None

            return {
                "success": True,
                "content": content,
                "title": title,
                "error": None
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": None,
                "title": None
            }
```

**Step 2: Commit**

```bash
git add adapters/web_reader.py
git commit -m "feat: add WebReaderAdapter using trafilatura"
```

---

## Task 5: Create Tool Schemas

**Files:**
- Create: `tools/__init__.py`
- Create: `tools/schemas.py`

**Step 1: Create tools package**

```python
# tools/__init__.py
"""Tool definitions and handlers for the agent."""
```

**Step 2: Define tool schemas**

Create `tools/schemas.py`:

```python
"""Tool JSON schemas for Claude's function calling."""

from typing import List

# =============================================================================
# Base Tools
# =============================================================================

BASE_TOOLS = [
    {
        "name": "read_file",
        "description": "Read file contents from the workspace.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path relative to workspace"},
                "limit": {"type": "integer", "description": "Max lines to read"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file. Creates directories if needed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path relative to workspace"},
                "content": {"type": "string", "description": "Content to write"}
            },
            "required": ["path", "content"]
        }
    },
]

# =============================================================================
# Subagent Types
# =============================================================================

AGENT_TYPES = {
    "analyze_story": {
        "description": "Analyze a single HN story for interest, controversy, technical significance. Read the article, check comments, and provide verdict.",
        "tools": ["read_file", "write_file"],
    },
}

def get_agent_descriptions() -> str:
    """Generate agent type descriptions for system prompt."""
    return "\n".join(
        f"- {name}: {cfg['description']}" for name, cfg in AGENT_TYPES.items()
    )

# =============================================================================
# Task Tool - Spawn Subagents
# =============================================================================

TASK_TOOL = {
    "name": "Task",
    "description": f"""Spawn a subagent for focused analysis.

Available subagent types:
{get_agent_descriptions()}

Use this to delegate analysis of individual HN stories. Each subagent works independently,
avoiding bias from previous articles. They can read the article, check comments, and write
their analysis to a file.""",
    "input_schema": {
        "type": "object",
        "properties": {
            "description": {
                "type": "string",
                "description": "Short task description (3-5 words)"
            },
            "prompt": {
                "type": "string",
                "description": "Detailed instructions for the subagent"
            },
            "agent_type": {
                "type": "string",
                "enum": list(AGENT_TYPES.keys()),
                "description": "Type of subagent to spawn"
            }
        },
        "required": ["description", "prompt", "agent_type"]
    }
}

# =============================================================================
# Hacker News Tools
# =============================================================================

HN_TOOLS = [
    {
        "name": "get_hn_stories",
        "description": "Fetch Hacker News stories. Returns list with id, title, url, score, author, time, comment count.",
        "input_schema": {
            "type": "object",
            "properties": {
                "story_type": {
                    "type": "string",
                    "enum": ["top", "new", "best", "ask", "show", "job"]
                },
                "limit": {"type": "integer", "minimum": 1, "maximum": 30}
            },
            "required": ["story_type"]
        }
    },
    {
        "name": "get_hn_item",
        "description": "Fetch a specific HN item (story, comment, job) by ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "item_id": {"type": "integer"}
            },
            "required": ["item_id"]
        }
    },
    {
        "name": "get_hn_comments",
        "description": "Fetch comments for a HN story. Returns top-level comments with preview.",
        "input_schema": {
            "type": "object",
            "properties": {
                "story_id": {"type": "integer"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 50}
            },
            "required": ["story_id"]
        }
    },
    {
        "name": "read_webpage",
        "description": "Read the full content of a webpage. Returns main article text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string"}
            },
            "required": ["url"]
        }
    },
    {
        "name": "finish_exploration",
        "description": "Stop exploration and provide summary. Call when you've found enough interesting content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "interesting_stories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Paths to story analysis files"
                }
            },
            "required": ["summary"]
        }
    }
]

# =============================================================================
# All Tools Combined
# =============================================================================

ALL_TOOLS = BASE_TOOLS + [TASK_TOOL] + HN_TOOLS
```

**Step 3: Commit**

```bash
git add tools/
git commit -m "feat: add tool schemas for HN exploration and subagents"
```

---

## Task 6: Create Prompts

**Files:**
- Create: `prompts/__init__.py`
- Create: `prompts/system.py`
- Create: `prompts/subagent.py`

**Step 1: Create prompts package**

```python
# prompts/__init__.py
"""System and subagent prompts."""
```

**Step 2: Create main agent system prompt**

Create `prompts/system.py`:

```python
"""Main agent system prompt."""
from datetime import datetime

TODAY = datetime.now().strftime("%Y-%m-%d")

SYSTEM_PROMPT = f"""You are a News Exploration Agent. Your job is to browse Hacker News and discover interesting, noteworthy content.

## Today's Date

{TODAY}

## Your Goal

Find stories worth the user's attention:
- **Highly discussed** - Active debate (50+ comments)
- **Technically significant** - Major releases, security issues, new paradigms
- **Controversial** - Sparking disagreement
- **Surprising** - Unexpected news, novel ideas

## How to Explore

1. Use `get_hn_stories` to scan different story types (top, new, best, ask, show)
2. For promising stories, **spawn a subagent** using `Task` with agent_type="analyze_story"
   - Each subagent works independently (no bias from other stories)
   - Subagent will: read the article, check comments, assess interest level
   - Subagent writes analysis to: `{TODAY}/<sanitized-title>.md`
3. After subagents finish, call `finish_exploration` with summary

## Subagent Delegation Pattern

**Why use subagents?**
- Independent analysis per story (no context contamination)
- Clean separation of concerns

**When to delegate:**
- Any story that seems potentially interesting based on title/score
- Stories with high comment counts
- Technical topics you're not certain about

**What to tell the subagent:**
- Story ID, title, URL
- What to look for (technical significance, controversy, etc.)
- Output file path: `{TODAY}/<title>.md`

## File Output Format

Subagents should write markdown files:
```markdown
# {TODAY}: [Story Title]

**Source:** Hacker News
**Story ID:** {{id}}
**URL:** {{url}}
**Score:** {{score}} | **Comments:** {{count}}

## Summary
[Brief 2-3 sentence summary]

## Why Interesting
[Explain why this story matters: technical significance, controversy, etc.]

## Key Discussion Points
[Main themes from comments]

## Verdict
[INTERESTING / WORTH_READING / SKIP]
```

## Important Constraints

- Max 30 tool calls per session
- Use subagents for story analysis (don't do it yourself)
- Always call `finish_exploration` when done
- Create `{TODAY}/` directory if it doesn't exist"""
```

**Step 3: Create subagent prompt template**

Create `prompts/subagent.py`:

```python
"""Subagent prompt templates."""

ANALYZE_STORY_PROMPT = """You are a Story Analysis Subagent. Your job is to analyze a single Hacker News story and determine if it's interesting.

## Your Task

Analyze this HN story:
- Story ID: {story_id}
- Title: {title}
- URL: {url}
- Score: {score} | Comments: {comment_count}

## Analysis Steps

1. Read the article (use `read_webpage`)
2. Check comments (use `get_hn_comments`) to gauge discussion
3. Assess: Is this technically significant? Controversial? Surprising?

## Output

Write your analysis to: `{output_path}`

Format:
```markdown
# {TODAY}: {title}

**Source:** Hacker News
**Story ID:** {story_id}
**URL:** {url}
**Score:** {score} | **Comments:** {comment_count}

## Summary
[2-3 sentence summary of the article/story]

## Why Interesting
[Why does this matter? Technical significance? Controversy? Novel insights?]

## Key Discussion Points
[What are people talking about in comments? Any debates?]

## Verdict
[One of: INTERESTING | WORTH_READING | SKIP - and brief reason]
```

After writing the file, return a concise summary of your analysis."""

def format_analyze_story_prompt(story_id: int, title: str, url: str, score: int,
                                 comment_count: int, output_path: str) -> str:
    """Format the analyze_story subagent prompt with story details."""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")

    return ANALYZE_STORY_PROMPT.format(
        story_id=story_id,
        title=title,
        url=url,
        score=score,
        comment_count=comment_count,
        output_path=output_path,
        TODAY=today
    )
```

**Step 4: Commit**

```bash
git add prompts/
git commit -m "feat: add system and subagent prompts"
```

---

## Task 7: Implement Main Agent Loop

**Files:**
- Modify: `main.py`

**Step 1: Implement main agent**

Replace `main.py` with:

```python
#!/usr/bin/env python3
"""
News Explorer Agent - Browse Hacker News intelligently with Claude.

Follows the v4_skills_agent.py pattern:
- Explicit agent loop with client.messages.create()
- Tool-use blocks processed explicitly
- Tool results appended with correct structure
- Subagent delegation for independent story analysis
"""
import os
import sys
import re
import subprocess
from pathlib import Path
from dotenv import load_dotenv

from anthropic import Anthropic
from anthropic.types import ToolUseBlock

from adapters.hackernews import HackerNewsAdapter
from adapters.web_reader import WebReaderAdapter
from tools.schemas import ALL_TOOLS, AGENT_TYPES, BASE_TOOLS
from prompts.system import SYSTEM_PROMPT

load_dotenv()

# Configuration
MODEL = os.getenv("MODEL_ID", "claude-sonnet-4-5-20250929")
MAX_TOOL_CALLS = 30
WORKDIR = Path.cwd()


class NewsExplorerAgent:
    """Agent that explores Hacker News using Claude."""

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")

        base_url = os.getenv("ANTHROPIC_BASE_URL")
        self.client = Anthropic(api_key=api_key, base_url=base_url)
        self.hn = HackerNewsAdapter()
        self.web_reader = WebReaderAdapter()
        self.tool_call_count = 0
        self.is_finished = False
        self.final_summary = None

    def execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """Execute a tool call and return the result."""
        self.tool_call_count += 1

        try:
            if tool_name == "read_file":
                return self._read_file(tool_input["path"], tool_input.get("limit"))

            elif tool_name == "write_file":
                return self._write_file(tool_input["path"], tool_input["content"])

            elif tool_name == "get_hn_stories":
                result = self.hn.get_stories(
                    story_type=tool_input["story_type"],
                    limit=tool_input.get("limit", 10)
                )
                return self._format_stories(result)

            elif tool_name == "get_hn_item":
                result = self.hn.get_item(tool_input["item_id"])
                return self._format_item(result)

            elif tool_name == "get_hn_comments":
                result = self.hn.get_comments(
                    story_id=tool_input["story_id"],
                    limit=tool_input.get("limit", 20)
                )
                return self._format_comments(result)

            elif tool_name == "read_webpage":
                result = self.web_reader.read(tool_input["url"])
                if result["success"]:
                    content = result["content"]
                    title = result.get("title", "")
                    output = f"Title: {title}\n\n{content[:10000]}"
                    if len(content) > 10000:
                        output += f"\n\n... (content truncated, was {len(content)} chars)"
                    return output
                else:
                    return f"Failed to read webpage: {result['error']}"

            elif tool_name == "Task":
                return self._run_subagent(
                    tool_input["agent_type"],
                    tool_input["description"],
                    tool_input["prompt"]
                )

            elif tool_name == "finish_exploration":
                self.is_finished = True
                self.final_summary = tool_input.get("summary", "")
                stories = tool_input.get("interesting_stories", [])
                output = f"**EXPLORATION FINISHED**\n\nSummary: {self.final_summary}"
                if stories:
                    output += f"\n\nInteresting stories:\n" + "\n".join(f"- {s}" for s in stories)
                return output

            else:
                return f"Unknown tool: {tool_name}"

        except Exception as e:
            return f"Error executing {tool_name}: {e}"

    def _read_file(self, path: str, limit: int = None) -> str:
        """Read file contents."""
        file_path = (WORKDIR / path).resolve()
        if not file_path.is_relative_to(WORKDIR):
            return "Error: Path escapes workspace"
        try:
            lines = file_path.read_text().splitlines()
            if limit:
                lines = lines[:limit]
            return "\n".join(lines)
        except Exception as e:
            return f"Error reading file: {e}"

    def _write_file(self, path: str, content: str) -> str:
        """Write content to file."""
        file_path = (WORKDIR / path).resolve()
        if not file_path.is_relative_to(WORKDIR):
            return "Error: Path escapes workspace"
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            return f"Wrote {len(content)} bytes to {path}"
        except Exception as e:
            return f"Error writing file: {e}"

    def _format_stories(self, stories: list) -> str:
        """Format stories list for display."""
        if not stories:
            return "No stories found."
        lines = []
        for s in stories:
            line = f"[{s['id']}] {s['title']}"
            if s.get("url"):
                line += f" ({s['url']})"
            line += f" | score: {s['score']} | comments: {s['descendants']} | by: {s['by']}"
            lines.append(line)
        return "\n".join(lines)

    def _format_item(self, item: dict) -> str:
        """Format single item for display."""
        if not item:
            return "Item not found."
        lines = [
            f"ID: {item.get('id')}",
            f"Type: {item.get('type')}",
            f"Title: {item.get('title')}",
            f"URL: {item.get('url')}",
            f"Score: {item.get('score')}",
            f"By: {item.get('by')}",
            f"Time: {item.get('time_iso')}",
        ]
        if item.get("text"):
            lines.append(f"\nText: {item['text'][:500]}...")
        return "\n".join(lines)

    def _format_comments(self, comments: list) -> str:
        """Format comments for display."""
        if not comments:
            return "No comments found."
        lines = []
        for c in comments:
            text_preview = c.get("text", "")[:200].replace("\n", " ")
            lines.append(f"[{c['id']}] by {c['by']}: {text_preview}...")
        return "\n".join(lines)

    def _run_subagent(self, agent_type: str, description: str, prompt: str) -> str:
        """Run a subagent for isolated task execution."""
        if agent_type not in AGENT_TYPES:
            return f"Unknown agent type: {agent_type}"

        config = AGENT_TYPES[agent_type]
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")

        sub_system = f"""You are a {agent_type} subagent at {WORKDIR}.

Today's date: {today}

{config['description']}

Complete the task and return a clear, concise summary."""

        # Filter tools for subagent (only BASE_TOOLS for analyze_story)
        sub_tools = [t for t in BASE_TOOLS if t["name"] in config.get("tools", BASE_TOOLS)]
        sub_messages = [{"role": "user", "content": prompt}]

        print(f"  [{agent_type}] {description}")
        tool_count = 0

        while True:
            response = self.client.messages.create(
                model=MODEL,
                system=sub_system,
                messages=sub_messages,
                tools=sub_tools,
                max_tokens=4096,
            )

            # Collect text and tool calls
            text_blocks = []
            tool_calls = []

            for block in response.content:
                if hasattr(block, "text") and block.text:
                    text_blocks.append(block.text)
                if block.type == "tool_use":
                    tool_calls.append(block)

            # Append assistant message
            sub_messages.append({"role": "assistant", "content": response.content})

            # Check stop condition
            if response.stop_reason != "tool_use" or not tool_calls:
                break

            # Execute tools
            results = []
            for tc in tool_calls:
                tool_count += 1
                result = self._execute_tool_for_subagent(tc.name, tc.input)
                results.append({
                    "type": "tool_result",
                    "tool_use_id": tc.id,
                    "content": result
                })

            # Append tool results
            sub_messages.append({"role": "user", "content": results})

        # Get final text response
        for block in response.content:
            if hasattr(block, "text") and block.text:
                return f"[{agent_type}] {description} - done ({tool_count} tools)\n{block.text}"

        return f"[{agent_type}] {description} - done ({tool_count} tools)\n(subagent returned no text)"

    def _execute_tool_for_subagent(self, tool_name: str, tool_input: dict) -> str:
        """Execute tool for subagent (limited set)."""
        try:
            if tool_name == "read_file":
                return self._read_file(tool_input["path"], tool_input.get("limit"))
            elif tool_name == "write_file":
                return self._write_file(tool_input["path"], tool_input["content"])
            else:
                return f"Unknown tool for subagent: {tool_name}"
        except Exception as e:
            return f"Error: {e}"

    def run(self, user_message: str = None):
        """Run the agent loop."""
        if user_message is None:
            user_message = "Explore Hacker News and find interesting content."

        print(f"🤖 News Explorer Agent - {WORKDIR}")
        print(f"Model: {MODEL}")
        print(f"Max tool calls: {MAX_TOOL_CALLS}")
        print("-" * 50)

        messages = [
            {"role": "user", "content": user_message}
        ]

        while not self.is_finished and self.tool_call_count < MAX_TOOL_CALLS:
            response = self.client.messages.create(
                model=MODEL,
                system=SYSTEM_PROMPT,
                messages=messages,
                tools=ALL_TOOLS,
                max_tokens=4096,
            )

            # Extract text content and tool calls
            text_blocks = []
            tool_calls = []

            for block in response.content:
                if hasattr(block, "text") and block.text:
                    text_blocks.append(block.text)
                    print(block.text)
                if block.type == "tool_use":
                    tool_calls.append(block)

            # Append assistant message
            messages.append({"role": "assistant", "content": response.content})

            # Check stop condition
            if response.stop_reason != "tool_use" or not tool_calls:
                break

            # Execute tools and build results
            results = []
            for tc in tool_calls:
                print(f"\n> {tc.name}")

                # Safety check
                if self.tool_call_count >= MAX_TOOL_CALLS:
                    result = "Max tool calls reached. Please call finish_exploration."
                else:
                    result = self.execute_tool(tc.name, tc.input)

                # Show preview
                preview = result[:200] + "..." if len(result) > 200 else result
                print(f"  {preview}")

                results.append({
                    "type": "tool_result",
                    "tool_use_id": tc.id,
                    "content": result
                })

            # Append tool results as user message
            messages.append({"role": "user", "content": results})

        # Final summary
        print("\n" + "=" * 50)
        if self.final_summary:
            print(f"📋 Summary: {self.final_summary}")
        print(f"📊 Tool calls made: {self.tool_call_count}/{MAX_TOOL_CALLS}")
        print("=" * 50)


def main():
    """Entry point."""
    agent = NewsExplorerAgent()
    agent.run()


if __name__ == "__main__":
    main()
```

**Step 2: Commit**

```bash
git add main.py
git commit -m "feat: implement main agent loop with subagent support"
```

---

## Task 8: Create .env File

**Files:**
- Create: `.env`

**Step 1: Create .env from template**

```bash
cp .env.example .env
# Edit .env with your actual API keys
```

**Step 2: Add to .gitignore (if not already there)**

The `.gitignore` should have `.env` in it (from Task 2).

**Step 3: Do NOT commit .env**

The `.env` file contains secrets and should never be committed.

---

## Task 9: Manual Testing

**Files:**
- Test: Run the agent manually

**Step 1: Run the agent**

```bash
cd /home/swind/Program/reddit-explorer
python main.py
```

**Step 2: Verify behavior**

Expected:
1. Agent scans HN stories
2. Spawns subagents for interesting stories
3. Creates `{YYYY-MM-DD}/` directory with analysis files
4. Calls `finish_exploration` with summary

**Step 3: Check output files**

```bash
ls -la */*.md  # List generated markdown files
cat */*.md     # Read analysis files
```

---

## Task 10: Clean Up Worktree

**After implementation is complete:**

**Step 1: Return to main branch**

```bash
cd /home/swind/Program/reddit-explorer
git checkout master
```

**Step 2: Merge feature branch**

```bash
git merge feature/hn-explorer
```

**Step 3: Remove worktree**

```bash
git worktree remove .worktrees/hn-explorer
git branch -d feature/hn-explorer  # Delete branch after merge
```

---
