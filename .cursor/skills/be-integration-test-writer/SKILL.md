---
name: be-integration-test-writer
description: Write integration tests for Python/FastAPI API endpoints. Use when creating tests that exercise the full HTTP request/response cycle, testing controllers and routes.
---

# Backend Integration Test Writer

Write comprehensive **integration tests** for Python/FastAPI API endpoints, testing the full HTTP request/response cycle.

## When to Use

- Creating tests for API endpoints (GET, POST, PUT, DELETE)
- Testing authentication and authorization flows
- Validating HTTP status codes and response formats
- Testing request validation and error responses
- End-to-end API workflow testing

## Framework & Tools

- **pytest** with **pytest-asyncio** for async test support
- **httpx.AsyncClient** for API endpoint testing
- **SQLite in-memory database** for isolated database tests

## Test File Organization

| Test Type | File Pattern | Purpose |
|-----------|--------------|---------|
| API tests | `test_api_*.py` | Endpoint integration, HTTP responses |

## Available Fixtures

Use these fixtures from `conftest.py` — do NOT recreate them:

```python
# HTTP client for API tests
async def test_api_example(client):
    # client is an httpx.AsyncClient configured for the app
    response = await client.get("/api/endpoint")
    pass

# Database session (for setup/verification)
async def test_with_db(db_session, client):
    # Use db_session for test data setup
    # Use client for API calls
    pass
```

## Test Structure Pattern

Follow the **AAA pattern** (Arrange, Act, Assert):

```python
class TestSettingsAPI:
    """Integration tests for Settings API endpoints."""

    @pytest.mark.asyncio
    async def test_create_setting_returns_201(self, client):
        """Test POST /api/settings creates setting and returns 201."""
        # Arrange
        payload = {
            "key": "test.setting",
            "category": "test",
            "value": "test_value",
            "value_type": "string",
        }
        
        # Act
        response = await client.post("/api/settings", json=payload)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["key"] == "test.setting"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_setting_not_found_returns_404(self, client):
        """Test GET /api/settings/{key} returns 404 for missing key."""
        # Act
        response = await client.get("/api/settings/nonexistent-key")
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
```

## Naming Conventions

- **Test files**: `test_api_<resource>.py` (e.g., `test_api_settings.py`, `test_api_users.py`)
- **Test classes**: `Test<Resource>API` (e.g., `TestSettingsAPI`, `TestUsersAPI`)
- **Test functions**: `test_<action>_<scenario>_returns_<status>` (e.g., `test_create_setting_returns_201`, `test_get_missing_returns_404`)

## Required Test Categories

For each endpoint, write tests covering:

1. **Success cases** — valid requests return correct status and data
2. **Not found (404)** — missing resources handled correctly
3. **Validation errors (422)** — invalid payloads rejected with clear errors
4. **Authentication (401/403)** — protected endpoints require valid credentials
5. **Edge cases** — empty payloads, boundary values, special characters

## Common HTTP Status Codes to Test

| Status | Scenario |
|--------|----------|
| 200 | Successful GET, PUT, PATCH |
| 201 | Successful POST (resource created) |
| 204 | Successful DELETE (no content) |
| 400 | Bad request (malformed JSON) |
| 401 | Unauthorized (missing/invalid auth) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Resource not found |
| 422 | Validation error (invalid payload) |
| 500 | Server error (should be rare in tests) |

## Test Data Isolation

Use unique identifiers to avoid test collisions:

```python
import uuid

def unique_id():
    """Generate a unique ID for test isolation."""
    return str(uuid.uuid4())[:8]

# Usage in API tests
payload = {"key": f"test.setting.{unique_id()}"}
```

## Testing Response Structure

Always validate response structure, not just status:

```python
@pytest.mark.asyncio
async def test_list_settings_returns_paginated_response(self, client):
    """Test GET /api/settings returns paginated list."""
    response = await client.get("/api/settings")
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate structure
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)
```

## Running Tests

```bash
cd backend
pytest -v                              # Run all tests
pytest -v tests/test_api_*.py          # Run API tests only
pytest -v tests/test_api_settings.py   # Run specific API test file
pytest -v -k "test_create"             # Run tests matching pattern
```

## Quality Checklist

- [ ] Each endpoint has at least one test per HTTP method
- [ ] Success and error responses are both tested
- [ ] Response status codes are validated
- [ ] Response body structure is validated
- [ ] Tests are independent and can run in any order
- [ ] No hardcoded IDs or values that could collide
- [ ] Every test has a docstring
- [ ] Async tests use `@pytest.mark.asyncio`

## Anti-Patterns to Avoid

- **Shared mutable state** between tests
- **Test interdependence** — tests that rely on other tests running first
- **Only testing happy paths** — always test error scenarios
- **Ignoring response body** — validate data, not just status codes
- **Flaky tests** — tests that sometimes pass, sometimes fail
