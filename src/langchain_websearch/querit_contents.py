"""
Querit Contents backend implementation.
"""

import os
import requests
from typing import Any, Dict, List, Optional, Set

from .core import ContentMeta, ContentResult


class QueritContentsBackend:
    """Querit Contents API backend."""

    BASE_URL = "https://api.querit.ai/v1/contents"
    MAX_URLS = 10
    CONNECT_TIMEOUT = 10
    VALID_STATUSES = ("success", "failed")

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("QUERIT_API_KEY")

    def validate_credentials(self) -> bool:
        """Validate Querit API credentials."""
        return bool(self.api_key)

    def fetch(
        self,
        urls: List[str],
        format: str = "markdown",
        crawl_timeout: int = 10,
        extras_meta: bool = False,
        **kwargs: Any,
    ) -> List[ContentResult]:
        """Fetch page content for the given URLs using Querit Contents API."""
        # Validate the input shape before the credential check, so a bad URL list
        # is not reported as a missing key.
        if not urls:
            raise ValueError("At least one URL is required.")

        if len(urls) > self.MAX_URLS:
            raise ValueError(
                f"Too many URLs: {len(urls)}. "
                f"Querit Contents API accepts at most {self.MAX_URLS} URLs."
            )

        if not self.validate_credentials():
            raise ValueError(
                "Querit API key not found. "
                "Please set QUERIT_API_KEY environment variable."
            )

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "urls": urls,
            "format": format,
            "crawlTimeout": crawl_timeout,
            "extrasMeta": extras_meta,
        }

        # requests applies a single scalar to both the connect and the read
        # timeout, so pass an explicit pair. crawlTimeout is per page, so the
        # read budget has to scale with the number of pages requested.
        response = requests.post(
            self.BASE_URL,
            headers=headers,
            json=payload,
            timeout=(self.CONNECT_TIMEOUT, crawl_timeout * len(urls) + 30),
        )
        response.raise_for_status()

        return self._parse(response.json())

    def _parse(self, data: Dict[str, Any]) -> List[ContentResult]:
        """Merge the separate results/statuses arrays into ContentResult items."""
        # Content and success/failure arrive in two separate arrays that are
        # correlated by id, so join on id rather than on list position. Entries
        # without an id are skipped rather than collapsed onto a shared "" key,
        # which would attribute one entry's status to unrelated results.
        status_by_id = {
            str(item.get("id")): self._normalise_status(item.get("status"))
            for item in data.get("statuses") or []
            if item.get("id")
        }

        results: List[ContentResult] = []
        seen: Set[str] = set()

        for item in data.get("results") or []:
            item_id = str(item.get("id") or "")
            if item_id:
                seen.add(item_id)
            results.append(
                ContentResult(
                    id=item_id,
                    url=item.get("url") or "",
                    content=item.get("content") or "",
                    status=status_by_id.get(item_id, "unknown"),
                    meta=self._parse_meta(item.get("extrasMeta")),
                )
            )

        # An id present in statuses but missing from results would otherwise
        # vanish, silently returning fewer URLs than were requested.
        for item_id, status in status_by_id.items():
            if item_id not in seen:
                results.append(
                    ContentResult(id=item_id, url="", content="", status=status)
                )

        return results

    @classmethod
    def _normalise_status(cls, value: Any) -> str:
        """Map the server-reported status onto success / failed / unknown."""
        status = str(value or "").strip().lower()
        return status if status in cls.VALID_STATUSES else "unknown"

    @staticmethod
    def _parse_meta(extras: Optional[Dict[str, Any]]) -> Optional[ContentMeta]:
        """Build ContentMeta from the extrasMeta payload, if present."""
        if not extras:
            return None

        return ContentMeta(
            title=extras.get("title") or "",
            url=extras.get("url") or "",
            publish_time=extras.get("publishTime") or "",
            site_name=extras.get("siteName") or "",
            site_icon=extras.get("siteIcon") or "",
        )
