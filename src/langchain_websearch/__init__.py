"""
LangChain WebSearch Tool
A powerful search tool for LangChain using Querit Search API.
"""

from .core import (
    ContentMeta,
    ContentResult,
    ContentsInput,
    MonitorCreateInput,
    MonitorCreateTool,
    MonitorDeleteTool,
    MonitorGetTool,
    MonitorIdInput,
    MonitorListInput,
    MonitorListTool,
    MonitorPauseTool,
    MonitorRecentInput,
    MonitorRecentTool,
    MonitorResumeTool,
    MonitorTriggerTool,
    MonitorUpdateInput,
    MonitorUpdateTool,
    SearchResult,
    WebContentsTool,
    WebSearchTool,
)
from .querit_contents import QueritContentsBackend
from .querit_monitor import QueritMonitorBackend
from .querit_search import QueritSearchBackend

__version__ = "0.0.4"
__all__ = [
    "WebSearchTool",
    "SearchResult",
    "QueritSearchBackend",
    "WebContentsTool",
    "ContentResult",
    "ContentMeta",
    "ContentsInput",
    "QueritContentsBackend",
    # Monitor tools
    "QueritMonitorBackend",
    "MonitorCreateTool",
    "MonitorListTool",
    "MonitorGetTool",
    "MonitorUpdateTool",
    "MonitorDeleteTool",
    "MonitorPauseTool",
    "MonitorResumeTool",
    "MonitorTriggerTool",
    "MonitorRecentTool",
    "MonitorCreateInput",
    "MonitorListInput",
    "MonitorIdInput",
    "MonitorUpdateInput",
    "MonitorRecentInput",
]
