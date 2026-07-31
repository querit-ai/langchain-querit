# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.3] - 2026-07-31

### Added

- `WebContentsTool`, a LangChain tool wrapping the Querit Contents API
  (`POST /v1/contents`). Fetches the full text of 1 to 10 URLs per call, with
  `format` (`text` / `markdown` / `html`), `crawl_timeout` and `extras_meta`
  options.
- `QueritContentsBackend`, the LangChain-independent backend for the Contents
  API, usable on its own.
- `ContentResult`, `ContentMeta` and `ContentsInput` models. Each result carries
  its own `status`, so one unreachable page does not fail the whole call.
- `examples/contents_usage.py`, a runnable smoke test for the Contents tool that
  exits non-zero on failure.
- `tests/test_contents.py` with 13 assertions, covering batch partial failure,
  metadata handling and input validation.

### Changed

- **Breaking:** minimum supported Python is now 3.9. On 3.8, `pip` can only
  resolve `langchain-core` 0.2.x, whose `BaseTool` is built on the pydantic v1
  compatibility layer, and the tools cannot be instantiated there. 0.0.2 already
  did not work on 3.8; the metadata now reflects reality.
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

### Notes

- Errors in `WebContentsTool` propagate instead of being returned as text: a
  missing key, an empty URL list or more than 10 URLs raise `ValueError`
  (no HTTP request is sent), and HTTP 4xx/5xx raise `requests.HTTPError`.
  `WebSearchTool` keeps its existing behaviour of returning errors as strings.

## [0.0.2] - 2026-02-26

### Added

- Initial public release: `WebSearchTool` and `QueritSearchBackend` wrapping the
  Querit Search API (`POST /v1/search`).

[0.0.3]: https://github.com/querit-ai/langchain-querit/releases/tag/v0.0.3
[0.0.2]: https://github.com/querit-ai/langchain-querit/releases/tag/v0.0.2
