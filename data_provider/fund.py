"""This module provides functions to fetch fund-related data using akshare."""

import logging
from typing import Any, cast

import akshare as ak  # type: ignore
import pandas as pd

logger = logging.getLogger(__name__)


def get_fund_info(fund_code: str) -> dict[str, Any] | None:
    """Get basic information about a fund by its code using akshare's API.

    Args:
        fund_code (str): A six-digit fund code, e.g., "000001"

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing fund information with the following keys:
            - 基金代码: Fund code (str)
            - 基金名称: Fund name (str)
            - 基金全称: Full fund name (str)
            - 成立时间: Establishment date (str, format: YYYY-MM-DD)
            - 最新规模: Latest fund size (str, e.g., "27.30亿")
            - 基金公司: Fund company name (str)
            - 基金经理: Fund manager(s) name (str)
            - 托管银行: Custodian bank (str)
            - 基金类型: Fund type (str)
            - 评级机构: Rating agency (str)
            - 基金评级: Fund rating (str)
            - 投资策略: Investment strategy (str)
            - 投资目标: Investment objective (str)
            - 业绩比较基准: Performance benchmark (str)

        Returns None if:
            - The fund code is not found
            - The API request fails
            - The returned data is empty

    Example:
        info = get_fund_info("000001")
        if info:
            print(f"Fund Name: {info['基金名称']}")
            print(f"Fund Type: {info['基金类型']}")
            print(f"Fund Size: {info['最新规模']}")

    """
    try:
        # Get fund information from akshare
        df = ak.fund_individual_basic_info_xq(symbol=fund_code)

        if df.empty:
            return None

        # Convert DataFrame to dictionary
        # Take the first row of data and convert to dictionary
        return dict(zip(df["item"], df["value"], strict=False))

    except Exception:
        logger.exception(f"Error fetching fund info for {fund_code}")
        return None


def get_fund_individual_detail_info(fund_code: str) -> pd.DataFrame | None:
    """Get fund transaction rules and fee information by its code using akshare's API.

    Args:
        fund_code (str): A six-digit fund code, e.g., "000001"

    Returns:
        Optional[pd.DataFrame]: A DataFrame containing fund transaction rules with the following columns:
            - 费用类型: Fee type (object)
            - 条件或名称: Condition or name (object)
            - 费用: Fee rate in percentage(float64)

        Returns None if:
            - The fund code is not found
            - The API request fails
            - The returned data is empty

    Example:
        rules = get_fund_individual_detail_info("000001")
        if rules is not None:
            print(rules[rules['费用类型'] == '买入规则'])  # Show purchase rules
            print(rules[rules['费用类型'] == '卖出规则'])  # Show redemption rules

    """
    try:
        # Get fund transaction rules from akshare
        df: pd.DataFrame = ak.fund_individual_detail_info_xq(symbol=fund_code)

        if df.empty:
            return None

        return df
    except Exception:
        logger.exception(f"Error fetching fund transaction rules for {fund_code}")
        return None


def get_fund_performance(fund_code: str, timeout: float | None = None) -> pd.DataFrame | None:
    """Get fund performance data using akshare's API.

    Args:
        fund_code (str): A six-digit fund code, e.g., "000001"
        timeout (Optional[float]): Request timeout in seconds. Defaults to None.

    Returns:
        Optional[pd.DataFrame]: A DataFrame containing fund performance data with the following columns:
            - 业绩类型: Performance type (object) - '年度业绩' for annual or '阶段业绩' for periodic
            - 周期: Period (object) - e.g., '近1月', '近3月', '2023', '成立以来', etc.
            - 本产品区间收益: Product interval return (float64) - in percentage
            - 本产品最大回撒: Maximum drawdown (float64) - in percentage
            - 周期收益同类排名: Period return ranking among peers (object) - e.g., '128/7671'

        Returns None if:
            - The fund code is not found
            - The API request fails
            - The returned data is empty

    Example:
        perf = get_fund_performance("000001")
        if perf is not None:
            # Get annual performance
            annual_perf = perf[perf['业绩类型'] == '年度业绩']
            print(annual_perf)
            # Get periodic performance
            period_perf = perf[perf['业绩类型'] == '阶段业绩']
            print(period_perf)

    """
    try:
        # Get fund performance data from akshare
        df: pd.DataFrame = ak.fund_individual_achievement_xq(symbol=fund_code, timeout=timeout)

        if df.empty:
            return None

        return df
    except Exception:
        logger.exception(f"Error fetching fund performance for {fund_code}")
        return None


