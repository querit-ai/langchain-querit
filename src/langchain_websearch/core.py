"""
Core components for LangChain WebSearch Tool.
"""

import json
from typing import Any, List, Literal, Optional, Type

from pydantic import BaseModel, Field, PrivateAttr
from langchain.tools import BaseTool


class SearchResult(BaseModel):
    """Search result model."""

    title: str
    link: str
    snippet: str
    display_link: str
    position: int


class WebSearchTool(BaseTool):
    """LangChain tool for web search functionality using Querit Search API."""

    name: str = "web_search"
    description: str = (
        "A tool for searching the web using Querit Search API. "
        "Useful for finding up-to-date information, news, and facts. "
        "Input should be a search query string."
    )

    num_results: int = Field(default=10, ge=1, le=50)
    region: str = Field(default="en-US")  # 保留但不使用
    safe_search: bool = Field(default=True)  # 保留但不使用

    # Declared explicitly so the assignment in __init__ also works under the
    # pydantic v1 semantics that older langchain-core releases are built on.
    _backend_instance: Any = PrivateAttr(default=None)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 延迟导入以避免循环导入
        from .querit_search import QueritSearchBackend

        self._backend_instance = QueritSearchBackend()

    def _run(self, query: str) -> str:
        """Execute the search and return formatted results."""
        try:
            results = self._backend_instance.search(
                query=query, num_results=self.num_results
            )

            if not results:
                return "No search results found."

            return self._format_results(results)

        except Exception as e:
            return f"Search failed: {str(e)}"

    def _format_results(self, results: List[SearchResult]) -> str:
        """Format search results into a readable string."""
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(f"{i}. {result.title}")
            formatted.append(f"   URL: {result.link}")
            formatted.append(f"   Preview: {result.snippet}")
            formatted.append("")

        return "\n".join(formatted)

    # _arun is intentionally not overridden: BaseTool's default already offloads
    # _run to a thread executor, whereas awaiting _run directly would block the
    # event loop for the whole HTTP call.


class ContentMeta(BaseModel):
    """Extra metadata for a fetched page, returned when extras_meta is enabled."""

    title: str = ""
    url: str = ""
    publish_time: str = ""
    site_name: str = ""
    site_icon: str = ""


class ContentResult(BaseModel):
    """Fetched web page content model."""

    id: str
    url: str
    content: str
    status: str  # "success" | "failed" | "unknown"
    meta: Optional[ContentMeta] = None


class ContentsInput(BaseModel):
    """Input schema for WebContentsTool."""

    urls: List[str] = Field(
        ..., description="A list of 1 to 10 URLs to fetch page content from."
    )


class WebContentsTool(BaseTool):
    """LangChain tool for fetching page content using Querit Contents API."""

    name: str = "web_contents"
    description: str = (
        "A tool for fetching the full content of web pages using Querit Contents "
        "API. Useful when you already have URLs and need their actual text. "
        "Input should be a list of 1 to 10 URLs."
    )
    args_schema: Type[BaseModel] = ContentsInput

    format: Literal["text", "markdown", "html"] = Field(default="markdown")
    crawl_timeout: int = Field(default=10, ge=1, le=60)
    extras_meta: bool = Field(default=False)

    _backend_instance: Any = PrivateAttr(default=None)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 延迟导入以避免循环导入
        from .querit_contents import QueritContentsBackend

        self._backend_instance = QueritContentsBackend()

    def _run(self, urls: List[str]) -> str:
        """Fetch page content and return formatted results."""
        results = self._backend_instance.fetch(
            urls=urls,
            format=self.format,
            crawl_timeout=self.crawl_timeout,
            extras_meta=self.extras_meta,
        )

        if not results:
            return "No content retrieved."

        return self._format_results(results)

    def _format_results(self, results: List[ContentResult]) -> str:
        """Format fetched contents into a readable string."""
        formatted = []
        for i, result in enumerate(results, 1):
            succeeded = result.status.lower() == "success"
            label = result.status if succeeded else result.status.upper()
            formatted.append(f"{i}. {result.url}  [{label}]")

            if result.meta is not None:
                if result.meta.title:
                    formatted.append(f"   Title: {result.meta.title}")
                if result.meta.site_name:
                    formatted.append(f"   Site: {result.meta.site_name}")
                if result.meta.publish_time:
                    formatted.append(f"   Published: {result.meta.publish_time}")

            if result.content:
                formatted.append(f"   Content ({len(result.content)} chars):")
                formatted.append(result.content)
            elif succeeded:
                # Distinguish "crawled but empty" from "could not be crawled".
                formatted.append("   Content is empty.")
            else:
                formatted.append("   No content retrieved.")

            formatted.append("")

        return "\n".join(formatted)

    # See the note on WebSearchTool: BaseTool's default _arun already offloads
    # _run to a thread executor, which matters more here because a contents
    # request can legitimately take a minute.


