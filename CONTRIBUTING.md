# Contributing Guide

Thank you for your interest in contributing to LangChain WebSearch Tool!

## 🛠 Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/querit-ai/langchain-querit.git
cd langchain-querit
```

### 2. Install Dependencies

Requires Python 3.9 or newer.

```bash
pip install -e ".[dev]"
```

### 3. Set Up Environment Variables
```bash
export QUERIT_API_KEY="your-querit-api-key"
```

For permanent setup, add to your shell profile:
```bash
echo 'export QUERIT_API_KEY="your-querit-api-key"' >> ~/.bashrc  # or ~/.zshrc
source ~/.bashrc
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
export QUERIT_API_KEY="your-querit-api-key" && pytest tests/

# Run specific test file
export QUERIT_API_KEY="your-querit-api-key" && python3 tests/test_basic.py

# Run with coverage report
export QUERIT_API_KEY="your-querit-api-key" && pytest --cov=src tests/
```

### Test Types

1. **Unit Tests**
   - Test individual components
   - Located in `tests/` directory
   - Can be run without API key

2. **Integration Tests**
   - Test API interactions
   - Require valid API key
   - Test real Querit API calls

### Test Coverage
Ensure your changes maintain or improve test coverage:
```bash
export QUERIT_API_KEY="your-querit-api-key" && pytest --cov=src --cov-report=html tests/
```

## ?? Development Workflow

### 1. Create a New Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes
- Follow Python best practices
- Add type hints where appropriate
- Write comprehensive docstrings

### 3. Run Tests
```bash
export QUERIT_API_KEY="your-querit-api-key" && pytest
```

### 4. Check Code Quality
```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking (if available)
mypy src/
```

### 5. Commit Changes
```bash
git add .
git commit -m "feat: add your feature"
```

### 6. Push to GitHub
```bash
git push origin feature/your-feature-name
```

### 7. Create a Pull Request
- Provide clear description of changes
- Reference related issues
- Include test results

## 📝 Code Style Guidelines

### General Guidelines
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use meaningful variable and function names
- Keep functions small and focused

### Documentation
- Document all public APIs with docstrings
- Use Google-style docstrings
- Include examples for complex functions

### Type Hints
- Use type hints for function signatures
- Add type hints for return values
- Use `Optional` for nullable types

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Steps to Reproduce**
   - Clear, step-by-step instructions
   - Minimum code to reproduce

2. **Expected Behavior**
   - What you expected to happen

3. **Actual Behavior**
   - What actually happened
   - Error messages or stack traces

4. **Environment Details**
   - Python version
   - Package version
   - Operating system

## ✨ Feature Requests

When suggesting new features:

1. **Problem Description**
   - What problem are you trying to solve?

2. **Proposal**
   - How do you suggest solving it?

3. **Use Cases**
   - Example use cases

4. **Alternatives Considered**
   - Other approaches you considered

## 🏷️ Commit Message Format

Follow conventional commits format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test changes
- `chore:` for maintenance tasks
- `refactor:` for code refactoring

## 📊 Pull Request Checklist

- [ ] Tests pass
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Changelog updated (if needed)
- [ ] No breaking changes (or clearly documented)

## 🤝 Code of Conduct

Please be respectful and constructive in all interactions.

## ❓ Questions?

Open an issue or start a discussion for any questions about contributing.
