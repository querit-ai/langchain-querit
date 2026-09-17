"""
Querit Monitor backend implementation.

A Monitor turns a single search into a scheduled task: register a query and an
interval, and the API reruns it on schedule, deduplicates against past runs and
returns only new results. This backend wraps the Monitor REST endpoints under
``https://api.querit.ai/v1/monitors``.
"""

import os
import requests
from typing import Any, Dict, Optional


class QueritMonitorBackend:
    """Querit Monitor API backend."""

    BASE_URL = "https://api.querit.ai"
    TIMEOUT = 120

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("QUERIT_API_KEY")

    def validate_credentials(self) -> bool:
        """Validate Querit API credentials."""
        return bool(self.api_key)

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Send a request to the Monitor API and return the parsed JSON."""
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
        # Drop empty query params so the URL is not polluted with None values.
        clean_params = {
            k: v for k, v in (params or {}).items() if v not in (None, "")
        }

        response = requests.request(
            method,
            f"{self.BASE_URL}{path}",
            headers=headers,
            params=clean_params or None,
            json=json_body,
            timeout=self.TIMEOUT,
        )
        response.raise_for_status()
        return response.json()

    # ----- write operations -------------------------------------------------

    def create(
        self,
        name: str,
        query: str,
        period: str,
        count: Optional[int] = None,
        need_content: bool = False,
    ) -> Dict[str, Any]:
        """Create a scheduled monitor. ``period`` is one of 1h/2h/6h/12h/24h/1d/7d."""
        search: Dict[str, Any] = {"query": query}
        if count is not None:
            search["count"] = count
        if need_content:
            search["needContent"] = True
        body = {
            "name": name,
            "schedule": {"type": "interval", "period": period},
            "search": search,
        }
        return self._request("POST", "/v1/monitors", json_body=body)

    def update(
        self,
        monitor_id: str,
        name: Optional[str] = None,
        period: Optional[str] = None,
        query: Optional[str] = None,
        count: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Update a monitor. Provide at least one of name / period / query.

        Note: ``search`` is replaced as a whole object by the API, so when
        ``query`` is given the whole search object is rebuilt (include ``count``
        again to keep it).
        """
        body: Dict[str, Any] = {}
        if name:
            body["name"] = name
        if period:
            body["schedule"] = {"type": "interval", "period": period}
        if query:
            search: Dict[str, Any] = {"query": query}
            if count is not None:
                search["count"] = count
            body["search"] = search
        if not body:
            raise ValueError("Provide at least one of name / period / query.")
        return self._request("POST", f"/v1/monitors/{monitor_id}", json_body=body)

    def delete(self, monitor_id: str) -> Dict[str, Any]:
        """Delete a monitor (irreversible)."""
        return self._request("DELETE", f"/v1/monitors/{monitor_id}")

    def pause(self, monitor_id: str) -> Dict[str, Any]:
        """Pause a monitor; while paused it does not run and consumes no token."""
        return self._request("POST", f"/v1/monitors/{monitor_id}/pause")

    def resume(self, monitor_id: str) -> Dict[str, Any]:
        """Resume a paused monitor."""
        return self._request("POST", f"/v1/monitors/{monitor_id}/resume")

    def trigger(self, monitor_id: str) -> Dict[str, Any]:
        """Run a monitor once immediately (consumes one search from your quota)."""
        return self._request("POST", f"/v1/monitors/{monitor_id}/trigger")

    # ----- read operations --------------------------------------------------

    def list(
        self,
        status: Optional[str] = None,
        name: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List monitors, optionally filtered by status / name, with pagination."""
        return self._request(
            "GET",
            "/v1/monitors",
            params={
                "status": status,
                "name": name,
                "page": page,
                "page_size": page_size,
            },
        )

    def get(self, monitor_id: str) -> Dict[str, Any]:
        """Get a single monitor's full details, including its search config."""
        return self._request("GET", f"/v1/monitors/{monitor_id}")

    def recent(self, monitor_id: str, limit: int = 10) -> Dict[str, Any]:
        """Fetch the most recent executions together with their result content.

        The new results of each execution are in ``events[].payload``.
        """
        return self._request(
            "GET",
            f"/v1/monitors/{monitor_id}/executions/recent",
            params={"limit": limit},
        )
