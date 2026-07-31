"""
Minimal working example for the Querit Contents tool.

Run it with a real API key:

    export QUERIT_API_KEY="your-querit-api-key"
    python3 examples/contents_usage.py

The script exits non-zero if anything fails, so it can be used as a smoke test.
"""

import os
import sys

from langchain_websearch import QueritContentsBackend, WebContentsTool

GOOD_URL = "https://example.com"
SECOND_URL = "https://www.python.org"
MISSING_URL = "https://this-domain-really-does-not-exist-xyz123.com"

PREVIEW_CHARS = 300


def preview(text: str) -> str:
    """Shorten long output for display only; the tool itself never truncates."""
    if len(text) <= PREVIEW_CHARS:
        return text
    return f"{text[:PREVIEW_CHARS]}\n... ({len(text)} chars total)"


def basic_example() -> None:
    """Fetch a single page with default settings."""
    tool = WebContentsTool()
    print(preview(tool.invoke({"urls": [GOOD_URL]})))


def advanced_configuration_example() -> None:
    """Fetch several pages with explicit format, timeout and metadata."""
    tool = WebContentsTool(
        format="markdown",  # "text" | "markdown" | "html"
        crawl_timeout=10,  # per-page crawl timeout in seconds, 1-60
        extras_meta=True,  # also return title / site name / publish time
    )
    print(preview(tool.invoke({"urls": [GOOD_URL, SECOND_URL]})))


def partial_failure_example() -> None:
    """A page that cannot be crawled does not fail the whole call."""
    tool = WebContentsTool()
    output = tool.invoke({"urls": [GOOD_URL, MISSING_URL]})
    print(preview(output))

    if "[FAILED]" not in output:
        raise AssertionError("expected the unreachable URL to be marked [FAILED]")


def structured_access_example() -> None:
    """Use the backend directly to get ContentResult objects instead of a string."""
    backend = QueritContentsBackend()
    for result in backend.fetch([GOOD_URL], extras_meta=True):
        print(f"status={result.status} url={result.url} chars={len(result.content)}")
        if result.meta:
            print(f"  title={result.meta.title} site={result.meta.site_name}")


def error_handling_example() -> None:
    """Request-level problems raise instead of being returned as text."""
    try:
        WebContentsTool().invoke(
            {"urls": [f"https://example.com/{i}" for i in range(11)]}
        )
    except ValueError as exc:
        print(f"ValueError as expected: {exc}")
    else:
        raise AssertionError("expected ValueError for more than 10 URLs")


def agent_integration_example() -> None:
    """Both tools can be handed to a LangChain agent together."""
    from langchain_websearch import WebSearchTool

    tools = [WebSearchTool(num_results=5), WebContentsTool(extras_meta=True)]
    for tool in tools:
        print(f"{tool.name}: args={list(tool.args.keys())}")

    # With an LLM configured, pass the list straight to your agent constructor:
    #
    #     from langchain.agents import create_agent
    #     agent = create_agent(model="openai:gpt-4o-mini", tools=tools)
    #     agent.invoke({"messages": [("user", "Summarise python.org")]})


EXAMPLES = [
    ("Basic", basic_example),
    ("Advanced configuration", advanced_configuration_example),
    ("Partial failure", partial_failure_example),
    ("Structured access", structured_access_example),
    ("Error handling", error_handling_example),
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
