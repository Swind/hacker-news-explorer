# Reddit Explorer Refactor Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor main.py (435 lines) into modular architecture with tools/, agents/, and prompts/ packages.

**Architecture:** Separate concerns using BaseTool and BaseAgent classes. Tools execute independently. Agents share agent loop logic via BaseAgent. Prompts organized by function.

**Tech Stack:** Python 3.10+, Anthropic SDK, abc module

---

## Task 1: Create config.py

**Files:**
- Create: `config.py`

**Step 1: Write the configuration file**

```python
# config.py
"""Centralized configuration."""
import os
from pathlib import Path

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL")
MODEL = os.getenv("MODEL_ID", "claude-sonnet-4-5-20250929")

# Agent Configuration
MAX_TOOL_CALLS = 30
MAX_TOKENS = 4096
WORKDIR = Path.cwd()

# Debug
DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

# Output Paths
REPORT_BASE_DIR = WORKDIR / "report"
REPORT_DATE_FORMAT = "%Y-%m-%d"
```

**Step 2: Verify imports work**

Run: `python -c "import config; print(config.MODEL)"`
Expected: Output model name

**Step 3: Commit**

```bash
git add config.py
git commit -m "feat: add centralized configuration module"
```

---

## Task 2: Create prompts/templates.py

**Files:**
- Create: `prompts/templates.py`

**Step 1: Write the templates module**

```python
# prompts/templates.py
"""Output format templates."""

CHINESE_OUTPUT_TEMPLATE = """# {TODAY}: [故事標題]

**來源：** Hacker News
**故事 ID：** {{id}}
**網址：** {{url}}
**分數：** {{score}} | **評論數：** {{count}}

## 摘要
[簡短的 2-3 句話摘要]

## 為什麼有趣
[解釋為什麼這個故事重要：技術意義、爭議等]

## 主要討論點
[評論中的主題]

## 評價
[有趣 / 值得閱讀 / 跳過]
"""
```

**Step 2: Verify imports work**

Run: `python -c "from prompts.templates import CHINESE_OUTPUT_TEMPLATE; print(len(CHINESE_OUTPUT_TEMPLATE))"`
Expected: Output template length

**Step 3: Commit**

```bash
git add prompts/templates.py
git commit -m "feat: add output format templates"
```

---

## Task 3: Update prompts/system.py to use templates

**Files:**
- Modify: `prompts/system.py`

**Step 1: Update system prompt to use templates**

```python
# prompts/system.py
"""Main agent system prompt."""
from datetime import datetime
from .templates import CHINESE_OUTPUT_TEMPLATE

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
   - Subagent writes analysis to: `report/{{TODAY}}/hacker-news/<sanitized-title>.md`
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
- Output file path: `report/{{TODAY}}/hacker-news/<title>.md`

## File Output Format

Subagents should write markdown files in **Chinese** (translate your analysis):
{CHINESE_OUTPUT_TEMPLATE}

## Important Constraints

- Max 30 tool calls per session
- Use subagents for story analysis (don't do it yourself)
- Always call `finish_exploration` when done
- Create `report/{{TODAY}}/hacker-news/` directory if it doesn't exist"""
```

**Step 2: Verify it still works**

Run: `python -c "from prompts.system import SYSTEM_PROMPT; print(len(SYSTEM_PROMPT))"`
Expected: Output prompt length

**Step 3: Commit**

```bash
git add prompts/system.py
git commit -m "refactor: use templates in system prompt"
```

---

## Task 4: Update prompts/subagent.py

**Files:**
- Modify: `prompts/subagent.py`

**Step 1: Update subagent prompt function**

```python
# prompts/subagent.py
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
```

**Step 2: Verify it works**

Run: `python -c "from prompts.subagent import get_subagent_prompt; print(get_subagent_prompt('analyze_story', '/tmp'))"`
Expected: Output formatted prompt

**Step 3: Commit**

```bash
git add prompts/subagent.py
git commit -m "refactor: improve subagent prompt function"
```

---

## Task 5: Create tools/base.py

**Files:**
- Create: `tools/base.py`

**Step 1: Write BaseTool abstract class**

```python
# tools/base.py
"""Base class for all tools."""
from abc import ABC, abstractmethod

class BaseTool(ABC):
    """Base class for all tools."""

    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        """Return the tool name."""
        pass

    @classmethod
    @abstractmethod
    def get_schema(cls) -> dict:
        """Return the JSON schema for this tool."""
        pass

    def __init__(self, context: dict):
        """Initialize with execution context (adapters, workdir, etc.)."""
        self.context = context

    def execute(self, **kwargs) -> str:
        """Execute the tool with error handling wrapper."""
        try:
            return self._execute(**kwargs)
        except Exception as e:
            return f"Error executing {self.get_name()}: {str(e)}"

    @abstractmethod
    def _execute(self, **kwargs) -> str:
        """Actual implementation - subclasses override this."""
        pass


class ToolExecutionError(Exception):
    """Base exception for tool execution errors."""
    pass
```

**Step 2: Verify imports work**

Run: `python -c "from tools.base import BaseTool; print('BaseTool imported successfully')"`
Expected: Output success message

**Step 3: Commit**

