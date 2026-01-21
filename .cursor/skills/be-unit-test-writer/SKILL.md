---
name: be-unit-test-writer
description: Write unit tests for Python/FastAPI backend models and services. Use when creating tests for database models, service functions, or business logic that should be tested in isolation.
---

# Backend Unit Test Writer

Write comprehensive **unit tests** for Python/FastAPI backend code, focusing on models and services tested in isolation.

## When to Use

- Creating tests for SQLAlchemy models (constraints, relationships, validation)
- Testing service functions with mocked or isolated dependencies
- Writing tests for business logic that doesn't require HTTP layer
- Testing utility functions and helpers

## Framework & Tools

- **pytest** with **pytest-asyncio** for async test support
- **SQLite in-memory database** for isolated database tests
- **SQLAlchemy async sessions** for database operations

## Test File Organization

| Test Type | File Pattern | Purpose |
|-----------|--------------|---------|
| Model tests | `test_models_*.py` | Database layer, constraints, relationships |
| Service tests | `test_*_service.py` | Business logic, service functions |

## Available Fixtures

Use these fixtures from `conftest.py` — do NOT recreate them:

```python
# Database session for model and service tests
async def test_example(db_session):
    # db_session is an isolated AsyncSession
    pass

# Raw engine access (rarely needed)
async def test_engine_example(async_engine):
    pass
```

## Test Structure Pattern

Follow the **AAA pattern** (Arrange, Act, Assert):

```python
class TestSettingService:
    """Tests for Setting service functions."""

    @pytest.mark.asyncio
    async def test_create_setting_success(self, db_session):
        """Test create_setting creates and returns new setting."""
        # Arrange
        data = SettingCreate(
            key="new.setting",
            category="test",
            value="new_value",
            value_type="string",
        )
        
        # Act
        setting = await setting_service.create_setting(db_session, data)
        
        # Assert
        assert setting.id is not None
        assert setting.key == "new.setting"
        assert setting.value == "new_value"
```

## Naming Conventions

- **Test files**: `test_<module_name>.py`
- **Test classes**: `Test<EntityOrFeature>` (e.g., `TestSettingModel`, `TestSettingService`)
- **Test functions**: `test_<action>_<expected_result>` (e.g., `test_create_setting_success`, `test_get_setting_not_found`)

## Required Test Categories

For each feature, write tests covering:

1. **Happy path** — normal successful operations
2. **Not found / missing** — None returns, empty results
3. **Validation errors** — invalid input, constraint violations
4. **Edge cases** — empty lists, boundary values, special characters
5. **Idempotency** — operations that should be safe to repeat

## Test Data Isolation

Use unique identifiers to avoid test collisions:

```python
import uuid

def unique_id():
    """Generate a unique ID for test isolation."""
    return str(uuid.uuid4())[:8]

# Usage
category = f"test_category_{unique_id()}"
```

- Always clean up created test data or rely on transaction rollback.
- Never depend on data from other tests.

## Async Test Decorator

Always use the async marker for async tests:

```python
@pytest.mark.asyncio
async def test_async_operation(self, db_session):
    pass
```

## Docstrings

Every test function MUST have a docstring explaining what it tests:

```python
@pytest.mark.asyncio
async def test_delete_setting_not_found(self, db_session):
    """Test delete_setting returns False for missing key."""
    result = await setting_service.delete_setting(db_session, "nonexistent")
    assert result is False
```

## Running Tests

```bash
cd backend
pytest -v                              # Run all tests
pytest -v tests/test_models_*.py       # Run model tests
pytest -v tests/test_*_service.py      # Run service tests
pytest -v -k "test_create"             # Run tests matching pattern
```

## Quality Checklist

- [ ] Each public function has at least one test
- [ ] Error/exception paths are tested
- [ ] Edge cases are identified and tested
- [ ] Tests are independent and can run in any order
- [ ] No hardcoded IDs or values that could collide
- [ ] Descriptive test names that explain the scenario
- [ ] Every test has a docstring
- [ ] Async tests use `@pytest.mark.asyncio`

## Anti-Patterns to Avoid

- **Shared mutable state** between tests
- **Test interdependence** — tests that rely on other tests running first
- **Overly broad assertions** — `assert result` instead of specific checks
- **Missing negative tests** — only testing happy paths
- **Testing implementation details** — focus on behavior, not internals
