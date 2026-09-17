# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.4] - 2026-09-17

### Added

- Querit Monitor integration. A Monitor turns a single search into a scheduled
  task that reruns on an interval, deduplicates against past runs and surfaces
  only new results. Nine LangChain tools wrap the Monitor REST API
  (`/v1/monitors...`): `MonitorCreateTool`, `MonitorListTool`, `MonitorGetTool`,
  `MonitorUpdateTool`, `MonitorDeleteTool`, `MonitorPauseTool`,
  `MonitorResumeTool`, `MonitorTriggerTool` and `MonitorRecentTool`.
- `QueritMonitorBackend`, the HTTP backend for the Monitor API, usable directly
  when you want the raw JSON instead of a formatted string.
- Input models `MonitorCreateInput`, `MonitorListInput`, `MonitorIdInput`,
  `MonitorUpdateInput` and `MonitorRecentInput`.
- `examples/monitor_usage.py`, a runnable smoke test that creates, triggers and
  reads a monitor, then deletes it.
- `tests/test_monitor.py`, verifying the request method, URL, query params and
  JSON body each backend method builds, plus the missing-key error path.

## [0.0.3] - 2026-07-31

### Added

- `WebContentsTool`, a LangChain tool wrapping the Querit Contents API
  (`POST /v1/contents`). Fetches the full text of 1 to 10 URLs per call, with
  `format` (`text` / `markdown` / `html`), `crawl_timeout` and `extras_meta`
  options.
- `QueritContentsBackend`, the HTTP backend for the Contents API. It returns
  `ContentResult` objects and can be used directly when a formatted string is not
  what you want.
- `ContentResult`, `ContentMeta` and `ContentsInput` models. Each result carries
  its own `status`, so one unreachable page does not fail the whole call.
- `examples/contents_usage.py`, a runnable smoke test for the Contents tool that
  exits non-zero on failure.
- `tests/test_contents.py` with 17 tests, covering batch partial failure, status
  correlation by `id`, request payload field names, metadata handling and input
  validation.

### Changed

- **Breaking:** minimum supported Python is now 3.9, and the dependency floors are
  now `langchain>=0.3` / `pydantic>=2.0`. The previous floors
  (`langchain>=0.0.300`, `pydantic>=1.10.0`) were not real: pinning `pydantic<2`
  made pip resolve `langchain-core` 0.2.x, whose `BaseTool` is built on the
  pydantic v1 compatibility layer, and both tools then failed to construct with
  `ValueError: object has no field "_backend_instance"`. That affected 0.0.2 on
  any Python version, not just 3.8. The floors now describe what is tested.
- Both tools declare `_backend_instance` as a pydantic `PrivateAttr`, so the
  assignment also works under pydantic v1 semantics.
- Dropped the `_arun` overrides. `BaseTool` already offloads `_run` to a thread
  executor, whereas awaiting `_run` directly blocked the event loop for the whole
  HTTP request.
- `examples/basic_usage.py` now reads `QUERIT_API_KEY` from the environment
  instead of overwriting it with a placeholder, and exits non-zero on failure.
  It previously always failed with HTTP 401 even when a valid key was exported.
- Examples and README use the public `tool.invoke(...)` entry point instead of
  the internal `tool._run(...)`.
- Removed the dead agent example that imported `initialize_agent` and
  `langchain.llms.OpenAI`, both removed in langchain 1.x.
- Repository URLs now point at `querit-ai/langchain-querit`.
- Package author metadata is now `Querit.ai <support@querit.ai>`, replacing the
  placeholder values shipped in 0.0.2.

### Fixed

- A URL whose id appeared in the response `statuses[]` but not in `results[]` was
  silently dropped, returning fewer entries than were requested. Both arrays are
  now merged on the union of their ids.
- Response entries without an id no longer share a single lookup key, which could
  attribute one entry's status to unrelated results.
- Status values that are missing, `null` or unexpectedly cased are normalised to
  `unknown` instead of reaching the formatted output as `[]` or `[NONE]`.
- The URL count is validated before the credential check, so a bad URL list is no
  longer reported as a missing API key.
- The request timeout is now an explicit `(connect, read)` pair, and the read
  budget scales with the number of URLs. Previously a single value was applied to
  both, giving a 40 second connect timeout, and the read budget ignored the fact
  that `crawlTimeout` is per page.

### Notes

- Errors in `WebContentsTool` propagate instead of being returned as text: a
  missing key, an empty URL list or more than 10 URLs raise `ValueError`
  (no HTTP request is sent), and HTTP 4xx/5xx raise `requests.HTTPError`.
  `WebSearchTool` keeps its existing behaviour of returning errors as strings.

## [0.0.2] - 2026-02-26

### Added

- Initial public release: `WebSearchTool` and `QueritSearchBackend` wrapping the
  Querit Search API (`POST /v1/search`).

[0.0.4]: https://github.com/querit-ai/langchain-querit/releases/tag/v0.0.4
[0.0.3]: https://github.com/querit-ai/langchain-querit/releases/tag/v0.0.3
[0.0.2]: https://github.com/querit-ai/langchain-querit/releases/tag/v0.0.2