```bash
git add tools/base.py
git commit -m "feat: add BaseTool abstract class"
```

---

## Task 6: Create tools/file_read.py

**Files:**
- Create: `tools/file_read.py`

**Step 1: Write ReadFileTool**

```python
# tools/file_read.py
"""Read file tool."""
from pathlib import Path
from .base import BaseTool

class ReadFileTool(BaseTool):
    """Tool for reading file contents from workspace."""

    @classmethod
    def get_name(cls) -> str:
        return "read_file"

    @classmethod
    def get_schema(cls) -> dict:
        return {
            "name": "read_file",
            "description": "Read file contents from the workspace.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path relative to workspace"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max lines to read"
                    }
                },
                "required": ["path"]
            }
        }

    def _execute(self, path: str, limit: int = None) -> str:
        """Read file contents."""
        workdir = self.context.get("workdir", Path.cwd())
        file_path = (workdir / path).resolve()

        if not file_path.is_relative_to(workdir):
            return "Error: Path escapes workspace"

        try:
            lines = file_path.read_text().splitlines()
            if limit:
                lines = lines[:limit]
            return "\\n".join(lines)
        except Exception as e:
            return f"Error reading file: {e}"
```

**Step 2: Verify imports work**

Run: `python -c "from tools.file_read import ReadFileTool; print(ReadFileTool.get_name())"`
Expected: Output "read_file"

**Step 3: Commit**

```bash
git add tools/file_read.py
git commit -m "feat: add ReadFileTool"
```

---

## Task 7: Create tools/file_write.py

**Files:**
- Create: `tools/file_write.py`

**Step 1: Write WriteFileTool**

```python
# tools/file_write.py
"""Write file tool."""
from pathlib import Path
from .base import BaseTool

class WriteFileTool(BaseTool):
    """Tool for writing content to files."""

    @classmethod
    def get_name(cls) -> str:
        return "write_file"

    @classmethod
    def get_schema(cls) -> dict:
        return {
            "name": "write_file",
            "description": "Write content to a file. Creates directories if needed.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path relative to workspace"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write"
                    }
                },
                "required": ["path", "content"]
            }
        }

    def _execute(self, path: str, content: str) -> str:
        """Write content to file."""
        workdir = self.context.get("workdir", Path.cwd())
        file_path = (workdir / path).resolve()

        if not file_path.is_relative_to(workdir):
            return "Error: Path escapes workspace"

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            return f"Wrote {len(content)} bytes to {path}"
        except Exception as e:
            return f"Error writing file: {e}"
```

**Step 2: Verify imports work**

Run: `python -c "from tools.file_write import WriteFileTool; print(WriteFileTool.get_name())"`
Expected: Output "write_file"

**Step 3: Commit**

```bash
git add tools/file_write.py
git commit -m "feat: add WriteFileTool"
```

---

## Task 8: Create tools/webpage.py

**Files:**
- Create: `tools/webpage.py`

**Step 1: Write ReadWebpageTool**

```python
# tools/webpage.py
"""Read webpage tool."""
from .base import BaseTool

class ReadWebpageTool(BaseTool):
    """Tool for reading webpage content."""

    @classmethod
    def get_name(cls) -> str:
        return "read_webpage"

    @classmethod
    def get_schema(cls) -> dict:
        return {
            "name": "read_webpage",
            "description": "Read the full content of a webpage. Returns main article text.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"}
                },
                "required": ["url"]
            }
        }

    def _execute(self, url: str) -> str:
        """Read webpage content."""
        web_reader = self.context.get("web_reader")
        if not web_reader:
            return "Error: web_reader not available in context"

        result = web_reader.read(url)
        if result["success"]:
            content = result["content"]
            title = result.get("title", "")
            output = f"Title: {title}\\n\\n{content[:10000]}"
            if len(content) > 10000:
                output += f"\\n\\n... (content truncated, was {len(content)} chars)"
            return output
        else:
            return f"Failed to read webpage: {result['error']}"
```

**Step 2: Verify imports work**

Run: `python -c "from tools.webpage import ReadWebpageTool; print(ReadWebpageTool.get_name())"`
Expected: Output "read_webpage"

**Step 3: Commit**

```bash
git add tools/webpage.py
git commit -m "feat: add ReadWebpageTool"
```

---

## Task 9: Create tools/hn_stories.py

**Files:**
- Create: `tools/hn_stories.py`

**Step 1: Write GetHNStoriesTool**

```python
# tools/hn_stories.py
"""Get Hacker News stories tool."""
from .base import BaseTool

class GetHNStoriesTool(BaseTool):
    """Tool for fetching HN stories."""

    @classmethod
    def get_name(cls) -> str:
        return "get_hn_stories"

    @classmethod
    def get_schema(cls) -> dict:
        return {
            "name": "get_hn_stories",
            "description": "Fetch Hacker News stories. Returns list with id, title, url, score, author, time, comment count.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "story_type": {
                        "type": "string",
                        "enum": ["top", "new", "best", "ask", "show", "job"]
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 30
                    }
                },
                "required": ["story_type"]
            }
        }

    def _execute(self, story_type: str, limit: int = 10) -> str:
        """Fetch HN stories."""
        hn_adapter = self.context.get("hn_adapter")
        if not hn_adapter:
            return "Error: hn_adapter not available in context"

        result = hn_adapter.get_stories(story_type=story_type, limit=limit)
        return self._format_stories(result)

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
        return "\\n".join(lines)
```

