# 🚀 PyPI Publishing Configuration Guide - Two Methods Explained

This guide provides detailed instructions on how to configure your project to automatically publish to PyPI from GitHub Actions. You can choose one of two methods:

## 📋 **Method 1: PyPI Trusted Publishing (Recommended, More Secure)**

### ✅ **Advantages**
- No API token configuration required
- Uses OpenID Connect (OIDC) for authentication
- Native integration with GitHub Actions
- More secure, no risk of permanent token leakage

### 🔧 **Configuration Steps**

#### **1. Create PyPI Project**
1. Visit https://pypi.org/
2. Log in to your account (or register for a new account)
3. If the project doesn't exist, it will be automatically created during the first publication

#### **2. Configure PyPI Trusted Publisher**
1. After logging into PyPI, click on your account in the upper right corner -> "PyPI publishing" (or in project settings)
2. Select "Add a new trusted publisher"
3. Fill in the following information:
   - **GitHub Actions workflow file**: `.github/workflows/publish.yml`
   - **Repository**: `querit-ai/langchain-querit`
   - **Workflow name**: Leave blank or fill in the complete workflow path
4. Click "Add trusted publisher"

#### **3. Verify PyPI Configuration**
1. The newly created Trusted Publisher will appear in the list
2. Status should be "Active" or "Pending first use"
3. Ensure the following information is correct:
   - GitHub repository: `querit-ai/langchain-querit`
   - Workflow file: `.github/workflows/publish.yml`

### 🛡️ **Security Features**
- Generates temporary tokens for each publication, automatically expires
- Tokens are only valid during runtime
- Cannot be reused or leaked
- No need to store any tokens in GitHub Secrets

---

## 📋 **Method 2: Traditional API Token Method (Backup)**

### ⚠️ **Note: Trusted Publishing Recommended**
Use this method only when Trusted Publishing is not available

### 🔧 **Configuration Steps**

#### **1. Create PyPI API Token**
1. Log in to https://pypi.org/manage/account/
2. Click "API tokens" in the bottom left
3. Click "Add API token"
4. Configure the token:
   - **Token name**: `langchain-querit-github`
   - **Scope**: Project-specific (Select "langchain-querit" project)
   - **Scope specifics**: Entire project
5. Click "Create token"
6. **⚠️ Copy the token immediately (displayed only once)**

#### **2. Configure GitHub Secrets**
1. In GitHub repository -> Settings -> Secrets and variables -> Actions
2. Click "New repository secret"
3. Add the following Secret:
   - **Name**: `PYPI_API_TOKEN`
   - **Value**: Paste the API token copied from PyPI

#### **3. Modify Workflow Configuration**
If you choose the API Token method, you need to change from Trusted Publishing to Token method in `publish.yml`:

```yaml
# Change from:
- uses: pypa/gh-action-pypi-publish@release/v1
  with:
    verbose: true
    repository-url: https://upload.pypi.org/legacy/

# To:
- uses: pypa/gh-action-pyi-publish@release/v1
  with:
    user: __token__
    password: ${{ secrets.PYPI_API_TOKEN }}
    repository-url: https://upload.pypi.org/legacy/
```

---

## 🎯 **Current Configuration (Trusted Publishing Recommended)**

Your current workflow `publish.yml` is already configured for:

### ✅ **Trusted Publishing Configuration**
```yaml
environment:
  name: pypi
  url: https://pypi.org/p/langchain-querit
  
permissions:
  id-token: write  # Required for Trusted Publishing

steps:
  - name: Publish to PyPI
    uses: pypa/gh-action-pypi-publish@release/v1
    with:
      verbose: true
      repository-url: https://upload.pypi.org/legacy/
```

### ✅ **Workflow Includes:**
1. **Multi-Python version testing** (3.9-3.11)
2. **Code quality checks** (black, flake8, mypy)
3. **Package build verification**
4. **Conditional publishing** (only main branch and release triggers)
5. **Publishing notifications**

---

## 🚀 **Publishing Process**

### **Publishing Steps:**
1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Release v0.0.2: Complete publishing configuration"
   git push origin main
   ```

2. **Create GitHub Release**
   - Visit the "Releases" tab on the repository page
   - Click "Create a new release"
   - Tag: `v0.0.2`
   - Title: `LangChain Querit Tool v0.0.2`
   - Description: Copy from `CHANGELOG.md`
   - Click "Publish release"

3. **Automatic triggering process**
   - GitHub Actions runs automatically
   - Identity verification via Trusted Publishing
   - Build and publish to PyPI

---

## 🔍 **Verify Publishing Success**

### **1. Check GitHub Actions**
- Go to the repository's "Actions" tab
- View the "Publish Python Package" workflow
- All jobs should show ✅ (green passed)

### **2. Verify PyPI Publication**
```bash
# Test installation
pip install langchain-querit==0.0.2

# Verification
python -c "from langchain_websearch import __version__; print(f'Version {__version__} installed')"
```

### **3. View PyPI Page**
- Visit https://pypi.org/project/langchain-querit/
- Confirm version 0.0.2 is displayed
- Ensure package information is complete

---

## 🛡️ **Security Recommendations**

### **Add extra security layer for Trusted Publishing (Optional):**
1. **Create GitHub Environment**
   ```yaml
   environment:
     name: pypi
     url: https://pypi.org/p/langchain-querit
   ```

2. **Configure Environment Protection Rules**
   - Repository Settings -> Environments -> "pypi"
   - Enable "Required reviewers"
   - Add your GitHub account as reviewer

3. **Add Conditions to Workflow**
   ```yaml
   - name: Publish to PyPI
     if: github.event_name == 'release' && github.ref == 'refs/heads/main'
   ```

---

## ❌ **Troubleshooting**

### **Common Issue 1: Trusted Publishing Failure**
**Symptom**: "Invalid OIDC identity" error
**Solution**:
1. Confirm PyPI Trusted Publisher configuration is correct
2. Ensure repository and workflow names match
3. Check GitHub Actions has `id-token: write` permission

### **Common Issue 2: Version Already Exists**
**Symptom**: "File already exists" error
**Solution**:
1. PyPI doesn't allow duplicate version numbers
2. Update version (e.g., 0.2.1) and republish
3. Or delete old version on PyPI (if needed)

### **Common Issue 3: Insufficient Permissions**
**Symptom**: "Forbidden" or "Unauthorized"
**Solution**:
1. Confirm PyPI account has permission to publish to this project
2. Check API token scope is correct (entire project)
3. Token may have expired, regenerate

---

## 📞 **Support Resources**

1. **PyPI Trusted Publishing Documentation**
   - https://docs.pypi.org/trusted-publishers/

2. **GitHub Actions OIDC Configuration**
   - https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect

3. **pypa/gh-action-pypi-publish**
   - https://github.com/pypa/gh-action-pypi-publish

4. **Python Packaging Guide**
   - https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/

---

## ✅ **Recommended Configuration Summary**

For your **langchain-querit** project, **PyPI Trusted Publishing is strongly recommended** because:

1. **Already configured** - Workflow is already set up for Trusted Publishing
2. **More secure** - No risk of long-term token storage
3. **Zero configuration** - No need to manage GitHub Secrets
4. **Best practice compliant** - Officially recommended by PyPI

Just configure the Trusted Publisher once on PyPI, and all subsequent publications will be automatic!

**Next Steps**:
1. Configure PyPI following "Method 1: PyPI Trusted Publishing"
2. Create a GitHub Release to trigger publishing
3. Verify publishing success

> Publication Date: 2026-02-26  
> Version: v0.0.2  
> Configuration Status: Trusted Publishing configuration completed ✅