# Testing Guide

This document explains how to safely test the MathWizard web application without relying on manual clicking in Docker.

## Testing Options (Best to Use)

### 1. 🚀 Local Development Server (Fastest)

Run the app locally without Docker for rapid iteration:

```bash
./scripts/dev-local.sh
```

**Advantages:**
- Instant reload on code changes
- Faster startup (no Docker overhead)
- Direct access to your local data
- Easy debugging with print statements/breakpoints

**When to use:**
- Active development
- UI tweaks and styling
- Quick feature testing

---

### 2. ✅ Automated Tests (Most Safe)

Run automated tests that make HTTP requests to your app:

```bash
# Install dev dependencies (includes httpx for TestClient)
uv sync --group dev

# Run all web tests
uv run pytest tests/test_web/ -v

# Run specific test class
uv run pytest tests/test_web/test_routes.py::TestPracticeRoutes -v

# Run with coverage
uv run pytest tests/test_web/ --cov=exercise_finder.web
```

**Advantages:**
- Automated, repeatable tests
- Catches regressions automatically
- No manual clicking required
- Fast feedback loop
- Can run in CI/CD

**Test file location:**
- `tests/test_web/test_routes.py` - Route/endpoint tests

**When to use:**
- Before committing code
- Before deploying
- Continuous integration
- Regression testing

---

### 3. 🐳 Docker Testing (Pre-Deployment)

Test the exact container that will be deployed:

```bash
# Build and start
docker compose up

# Or rebuild if dependencies changed
docker compose build
docker compose up

# Stop
docker compose down
```

**Advantages:**
- Tests production environment
- Catches Docker-specific issues
- Validates deployment configuration

**When to use:**
- Final check before deployment
- Testing environment-specific behavior
- Validating Docker configuration

---

## Testing Workflow (Recommended)

### During Development

```bash
# 1. Start local dev server in one terminal
./scripts/dev-local.sh

# 2. Make changes to code
# 3. Browser auto-refreshes (if using live-reload extension)
# 4. Or manually refresh: http://localhost:8000
```

### Before Committing

```bash
# Run all tests
uv run pytest -xvs

# Or just web tests
uv run pytest tests/test_web/ -v
```

### Before Deploying

```bash
# 1. Run all tests
uv run pytest -xvs

# 2. Test in Docker
docker compose build
docker compose up

# 3. Manual smoke test at http://localhost:8000
# 4. Stop Docker
docker compose down

# 5. Deploy
./scripts/deploy.sh
```

---

## Writing New Tests

### Example: Test a New Practice Page

```python
# tests/test_web/test_routes.py

def test_new_topic_page_loads(self, client):
    """New topic page should load successfully."""
    with patch("exercise_finder.web.app.routes.practice.require_authentication"):
        response = client.get("/practice/newtopic")
        assert response.status_code == 200
        
        # Check content
        content = response.content.decode()
        assert "expected text" in content.lower()
```

### Example: Test API Endpoint

```python
def test_api_search_endpoint(self, client):
    """Search API should return results."""
    response = client.post(
        "/api/v1/search",
        json={"query": "test query"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
```

---

## Debugging Tips

### Check Logs

```bash
# Local server logs
# Output is in your terminal

# Docker logs
docker compose logs -f

# Or for a specific container
docker compose logs -f app
```

### Interactive Debugging

When running locally (`./scripts/dev-local.sh`), you can use:

```python
# In your route handler
import pdb; pdb.set_trace()
```

Or use your IDE's debugger:
- VSCode: Set breakpoint, run "Python: Debug"
- PyCharm: Set breakpoint, run debug configuration

---

## Common Issues

### Issue: Tests fail with "ModuleNotFoundError"

**Solution:**
```bash
# Sync dev dependencies
uv sync --group dev
```

### Issue: Local server can't find templates

**Solution:**
Make sure you're running from the project root:
```bash
cd /path/to/exercise_finder
./scripts/dev-local.sh
```

### Issue: Docker container missing dependencies

**Solution:**
```bash
# Rebuild the image
docker compose build
docker compose up
```

### Issue: Port 8000 already in use

**Solution:**
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9

# Or use a different port
uv run uvicorn exercise_finder.web.app:app_factory --factory --reload --port 8001
```

---

## CI/CD Integration

Add to your CI pipeline (GitHub Actions example):

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install uv
          uv sync --group dev
      
      - name: Run tests
        run: uv run pytest -xvs
```

---

## Summary

**Don't rely on manual Docker testing!**

Instead:
1. **Develop** with `./scripts/dev-local.sh`
2. **Test** with `uv run pytest tests/test_web/`
3. **Verify** with Docker before deploying

This workflow is:
- ✅ Faster
- ✅ Safer
- ✅ More maintainable
- ✅ Automatable

