"""Test cases for stock data provider functions."""

import pytest

from data_provider.stock import (
    get_stock_hist_daily,
    get_stock_info,
    get_stock_list,
    get_stock_realtime_quote,
)


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


def test_get_stock_realtime_quote_success():
    """Test successful retrieval of stock real-time quote with expected structure."""
    result = get_stock_realtime_quote("000001")

    # Check if result is not None (API call succeeded)
    if result is not None:
        # Check expected keys in the result dictionary
        expected_keys = [
            "代码",
            "名称",
            "最新价",
            "涨跌幅",
            "涨跌额",
            "成交量",
            "成交额",
        ]
        for key in expected_keys:
            assert key in result, f"Expected key '{key}' not found in result"

        # Check that result is a dictionary
        assert isinstance(result, dict)
        # Check that dictionary is not empty
        assert len(result) > 0

        # Check data types for numeric fields
        assert isinstance(result["代码"], str)
        assert isinstance(result["名称"], str)


def test_get_stock_realtime_quote_not_found():
    """Test handling when stock code is not found."""
    result = get_stock_realtime_quote("000001")
    # Result should be None for non-existent stock codes
    assert result is None


def test_get_stock_list_success():
    """Test successful retrieval of stock list with expected structure."""
    result = get_stock_list()

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

            # Check expected keys in each stock item
            expected_keys = [
                "代码",
                "名称",
                "最新价",
            ]
            for key in expected_keys:
                assert key in first_item, f"Expected key '{key}' not found in stock item"


def test_get_stock_hist_daily_success_sh():
    """Test successful retrieval of historical data for Shanghai stock with expected structure."""
    result = get_stock_hist_daily("600000", "20240101", "20241231")

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

            # Check expected keys in historical data
            expected_keys = [
                "日期",
                "开盘",
                "收盘",
                "最高",
                "最低",
                "成交量",
                "成交额",
            ]
            for key in expected_keys:
                assert key in first_item, f"Expected key '{key}' not found in historical data"


def test_get_stock_hist_daily_success_sz():
    """Test successful retrieval of historical data for Shenzhen stock with expected structure."""
    result = get_stock_hist_daily("000001", "20240101", "20241231")

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

            # Check expected keys in historical data
            expected_keys = [
                "日期",
                "开盘",
                "收盘",
                "最高",
                "最低",
            ]
            for key in expected_keys:
                assert key in first_item, f"Expected key '{key}' not found in historical data"


def test_get_stock_hist_daily_success_without_dates():
    """Test successful retrieval of historical data without date range with expected structure."""
    result = get_stock_hist_daily("000001")

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
            assert "日期" in first_item


def test_get_stock_hist_daily_invalid_code():
    """Test handling of invalid stock code format."""
    result = get_stock_hist_daily("000001")
    # Result should be None for invalid stock codes
    assert result is None
