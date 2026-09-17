"""
Minimal working example for the Querit Monitor tools.

Run it with a real API key:

    export QUERIT_API_KEY="your-querit-api-key"
    python3 examples/monitor_usage.py

The script creates a monitor, triggers one run, reads the recent results and
then deletes the monitor. It exits non-zero if anything fails, so it can be
used as a smoke test.
"""

import os
import sys

from langchain_websearch import (
    MonitorCreateTool,
    MonitorTriggerTool,
    MonitorRecentTool,
    MonitorDeleteTool,
    MonitorListTool,
)

PREVIEW_CHARS = 600


def preview(text: str) -> str:
    """Shorten long output for display only."""
    if len(text) <= PREVIEW_CHARS:
        return text
    return f"{text[:PREVIEW_CHARS]}\n... ({len(text)} chars total)"


def check(output: str, action: str) -> str:
    """Monitor tools return failures as a plain string; fail loudly on them."""
    if not output or "failed:" in output.lower():
        raise RuntimeError(f"{action} did not succeed: {output!r}")
    return output


def main() -> int:
    if not os.getenv("QUERIT_API_KEY"):
        print("QUERIT_API_KEY is not set. Export it and run this script again.")
        return 1

    print("=== Create monitor ===")
    created = check(
        MonitorCreateTool().invoke(
            {
                "name": "LangChain example monitor",
                "query": "AI startups Series A funding",
                "period": "1d",
                "count": 10,
            }
        ),
        "create",
    )
    print(created)

    # The create tool prints the id; pull it back out for the follow-up calls.
    monitor_id = created.split("Created monitor", 1)[1].split(" ", 2)[1]
    print(f"monitor_id = {monitor_id}")

    print("\n=== List monitors ===")
    print(preview(check(MonitorListTool().invoke({}), "list")))

    print("\n=== Trigger once ===")
    print(check(MonitorTriggerTool().invoke({"monitor_id": monitor_id}), "trigger"))

    print("\n=== Recent results ===")
    print(
        preview(
            MonitorRecentTool().invoke({"monitor_id": monitor_id, "limit": 5})
        )
    )

    print("\n=== Delete monitor ===")
    print(check(MonitorDeleteTool().invoke({"monitor_id": monitor_id}), "delete"))

    print("\nAll examples completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
