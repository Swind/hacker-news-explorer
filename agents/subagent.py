# agents/subagent.py
"""Subagent for isolated task execution."""
from config import DEBUG, MAX_TOKENS, MODEL
from prompts.subagent import get_subagent_prompt
from tools import get_tool_class

from .base import BaseAgent, retry_api_call


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
        from pathlib import Path

        from adapters.hackernews import HackerNewsAdapter
        from adapters.web_reader import WebReaderAdapter

        return {
            "workdir": Path(self.workdir),
            "hn_adapter": HackerNewsAdapter(),
            "web_reader": WebReaderAdapter(),
        }

    def run(self, prompt: str) -> str:
        """Run the subagent with a prompt."""
        messages = [{"role": "user", "content": prompt}]

        while True:
            # DEBUG: Show what we're sending to LLM
            if DEBUG:
                print(f"\n  {'─' * 56}")
                print(f"  🔍 [SUBAGENT DEBUG] Step {self.tool_call_count + 1}")
                print(f"  {'─' * 56}")
                print(f"  📋 Available tools: {[t['name'] for t in self.tools]}")
                print(f"\n  📨 Sending to LLM:")
                for msg in messages[-2:] if len(messages) > 2 else messages:
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")
                    if isinstance(content, list):
                        for item in content:
                            print(f"    ▪️ ({role}) {item}")
                    else:
                        print(f"    ▪️ ({role}) {content}")

            response = retry_api_call(
                self.client.messages.create,
                model=MODEL,
                system=self.get_system_prompt(),
                messages=messages,
                tools=self.tools,
                max_tokens=self.max_tokens,
            )

            # DEBUG: Dump LLM response details
            if DEBUG:
                print(f"\n  📥 LLM Response:")

            # Extract text and tool calls
            text_blocks = []
            tool_calls = []

            for block in response.content:
                if hasattr(block, "text") and block.text:
                    text_blocks.append(block.text)
                    # DEBUG mode: show text block info and always output text
                    if DEBUG:
                        preview = (
                            block.text[:100] + "..."
                            if len(block.text) > 100
                            else block.text
                        )
                        print(f"     📝 [TEXT] {preview}")
                    print(block.text)
                if block.type == "tool_use":
                    tool_calls.append(block)
                    # DEBUG mode: show tool call details
                    if DEBUG:
                        print(f"     🔧 [TOOL] {block.name}")
                        for key, value in block.input.items():
                            value_preview = (
                                str(value)[:100] + "..."
                                if len(str(value)) > 100
                                else str(value)
                            )
                            print(f"        {key}: {value_preview}")

            # Append assistant message
            messages.append({"role": "assistant", "content": response.content})

            # Check stop condition
            if self.should_stop(response):
                break

            # Execute tools
            results = []
            for tc in tool_calls:
                result = self.execute_tool(tc.name, tc.input)
                results.append(
                    {"type": "tool_result", "tool_use_id": tc.id, "content": result}
                )

            # Append tool results
            messages.append({"role": "user", "content": results})

        # Get final text
        for block in response.content:
            if hasattr(block, "text") and block.text:
                return f"[{self.agent_type}] done ({self.tool_call_count} tools)\n{block.text}"

        return f"[{self.agent_type}] done ({self.tool_call_count} tools)\n(no text returned)"
