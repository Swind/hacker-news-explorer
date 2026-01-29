# Reddit Explorer Refactor Design

**Date:** 2026-01-29
**Status:** Design Approved

## Overview

Refactor `main.py` (435 lines) into a modular architecture with clear separation of concerns:
- Tools as independent classes in `tools/` package
- Agents with shared base class in `agents/` package
- Prompts organized by function in `prompts/` package
- Centralized configuration in `config.py`

## Directory Structure

```
reddit-explorer/
├── agents/
│   ├── __init__.py
│   ├── base.py           # BaseAgent class (shared agent loop)
│   ├── main.py           # NewsExplorerAgent (main agent)
│   └── subagent.py       # SubAgent (sub agent with restrictions)
├── tools/
│   ├── __init__.py       # Auto-collect and register all tools
│   ├── base.py           # BaseTool abstract class
│   ├── file_read.py      # read_file tool
│   ├── file_write.py     # write_file tool
│   ├── webpage.py        # read_webpage tool
│   ├── hn_stories.py     # get_hn_stories tool
│   ├── hn_item.py        # get_hn_item tool
│   ├── hn_comments.py    # get_hn_comments tool
│   ├── task.py           # Task tool (spawn subagent)
│   └── finish.py         # finish_exploration tool
├── prompts/
│   ├── __init__.py
│   ├── system.py         # Main agent system prompt
│   ├── subagent.py       # Subagent system prompt
│   └── templates.py      # Output format templates (Chinese report)
├── adapters/             # Unchanged
├── main.py               # Simplified entry point
└── config.py             # New: centralized configuration
```

## Tools Layer

### BaseTool Interface

```python
# tools/base.py
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

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Execute the tool and return result string."""
        pass
```

### Example Tool Implementation

```python
# tools/file_read.py
from .base import BaseTool

class ReadFileTool(BaseTool):
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
                    "path": {"type": "string"},
                    "limit": {"type": "integer"}
                },
                "required": ["path"]
            }
        }

    def execute(self, path: str, limit: int = None) -> str:
        # Implementation
        pass
```

### Tool Registration

```python
# tools/__init__.py
from .base import BaseTool
from .file_read import ReadFileTool
from .file_write import WriteFileTool
# ... import all tools

ALL_TOOLS = [ReadFileTool, WriteFileTool, ...]

def get_tool_schemas() -> list:
    return [tool.get_schema() for tool in ALL_TOOLS]
```

## Agents Layer

### BaseAgent (Shared Logic)

```python
# agents/base.py
from abc import ABC, abstractmethod
from anthropic import Anthropic

class BaseAgent(ABC):
    """Shared agent logic for main and sub agents."""

    def __init__(self, client: Anthropic, tools: list, max_tokens: int = 4096):
        self.client = client
        self.tools = tools
        self.max_tokens = max_tokens
        self.tool_call_count = 0

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return system prompt for this agent type."""
        pass

    @abstractmethod
    def should_stop(self, response) -> bool:
        """Determine if agent should stop."""
        pass

    def run_loop(self, messages: list, initial_tools: list) -> tuple:
        """Shared agent loop. Returns (messages, stopped_reason)."""
        while True:
            response = self.client.messages.create(
                model=MODEL,
                system=self.get_system_prompt(),
                messages=messages,
                tools=initial_tools,
                max_tokens=self.max_tokens,
            )

            messages.append({"role": "assistant", "content": response.content})

            if self.should_stop(response):
                break

            # Execute tools...

        return messages, response.stop_reason
```

### NewsExplorerAgent (Main Agent)

```python
# agents/main.py
from .base import BaseAgent

class NewsExplorerAgent(BaseAgent):
    def __init__(self, client: Anthropic):
        all_tools = get_tool_schemas()
        super().__init__(client, tools=all_tools)
        self.is_finished = False

    def get_system_prompt(self) -> str:
        return SYSTEM_PROMPT

    def should_stop(self, response) -> bool:
        return response.stop_reason != "tool_use" or self.is_finished
```

### SubAgent (Restricted)

