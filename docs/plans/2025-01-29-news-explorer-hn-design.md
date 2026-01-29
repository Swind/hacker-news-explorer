# News Explorer Agent - Hacker News Implementation Design

**Date:** 2025-01-29
**Status:** Design Approved (Updated with Subagent Support)
**Scope:** Hacker News exploration agent using Anthropic SDK with independent subagent analysis

## Overview

An autonomous agent that uses Claude (via Anthropic Python SDK) to intelligently browse Hacker News, discover interesting content, and delegate story analysis to independent subagents. Each story is analyzed in isolation to avoid context contamination, with results saved as markdown files.

## Key Architecture Decision: Subagent Delegation

**Why subagents?**
- Each HN story analyzed independently (no bias from previous articles)
- Parallel processing potential
- Clean separation: main agent orchestrates, subagents analyze
- Prevents "halo effect" where early stories influence later judgments

## Architecture

### Simplified 2-Layer Structure

```
reddit-explorer/
├── main.py                    # Main agent loop (orchestrator)
├── pyproject.toml             # Dependencies
├── .env                       # ANTHROPIC_API_KEY
├── adapters/
│   ├── hackernews.py         # HN Firebase API client
│   └── web_reader.py         # Trafilatura web scraper
├── tools/
│   ├── schemas.py            # Tool JSON schemas (BASE + HN + Task)
│   └── handlers.py           # Tool execution handlers
└── prompts/
    ├── system.py             # Main agent system prompt
    └── subagent.py           # Subagent prompt template
```

### Dependencies

```toml
anthropic>=0.40.0
httpx>=0.27.0
trafilatura>=1.12.0
python-dotenv>=1.0.0
```

## Tool Definitions

### Base Tools (file operations only)

| Tool | Purpose |
|------|---------|
| `read_file` | Read file contents from workspace |
| `write_file` | Write content (creates dirs if needed) |

### Hacker News Tools

| Tool | Purpose |
|------|---------|
| `get_hn_stories` | Fetch stories by type (top, new, best, ask, show, job) |
| `get_hn_item` | Fetch single item (story/comment) by ID |
| `get_hn_comments` | Fetch top-level comments for a story |
| `read_webpage` | Extract article content from URL |
| `finish_exploration` | Stop session and provide summary |

### Subagent Tools

| Tool | Purpose |
|------|---------|
| `Task` | Spawn `analyze_story` subagent for independent story analysis |

### Subagent Type: `analyze_story`

**Tools available:** read_file, write_file
**Purpose:** Analyze a single HN story for interest, controversy, technical significance
**Process:**
1. Read the article content
2. Check comments for discussion quality
3. Assess interest level
4. Write analysis to `{YYYY-MM-DD}/<sanitized-title>.md`

## File Output Format

Analysis files are saved as:

```
YYYY-MM-DD/
├── story-1-title.md
├── story-2-title.md
└── ...
```

Each file contains:
```markdown
# YYYY-MM-DD: [Story Title]

**Source:** Hacker News
**Story ID:** {id}
**URL:** {url}
**Score:** {score} | **Comments:** {count}

## Summary
[Brief 2-3 sentence summary]

## Why Interesting
[Technical significance, controversy, novelty]

## Key Discussion Points
[Main themes from comments]

## Verdict
[INTERESTING | WORTH_READING | SKIP]
```

## Agent Loop

### Main Agent (Orchestrator)

Follows `v4_skills_agent.py` pattern:

1. Call `client.messages.create()` with system prompt, messages, and tools
2. Iterate over `response.content`:
   - Print text blocks
   - Collect `tool_use` blocks
3. If `stop_reason != "tool_use"`: exit loop
4. Execute each tool:
   - For `Task` tool: spawn subagent with isolated context
   - For other tools: execute directly
5. Append assistant message, then tool results (as user message)
6. Repeat until `finish_exploration` or `MAX_TOOL_CALLS` (30)

### Subagent (Story Analyzer)

Isolated context per story:
- Receives story details via prompt
- Has access to: read_file, write_file
- Cannot access main agent's conversation history
- Returns summary to main agent upon completion

## System Prompt Guidance

### Main Agent

- Scan stories using `get_hn_stories`
- Delegate interesting-looking stories to subagents via `Task` tool
- Don't analyze stories yourself - use subagents
- Call `finish_exploration` with summary and list of analysis files

### Subagent

- Focus on single story
- Read article + check comments
- Assess: technical significance? controversy? surprising?
- Write analysis to `{YYYY-MM-DD}/<title>.md`
- Return concise summary

## Safety Constraints

- Maximum 30 tool calls per session (main agent)
- Story/comment fetching limited (max 50 items)
- Webpage content truncated to 10k characters
- File paths restricted to workspace directory
- Explicit `finish_exploration` tool for controlled termination

## Success Criteria

Claude is guided to find:
- High engagement stories (50+ comments)
- Technical significance (releases, security, paradigms)
- Heated debate (controversy, disagreement)
- Intellectual value (insights, learning)

## Future Extensions

- Add Reddit adapter (PRAW) when API credentials available
- Skill system for loading domain knowledge
- Parallel subagent execution
- Daily digest compilation
- Web interface for exploration history