# ---------------------------------------------------------------------------
# Querit Monitor tools
#
# A Monitor turns a single search into a scheduled task that reruns on an
# interval, deduplicates against past runs and surfaces only new results.
# Each capability below is a BaseTool subclass backed by QueritMonitorBackend.
# ---------------------------------------------------------------------------


def _monitor_data(response: Any) -> dict:
    """Unwrap the {error_code, error_msg, data} envelope and return ``data``."""
    if isinstance(response, dict) and "data" in response:
        return response.get("data") or {}
    return response if isinstance(response, dict) else {}


class _MonitorToolBase(BaseTool):
    """Shared wiring for monitor tools: lazily build one backend instance.

    This class is never instantiated directly; concrete subclasses supply the
    name, description and args_schema.
    """

    _backend_instance: Any = PrivateAttr(default=None)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 延迟导入以避免循环导入
        from .querit_monitor import QueritMonitorBackend

        self._backend_instance = QueritMonitorBackend()

    # _arun intentionally not overridden: BaseTool's default offloads _run to a
    # thread executor, and monitor_trigger can legitimately take several seconds.


class MonitorIdInput(BaseModel):
    """Input schema for tools that operate on a single monitor by id."""

    monitor_id: str = Field(
        ..., description="The monitor id (a 32-character hexadecimal string)."
    )


class MonitorCreateInput(BaseModel):
    """Input schema for MonitorCreateTool."""

    name: str = Field(..., description="A human-readable name for the monitor.")
    query: str = Field(..., description="The search query to run on each execution.")
    period: str = Field(
        ...,
        description="Schedule interval, one of 1h, 2h, 6h, 12h, 24h, 1d, 7d.",
    )
    count: Optional[int] = Field(
        default=None, description="Maximum number of results per execution."
    )


class MonitorCreateTool(_MonitorToolBase):
    """Create a scheduled Querit search monitor."""

    name: str = "monitor_create"
    description: str = (
        "Create a scheduled Querit search monitor that reruns a query on an "
        "interval and returns only newly found results. Inputs: name, query, "
        "period (1h/2h/6h/12h/24h/1d/7d), and optional count."
    )
    args_schema: Type[BaseModel] = MonitorCreateInput

    def _run(
        self, name: str, query: str, period: str, count: Optional[int] = None
    ) -> str:
        try:
            m = _monitor_data(
                self._backend_instance.create(name, query, period, count)
            )
            return (
                f"Created monitor {m.get('monitor_id')} "
                f"(status={m.get('status')}, "
                f"next_trigger_at={m.get('next_trigger_at')})."
            )
        except Exception as e:
            return f"Create monitor failed: {e}"


class MonitorListInput(BaseModel):
    """Input schema for MonitorListTool."""

    status: Optional[str] = Field(
        default=None, description="Filter by status: active or paused."
    )
    name: Optional[str] = Field(
        default=None, description="Fuzzy match on monitor name."
    )
    page: Optional[int] = Field(
        default=None, description="Page number, starting at 1."
    )
    page_size: Optional[int] = Field(
        default=None, description="Items per page, capped at 100."
    )


