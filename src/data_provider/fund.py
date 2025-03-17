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


if __name__ == "__main__":
    print(get_fund_info("000001"))