def get_fund_list() -> list[dict[str, Any]] | None:
    """Get list of all funds with basic information using akshare's API.

    Returns:
        Optional[List[Dict[str, Any]]]: A list of dictionaries, each containing fund information with keys:
            - 基金代码: Fund code (str)
            - 拼音缩写: Pinyin abbreviation (str)
            - 基金简称: Fund short name (str)
            - 基金类型: Fund type (str)
            - 拼音全称: Full pinyin name (str)

        Returns None if:
            - The API request fails
            - The returned data is empty

    Example:
        funds = get_fund_list()
        if funds:
            print(f"Total funds: {len(funds)}")
            print(f"First fund: {funds[0]['基金简称']}")

    """
    try:
        # Get all fund information from akshare
        # API: fund_name_em - 东方财富网-天天基金网-基金数据-所有基金的基本信息数据
        df = ak.fund_name_em()

        if df.empty:
            logger.warning("No fund data available")
            return None

        # Convert DataFrame to list of dictionaries
        return cast("list[dict[str, Any]]", df.to_dict(orient="records"))

    except Exception:
        logger.exception("Error fetching fund list")
        return None


def get_fund_net_value(
    fund_code: str, start_date: str | None = None, end_date: str | None = None
) -> list[dict[str, Any]] | None:
    """Get historical net value data for a fund using akshare's API.

    Args:
        fund_code (str): A six-digit fund code, e.g., "000001"
        start_date (Optional[str]): Start date in format "YYYYMMDD", e.g., "20240101". Defaults to None.
        end_date (Optional[str]): End date in format "YYYYMMDD", e.g., "20241231". Defaults to None.

    Returns:
        Optional[List[Dict[str, Any]]]: A list of dictionaries, each containing net value data with keys:
            - 净值日期: Net value date (date or str, format: YYYY-MM-DD)
            - 单位净值: Net asset value per unit (float)
            - 日增长率: Daily growth rate (float, percentage)

        Returns None if:
            - The fund code is not found
            - The API request fails
            - The returned data is empty

    Example:
        nav = get_fund_net_value("000001", "20240101", "20241231")
        if nav:
            print(f"Total records: {len(nav)}")
            print(f"Latest NAV: {nav[-1]['单位净值']}")

    """
    try:
        # Get fund net value history
        # API: fund_open_fund_info_em - 东方财富网-天天基金网-开放式基金-历史净值数据
        df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势", period="成立来")

        if df.empty:
            logger.warning(f"No net value data found for fund code: {fund_code}")
            return None

        # Filter by date range if provided
        if start_date or end_date:
            df["净值日期"] = pd.to_datetime(df["净值日期"])
            if start_date:
                start_dt = pd.to_datetime(start_date, format="%Y%m%d")
                df = df[df["净值日期"] >= start_dt]
            if end_date:
                end_dt = pd.to_datetime(end_date, format="%Y%m%d")
                df = df[df["净值日期"] <= end_dt]
            # Convert back to string format
            df["净值日期"] = df["净值日期"].dt.strftime("%Y-%m-%d")

        # Convert DataFrame to list of dictionaries
        return cast("list[dict[str, Any]]", df.to_dict(orient="records"))

    except Exception:
        logger.exception(f"Error fetching fund net value for {fund_code}")
        return None


def get_fund_portfolio(fund_code: str, date: str = "2024") -> list[dict[str, Any]] | None:
    """Get fund portfolio/holdings information by its code using akshare's API.

    Args:
        fund_code (str): A six-digit fund code, e.g., "000001"
        date (str): Year for portfolio data, e.g., "2024". Defaults to "2024".

    Returns:
        Optional[List[Dict[str, Any]]]: A list of dictionaries, each containing holding information with keys:
            - 序号: Sequence number (int)
            - 股票代码: Stock code (str)
            - 股票名称: Stock name (str)
            - 占净值比例: Percentage of net value (float)
            - 持股数: Number of shares held (float)
            - 持仓市值: Market value of holdings (float)
            - 季度: Quarter description (str, e.g., "2024年1季度股票投资明细")

        Returns None if:
            - The fund code is not found
            - The API request fails
            - The returned data is empty

    Example:
        portfolio = get_fund_portfolio("000001", "2024")
        if portfolio:
            print(f"Total holdings: {len(portfolio)}")
            print(f"Top holding: {portfolio[0]['股票名称']}")

    """
    try:
        # Get fund portfolio information from akshare
        # API: fund_portfolio_hold_em - 东方财富网-天天基金网-基金持仓
        df = ak.fund_portfolio_hold_em(symbol=fund_code, date=date)

        if df.empty:
            logger.warning(f"No portfolio data found for fund code: {fund_code}")
            return None

        # Convert DataFrame to list of dictionaries
        return cast("list[dict[str, Any]]", df.to_dict(orient="records"))

    except Exception:
        logger.exception(f"Error fetching fund portfolio for {fund_code}")
        return None


if __name__ == "__main__":
    portfolio = get_fund_portfolio("000001", "2024")
    if portfolio:
        print(f"Total holdings: {len(portfolio)}")
        print(f"Top holding: {portfolio[0]['股票名称']}")
