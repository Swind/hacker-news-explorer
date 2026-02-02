# agents/main.py
"""Main agent for HN exploration."""
from anthropic.types import TextBlock

from config import DEBUG, MAX_TOKENS, MAX_TOOL_CALLS, MODEL, WORKDIR
from prompts.system import SYSTEM_PROMPT
from tools import get_tool_class, get_tool_schemas

from .base import BaseAgent, retry_api_call
from .config import AGENT_TYPES


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
            output = f"**EXPLORATION FINISHED**\n\nSummary: {self.final_summary}"
            if stories:
                output += f"\n\nInteresting stories:\n" + "\n".join(
                    f"- {s}" for s in stories
                )
            return output

        # Handle Task tool (spawn subagent)
        if tool_name == "Task":
            return self._run_subagent(
                tool_input.get("agent_type", ""),
                tool_input.get("description", ""),
                tool_input.get("prompt", ""),
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
            print(f"\n  📤 SPAWNING SUBAGENT: {agent_type}")
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
            # DEBUG: Show what we're sending to LLM
            if DEBUG:
                print(f"\n{'=' * 60}")
                print(f"🤖 [DEBUG] Step {self.tool_call_count + 1}")
                print(f"{'=' * 60}")
                print(f"📋 Available tools: {[t['name'] for t in self.tools]}")
                print(f"\n📨 Sending to LLM:")
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
                print(f"\n📥 LLM Response:")

            # Extract text and tool calls
            tool_calls = []
            for block in response.content:
                if hasattr(block, "text") and block.text:
                    # DEBUG mode: show text block info and always output text
                    if DEBUG:
                        preview = (
                            block.text[:100] + "..."
                            if len(block.text) > 100
                            else block.text
                        )
                        print(f"  📝 [TEXT] {preview}")
                    print(block.text)
                if block.type == "tool_use":
                    tool_calls.append(block)
                    # DEBUG mode: show tool call details
                    if DEBUG:
                        print(f"  🔧 [TOOL] {block.name}")
                        for key, value in block.input.items():
                            value_preview = (
                                str(value)[:100] + "..."
                                if len(str(value)) > 100
                                else str(value)
                            )
                            print(f"     {key}: {value_preview}")

            # Append assistant message
            messages.append({"role": "assistant", "content": response.content})

            # Check stop condition
            if self.should_stop(response):
                break

            # Execute tools
            results = []
            for tc in tool_calls:
                if not DEBUG:
                    print(f"\n> {tc.name}")

                if self.tool_call_count >= MAX_TOOL_CALLS:
                    result = "Max tool calls reached. Please call finish_exploration."
                else:
                    result = self.execute_tool(tc.name, tc.input)

                if not DEBUG:
                    preview = result[:200] + "..." if len(result) > 200 else result
                    print(f"  {preview}")

                results.append(
                    {"type": "tool_result", "tool_use_id": tc.id, "content": result}
                )

            # Append tool results
            messages.append({"role": "user", "content": results})

        # Final summary
        print("\n" + "=" * 50)
        if self.final_summary:
            print(f"📋 Summary: {self.final_summary}")
        print(f"📊 Tool calls made: {self.tool_call_count}/{MAX_TOOL_CALLS}")
        print("=" * 50)