**Step 2: Verify imports work**

Run: `python -c "from tools.hn_stories import GetHNStoriesTool; print(GetHNStoriesTool.get_name())"`
Expected: Output "get_hn_stories"

**Step 3: Commit**

```bash
git add tools/hn_stories.py
git commit -m "feat: add GetHNStoriesTool"
```

---

## Task 10: Create tools/hn_item.py

**Files:**
- Create: `tools/hn_item.py`

**Step 1: Write GetHNItemTool**

```python
# tools/hn_item.py
"""Get Hacker News item tool."""
from .base import BaseTool

class GetHNItemTool(BaseTool):
    """Tool for fetching a specific HN item."""

    @classmethod
    def get_name(cls) -> str:
        return "get_hn_item"

    @classmethod
    def get_schema(cls) -> dict:
        return {
            "name": "get_hn_item",
            "description": "Fetch a specific HN item (story, comment, job) by ID.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "item_id": {"type": "integer"}
                },
                "required": ["item_id"]
            }
        }

    def _execute(self, item_id: int) -> str:
        """Fetch HN item."""
        hn_adapter = self.context.get("hn_adapter")
        if not hn_adapter:
            return "Error: hn_adapter not available in context"

        result = hn_adapter.get_item(item_id)
        return self._format_item(result)

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
            f"Time: {item.get('time_iso')}"
        ]
        if item.get("text"):
            lines.append(f"\\nText: {item['text'][:500]}...")
        return "\\n".join(lines)
```

**Step 2: Verify imports work**

Run: `python -c "from tools.hn_item import GetHNItemTool; print(GetHNItemTool.get_name())"`
Expected: Output "get_hn_item"

**Step 3: Commit**

```bash
git add tools/hn_item.py
git commit -m "feat: add GetHNItemTool"
```

---

## Task 11: Create tools/hn_comments.py

**Files:**
- Create: `tools/hn_comments.py`

**Step 1: Write GetHNCommentsTool**

```python
# tools/hn_comments.py
"""Get Hacker News comments tool."""
from .base import BaseTool

class GetHNCommentsTool(BaseTool):
    """Tool for fetching HN story comments."""

    @classmethod
    def get_name(cls) -> str:
        return "get_hn_comments"

    @classmethod
    def get_schema(cls) -> dict:
        return {
            "name": "get_hn_comments",
            "description": "Fetch comments for a HN story. Returns top-level comments with preview.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "story_id": {"type": "integer"},
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 50
                    }
                },
                "required": ["story_id"]
            }
        }

    def _execute(self, story_id: int, limit: int = 20) -> str:
        """Fetch HN comments."""
        hn_adapter = self.context.get("hn_adapter")
        if not hn_adapter:
            return "Error: hn_adapter not available in context"

        result = hn_adapter.get_comments(story_id=story_id, limit=limit)
        return self._format_comments(result)

    def _format_comments(self, comments: list) -> str:
        """Format comments for display."""
        if not comments:
            return "No comments found."
        lines = []
        for c in comments:
            text_preview = c.get("text", "")[:200].replace("\\n", " ")
            lines.append(f"[{c['id']}] by {c['by']}: {text_preview}...")
        return "\\n".join(lines)
```

**Step 2: Verify imports work**

Run: `python -c "from tools.hn_comments import GetHNCommentsTool; print(GetHNCommentsTool.get_name())"`
Expected: Output "get_hn_comments"

**Step 3: Commit**

```bash
git add tools/hn_comments.py
git commit -m "feat: add GetHNCommentsTool"
```

---

## Task 12: Create tools/finish.py

**Files:**
- Create: `tools/finish.py`

**Step 1: Write FinishExplorationTool**

```python
# tools/finish.py
"""Finish exploration tool."""
from .base import BaseTool

class FinishExplorationTool(BaseTool):
    """Tool for stopping exploration and providing summary."""

    @classmethod
    def get_name(cls) -> str:
        return "finish_exploration"

    @classmethod
    def get_schema(cls) -> dict:
        return {
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

    def _execute(self, summary: str, interesting_stories: list = None) -> str:
        """Mark exploration as finished."""
        # Set flag in context for agent to check
        self.context["is_finished"] = True
        self.context["final_summary"] = summary

        output = f"**EXPLORATION FINISHED**\\n\\nSummary: {summary}"
        if interesting_stories:
            output += f"\\n\\nInteresting stories:\\n" + "\\n".join(f"- {s}" for s in interesting_stories)
        return output
```

**Step 2: Verify imports work**

Run: `python -c "from tools.finish import FinishExplorationTool; print(FinishExplorationTool.get_name())"`
Expected: Output "finish_exploration"

**Step 3: Commit**

```bash
git add tools/finish.py
git commit -m "feat: add FinishExplorationTool"
```

---

## Task 13: Update tools/__init__.py

**Files:**
- Modify: `tools/__init__.py`

**Step 1: Update to collect all tool classes**

