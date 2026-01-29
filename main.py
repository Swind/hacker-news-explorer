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
