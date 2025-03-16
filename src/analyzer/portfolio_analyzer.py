"""
Portfolio analyzer for processing investment Excel files.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum
import pandas as pd


class DividendMethod(Enum):
    """Dividend distribution methods."""
    CASH = "现金分红"
    REINVEST = "红利转投"


# Currency mapping
CURRENCY_MAP = {
    "人民币": "CNY",
    "美元": "USD",
    "港币": "HKD"
}

@dataclass
class FundPosition:
    """Represents a single fund position in the portfolio."""
    fund_code: str  # 基金代码
    fund_name: str  # 基金名称
    shares: float  # 持有份额
    nav: float  # 基金净值
    nav_date: datetime  # 净值日期
    currency: str  # 结算币种
    dividend_method: DividendMethod  # 分红方式
    
    @property
    def market_value(self) -> float:
        """Calculate the market value of the position."""
        return self.shares * self.nav


class PortfolioAnalyzer:
    """Analyzes investment portfolio Excel files."""
    
    def __init__(self, file_path: str):
        """Initialize the analyzer with an Excel file path."""
        self.file_path = file_path
        self.positions: List[FundPosition] = []
        
    def load_data(self) -> None:
        """Load and process data from the Excel file."""
        try:
            # Read Excel file starting from row 5 (0-based index 4)
            df = pd.read_excel(
                self.file_path,
                skiprows=4,
                usecols=[
                    1,  # 基金代码
                    2,  # 基金名称
                    8,  # 持有份额
                    10,  # 基金净值
                    11,  # 净值日期
                    13,  # 结算币种
                    14,  # 分红方式
                ]
            )
            
            # Process each row into a FundPosition object
            for _, row in df.iterrows():
                # Break if fund code is empty or NaN
                fund_code = row.iloc[0]
                if pd.isna(fund_code) or str(fund_code).strip() == "":
                    break
                    
                # Format fund code as six digits
                fund_code = str(int(fund_code)).zfill(6)
                
                # Map currency to standardized format
                raw_currency = str(row.iloc[5])
                currency = CURRENCY_MAP.get(raw_currency, "CNY")  # Default to CNY if mapping not found
                
                position = FundPosition(
                    fund_code=fund_code,
                    fund_name=str(row.iloc[1]),
                    shares=float(row.iloc[2]),
                    nav=float(row.iloc[3]),
                    nav_date=pd.to_datetime(row.iloc[4]).to_pydatetime(),
                    currency=currency,
                    dividend_method=DividendMethod(str(row.iloc[6]))
                )
                self.positions.append(position)
                
        except Exception as e:
            raise ValueError(f"Error processing Excel file: {str(e)}")
    
    def get_total_market_value(self) -> float:
        """Calculate total market value of all positions."""
        return sum(position.market_value for position in self.positions)
    
    def get_position_by_fund_code(self, fund_code: str) -> Optional[FundPosition]:
        """Get a position by fund code."""
        for position in self.positions:
            if position.fund_code == fund_code:
                return position
        return None
    
    def get_positions_by_currency(self, currency: str) -> List[FundPosition]:
        """Get all positions in a specific currency."""
        return [pos for pos in self.positions if pos.currency == currency]
    
    def get_summary(self) -> dict:
        """Get a summary of the portfolio."""
        if not self.positions:
            return {"error": "No positions loaded"}
            
        currencies = set(pos.currency for pos in self.positions)
        summary = {
            "total_positions": len(self.positions),
            "total_value_by_currency": {
                currency: sum(pos.market_value for pos in self.get_positions_by_currency(currency))
                for currency in currencies
            },
            "position_count_by_currency": {
                currency: len(self.get_positions_by_currency(currency))
                for currency in currencies
            },
            "latest_nav_date": max(pos.nav_date for pos in self.positions),
            "earliest_nav_date": min(pos.nav_date for pos in self.positions)
        }
        return summary 