```python
# agents/subagent.py
from .base import BaseAgent

class SubAgent(BaseAgent):
    def __init__(self, client: Anthropic, agent_type: str, allowed_tools: list):
        super().__init__(client, tools=allowed_tools)
        self.agent_type = agent_type

    def get_system_prompt(self) -> str:
        from prompts.subagent import get_subagent_prompt
        return get_subagent_prompt(self.agent_type)

    def should_stop(self, response) -> bool:
        return response.stop_reason != "tool_use"
```

## Prompts Organization

### system.py (Main Agent)

```python
# prompts/system.py
from datetime import datetime
from .templates import CHINESE_OUTPUT_TEMPLATE

TODAY = datetime.now().strftime("%Y-%m-%d")

SYSTEM_PROMPT = f"""You are a News Exploration Agent...

## File Output Format

Subagents should write markdown files in **Chinese**:
{CHINESE_OUTPUT_TEMPLATE}
...
"""
```

### subagent.py (Subagent)

```python
# prompts/subagent.py
from datetime import datetime
from tools.schemas import AGENT_TYPES

def get_subagent_prompt(agent_type: str, workdir: str) -> str:
    config = AGENT_TYPES.get(agent_type, {})
    today = datetime.now().strftime("%Y-%m-%d")

    template = f"""You are a {agent_type} subagent at {workdir}.

Today's date: {today}

{config.get('description', '')}

Complete the task and return a clear, concise summary."""

    return template
```

### templates.py (Output Formats)

```python
# prompts/templates.py

CHINESE_OUTPUT_TEMPLATE = """
# {TODAY}: [故事標題]

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

## Configuration

```python
# config.py
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
DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

# Output Paths
REPORT_BASE_DIR = WORKDIR / "report"
REPORT_DATE_FORMAT = "%Y-%m-%d"
```

## Simplified Entry Point

```python
# main.py
from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL
from agents.main import NewsExplorerAgent

def main():
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set")

    client = Anthropic(api_key=ANTHROPIC_API_KEY, base_url=ANTHROPIC_BASE_URL)
    agent = NewsExplorerAgent(client)
    agent.run()

if __name__ == "__main__":
    main()
```

## Data Flow

```
main.py
    │
    ▼
NewsExplorerAgent
    │
    ├─→ run_loop() [from BaseAgent]
    │       │
    │       ├─→ Anthropic API
    │       │
    │       └─→ execute_tool()
    │               ├─→ ReadFileTool
    │               ├─→ WriteFileTool
    │               ├─→ GetHNStoriesTool
    │               ├─→ Task tool ──────┐
    │               └─→ finish          │
    │                                  │
    └──────────────────────────────────┘
                                       │
                                       ▼
                              SubAgent
                                  │
                                  ├─→ Tool whitelist
                                  ├─→ Independent system prompt
                                  └─→ run_loop() [from BaseAgent]
```

## Error Handling

```python
# tools/base.py
class ToolExecutionError(Exception):
    pass

class BaseTool(ABC):
    def execute(self, **kwargs) -> str:
        try:
            return self._execute(**kwargs)
        except ToolExecutionError:
            raise
        except Exception as e:
            return f"Error executing {self.get_name()}: {str(e)}"

    @abstractmethod
    def _execute(self, **kwargs) -> str:
        pass
```

## Testing Strategy

```
tests/
├── tools/
│   ├── test_file_read.py
│   ├── test_hn_stories.py
│   └── ...
├── agents/
│   ├── test_base_agent.py
│   └── test_subagent.py
└── fixtures/
    └── mock_hn_responses.py
```

## Implementation Checklist

- [ ] Create `tools/base.py` with BaseTool
- [ ] Create individual tool files (file_read.py, file_write.py, etc.)
- [ ] Update `tools/__init__.py` to auto-collect tools
- [ ] Create `agents/base.py` with BaseAgent
- [ ] Create `agents/main.py` with NewsExplorerAgent
- [ ] Create `agents/subagent.py` with SubAgent
- [ ] Update `prompts/` structure (add templates.py)
- [ ] Create `config.py`
- [ ] Refactor `main.py` to simple entry point
- [ ] Update imports across all files
- [ ] Test the refactored application