```python
# tools/__init__.py
"""Tool collection and registration."""
from .base import BaseTool
from .file_read import ReadFileTool
from .file_write import WriteFileTool
from .webpage import ReadWebpageTool
from .hn_stories import GetHNStoriesTool
from .hn_item import GetHNItemTool
from .hn_comments import GetHNCommentsTool
from .finish import FinishExplorationTool

# All tool classes
ALL_TOOL_CLASSES = [
    ReadFileTool,
    WriteFileTool,
    ReadWebpageTool,
    GetHNStoriesTool,
    GetHNItemTool,
    GetHNCommentsTool,
    FinishExplorationTool,
]

def get_tool_schemas() -> list:
    """Get JSON schemas for all tools."""
    return [tool.get_schema() for tool in ALL_TOOL_CLASSES]

def get_tool_class(name: str) -> type:
    """Get tool class by name."""
    for tool_class in ALL_TOOL_CLASSES:
        if tool_class.get_name() == name:
            return tool_class
    raise ValueError(f"Unknown tool: {name}")
```

**Step 2: Verify imports work**

Run: `python -c "from tools import get_tool_schemas; print(f'{len(get_tool_schemas())} tools')"`
Expected: Output "7 tools"

**Step 3: Commit**

```bash
git add tools/__init__.py
git commit -m "refactor: update tools module to collect all tools"
```

---

## Task 14: Create agents/base.py

**Files:**
- Create: `agents/base.py`
- Create: `agents/__init__.py`

**Step 1: Write BaseAgent class**

```python
# agents/__init__.py
"""Agent classes."""
from .base import BaseAgent

__all__ = ["BaseAgent"]
```

```python
# agents/base.py
"""Base agent with shared loop logic."""
from abc import ABC, abstractmethod
from anthropic import Anthropic
from config import MODEL, MAX_TOKENS

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
```

**Step 2: Verify imports work**

Run: `python -c "from agents import BaseAgent; print('BaseAgent imported')"`
Expected: Output success message

**Step 3: Commit**

```bash
git add agents/ agents/__init__.py agents/base.py
git commit -m "feat: add BaseAgent with shared logic"
```

---

## Task 15: Create agents/subagent.py

**Files:**
- Create: `agents/subagent.py`

**Step 1: Write SubAgent class**

```python
# agents/subagent.py
"""Subagent for isolated task execution."""
from .base import BaseAgent
from config import MODEL, MAX_TOKENS, DEBUG
from prompts.subagent import get_subagent_prompt
from tools import get_tool_class

class SubAgent(BaseAgent):
    """Subagent with limited tool access."""

    def __init__(self, client, agent_type: str, allowed_tool_names: list, workdir: str):
        # Filter tools to only allowed ones
        from tools import get_tool_schemas
        all_schemas = get_tool_schemas()
        allowed_tools = [s for s in all_schemas if s["name"] in allowed_tool_names]

        super().__init__(client, tools=allowed_tools, max_tokens=MAX_TOKENS)
        self.agent_type = agent_type
        self.workdir = workdir
        self.allowed_tool_names = allowed_tool_names

    def get_system_prompt(self) -> str:
        return get_subagent_prompt(self.agent_type, self.workdir)

    def should_stop(self, response, is_finished: bool = False) -> bool:
        return response.stop_reason != "tool_use"

    def execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """Execute a tool with limited set."""
        if tool_name not in self.allowed_tool_names:
            return f"Unknown tool for subagent: {tool_name}"

        # Get tool class and execute
        tool_class = get_tool_class(tool_name)
        context = self._get_context()
        tool = tool_class(context)
        self.tool_call_count += 1
        return tool.execute(**tool_input)

    def _get_context(self) -> dict:
        """Build execution context."""
        from adapters.hackernews import HackerNewsAdapter
        from adapters.web_reader import WebReaderAdapter
        from pathlib import Path

        return {
            "workdir": Path(self.workdir),
            "hn_adapter": HackerNewsAdapter(),
            "web_reader": WebReaderAdapter(),
        }

    def run(self, prompt: str) -> str:
        """Run the subagent with a prompt."""
        messages = [{"role": "user", "content": prompt}]

        while True:
            response = self.client.messages.create(
                model=MODEL,
                system=self.get_system_prompt(),
                messages=messages,
                tools=self.tools,
                max_tokens=self.max_tokens,
            )

            # Extract text and tool calls
            text_blocks = []
            tool_calls = []

            for block in response.content:
                if hasattr(block, "text") and block.text:
                    text_blocks.append(block.text)
                if block.type == "tool_use":
                    tool_calls.append(block)

            # Append assistant message
            messages.append({"role": "assistant", "content": response.content})

            # Check stop condition
            if self.should_stop(response):
                break

            # Execute tools
            results = []
            for tc in tool_calls:
                result = self.execute_tool(tc.name, tc.input)
                results.append({
                    "type": "tool_result",
                    "tool_use_id": tc.id,
                    "content": result
                })

            # Append tool results
            messages.append({"role": "user", "content": results})

        # Get final text
        for block in response.content:
            if hasattr(block, "text") and block.text:
                return f"[{self.agent_type}] done ({self.tool_call_count} tools)\\n{block.text}"

        return f"[{self.agent_type}] done ({self.tool_call_count} tools)\\n(no text returned)"
```

