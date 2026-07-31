# LangChain WebSearch Tool

A powerful LangChain toolkit for Querit APIs: web search and web page content fetching.

## 🔍 Features

- **Querit Search API Integration**: Powered by Querit Search API
- **Querit Contents API Integration**: Fetch full page content by URL, up to 10 URLs per call
- **API Key Management**: Secure API key handling with environment variables
- **LangChain Integration**: Seamlessly integrates with LangChain agents and chains
- **Structured Results**: Returns formatted search results with metadata
- **Async Support**: Asynchronous version available
- **Flexible Configuration**: Customizable search parameters

## 🚀 Quick Start

### Requirements

Python 3.9 or newer, with `langchain>=0.3` and `pydantic>=2.0`. Older floors were
declared through 0.0.2 but did not work: pinning `pydantic<2` makes pip resolve
`langchain-core` 0.2.x, whose `BaseTool` is built on the pydantic v1 compatibility
layer, and the tools then fail to construct.

### Installation

```bash
pip install langchain-querit
```

### Basic Usage

```python
from langchain_websearch import WebSearchTool

# Read the API key from the QUERIT_API_KEY environment variable:
#   export QUERIT_API_KEY="your-querit-api-key"

# Initialize the tool
search_tool = WebSearchTool()

# Perform a search
results = search_tool.invoke("latest Python programming news")
print(results)
```

### Advanced Configuration

```python
from langchain_websearch import WebSearchTool

# Configure with specific parameters
search_tool = WebSearchTool(
    num_results=5  # Number of results to return
)

# Use with custom query
results = search_tool.invoke("machine learning tutorials")
print(results)
```

## 📄 Web Contents Tool

`WebContentsTool` fetches the full text of web pages by URL, using the Querit
Contents API. It is a separate tool from `WebSearchTool`: search finds URLs,
contents fetches what is behind them.

### Basic Usage

```python
from langchain_websearch import WebContentsTool

# Read the API key from the QUERIT_API_KEY environment variable:
#   export QUERIT_API_KEY="your-querit-api-key"

contents_tool = WebContentsTool()

# Input is a list of 1 to 10 URLs
results = contents_tool.invoke({"urls": ["https://example.com"]})
print(results)
```

### Advanced Configuration

```python
from langchain_websearch import WebContentsTool

contents_tool = WebContentsTool(
    format="markdown",   # "text" | "markdown" | "html"
    crawl_timeout=10,    # per-page crawl timeout in seconds, 1-60
    extras_meta=True,    # also return title / site name / publish time
)

results = contents_tool.invoke({
    "urls": [
        "https://example.com",
        "https://docs.python.org/3/whatsnew/3.13.html",
    ]
})
print(results)
```

Output marks each URL with its own status, so a page that fails to crawl does not
fail the whole call:

```
1. https://example.com  [success]
   Title: Example Domain
   Site: example.com
   Content (113 chars):
This domain is for use in documentation examples without needing permission. Avoid use in operations.

Learn more

2. https://this-domain-does-not-exist-xyz123.com  [FAILED]
   No content retrieved.
```

### Using Both Tools in an Agent

```python
from langchain_websearch import WebSearchTool, WebContentsTool

tools = [WebSearchTool(num_results=5), WebContentsTool(extras_meta=True)]
# pass `tools` to your LangChain agent constructor
```

### Structured Access

For programmatic use, the backend returns `ContentResult` objects instead of a
formatted string:

```python
from langchain_websearch import QueritContentsBackend

backend = QueritContentsBackend()
for result in backend.fetch(["https://example.com"], extras_meta=True):
    print(result.status, result.url, len(result.content))
    if result.meta:
        print(result.meta.title, result.meta.site_name)
```

### Error Behavior

Request-level failures raise instead of being returned as text, so callers and
tests can tell success from failure:

- Missing API key, empty `urls`, or more than 10 URLs → `ValueError` (no HTTP request sent)
- Invalid `format` → `pydantic.ValidationError`
- HTTP 401 / 400 / 429 / 5xx → `requests.HTTPError`
- A single URL that cannot be crawled → not an exception; that entry gets `status="failed"`

## 🧪 Testing

To run tests with your API key:

```bash
export QUERIT_API_KEY="your-querit-api-key" && python3 -m pytest tests/
```

For verbose test output:

```bash
export QUERIT_API_KEY="your-querit-api-key" && python3 tests/test_basic.py
```

## ⚙️ Configuration

### Environment Variables

- `QUERIT_API_KEY`: Your Querit Search API key (required)

### WebSearchTool Parameters

- `num_results`: Number of results to return (default: 10, range: 1-50)
- `region`: Search region/language (default: "en-US", currently not used)
- `safe_search`: Enable safe search filtering (default: True, currently not used)

### WebContentsTool Parameters

- `format`: Output format, one of `"text"`, `"markdown"`, `"html"` (default: `"markdown"`)
- `crawl_timeout`: Per-page crawl timeout in seconds (default: 10, range: 1-60)
- `extras_meta`: Return title, site name, site icon and publish time (default: False)

## 📚 Documentation

For full API reference and examples, see the [examples directory](examples/).

### Example Usage

Check [`examples/basic_usage.py`](examples/basic_usage.py) for complete usage examples including LangChain agent integration.

For the Contents tool, [`examples/contents_usage.py`](examples/contents_usage.py) is a
runnable smoke test that reads `QUERIT_API_KEY` from the environment and exits
non-zero on failure:

```bash
export QUERIT_API_KEY="your-querit-api-key"
python3 examples/contents_usage.py
```

## 🔧 Development

### Development Setup

```bash
# Clone the repository
git clone https://github.com/querit-ai/langchain-querit.git
cd langchain-querit

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
export QUERIT_API_KEY="your-querit-api-key" && pytest tests/

# Run with coverage
export QUERIT_API_KEY="your-querit-api-key" && pytest --cov=src tests/

# Run specific test file
export QUERIT_API_KEY="your-querit-api-key" && python3 tests/test_basic.py
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development guidelines.

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute.

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

## 🔗 Links

- [Querit API Documentation](https://api.querit.ai/docs)
- [LangChain Documentation](https://python.langchain.com/docs/)
- [Issue Tracker](https://github.com/querit-ai/langchain-querit/issues)