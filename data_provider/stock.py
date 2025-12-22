"""This module provides functions to fetch stock-related data using akshare."""

import logging
from typing import Any, cast

import akshare as ak  # type: ignore

logger = logging.getLogger(__name__)


def get_stock_info(stock_code: str) -> dict[str, Any] | None:
    """Get basic information about an A-share stock by its code using akshare's API.

    Args:
        stock_code (str): A six-digit stock code, e.g., "000001" for Ping An Bank

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing stock information with the following keys:
            - 最新: Latest price (float)
            - 股票代码: Stock code (str)
            - 股票简称: Stock short name (str)
            - 总股本: Total shares (float)
            - 流通股: Circulating shares (float)
            - 总市值: Total market cap (float)
            - 流通市值: Circulating market cap (float)
            - 行业: Industry (str)
            - 上市时间: Listing date (int, format: YYYYMMDD)

        Returns None if:
            - The stock code is not found
            - The API request fails
            - The returned data is empty

    Example:
        info = get_stock_info("000001")
        if info:
            print(f"Stock Name: {info['股票简称']}")
            print(f"Industry: {info['行业']}")
            print(f"Market Cap: {info['总市值']}")

    """
    try:
        # Get stock information from akshare
        df = ak.stock_individual_info_em(symbol=stock_code)

        if df.empty:
            logger.warning(f"No data found for stock code: {stock_code}")
            return None

        # Convert DataFrame to dictionary
        # Take the first row of data and convert to dictionary
        return dict(zip(df["item"], df["value"], strict=False))

    except Exception:
        logger.exception(f"Error fetching stock info for {stock_code}")
        return None


def get_stock_realtime_quote(stock_code: str) -> dict[str, Any] | None:
    """Get real-time quote for an A-share stock by its code using akshare's API.

    Args:
        stock_code (str): A six-digit stock code, e.g., "000001"

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing real-time quote data with the following keys:
            - 代码: Stock code (str)
            - 名称: Stock name (str)
            - 最新价: Latest price (float)
            - 涨跌幅: Price change percentage (float)
            - 涨跌额: Price change amount (float)
            - 成交量: Trading volume (float)
            - 成交额: Trading amount (float)
            - 振幅: Amplitude (float)
            - 最高: Highest price (float)
            - 最低: Lowest price (float)
            - 今开: Today's opening price (float)
            - 昨收: Yesterday's closing price (float)
            - 量比: Volume ratio (float)
            - 换手率: Turnover rate (float)
            - 市盈率-动态: Dynamic P/E ratio (float)
            - 市净率: P/B ratio (float)
            - 总市值: Total market cap (float)
            - 流通市值: Circulating market cap (float)

        Returns None if:
            - The stock code is not found
            - The API request fails
            - The returned data is empty

    Example:
        quote = get_stock_realtime_quote("000001")
        if quote:
            print(f"Latest Price: {quote['最新价']}")
            print(f"Change: {quote['涨跌幅']}%")

    """
    try:
        # Get all A-share real-time quotes
        df = ak.stock_zh_a_spot_em()

        if df.empty:
            logger.warning("No real-time stock data available")
            return None

        # Filter by stock code
        stock_data = df[df["代码"] == stock_code]

        if stock_data.empty:
            logger.warning(f"Stock code {stock_code} not found in real-time data")
            return None

        # Convert first matching row to dict
        return cast("dict[str, Any]", stock_data.iloc[0].to_dict())

    except Exception:
        logger.exception(f"Error fetching real-time quote for {stock_code}")
        return None


def get_stock_list() -> list[dict[str, Any]] | None:
    """Get list of all A-share stocks with basic information using akshare's API.

    Returns:
        Optional[List[Dict[str, Any]]]: A list of dictionaries, each containing stock information with keys:
            - 代码: Stock code (str)
            - 名称: Stock name (str)
            - 最新价: Latest price (float)
            - 涨跌幅: Price change percentage (float)
            - 涨跌额: Price change amount (float)
            - 成交量: Trading volume (float)
            - 成交额: Trading amount (float)
            - 振幅: Amplitude (float)
            - 最高: Highest price (float)
            - 最低: Lowest price (float)
            - 今开: Today's opening price (float)
            - 昨收: Yesterday's closing price (float)
            - 量比: Volume ratio (float)
            - 换手率: Turnover rate (float)
            - 市盈率-动态: Dynamic P/E ratio (float)
            - 市净率: P/B ratio (float)
            - 总市值: Total market cap (float)
            - 流通市值: Circulating market cap (float)

        Returns None if:
            - The API request fails
            - The returned data is empty

    Example:
        stocks = get_stock_list()
        if stocks:
            print(f"Total stocks: {len(stocks)}")
            print(f"First stock: {stocks[0]['名称']}")

    """
    try:
        # Get all A-share real-time quotes
        df = ak.stock_zh_a_spot_em()

        if df.empty:
            logger.warning("No stock data available")
            return None

        # Convert DataFrame to list of dictionaries
        return cast("list[dict[str, Any]]", df.to_dict(orient="records"))

    except Exception:
        logger.exception("Error fetching stock list")
        return None


def get_stock_hist_daily(
    stock_code: str, start_date: str | None = None, end_date: str | None = None
) -> list[dict[str, Any]] | None:
    """Get historical daily price data for an A-share stock using akshare's API.

    Args:
        stock_code (str): A six-digit stock code, e.g., "000001"
        start_date (Optional[str]): Start date in format "YYYYMMDD", e.g., "20240101". Defaults to None.
        end_date (Optional[str]): End date in format "YYYYMMDD", e.g., "20241231". Defaults to None.

    Returns:
        Optional[List[Dict[str, Any]]]: A list of dictionaries, each containing daily price data with keys:
            - 日期: Date (str, format: YYYY-MM-DD)
            - 开盘: Opening price (float)
            - 收盘: Closing price (float)
            - 最高: Highest price (float)
            - 最低: Lowest price (float)
            - 成交量: Trading volume (float)
            - 成交额: Trading amount (float)
            - 振幅: Amplitude (float)
            - 涨跌幅: Price change percentage (float)
            - 涨跌额: Price change amount (float)
            - 换手率: Turnover rate (float)

        Returns None if:
            - The stock code is not found
            - The API request fails
            - The returned data is empty

    Example:
        hist = get_stock_hist_daily("000001", "20240101", "20241231")
        if hist:
            print(f"Total trading days: {len(hist)}")
            print(f"Latest close: {hist[-1]['收盘']}")

    """
    try:
        # Get historical daily data
        # Note: stock_zh_a_hist expects plain 6-digit stock code, not with sh/sz prefix
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date, end_date=end_date, adjust="")

        if df.empty:
            logger.warning(f"No historical data found for stock code: {stock_code}")
            return None

        # Convert DataFrame to list of dictionaries
        return cast("list[dict[str, Any]]", df.to_dict(orient="records"))

    except Exception:
        logger.exception(f"Error fetching historical data for {stock_code}")
        return None


if __name__ == "__main__":
    quote = get_stock_realtime_quote("000001")
    if quote:
        print(f"Latest Price: {quote['最新价']}")
        print(f"Change: {quote['涨跌幅']}%")
