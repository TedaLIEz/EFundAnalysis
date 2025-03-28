"""
Data provider package for fetching financial data using various APIs.
"""

from .fund import get_fund_info, get_fund_individual_detail_info

__all__ = ['get_fund_info', 'get_fund_individual_detail_info'] 