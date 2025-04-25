"""
This module provides functions to fetch fund-related data using akshare.
"""
from typing import Dict, Any, Optional

import akshare as ak
import pandas as pd


def get_fund_info(fund_code: str) -> Optional[Dict[str, Any]]:
    """
    Get basic information about a fund by its code using akshare's API.
    
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
        >>> info = get_fund_info("000001")
        >>> if info:
        ...     print(f"Fund Name: {info['基金名称']}")
        ...     print(f"Fund Type: {info['基金类型']}")
        ...     print(f"Fund Size: {info['最新规模']}")
    """
    try:
        # Get fund information from akshare
        df = ak.fund_individual_basic_info_xq(symbol=fund_code)
        
        if df.empty:
            return None
            
        # Convert DataFrame to dictionary
        # Take the first row of data and convert to dictionary
        fund_dict = dict(zip(df['item'], df['value']))
        
        return fund_dict
    except Exception as e:
        print(f"Error fetching fund info for {fund_code}: {str(e)}")
        return None 


def get_fund_individual_detail_info(fund_code: str) -> Optional[pd.DataFrame]:
    """
    Get fund transaction rules and fee information by its code using akshare's API.
    
    Args:
        fund_code (str): A six-digit fund code, e.g., "000001"
        
    Returns:
        Optional[pd.DataFrame]: A DataFrame containing fund transaction rules with the following columns:
            - 费用类型: Fee type (object)
            - 条件或名称: Condition or name (object)
            - 费用率: Fee rate in percentage(float64)
            
        Returns None if:
            - The fund code is not found
            - The API request fails
            - The returned data is empty
            
    Example:
        >>> rules = get_fund_individual_detail_info("000001")
        >>> if rules is not None:
        ...     print(rules[rules['费用类型'] == '买入规则'])  # Show purchase rules
        ...     print(rules[rules['费用类型'] == '卖出规则'])  # Show redemption rules
    """
    try:
        # Get fund transaction rules from akshare
        df = ak.fund_individual_detail_info_xq(symbol=fund_code)
        
        if df.empty:
            return None
            
        return df
    except Exception as e:
        print(f"Error fetching fund transaction rules for {fund_code}: {str(e)}")
        return None


def get_fund_performance(fund_code: str, timeout: Optional[float] = None) -> Optional[pd.DataFrame]:
    """
    Get fund performance data using akshare's API.
    
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
        >>> perf = get_fund_performance("000001")
        >>> if perf is not None:
        ...     # Get annual performance
        ...     annual_perf = perf[perf['业绩类型'] == '年度业绩']
        ...     print(annual_perf)
        ...     # Get periodic performance
        ...     period_perf = perf[perf['业绩类型'] == '阶段业绩']
        ...     print(period_perf)
    """
    try:
        # Get fund performance data from akshare
        df = ak.fund_individual_achievement_xq(symbol=fund_code, timeout=timeout)
        
        if df.empty:
            return None
            
        return df
    except Exception as e:
        print(f"Error fetching fund performance for {fund_code}: {str(e)}")
        return None

if __name__ == "__main__":
    # print(get_fund_individual_detail_info("000001"))
    # Test the new function
    print("\nTesting fund performance:")
    perf = get_fund_performance("000001")
    if perf is not None:
        print("\nAnnual Performance:")
        print(perf[perf['业绩类型'] == '年度业绩'].head())
        print("\nPeriodic Performance:")
        print(perf[perf['业绩类型'] == '阶段业绩'])