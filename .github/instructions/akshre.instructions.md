---
description: This rule provides guidelines for building data providers using akshare library for LlamaIndex FunctionTool. Refer to this rule when writing code in the `data_provider/` folder.
applyTo: "data_provider/**/*.py"
---
# Data Provider Guide for GitHub Copilot

This guide covers building data providers using akshare library for LlamaIndex FunctionTool.


You are an expert in Python, writing a scalable API wrapper with the akshare library for use with LlamaIndex FunctionTool.

**IMPORTANT: After writing any function in `data_provider`, you MUST create corresponding test cases in `tests/unit/`. See "Testing Requirements" section below for details.**

Key Principles

- Write concise, technical responses with accurate Python examples.
- Use functional, declarative programming; avoid classes where possible.
- Prefer iteration and modularization over code duplication.
- Use descriptive variable names with auxiliary verbs (e.g., is_active, has_permission).
- Use lowercase with underscores for directories and files (e.g., `data_provider/stock.py`, `data_provider/fund.py`).
- Favor named exports for routes and utility functions.
- Use the Receive an Object, Return an Object (RORO) pattern.
- Manage runtime within python virtual environment, this has been already included in the @.venv folder.
- Manage dependencies with uv, there is one [pyproject.toml] in the codebase.
- Always run python command under virtual environment by activating virtual environment with `source venv/bin/activate`

FunctionTool Compatibility Requirements

**CRITICAL: All functions in `data_provider` must be compatible with LlamaIndex `FunctionTool.from_defaults()`.**

1. **Type Hints**: All function parameters and return types MUST have complete type hints.
   - Use `str`, `int`, `float`, `bool` for primitive types
   - Use `dict[str, Any]` or `list[dict[str, Any]]` for complex return types
   - Use `Optional[T]` or `T | None` for nullable types
   - Avoid returning raw `pandas.DataFrame` - convert to dict/list first

2. **Docstring Format**: Use Google-style docstrings with clear descriptions:

   ```python
   def get_stock_info(symbol: str) -> dict[str, Any] | None:
       """Get basic information about a stock by its symbol.

       Args:
           symbol: Stock symbol (e.g., "000001" for A-shares, "AAPL" for US stocks)

       Returns:
           Optional[Dict[str, Any]]: Dictionary containing stock information.
           Returns None if the symbol is not found or API request fails.
       """
   ```

3. **Return Value Serialization**:
   - **NEVER return pandas.DataFrame directly** - FunctionTool needs JSON-serializable data
   - Convert DataFrame to dict: `df.to_dict(orient="records")` for list of dicts, or `df.to_dict()` for nested dict
   - For single-row results: `dict(zip(df.columns, df.iloc[0]))` or `df.iloc[0].to_dict()`
   - Return `None` instead of empty DataFrame/empty dict when no data found

4. **Error Handling Pattern**:

   ```python
   def get_data(param: str) -> dict[str, Any] | None:
       """Function description."""
       try:
           df = ak.some_api(symbol=param)
           if df.empty:
               return None
           # Convert to dict
           return df.iloc[0].to_dict()
       except Exception as e:
           logger.error(f"Error fetching data for {param}: {str(e)}")
           return None
   ```

5. **Function Naming**:
   - Use descriptive names: `get_stock_info`, `get_fund_performance`, `get_stock_realtime_quote`
   - Prefix with `get_` for data retrieval functions
   - Use clear, domain-specific names (stock, fund, bond, etc.)

Error Handling and Validation