**Step 2: Verify imports work**

Run: `python -c "from agents.subagent import SubAgent; print('SubAgent imported')"`
Expected: Output success message

**Step 3: Commit**

```bash
git add agents/subagent.py
git commit -m "feat: add SubAgent class"
```

---

## Task 16: Create agents/main.py

**Files:**
- Create: `agents/main.py`

**Step 1: Write NewsExplorerAgent class**

```python
# agents/main.py
"""Main agent for HN exploration."""
from .base import BaseAgent
from config import MODEL, MAX_TOKENS, DEBUG, MAX_TOOL_CALLS, WORKDIR
from prompts.system import SYSTEM_PROMPT
from tools import get_tool_schemas, get_tool_class
from tools.schemas import AGENT_TYPES

class NewsExplorerAgent(BaseAgent):
    """Main agent that explores HN."""

    def __init__(self, client):
        all_tools = get_tool_schemas()
        super().__init__(client, tools=all_tools, max_tokens=MAX_TOKENS)
        self.is_finished = False
        self.final_summary = None

    def get_system_prompt(self) -> str:
        return SYSTEM_PROMPT

    def should_stop(self, response, is_finished: bool = False) -> bool:
        return response.stop_reason != "tool_use" or self.is_finished

    def execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """Execute a tool."""
        self.tool_call_count += 1

        # Handle finish_exploration specially
        if tool_name == "finish_exploration":
            self.is_finished = True
            self.final_summary = tool_input.get("summary", "")
            stories = tool_input.get("interesting_stories", [])
            output = f"**EXPLORATION FINISHED**\\n\\nSummary: {self.final_summary}"
            if stories:
                output += f"\\n\\nInteresting stories:\\n" + "\\n".join(f"- {s}" for s in stories)
            return output

        # Handle Task tool (spawn subagent)
        if tool_name == "Task":
            return self._run_subagent(
                tool_input["agent_type"],
                tool_input["description"],
                tool_input["prompt"]
            )

        # Regular tools
        tool_class = get_tool_class(tool_name)
        context = self._get_context()
        tool = tool_class(context)
        return tool.execute(**tool_input)

    def _run_subagent(self, agent_type: str, description: str, prompt: str) -> str:
        """Spawn and run a subagent."""
        from agents.subagent import SubAgent

        if agent_type not in AGENT_TYPES:
            return f"Unknown agent type: {agent_type}"

        config = AGENT_TYPES[agent_type]
        allowed_tools = config.get("tools", [])

        if DEBUG:
            print(f"\\n  📤 SPAWNING SUBAGENT: {agent_type}")
            print(f"  Description: {description}")
        else:
            print(f"  [{agent_type}] {description}")

        subagent = SubAgent(self.client, agent_type, allowed_tools, str(WORKDIR))
        return subagent.run(prompt)

    def _get_context(self) -> dict:
        """Build execution context."""
        from adapters.hackernews import HackerNewsAdapter
        from adapters.web_reader import WebReaderAdapter

        return {
            "workdir": WORKDIR,
            "hn_adapter": HackerNewsAdapter(),
            "web_reader": WebReaderAdapter(),
        }

    def run(self, user_message: str = None):
        """Run the agent loop."""
        if user_message is None:
            user_message = "Explore Hacker News and find interesting content."

        print(f"🤖 News Explorer Agent - {WORKDIR}")
        print(f"Model: {MODEL}")
        print(f"Max tool calls: {MAX_TOOL_CALLS}")
        print(f"Debug mode: {DEBUG}")
        print("-" * 50)

        messages = [{"role": "user", "content": user_message}]

        while not self.is_finished and self.tool_call_count < MAX_TOOL_CALLS:
            response = self.client.messages.create(
                model=MODEL,
                system=self.get_system_prompt(),
                messages=messages,
                tools=self.tools,
                max_tokens=self.max_tokens,
            )

            # Extract text and tool calls
            tool_calls = []
            for block in response.content:
                if hasattr(block, "text") and block.text:
                    if not DEBUG:
                        print(block.text)
                if block.type == "tool_use":
                    tool_calls.append(block)

            # Append assistant message
            messages.append({"role": "assistant", "content": response.content})

            # Check stop condition
            if self.should_stop(response):
                break

            # Execute tools
            results = []
            for tc in tool_calls:
                if not DEBUG:
                    print(f"\\n> {tc.name}")

                if self.tool_call_count >= MAX_TOOL_CALLS:
                    result = "Max tool calls reached. Please call finish_exploration."
                else:
                    result = self.execute_tool(tc.name, tc.input)

                if not DEBUG:
                    preview = result[:200] + "..." if len(result) > 200 else result
                    print(f"  {preview}")

                results.append({
                    "type": "tool_result",
                    "tool_use_id": tc.id,
                    "content": result
                })

            # Append tool results
            messages.append({"role": "user", "content": results})

        # Final summary
        print("\\n" + "=" * 50)
        if self.final_summary:
            print(f"📋 Summary: {self.final_summary}")
        print(f"📊 Tool calls made: {self.tool_call_count}/{MAX_TOOL_CALLS}")
        print("=" * 50)
```

