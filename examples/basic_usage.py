"""
Minimal working example for the Querit search tool.

Run it with a real API key:

    export QUERIT_API_KEY="your-querit-api-key"
    python3 examples/basic_usage.py

The script exits non-zero if anything fails, so it can be used as a smoke test.
"""

import os
import sys

from langchain_websearch import WebSearchTool

PREVIEW_CHARS = 400


def preview(text: str) -> str:
    """Shorten long output for display only."""
    if len(text) <= PREVIEW_CHARS:
        return text
    return f"{text[:PREVIEW_CHARS]}\n... ({len(text)} chars total)"


def check(output: str) -> str:
    """Fail loudly on errors.

    WebSearchTool returns failures as a plain string instead of raising, so an
    example that only printed the result would look successful on a 401.
    """
    if not output or output.startswith("Search failed:"):
        raise RuntimeError(f"search did not succeed: {output!r}")
    return output


def basic_search_example() -> None:
    """Search with default settings."""
    tool = WebSearchTool()
    print(preview(check(tool.invoke("latest Python programming news"))))


def advanced_configuration_example() -> None:
    """Search with an explicit result count."""
    tool = WebSearchTool(num_results=5)
    print(preview(check(tool.invoke("machine learning tutorials"))))


def agent_integration_example() -> None:
    """The tool is ready to hand to a LangChain agent."""
    tool = WebSearchTool(num_results=5)
    print(f"{tool.name}: args={list(tool.args.keys())}")

    # With an LLM configured, pass the tool straight to your agent constructor:
    #
    #     from langchain.agents import create_agent
    #     agent = create_agent(model="openai:gpt-4o-mini", tools=[tool])
    #     agent.invoke({"messages": [("user", "What is new in Python?")]})


EXAMPLES = [
    ("Basic search", basic_search_example),
    ("Advanced configuration", advanced_configuration_example),
    ("Agent integration", agent_integration_example),
]


def main() -> int:
    if not os.getenv("QUERIT_API_KEY"):
        print("QUERIT_API_KEY is not set. Export it and run this script again.")
        return 1

    for title, func in EXAMPLES:
        print(f"\n=== {title} ===")
        func()

    print("\nAll examples completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