- Prioritize error handling and edge cases:
  - Handle errors and edge cases at the beginning of functions.
  - Use early returns for error conditions to avoid deeply nested if statements.
  - Place the happy path last in the function for improved readability.
  - Avoid unnecessary else statements; use the if-return pattern instead.
  - Use guard clauses to handle preconditions and invalid states early.
  - Implement proper error logging and user-friendly error messages.
  - Use custom error types or error factories for consistent error handling.
  - Always return `None` on error (don't raise exceptions) - let the agent handle error responses
  - Log errors using `logger.error()` or `logger.exception()` for debugging

Python/Akshare Integration

- **API Documentation**: Refer to [akshare documentation](https://akshare.akfamily.xyz/data/index.html) as the API documentation.
  - **Stock Functions**: Reference [akshare stock documentation](https://akshare.akfamily.xyz/data/stock/stock.html) and its sub-pages for stock-related function implementations.
  - **Fund Functions**: Reference [akshare fund documentation](https://akshare.akfamily.xyz/data/fund/fund_public.html) and its sub-pages for fund-related function implementations.
- **Function Verification**: Before using any akshare function, verify it exists in the current SDK version:
  - Use `uv run python -c "import akshare as ak; print(dir(ak))"` to list all available functions
  - Use `uv run python -c "import akshare as ak; help(ak.function_name)"` to check function signature and parameters
  - Use `uv run python -c "import akshare as ak; print(hasattr(ak, 'function_name'))"` to verify function existence
  - Always test function availability before implementing wrapper functions
  - Example: `uv run python -c "import akshare as ak; print(hasattr(ak, 'stock_individual_info_em'))"`
- **Function Types**: Use `def` for pure functions (akshare APIs are synchronous).
- **Type Hints**: Use type hints for all function signatures. Prefer Pydantic models over raw dictionaries for input validation when complex validation is needed.
- **Import Pattern**: Import akshare as `import akshare as ak  # type: ignore`
- **Import pandas**: Always import pandas for DataFrame operations: `import pandas as pd`

Finding and Verifying Akshare Functions

**CRITICAL: Always verify akshare function availability before implementing wrapper functions.**

1. **Check Function Existence**:

   ```bash
   # List all available functions
   uv run python -c "import akshare as ak; print([x for x in dir(ak) if not x.startswith('_')])"

   # Check if specific function exists
   uv run python -c "import akshare as ak; print(hasattr(ak, 'stock_individual_info_em'))"

   # Get function signature and help
   uv run python -c "import akshare as ak; help(ak.stock_individual_info_em)"
   ```

2. **Reference Official Documentation**:
   - **Stock Functions**: Browse and reference [akshare stock documentation](https://akshare.akfamily.xyz/data/stock/stock.html) and all its sub-pages
     - Check function names, parameters, and return formats
     - Understand data structure and column names
     - Note any required parameters or optional parameters
   - **Fund Functions**: Browse and reference [akshare fund documentation](https://akshare.akfamily.xyz/data/fund/fund_public.html) and all its sub-pages
     - Check function names, parameters, and return formats
     - Understand data structure and column names
     - Note any required parameters or optional parameters

3. **Test Function Before Implementation**:

   ```bash
   # Test function call with sample parameters
   uv run python -c "import akshare as ak; import pandas as pd; df = ak.stock_individual_info_em(symbol='000001'); print(df.head())"
   ```

4. **Function Naming Pattern**:
   - Akshare functions follow naming patterns like `stock_*`, `fund_*`, `bond_*`, etc.
   - Use documentation to find the exact function name matching your needs
   - Prefer functions that return structured data (DataFrame) over raw HTML/JSON

Data Provider Module Structure

- **File Organization**:
  - `data_provider/stock.py`: Stock-related functions (A-shares, US stocks, etc.)
  - `data_provider/fund.py`: Fund-related functions (already exists)
  - `data_provider/common_util.py`: Shared utility functions
  - `data_provider/__init__.py`: Export all public functions

- **Export Pattern**: Export functions in `__init__.py`:

  ```python
  from .stock import get_stock_info, get_stock_realtime_quote
  from .fund import get_fund_info, get_fund_performance

  __all__ = [
      "get_stock_info",
      "get_stock_realtime_quote",
      "get_fund_info",
      "get_fund_performance",
  ]
  ```

Example: Stock Data Function

```python
"""Stock data provider functions using akshare."""

import logging
from typing import Any

import akshare as ak  # type: ignore
import pandas as pd

logger = logging.getLogger(__name__)


def get_stock_info(symbol: str) -> dict[str, Any] | None:
    """Get basic information about a stock by its symbol.

    Args:
        symbol: Stock symbol (e.g., "000001" for A-shares, "AAPL" for US stocks)

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing stock information with keys:
            - 股票代码: Stock code
            - 股票名称: Stock name
            - 当前价格: Current price
            - 涨跌幅: Price change percentage
        Returns None if the symbol is not found or API request fails.

    Example:
        info = get_stock_info("000001")
        if info:
            print(f"Stock Name: {info['股票名称']}")
    """
    try:
        df = ak.stock_individual_info_em(symbol=symbol)

        if df.empty:
            logger.warning(f"No data found for stock symbol: {symbol}")
            return None

        # Convert DataFrame to dict (first row)
        result = dict(zip(df["item"], df["value"], strict=False))
        return result

    except Exception as e:
        logger.exception(f"Error fetching stock info for {symbol}: {str(e)}")
        return None


def get_stock_realtime_quote(symbol: str) -> dict[str, Any] | None:
    """Get real-time quote for a stock.

    Args:
        symbol: Stock symbol (e.g., "000001")

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing real-time quote data.
        Returns None if the symbol is not found or API request fails.
    """
    try:
        df = ak.stock_zh_a_spot_em()

        if df.empty:
            return None

        # Filter by symbol
        stock_data = df[df["代码"] == symbol]

        if stock_data.empty:
            logger.warning(f"Stock symbol {symbol} not found in real-time data")
            return None

        # Convert first matching row to dict
        return stock_data.iloc[0].to_dict()

    except Exception as e:
        logger.exception(f"Error fetching real-time quote for {symbol}: {str(e)}")
        return None
```

Example: Fund Data Function (Reference Implementation)

See `data_provider/fund.py` for reference implementation. Key points:

- Returns `dict[str, Any] | None` for single-record results
- Returns `pd.DataFrame | None` for multi-record results (but consider converting to list of dicts for FunctionTool compatibility)
- Proper error handling with try-except
- Clear docstrings with Args and Returns sections

Best Practices for FunctionTool Integration

1. **Keep functions pure**: No side effects, no global state modifications
2. **Idempotent operations**: Same input should produce same output
3. **Clear parameter names**: Use descriptive names that match domain terminology
4. **Comprehensive docstrings**: Help the LLM understand when to call the function
5. **Consistent return types**: Use `dict[str, Any] | None` or `list[dict[str, Any]] | None` consistently
6. **Handle edge cases**: Empty results, invalid inputs, API failures
7. **Logging**: Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)
8. **Type safety**: Use type hints everywhere, enable mypy checking

Testing Requirements

**CRITICAL: Every function in `data_provider` MUST have corresponding test cases in `tests/unit/`.**

1. **Test File Location and Naming**:
   - Test files must be placed in `tests/unit/` directory
   - Test file naming: `test_<module_name>.py` (e.g., `test_data_provider.py` for `data_provider/` module)
   - If testing specific module: `test_stock.py` for `data_provider/stock.py`, `test_fund.py` for `data_provider/fund.py`

2. **Test File Structure**:

   ```python
   """Test cases for the data provider module."""

   import pytest

   import pandas as pd

   from data_provider import get_stock_info, get_fund_info


   def test_get_stock_info_success():
       """Test successful retrieval of stock information with expected structure."""
       result = get_stock_info("000001")

       # Check if result is not None (API call succeeded)
       if result is not None:
           # Check expected keys in the result dictionary
           expected_keys = [
               "股票代码",
               "股票简称",
           ]
           for key in expected_keys:
               assert key in result, f"Expected key '{key}' not found in result"
               assert result[key] is not None, f"Key '{key}' should not be None"

           # Check that result is a dictionary
           assert isinstance(result, dict)
           # Check that dictionary is not empty
           assert len(result) > 0


   def test_get_stock_info_invalid_code():
       """Test handling of invalid stock code."""
       result = get_stock_info("000001")
       # Result can be None for invalid codes, or empty dict structure
       assert result is None or isinstance(result, dict)
   ```

3. **Test Approach - CRITICAL RULES**:

   **DO NOT MOCK THE API**: All tests MUST call the actual akshare API directly. Never use `unittest.mock.patch` or any mocking framework to mock akshare API calls.

   **TEST DATA STRUCTURES ONLY**: Tests should verify the structure of returned data, not specific values:
   - Check for expected keys in dictionaries
   - Check for expected columns in DataFrames
   - Verify data types (dict, list, str, int, float, etc.)
   - Verify that results are not empty when data is available
   - Do NOT assert specific values (e.g., `assert result["股票代码"] == "000001"`)

   **USE STANDARD TEST SYMBOLS**:
   - Stock symbols: Use `"000001"` for testing
   - Fund symbols: Use `"000001"` for testing
   - Index symbols: Use `"000001"` for testing
   - These symbols are used for structure validation, not value validation

4. **Required Test Cases** (at minimum):

   - **Success case**: Test with valid input (use `"000001"`) and verify correct output structure (keys, columns, data types)
   - **Invalid input**: Test with the same symbol `"000001"` to verify error handling (should return `None` or handle gracefully)
   - Note: Since we're calling real APIs, we don't test empty results or API errors separately - the function's error handling will naturally handle these cases

5. **Test Best Practices**:

   - **Call real akshare API**: Make actual API calls, do not mock
   - **Structure validation only**: Check for expected keys/columns and data types
   - Use descriptive test function names: `test_<function_name>_<scenario>`
   - Add docstrings to test functions explaining what is being tested
   - Verify return type: Check that functions return expected types (`dict[str, Any] | None`, `list[dict[str, Any]] | None`, `pd.DataFrame | None`)
   - Verify structure: Check that dictionaries have expected keys, lists contain dictionaries with expected keys, DataFrames have expected columns
   - Use conditional checks: Use `if result is not None:` before checking structure to handle cases where API returns None
   - Use `assert` statements with clear messages

6. **Example Test Patterns**:

   ```python
   def test_get_stock_info_success():
       """Test successful retrieval of stock information with expected structure."""
       result = get_stock_info("000001")

       if result is not None:
           # Check expected keys
           expected_keys = ["股票代码", "股票简称"]
           for key in expected_keys:
               assert key in result, f"Expected key '{key}' not found"
           assert isinstance(result, dict)
           assert len(result) > 0


   def test_get_fund_list_success():
       """Test successful retrieval of fund list with expected structure."""
       result = get_fund_list()

       if result is not None:
           assert isinstance(result, list)
           assert len(result) > 0
           if len(result) > 0:
               first_item = result[0]
               assert isinstance(first_item, dict)
               assert "基金代码" in first_item


   def test_get_fund_performance_success():
       """Test successful retrieval of fund performance with expected structure."""
       result = get_fund_performance("000001")

       if result is not None:
           assert isinstance(result, pd.DataFrame)
           assert not result.empty
           expected_columns = ["业绩类型", "周期"]
           for col in expected_columns:
               assert col in result.columns, f"Expected column '{col}' not found"
   ```

7. **Running Tests**:

   - Run all tests: `uv run pytest tests/unit/ -v`
   - Run specific test file: `uv run pytest tests/unit/test_stock.py -v`
   - Run specific test function: `uv run pytest tests/unit/test_stock.py::test_get_stock_info_success -v`
   - Run with coverage: `uv run pytest tests/unit/ --cov=data_provider --cov-report=html`

8. **Test Coverage Requirements**:

   - Aim for at least 80% code coverage for `data_provider` module
   - All public functions must have tests
   - Test both success paths (when data is available) and error handling paths
   - Test edge cases (different parameter combinations, optional parameters)

9. **Integration with CI/CD**:

   - Tests should pass before code is merged
   - Use `uv run pytest` command (not `pytest` directly)
   - Tests make real API calls, so they may take longer than mocked tests
   - Tests verify data structure, making them resilient to API data changes