**Step 2: Verify imports work**

Run: `python -c "from agents.main import NewsExplorerAgent; print('NewsExplorerAgent imported')"`
Expected: Output success message

**Step 3: Commit**

```bash
git add agents/main.py
git commit -m "feat: add NewsExplorerAgent class"
```

---

## Task 17: Update tools/schemas.py to remove AGENT_TYPES

**Files:**
- Modify: `tools/schemas.py`

**Step 1: Move AGENT_TYPES to agents package**

Since AGENT_TYPES is configuration for subagents, create `agents/config.py`:

```python
# agents/config.py
"""Agent type configurations."""

AGENT_TYPES = {
    "analyze_story": {
        "description": "Analyze a single HN story for interest, controversy, technical significance. Read the article, check comments, and provide verdict. Write the final analysis report in Chinese.",
        "tools": ["read_file", "write_file", "read_webpage"],
    },
}
```

**Step 2: Update tools/schemas.py to remove AGENT_TYPES**

Remove AGENT_TYPES and get_agent_descriptions from tools/schemas.py since they're now in agents/config.py.

**Step 3: Update imports in agents/main.py and agents/subagent.py**

Change:
```python
from tools.schemas import AGENT_TYPES
```

To:
```python
from agents.config import AGENT_TYPES
```

**Step 4: Verify imports work**

Run: `python -c "from agents.config import AGENT_TYPES; print(AGENT_TYPES.keys())"`
Expected: Output dict_keys(['analyze_story'])

**Step 5: Commit**

```bash
git add tools/schemas.py agents/config.py agents/main.py agents/subagent.py
git commit -m "refactor: move AGENT_TYPES to agents/config.py"
```

---

## Task 18: Update tools/schemas.py - add Task tool schema

**Files:**
- Modify: `tools/schemas.py`

**Step 1: Add Task tool schema**

```python
# tools/schemas.py
"""Tool JSON schemas for Claude's function calling."""

from typing import List
from agents.config import AGENT_TYPES

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
                "path": {
                    "type": "string",
                    "description": "File path relative to workspace",
                },
                "limit": {"type": "integer", "description": "Max lines to read"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a file. Creates directories if needed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path relative to workspace",
                },
                "content": {"type": "string", "description": "Content to write"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "read_webpage",
        "description": "Read the full content of a webpage. Returns main article text.",
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
        },
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
                    "description": "Paths to story analysis files",
                },
            },
            "required": ["summary"],
        },
    },
]


# =============================================================================
# Task Tool - Spawn Subagents
# =============================================================================

def get_agent_descriptions() -> str:
    """Generate agent type descriptions."""
    return "\\n".join(
        f"- {name}: {cfg['description']}" for name, cfg in AGENT_TYPES.items()
    )

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
                "description": "Short task description (3-5 words)",
            },
            "prompt": {
                "type": "string",
                "description": "Detailed instructions for the subagent",
            },
            "agent_type": {
                "type": "string",
                "enum": list(AGENT_TYPES.keys()),
                "description": "Type of subagent to spawn",
            },
        },
        "required": ["description", "prompt", "agent_type"],
    },
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
                    "enum": ["top", "new", "best", "ask", "show", "job"],
                },
                "limit": {"type": "integer", "minimum": 1, "maximum": 30},
            },
            "required": ["story_type"],
        },
    },
    {
        "name": "get_hn_item",
        "description": "Fetch a specific HN item (story, comment, job) by ID.",
        "input_schema": {
            "type": "object",
            "properties": {"item_id": {"type": "integer"}},
            "required": ["item_id"],
        },
    },
    {
        "name": "get_hn_comments",
        "description": "Fetch comments for a HN story. Returns top-level comments with preview.",
        "input_schema": {
            "type": "object",
            "properties": {
                "story_id": {"type": "integer"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 50},
            },
            "required": ["story_id"],
        },
    },
]

# =============================================================================
# All Tools Combined
# =============================================================================

ALL_TOOLS = BASE_TOOLS + [TASK_TOOL] + HN_TOOLS
```

**Step 2: Verify imports work**

Run: `python -c "from tools.schemas import ALL_TOOLS; print(f'{len(ALL_TOOLS)} tools in schema')"`
Expected: Output "8 tools in schema"

**Step 3: Commit**

```bash
git add tools/schemas.py
git commit -m "refactor: update tools schemas with Task tool"
```

---

## Task 19: Create tools/task.py

**Files:**
- Create: `tools/task.py`

**Step 1: Write TaskTool**

```python
# tools/task.py
"""Task tool for spawning subagents."""
from .base import BaseTool

class TaskTool(BaseTool):
    """Tool for spawning subagents."""

    @classmethod
    def get_name(cls) -> str:
        return "Task"

    @classmethod
    def get_schema(cls) -> dict:
        from tools.schemas import TASK_TOOL
        return TASK_TOOL

    def _execute(self, agent_type: str, description: str, prompt: str) -> str:
        """This is handled specially by the agent, not executed directly."""
        return "Task execution is handled by the agent's execute_tool method."
```

**Step 2: Verify imports work**

Run: `python -c "from tools.task import TaskTool; print(TaskTool.get_name())"`
Expected: Output "Task"

