"""Data provider package for fetching financial data using various APIs."""

from .fund import (
    get_fund_individual_detail_info,
    get_fund_info,
    get_fund_list,
    get_fund_net_value,
    get_fund_performance,
    get_fund_portfolio,
)
from .stock import (
    get_stock_hist_daily,
    get_stock_info,
    get_stock_list,
    get_stock_realtime_quote,
)

__all__ = [
    # Fund functions
    "get_fund_info",
    "get_fund_individual_detail_info",
    "get_fund_performance",
    "get_fund_list",
    "get_fund_net_value",
    "get_fund_portfolio",
    # Stock functions
    "get_stock_info",
    "get_stock_realtime_quote",
    "get_stock_list",
    "get_stock_hist_daily",
]
