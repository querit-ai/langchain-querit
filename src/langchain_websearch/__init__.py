"""
LangChain WebSearch Tool
A powerful search tool for LangChain using Querit Search API.
"""

from .core import (
    ContentMeta,
    ContentResult,
    ContentsInput,
    SearchResult,
    WebContentsTool,
    WebSearchTool,
)
from .querit_contents import QueritContentsBackend
from .querit_search import QueritSearchBackend

__version__ = "0.0.3"
__all__ = [
    "WebSearchTool",
    "SearchResult",
    "QueritSearchBackend",
    "WebContentsTool",
    "ContentResult",
    "ContentMeta",
    "ContentsInput",
    "QueritContentsBackend",
]