**Step 3: Commit**

```bash
git add tools/task.py
git commit -m "feat: add TaskTool class"
```

---

## Task 20: Update tools/__init__.py to include TaskTool

**Files:**
- Modify: `tools/__init__.py`

**Step 1: Add TaskTool to imports and list**

```python
# tools/__init__.py
"""Tool collection and registration."""
from .base import BaseTool
from .file_read import ReadFileTool
from .file_write import WriteFileTool
from .webpage import ReadWebpageTool
from .hn_stories import GetHNStoriesTool
from .hn_item import GetHNItemTool
from .hn_comments import GetHNCommentsTool
from .finish import FinishExplorationTool
from .task import TaskTool

# All tool classes
ALL_TOOL_CLASSES = [
    ReadFileTool,
    WriteFileTool,
    ReadWebpageTool,
    GetHNStoriesTool,
    GetHNItemTool,
    GetHNCommentsTool,
    FinishExplorationTool,
    TaskTool,
]

def get_tool_schemas() -> list:
    """Get JSON schemas for all tools."""
    return [tool.get_schema() for tool in ALL_TOOL_CLASSES]

def get_tool_class(name: str) -> type:
    """Get tool class by name."""
    for tool_class in ALL_TOOL_CLASSES:
        if tool_class.get_name() == name:
            return tool_class
    raise ValueError(f"Unknown tool: {name}")
```

**Step 2: Verify imports work**

Run: `python -c "from tools import get_tool_schemas; print(f'{len(get_tool_schemas())} tools')"`
Expected: Output "8 tools"

**Step 3: Commit**

```bash
git add tools/__init__.py
git commit -m "refactor: add TaskTool to tools registry"
```

---

## Task 21: Update prompts/subagent.py to use agents.config

**Files:**
- Modify: `prompts/subagent.py`

**Step 1: Update import**

```python
# prompts/subagent.py
"""Subagent system prompts."""
from datetime import datetime
from agents.config import AGENT_TYPES

def get_subagent_prompt(agent_type: str, workdir: str) -> str:
    """Generate system prompt for specific subagent type."""
    config = AGENT_TYPES.get(agent_type, {})
    today = datetime.now().strftime("%Y-%m-%d")

    template = f"""You are a {agent_type} subagent at {workdir}.

Today's date: {today}

{config.get('description', '')}

Complete the task and return a clear, concise summary."""

    return template
```

**Step 2: Verify imports work**

Run: `python -c "from prompts.subagent import get_subagent_prompt; print(get_subagent_prompt('analyze_story', '/tmp'))"`
Expected: Output formatted prompt

**Step 3: Commit**

```bash
git add prompts/subagent.py
git commit -m "refactor: update subagent prompt to use agents.config"
```

---

## Task 22: Refactor main.py to use new architecture

**Files:**
- Modify: `main.py`

**Step 1: Simplify main.py to entry point**

```python
#!/usr/bin/env python3
"""
News Explorer Agent - Browse Hacker News intelligently with Claude.

Modular architecture with tools/, agents/, and prompts/ packages.
"""
from anthropic import Anthropic
from dotenv import load_dotenv

from config import (
    ANTHROPIC_API_KEY,
    ANTHROPIC_BASE_URL,
    DEBUG,
    MODEL,
    MAX_TOOL_CALLS,
    WORKDIR,
)
from agents.main import NewsExplorerAgent

load_dotenv()


def main():
    """Entry point."""
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set in environment")

    client = Anthropic(api_key=ANTHROPIC_API_KEY, base_url=ANTHROPIC_BASE_URL)
    agent = NewsExplorerAgent(client)
    agent.run()


if __name__ == "__main__":
    main()
```

**Step 2: Verify it runs without errors**

Run: `python -c "import main; print('main.py imports successfully')"`
Expected: Output success message

**Step 3: Commit**

```bash
git add main.py
git commit -m "refactor: simplify main.py to entry point"
```

---

## Task 23: Test the refactored application

**Files:**
- No file changes

**Step 1: Run a smoke test**

Run: `python -c "
from anthropic import Anthropic
from agents.main import NewsExplorerAgent
from config import ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL

if ANTHROPIC_API_KEY:
    client = Anthropic(api_key=ANTHROPIC_API_KEY, base_url=ANTHROPIC_BASE_URL)
    agent = NewsExplorerAgent(client)
    print('✓ NewsExplorerAgent created successfully')
    print(f'✓ Has {len(agent.tools)} tools available')
else:
    print('⚠ No API key - skipping agent creation test')
"`
Expected: Output success messages

**Step 2: Verify tool loading**

Run: `python -c "
from tools import get_tool_schemas, get_tool_class
from tools.base import BaseTool

schemas = get_tool_schemas()
print(f'✓ Loaded {len(schemas)} tool schemas')

for schema in schemas:
    name = schema['name']
    tool_class = get_tool_class(name)
    assert issubclass(tool_class, BaseTool), f'{name} is not a BaseTool subclass'
    print(f'✓ {name}: {tool_class.__name__}')
"`
Expected: All tools verified

**Step 3: Verify agent structure**

