"""
Core components for LangChain WebSearch Tool.
"""

from typing import List, Literal, Optional, Type

from pydantic import BaseModel, Field
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

    async def _arun(self, query: str) -> str:
        """Async version of the search tool."""
        return self._run(query)


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
            label = (
                result.status if result.status == "success" else result.status.upper()
            )
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
            else:
                formatted.append("   No content retrieved.")

            formatted.append("")

        return "\n".join(formatted)

    async def _arun(self, urls: List[str]) -> str:
        """Async version of the contents tool."""
        return self._run(urls)
