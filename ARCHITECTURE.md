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