Run: `python -c "
from agents.main import NewsExplorerAgent
from agents.subagent import SubAgent
from agents.base import BaseAgent

# Check inheritance
assert issubclass(NewsExplorerAgent, BaseAgent)
assert issubclass(SubAgent, BaseAgent)
print('✓ Agent inheritance correct')
print(f'✓ NewsExplorerAgent: {NewsExplorerAgent.__name__}')
print(f'✓ SubAgent: {SubAgent.__name__}')
"`
Expected: All assertions pass

**Step 4: Run full test if API key available**

Run: `python main.py --help 2>&1 | head -20` (if API key set)

**Step 5: Commit test results**

```bash
# If all tests pass
git add tests/  # if test files created
git commit -m "test: verify refactored application works correctly"
```

---

## Task 24: Update ARCHITECTURE.md

**Files:**
- Modify: `ARCHITECTURE.md`

**Step 1: Update architecture documentation**

```markdown
# Reddit Explorer Architecture

## Overview

Modular agent system for exploring Hacker News with Claude.

## Directory Structure

```
reddit-explorer/
├── agents/           # Agent classes
│   ├── base.py       # BaseAgent with shared loop logic
│   ├── main.py       # NewsExplorerAgent
│   ├── subagent.py   # SubAgent
│   └── config.py     # Agent type configurations
├── tools/            # Tool classes
│   ├── base.py       # BaseTool abstract class
│   ├── file_read.py  # ReadFileTool
│   ├── file_write.py # WriteFileTool
│   ├── webpage.py    # ReadWebpageTool
│   ├── hn_stories.py # GetHNStoriesTool
│   ├── hn_item.py    # GetHNItemTool
│   ├── hn_comments.py # GetHNCommentsTool
│   ├── finish.py     # FinishExplorationTool
│   ├── task.py       # TaskTool
│   └── schemas.py    # JSON schemas for API
├── prompts/          # System prompts
│   ├── system.py     # Main agent prompt
│   ├── subagent.py   # Subagent prompts
│   └── templates.py  # Output format templates
├── adapters/         # External API adapters
├── config.py         # Centralized configuration
└── main.py           # Entry point
```

## Key Components

### BaseTool

All tools inherit from `BaseTool`:
- `get_name()` - Tool identifier
- `get_schema()` - JSON schema for Claude API
- `execute()` - Wrapper with error handling
- `_execute()` - Actual implementation

### BaseAgent

All agents inherit from `BaseAgent`:
- `get_system_prompt()` - System prompt
- `should_stop()` - Stop condition
- `execute_tool()` - Tool execution
- Shared agent loop pattern

### NewsExplorerAgent

Main agent that:
- Explores Hacker News
- Spawns subagents for analysis
- Manages tool execution
- Coordinates workflow

### SubAgent

Subagent with:
- Limited tool access (whitelist)
- Independent system prompt
- Shared agent loop via BaseAgent

## Data Flow

1. User runs `main.py`
2. NewsExplorerAgent starts with Claude API
3. Agent calls tools (HN, files, webpage)
4. For story analysis, spawns SubAgent via Task tool
5. SubAgent analyzes independently with limited tools
6. Results returned to main agent
7. Main agent calls finish_exploration

## Tool Execution

Tools receive context dict:
- `workdir` - Working directory
- `hn_adapter` - HackerNewsAdapter instance
- `web_reader` - WebReaderAdapter instance

## Prompts

- `system.py` - Main agent system prompt (uses templates)
- `subagent.py` - Generates subagent prompts per agent_type
- `templates.py` - Chinese output format templates
```

**Step 2: Commit**

```bash
git add ARCHITECTURE.md
git commit -m "docs: update architecture for modular design"
```

---

## Task 25: Final verification and cleanup

**Files:**
- Check all files

**Step 1: Verify all imports work**

Run: `python -c "
# Test all imports
from config import *
from prompts.system import SYSTEM_PROMPT
from prompts.subagent import get_subagent_prompt
from prompts.templates import CHINESE_OUTPUT_TEMPLATE
from tools import get_tool_schemas, get_tool_class
from agents.base import BaseAgent
from agents.main import NewsExplorerAgent
from agents.subagent import SubAgent
from agents.config import AGENT_TYPES

print('✓ All imports successful')
print(f'✓ {len(get_tool_schemas())} tools loaded')
print(f'✓ {len(AGENT_TYPES)} agent types defined')
"`
Expected: All imports successful

**Step 2: Check for unused imports**

Run: `python -c "
import main
import agents.main
import agents.subagent
print('✓ No circular import issues')
"`

**Step 3: Verify git status**

Run: `git status`
Expected: Clean working tree (no uncommitted changes)

**Step 4: Final commit**

```bash
# If any cleanup needed
git add -A
git commit -m "refactor: complete modular architecture refactor"
```

---

## Summary

This refactor:
- Separated tools into individual classes in `tools/`
- Created `BaseTool` for shared tool logic
- Separated agents into `agents/` with `BaseAgent`
- Moved prompts to `prompts/` by function
- Centralized configuration in `config.py`
- Simplified `main.py` to entry point

**Total tasks:** 25
**Estimated time:** 2-3 hours
**Testing:** Verify imports, tool loading, agent creation
