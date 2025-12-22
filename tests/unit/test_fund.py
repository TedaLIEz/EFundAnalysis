"""Test cases for fund data provider functions."""


import pandas as pd

from data_provider.fund import (
    get_fund_info,
    get_fund_individual_detail_info,
    get_fund_list,
    get_fund_net_value,
    get_fund_performance,
    get_fund_portfolio,
)


def test_get_fund_info_success():
    """Test successful retrieval of fund information with expected structure."""
    result = get_fund_info("000001")

    # Check if result is not None (API call succeeded)
    if result is not None:
        # Check expected keys in the result dictionary
        expected_keys = [
            "基金代码",
            "基金名称",
        ]
        for key in expected_keys:
            assert key in result, f"Expected key '{key}' not found in result"
            assert result[key] is not None, f"Key '{key}' should not be None"

        # Check that result is a dictionary
        assert isinstance(result, dict)
        # Check that dictionary is not empty
        assert len(result) > 0


def test_get_fund_info_invalid_code():
    """Test handling of invalid fund code."""
    result = get_fund_info("000001")
    # Result can be None for invalid codes, or empty dict structure
    assert result is None or isinstance(result, dict)


def test_get_fund_individual_detail_info_success():
    """Test successful retrieval of fund detail info with expected structure."""
    result = get_fund_individual_detail_info("000001")

    # Check if result is not None (API call succeeded)
    if result is not None:
        # Check that result is a DataFrame
        assert isinstance(result, pd.DataFrame)
        # Check that DataFrame is not empty
        assert not result.empty

        # Check expected columns in the DataFrame
        expected_columns = [
            "费用类型",
            "条件或名称",
            "费用",
        ]
        for col in expected_columns:
            assert col in result.columns, f"Expected column '{col}' not found in DataFrame"


def test_get_fund_individual_detail_info_invalid_code():
    """Test handling of invalid fund code."""
    result = get_fund_individual_detail_info("000001")
    # Result should be None for invalid fund codes
    assert result is None


def test_get_fund_performance_success():
    """Test successful retrieval of fund performance with expected structure."""
    result = get_fund_performance("000001")

    # Check if result is not None (API call succeeded)
    if result is not None:
        # Check that result is a DataFrame
        assert isinstance(result, pd.DataFrame)
        # Check that DataFrame is not empty
        assert not result.empty

        # Check expected columns in the DataFrame
        expected_columns = [
            "业绩类型",
            "周期",
        ]
        for col in expected_columns:
            assert col in result.columns, f"Expected column '{col}' not found in DataFrame"


def test_get_fund_performance_with_timeout():
    """Test fund performance retrieval with timeout parameter."""
    result = get_fund_performance("000001", timeout=30.0)

    # Check if result is not None (API call succeeded)
    if result is not None:
        # Check that result is a DataFrame
        assert isinstance(result, pd.DataFrame)
        # Check that DataFrame is not empty
        assert not result.empty


def test_get_fund_performance_invalid_code():
    """Test handling of invalid fund code."""
    result = get_fund_performance("000001")
    # Result should be None for invalid fund codes
    assert result is None


def test_get_fund_list_success():
    """Test successful retrieval of fund list with expected structure."""
    result = get_fund_list()

    # Check if result is not None (API call succeeded)
    if result is not None:
        # Check that result is a list
        assert isinstance(result, list)
        # Check that list is not empty
        assert len(result) > 0

        # Check structure of first item
        if len(result) > 0:
            first_item = result[0]
            assert isinstance(first_item, dict)

            # Check expected keys in each fund item
            expected_keys = [
                "基金代码",
                "基金简称",
            ]
            for key in expected_keys:
                assert key in first_item, f"Expected key '{key}' not found in fund item"


def test_get_fund_net_value_success():
    """Test successful retrieval of fund net value with expected structure."""
    result = get_fund_net_value("000001", "20240101", "20241231")

    # Check if result is not None (API call succeeded)
    if result is not None:
        # Check that result is a list
        assert isinstance(result, list)
        # Check that list is not empty
        assert len(result) > 0

        # Check structure of first item
        if len(result) > 0:
            first_item = result[0]
            assert isinstance(first_item, dict)

            # Check expected keys in net value data
            expected_keys = [
                "净值日期",
                "单位净值",
            ]
            for key in expected_keys:
                assert key in first_item, f"Expected key '{key}' not found in net value data"


def test_get_fund_net_value_without_dates():
    """Test successful retrieval of fund net value without date range with expected structure."""
    result = get_fund_net_value("000001")

    # Check if result is not None (API call succeeded)
    if result is not None:
        # Check that result is a list
        assert isinstance(result, list)
        # Check that list is not empty
        assert len(result) > 0

        # Check structure of first item
        if len(result) > 0:
            first_item = result[0]
            assert isinstance(first_item, dict)
            # Check that date key exists
            assert "净值日期" in first_item


def test_get_fund_net_value_invalid_code():
    """Test handling of invalid fund code."""
    result = get_fund_net_value("000001")
    # Result should be None for invalid fund codes
    assert result is None


def test_get_fund_portfolio_success():
    """Test successful retrieval of fund portfolio with expected structure."""
    result = get_fund_portfolio("000001", "2024")

    # Check if result is not None (API call succeeded)
    if result is not None:
        # Check that result is a list
        assert isinstance(result, list)
        # Check that list is not empty
        assert len(result) > 0

        # Check structure of first item
        if len(result) > 0:
            first_item = result[0]
            assert isinstance(first_item, dict)

            # Check expected keys in portfolio data
            expected_keys = [
                "股票代码",
                "股票名称",
            ]
            for key in expected_keys:
                assert key in first_item, f"Expected key '{key}' not found in portfolio data"


def test_get_fund_portfolio_default_date():
    """Test fund portfolio retrieval with default date parameter."""
    result = get_fund_portfolio("000001")

    # Check if result is not None (API call succeeded)
    if result is not None:
        # Check that result is a list
        assert isinstance(result, list)
        # Check that list is not empty
        assert len(result) > 0

        # Check structure of first item
        if len(result) > 0:
            first_item = result[0]
            assert isinstance(first_item, dict)


def test_get_fund_portfolio_invalid_code():
    """Test handling of invalid fund code."""
    result = get_fund_portfolio("000001", "2024")
    # Result should be None for invalid fund codes
    assert result is None
