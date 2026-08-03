# GitHub Actions for LangChain WebSearch Tool

This directory contains GitHub Actions workflows for automated testing, building, and publishing of the LangChain WebSearch Tool package.

## 📋 Available Workflows

### 1. `publish.yml` - Main publishing workflow
- **Triggers:** On new GitHub releases or manual dispatch
- **Jobs:**
  - `test`: Runs tests on multiple Python versions (3.9-3.11)
  - `deploy`: Builds and publishes to PyPI
  - `release-docs`: Updates documentation
  - `notify`: Success/failure notifications

## 🔧 Required Secrets

You need to set up the following secrets in your GitHub repository:

### 1. PyPI Publishing
For automatic publishing to PyPI, use **Trusted Publishing** (recommended) or API tokens:

**Option A: Trusted Publishing (Recommended)**
1. Enable PyPI Trusted Publishing for your project
2. No secrets needed - uses OpenID Connect

**Option B: API Token (Legacy)**
```bash
GITHUB Secrets to add:
- PYPI_API_TOKEN: Your PyPI API token
- TEST_PYPI_API_TOKEN: (Optional) Test PyPI API token
```

### 2. Testing Secrets (Optional but Recommended)
```bash
GITHUB Secrets to add:
- QUERIT_API_KEY: Your Querit Search API key
- CODECOV_TOKEN: Codecov token for coverage reporting
```

## 🚀 Setting Up Secrets

### Using GitHub Web Interface:
1. Go to your repository on GitHub
2. Click "Settings" → "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Add each secret with its name and value

### Using GitHub CLI:
```bash
gh secret set QUERIT_API_KEY --body "your-querit-api-key"
gh secret set PYPI_API_TOKEN --body "pypi-your-api-token"
```

## ⚙️ Manual Trigger

You can manually trigger the workflow:
1. Go to "Actions" tab
2. Select "Publish Python Package"
3. Click "Run workflow"

## 📊 Test Configuration

The workflow includes:
- Python 3.9, 3.10, 3.11 testing
- Code formatting (black)
- Linting (flake8)
- Type checking (mypy)
- Real API tests (if `QUERIT_API_KEY` is provided)
- Code coverage reporting

## 🛡️ Safety Features

1. **No secrets in logs:** Secrets are never printed in workflow logs
2. **Conditional real API tests:** Real API tests only run if API key is provided
3. **Version validation:** Verifies package can be imported after building
4. **Distribution validation:** Uses `twine check` to validate packages

## 🔍 Debugging

If the workflow fails:
1. Check the specific job that failed
2. Review logs for error messages
3. Ensure all required secrets are set
4. Verify version in setup.py matches expectations

## 📈 Release Process

1. Update version in `setup.py`
2. Update `CHANGELOG.md`
3. Create a new GitHub release
4. The workflow automatically:
   - Runs tests
   - Builds distributions
   - Publishes to PyPI
   - Notifies on completion

## 🔗 Useful Links

- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)
- [Python Packaging User Guide](https://packaging.python.org/en/latest/)