"""
Tests for WebContentsTool (Querit Contents API).

Tests that hit the real API are skipped when QUERIT_API_KEY is not set.
"""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from langchain_websearch import (
    ContentMeta,
    ContentResult,
    QueritContentsBackend,
    WebContentsTool,
)

GOOD_URL = "https://example.com"
BAD_URL = "https://this-domain-really-does-not-exist-xyz123.com"

requires_api_key = pytest.mark.skipif(
    not os.getenv("QUERIT_API_KEY"), reason="需要 QUERIT_API_KEY"
)


# --- 无需 API key 的用例 ---------------------------------------------------


def test_tool_metadata():
    """Tool 的名称、描述和入参 schema 应可用于 LangChain agent。"""
    tool = WebContentsTool()

    assert tool.name == "web_contents"
    assert "URL" in tool.description
    assert "urls" in tool.args


def test_missing_api_key_raises():
    """没有 API key 时应抛 ValueError，而不是静默返回字符串。"""
    backend = QueritContentsBackend(api_key=None)
    with patch.dict(os.environ, {}, clear=True):
        backend.api_key = None
        with pytest.raises(ValueError, match="API key not found"):
            backend.fetch([GOOD_URL])


def test_empty_urls_raises_without_request():
    """空 urls 应本地拦下，不发 HTTP 请求。"""
    backend = QueritContentsBackend(api_key="dummy-key")
    with patch("langchain_websearch.querit_contents.requests.post") as mock_post:
        with pytest.raises(ValueError, match="At least one URL"):
            backend.fetch([])
        mock_post.assert_not_called()


def test_too_many_urls_raises_without_request():
    """超过 10 个 URL 应本地拦下，不浪费一次请求换 400。"""
    backend = QueritContentsBackend(api_key="dummy-key")
    urls = [f"https://example.com/{i}" for i in range(11)]

    with patch("langchain_websearch.querit_contents.requests.post") as mock_post:
        with pytest.raises(ValueError, match="Too many URLs: 11"):
            backend.fetch(urls)
        mock_post.assert_not_called()


def test_invalid_format_rejected_locally():
    """非法 format 应被 pydantic 拦下，不发请求。"""
    with pytest.raises(ValidationError):
        WebContentsTool(format="pdf")


def test_status_joined_by_id_not_by_position():
    """statuses 与 results 顺序不一致时，仍应按 id 正确关联成败。"""
    backend = QueritContentsBackend(api_key="dummy-key")
    payload = {
        "results": [
            {"id": "1", "url": GOOD_URL, "content": "hello"},
            {"id": "2", "url": BAD_URL, "content": ""},
        ],
        # 故意与 results 顺序相反
        "statuses": [
            {"id": "2", "status": "failed"},
            {"id": "1", "status": "success"},
        ],
    }

    results = backend._parse(payload)

    assert [(r.url, r.status) for r in results] == [
        (GOOD_URL, "success"),
        (BAD_URL, "failed"),
    ]


def test_format_results_marks_failures():
    """失败条目在输出里应大写标记，成功条目附带字符数。"""
    tool = WebContentsTool()
    output = tool._format_results(
        [
            ContentResult(
                id="1",
                url=GOOD_URL,
                content="hello",
                status="success",
                meta=ContentMeta(title="Example Domain", site_name="example.com"),
            ),
            ContentResult(id="2", url=BAD_URL, content="", status="failed"),
        ]
    )

    assert "[success]" in output
    assert "[FAILED]" in output
    assert "Title: Example Domain" in output
    assert "Content (5 chars):" in output
    assert "No content retrieved." in output


# --- 需要真实 API key 的用例 ----------------------------------------------


@requires_api_key
def test_fetch_single_url_success():
    """单个 URL 应抓到非空正文。"""
    tool = WebContentsTool()
    output = tool.invoke({"urls": [GOOD_URL]})

    assert "[success]" in output
    assert "[FAILED]" not in output
    assert len(output) > 50


@requires_api_key
def test_batch_partial_failure():
    """好 URL + 不存在的域名：一条成功一条失败，整体请求不抛异常。"""
    backend = QueritContentsBackend()
    results = backend.fetch([GOOD_URL, BAD_URL])

    statuses = {r.url: r.status for r in results}
    assert statuses.get(GOOD_URL) == "success"
    assert statuses.get(BAD_URL) == "failed"


@requires_api_key
def test_extras_meta_enabled_populates_meta():
    """extras_meta=True 时应返回标题和站点名。"""
    backend = QueritContentsBackend()
    results = backend.fetch([GOOD_URL], extras_meta=True)

    assert results[0].meta is not None
    assert results[0].meta.title
    assert results[0].meta.site_name


@requires_api_key
def test_extras_meta_disabled_leaves_meta_none():
    """extras_meta=False 时不应返回元信息。"""
    backend = QueritContentsBackend()
    results = backend.fetch([GOOD_URL], extras_meta=False)

    assert results[0].meta is None


@requires_api_key
def test_invalid_api_key_raises_http_error():
    """key 无效时应抛 HTTPError，而不是返回看起来正常的字符串。"""
    import requests

    backend = QueritContentsBackend(api_key="querit-sk-invalid-key-for-testing")
    with pytest.raises(requests.HTTPError):
        backend.fetch([GOOD_URL])


@requires_api_key
def test_content_not_truncated():
    """正文应全文返回，不做截断。"""
    backend = QueritContentsBackend()
    results = backend.fetch(["https://docs.python.org/3/whatsnew/3.13.html"])

    assert results[0].status == "success"
    assert len(results[0].content) > 5000