class MonitorListTool(_MonitorToolBase):
    """List monitors with optional filters."""

    name: str = "monitor_list"
    description: str = (
        "List your Querit monitors, optionally filtered by status (active/"
        "paused) or name, with pagination."
    )
    args_schema: Type[BaseModel] = MonitorListInput

    def _run(
        self,
        status: Optional[str] = None,
        name: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> str:
        try:
            data = _monitor_data(
                self._backend_instance.list(status, name, page, page_size)
            )
            items = data.get("items", []) or []
            if not items:
                return "No monitors found."
            lines = [f"Total: {data.get('total', len(items))}"]
            for it in items:
                schedule = it.get("schedule") or {}
                lines.append(
                    f"- {it.get('monitor_id')} | {it.get('name')} | "
                    f"{it.get('status')} | {schedule.get('period')}"
                )
            return "\n".join(lines)
        except Exception as e:
            return f"List monitors failed: {e}"


class MonitorGetTool(_MonitorToolBase):
    """Get the full details of a single monitor."""

    name: str = "monitor_get"
    description: str = (
        "Get a single Querit monitor's full details, including its search "
        "configuration. Input: monitor_id."
    )
    args_schema: Type[BaseModel] = MonitorIdInput

    def _run(self, monitor_id: str) -> str:
        try:
            m = _monitor_data(self._backend_instance.get(monitor_id))
            return json.dumps(m, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"Get monitor failed: {e}"


class MonitorUpdateInput(BaseModel):
    """Input schema for MonitorUpdateTool."""

    monitor_id: str = Field(..., description="The monitor id to update.")
    name: Optional[str] = Field(default=None, description="New monitor name.")
    period: Optional[str] = Field(
        default=None,
        description="New interval, one of 1h, 2h, 6h, 12h, 24h, 1d, 7d.",
    )
    query: Optional[str] = Field(
        default=None,
        description="New search query. Replaces the whole search object.",
    )
    count: Optional[int] = Field(
        default=None, description="Result count, only used together with query."
    )


class MonitorUpdateTool(_MonitorToolBase):
    """Update a monitor's name, schedule or search query."""

    name: str = "monitor_update"
    description: str = (
        "Update a Querit monitor. Provide monitor_id plus at least one of name / "
        "period / query. Note: the search object is replaced as a whole, so "
        "re-supply count if you want to keep it."
    )
    args_schema: Type[BaseModel] = MonitorUpdateInput

    def _run(
        self,
        monitor_id: str,
        name: Optional[str] = None,
        period: Optional[str] = None,
        query: Optional[str] = None,
        count: Optional[int] = None,
    ) -> str:
        try:
            m = _monitor_data(
                self._backend_instance.update(
                    monitor_id, name, period, query, count
                )
            )
            return f"Updated monitor {m.get('monitor_id', monitor_id)}."
        except Exception as e:
            return f"Update monitor failed: {e}"


class MonitorDeleteTool(_MonitorToolBase):
    """Delete a monitor."""

    name: str = "monitor_delete"
    description: str = "Delete a Querit monitor by monitor_id. This is irreversible."
    args_schema: Type[BaseModel] = MonitorIdInput

    def _run(self, monitor_id: str) -> str:
        try:
            self._backend_instance.delete(monitor_id)
            return f"Deleted monitor {monitor_id}."
        except Exception as e:
            return f"Delete monitor failed: {e}"


class MonitorPauseTool(_MonitorToolBase):
    """Pause a monitor."""

    name: str = "monitor_pause"
    description: str = (
        "Pause a Querit monitor by monitor_id. While paused it does not run on "
        "schedule and consumes no token."
    )
    args_schema: Type[BaseModel] = MonitorIdInput

    def _run(self, monitor_id: str) -> str:
        try:
            self._backend_instance.pause(monitor_id)
            return f"Paused monitor {monitor_id}."
        except Exception as e:
            return f"Pause monitor failed: {e}"


class MonitorResumeTool(_MonitorToolBase):
    """Resume a paused monitor."""

    name: str = "monitor_resume"
    description: str = "Resume a paused Querit monitor by monitor_id."
    args_schema: Type[BaseModel] = MonitorIdInput

    def _run(self, monitor_id: str) -> str:
        try:
            self._backend_instance.resume(monitor_id)
            return f"Resumed monitor {monitor_id}."
        except Exception as e:
            return f"Resume monitor failed: {e}"


class MonitorTriggerTool(_MonitorToolBase):
    """Run a monitor once immediately."""

    name: str = "monitor_trigger"
    description: str = (
        "Run a Querit monitor once immediately by monitor_id. This is "
        "synchronous, consumes one search from your quota and updates the "
        "deduplication baseline. Returns execution_id and new_results."
    )
    args_schema: Type[BaseModel] = MonitorIdInput

    def _run(self, monitor_id: str) -> str:
        try:
            d = _monitor_data(self._backend_instance.trigger(monitor_id))
            return (
                f"Triggered monitor {monitor_id}: "
                f"execution_id={d.get('execution_id')}, "
                f"new_results={d.get('new_results')}."
            )
        except Exception as e:
            return f"Trigger monitor failed: {e}"


class MonitorRecentInput(BaseModel):
    """Input schema for MonitorRecentTool."""

    monitor_id: str = Field(..., description="The monitor id.")
    limit: int = Field(
        default=10,
        description="How many recent executions to return (capped at 100).",
    )


class MonitorRecentTool(_MonitorToolBase):
    """Fetch recent executions with their result content."""

    name: str = "monitor_recent_results"
    description: str = (
        "Fetch the most recent executions of a Querit monitor together with "
        "their result content. This is the main way to read a monitor's new "
        "results. Inputs: monitor_id, optional limit."
    )
    args_schema: Type[BaseModel] = MonitorRecentInput

    def _run(self, monitor_id: str, limit: int = 10) -> str:
        try:
            data = _monitor_data(self._backend_instance.recent(monitor_id, limit))
            items = data.get("items", []) or []
            if not items:
                return "No executions found."
            return json.dumps(items, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"Recent executions failed: {e}"
