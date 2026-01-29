# agents/main.py
"""Main agent for HN exploration."""
from .base import BaseAgent
from .config import AGENT_TYPES
from config import MODEL, MAX_TOKENS, DEBUG, MAX_TOOL_CALLS, WORKDIR
from prompts.system import SYSTEM_PROMPT
from tools import get_tool_schemas, get_tool_class

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
                output += f"\n\nInteresting stories:\n" + "\n".join(f"- {s}" for s in stories)
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
                    print(f"\n> {tc.name}")

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
        print("\n" + "=" * 50)
        if self.final_summary:
            print(f"📋 Summary: {self.final_summary}")
        print(f"📊 Tool calls made: {self.tool_call_count}/{MAX_TOOL_CALLS}")
        print("=" * 50)
