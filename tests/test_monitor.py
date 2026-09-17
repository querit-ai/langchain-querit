"""
Tests for the Querit Monitor backend.

These are mocked at the ``requests`` layer, so they run without a network
connection or an API key and assert exactly what each method sends: HTTP
method, URL, query params and JSON body.
"""

import os
from unittest.mock import patch, MagicMock

import pytest

from langchain_websearch.querit_monitor import QueritMonitorBackend


def _make_response():
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = {"error_code": 200, "error_msg": "", "data": {"ok": True}}
    return resp


def _run(method_name, *args, **kwargs):
    """Call a backend method with requests.request mocked, return the captured call."""
    captured = {}

    def fake_request(method, url, headers=None, params=None, json=None, timeout=None):
        captured.update(
            method=method, url=url, headers=headers, params=params, json=json
        )
        return _make_response()

    backend = QueritMonitorBackend(api_key="test-key")
    with patch(
        "langchain_websearch.querit_monitor.requests.request",
        side_effect=fake_request,
    ):
        getattr(backend, method_name)(*args, **kwargs)
    return captured


def test_create_builds_post_body():
    call = _run("create", "N", "Q", "1d", count=5, need_content=True)
    assert call["method"] == "POST"
    assert call["url"] == "https://api.querit.ai/v1/monitors"
    assert call["json"] == {
        "name": "N",
        "schedule": {"type": "interval", "period": "1d"},
        "search": {"query": "Q", "count": 5, "needContent": True},
    }
    assert call["headers"]["Authorization"] == "Bearer test-key"


def test_create_minimal_search():
    call = _run("create", "N", "Q", "1h")
    assert call["json"]["search"] == {"query": "Q"}


def test_list_drops_none_params():
    call = _run("list", status="active", page=2)
    assert call["method"] == "GET"
    assert call["url"] == "https://api.querit.ai/v1/monitors"
    assert call["params"] == {"status": "active", "page": 2}


def test_list_empty_params_become_none():
    call = _run("list")
    assert call["params"] is None


def test_get_url():
    call = _run("get", "abc")
    assert call["method"] == "GET"
    assert call["url"] == "https://api.querit.ai/v1/monitors/abc"


def test_update_rebuilds_search():
    call = _run("update", "abc", query="Q", count=3)
    assert call["method"] == "POST"
    assert call["url"] == "https://api.querit.ai/v1/monitors/abc"
    assert call["json"] == {"search": {"query": "Q", "count": 3}}


def test_update_name_and_schedule():
    call = _run("update", "abc", name="X", period="6h")
    assert call["json"] == {
        "name": "X",
        "schedule": {"type": "interval", "period": "6h"},
    }


def test_update_requires_a_field():
    backend = QueritMonitorBackend(api_key="test-key")
    with pytest.raises(ValueError):
        backend.update("abc")


def test_delete_uses_delete_method():
    call = _run("delete", "abc")
    assert call["method"] == "DELETE"
    assert call["url"] == "https://api.querit.ai/v1/monitors/abc"


@pytest.mark.parametrize(
    "method_name,suffix",
    [("pause", "/pause"), ("resume", "/resume"), ("trigger", "/trigger")],
)
def test_post_no_body_actions(method_name, suffix):
    call = _run(method_name, "abc")
    assert call["method"] == "POST"
    assert call["url"] == f"https://api.querit.ai/v1/monitors/abc{suffix}"
    assert call["json"] is None


def test_recent_params():
    call = _run("recent", "abc", limit=5)
    assert call["method"] == "GET"
    assert call["url"] == "https://api.querit.ai/v1/monitors/abc/executions/recent"
    assert call["params"] == {"limit": 5}


def test_missing_key_raises():
    with patch.dict(os.environ, {}, clear=True):
        backend = QueritMonitorBackend()
        with pytest.raises(ValueError):
            backend.get("abc")
