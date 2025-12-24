---
applyTo: tests/**/*
description: This rule is helpful for building project in python, you should refer to this rule when you found yourself writing python test code.
---
# Python Testing Guide for GitHub Copilot

This guide covers writing test cases in Python with pytest for the FinWeave project.

## Key Principles

- Write concise, technical responses with accurate Python examples.
- Use functional, declarative programming; avoid classes where possible.
- Prefer iteration and modularization over code duplication.
- Use descriptive variable names with auxiliary verbs (e.g., is_active, has_permission).
- Use lowercase with underscores for directories and files (e.g., routers/user_routes.py).
- Favor named exports for routes and utility functions.
- Manage dependencies with pip, there is one @requirements.txt in the codebase.
- Always run python command under virtual environment by activating virtual environment with `source venv/bin/activate`
- Cover the golden path and corner cases of the function you want to test.

## How to run the test?

You should always run the test for your code. You can run the following commands to verify:

```bash
uv run python -m pytest tests/ -v
```

## Test File Organization

- **Unit tests**: Place in `tests/unit/` directory
- **Integration tests**: Place in `tests/integration/` directory
- **Test data**: Store test data files in `tests/data/`
- **Test file naming**: Must match patterns `test_*.py` or `*_test.py`

## Test Structure

### Basic Test Pattern

```python
"""Test cases for the module."""

import pytest
from module import function_to_test


def test_function_success():
    """Test successful execution with valid input."""
    result = function_to_test("valid_input")

    assert result is not None
    assert isinstance(result, dict)
    # Add more specific assertions


def test_function_invalid_input():
    """Test handling of invalid input."""
    result = function_to_test("invalid_input")

    assert result is None  # or appropriate error handling
```

### Testing with Fixtures

```python
import pytest


@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {
        "key1": "value1",
        "key2": "value2"
    }


def test_with_fixture(sample_data):
    """Test using fixture data."""
    assert "key1" in sample_data
    assert sample_data["key1"] == "value1"
```

### Testing Async Functions

```python
import pytest


@pytest.mark.asyncio
async def test_async_function():
    """Test async function execution."""
    result = await async_function()
    assert result is not None
```

## Test Coverage Requirements

- Aim for at least 80% code coverage
- All public functions must have tests
- Test both success paths and error handling paths
- Test edge cases (empty inputs, boundary conditions, etc.)

## Best Practices

1. **Descriptive test names**: Use clear, descriptive names that explain what is being tested
   - Pattern: `test_<function_name>_<scenario>`
   - Example: `test_get_stock_info_success`, `test_get_stock_info_invalid_code`

2. **Docstrings**: Add docstrings to test functions explaining what is being tested
   ```python
   def test_function_success():
       """Test successful execution with valid input and expected output."""
   ```

3. **Assertions with messages**: Use clear assertion messages
   ```python
   assert key in result, f"Expected key '{key}' not found in result"
   ```

4. **Arrange-Act-Assert pattern**:
   ```python
   def test_function():
       # Arrange: Set up test data
       input_data = "test"

       # Act: Execute function
       result = function(input_data)

       # Assert: Verify results
       assert result is not None
   ```

5. **Test one thing at a time**: Each test should focus on a single scenario

6. **Avoid test interdependencies**: Tests should be independent and runnable in any order

7. **Use parameterized tests** for multiple similar test cases:
   ```python
   @pytest.mark.parametrize("input,expected", [
       ("input1", "output1"),
       ("input2", "output2"),
       ("input3", "output3"),
   ])
   def test_function_parametrized(input, expected):
       assert function(input) == expected
   ```

## Running Tests

### Run all tests
```bash
uv run pytest tests/ -v
```

### Run specific test directory
```bash
uv run pytest tests/unit/ -v
uv run pytest tests/integration/ -v
```

### Run specific test file
```bash
uv run pytest tests/unit/test_stock.py -v
```

### Run specific test function
```bash
uv run pytest tests/unit/test_stock.py::test_get_stock_info_success -v
```

### Run with coverage
```bash
uv run pytest tests/unit/ --cov=module_name --cov-report=html
```

## Common Test Patterns

### Testing Return Types

```python
def test_function_return_type():
    """Test that function returns correct type."""
    result = function()

    assert isinstance(result, dict)
    assert isinstance(result, list)
    assert isinstance(result, str)
```

### Testing Dictionary Structure

```python
def test_function_dict_structure():
    """Test that returned dictionary has expected keys."""
    result = function()

    if result is not None:
        expected_keys = ["key1", "key2", "key3"]
        for key in expected_keys:
            assert key in result, f"Expected key '{key}' not found"
            assert result[key] is not None, f"Key '{key}' should not be None"
```

### Testing List Contents

```python
def test_function_list_contents():
    """Test that returned list has expected structure."""
    result = function()

    if result is not None:
        assert isinstance(result, list)
        assert len(result) > 0

        if len(result) > 0:
            first_item = result[0]
            assert isinstance(first_item, dict)
            assert "key" in first_item
```

### Testing Error Handling

```python
def test_function_error_handling():
    """Test that function handles errors gracefully."""
    result = function("invalid_input")

    # Function should return None on error
    assert result is None

    # Or function should raise specific exception
    with pytest.raises(ValueError):
        function("invalid_input")
```

### Testing with Mocks (when needed)

```python
from unittest.mock import Mock, patch


def test_function_with_mock():
    """Test function using mocks for external dependencies."""
    with patch('module.external_function') as mock_external:
        mock_external.return_value = "mocked_value"

        result = function()

        assert result == "expected_result"
        mock_external.assert_called_once()
```

## Testing Data Provider Functions

For data provider functions (like those using akshare), follow these special guidelines:

1. **Call real APIs**: Don't mock API calls for data providers
2. **Test structure, not values**: Verify data structure, not specific values
3. **Use conditional checks**: Handle cases where API might return None
4. **Standard test symbols**: Use `"000001"` for testing Chinese stocks/funds

Example:
```python
def test_get_stock_info_success():
    """Test successful retrieval of stock information with expected structure."""
    result = get_stock_info("000001")

    if result is not None:
        expected_keys = ["股票代码", "股票简称"]
        for key in expected_keys:
            assert key in result, f"Expected key '{key}' not found"
        assert isinstance(result, dict)
        assert len(result) > 0
```

## Common Pitfalls to Avoid

- ❌ Don't hardcode specific values in assertions (test structure, not data)
- ❌ Don't create tests that depend on external state
- ❌ Don't create tests that are too broad (test one thing at a time)
- ❌ Don't forget to test error cases and edge cases
- ❌ Don't use `pytest` command directly (use `uv run pytest` instead)

## Integration with CI/CD

- Tests should pass before code is merged
- Use `uv run pytest` command (not `pytest` directly)
- Run tests with coverage reporting in CI pipeline
- Fail build if coverage drops below threshold
