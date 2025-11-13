"""Portfolio analyzer for processing investment Excel files."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import pandas as pd


class DividendMethod(Enum):
    """Dividend distribution methods."""

    CASH = "现金分红"
    REINVEST = "红利转投"


# Currency mapping
CURRENCY_MAP = {"人民币": "CNY", "美元": "USD", "港币": "HKD"}


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


@dataclass
class Portfolio:
    """Represents a user's investment portfolio containing multiple fund positions."""

    positions: list[FundPosition]

    @property
    def total_positions(self) -> int:
        """Get the total number of positions in the portfolio."""
        return len(self.positions)

    @property
    def total_market_value_by_currency(self) -> dict[str, float]:
        """Calculate total market value grouped by currency."""
        values: dict[str, float] = {}
        for position in self.positions:
            values[position.currency] = values.get(position.currency, 0) + position.market_value
        return values

    @property
    def total_market_value(self) -> float:
        """Calculate total market value across all positions."""
        return sum(position.market_value for position in self.positions)

    @property
    def position_percentages(self) -> dict[str, float]:
        """Calculate the percentage of each position relative to total portfolio value."""
        total_value = self.total_market_value
        if total_value == 0:
            return {}
        return {f"{pos.fund_code} ({pos.fund_name})": (pos.market_value / total_value) * 100 for pos in self.positions}

    def get_positions_by_currency(self, currency: str) -> list[FundPosition]:
        """Get all positions in a specific currency."""
        return [pos for pos in self.positions if pos.currency == currency]

    def get_position_by_fund_code(self, fund_code: str) -> FundPosition | None:
        """Get a position by fund code."""
        for position in self.positions:
            if position.fund_code == fund_code:
                return position
        return None


class PortfolioAnalyzer:
    """Analyzes investment portfolio Excel files."""

    def __init__(self, file_path: str):
        """Initialize the analyzer with an Excel file path."""
        self.file_path = file_path
        self.portfolio: Portfolio | None = None

    def load_data(self) -> None:
        """Load and process data from the Excel file."""
        positions: list[FundPosition] = []
        try:
            # Read Excel file starting from row 5 (0-based index 4)
            data = pd.read_excel(
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
                ],
            )

            # Process each row into a FundPosition object
            for _, row in data.iterrows():
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
                    dividend_method=DividendMethod(str(row.iloc[6])),
                )
                positions.append(position)

            self.portfolio = Portfolio(positions=positions)

        except Exception as e:
            raise ValueError(f"Error processing Excel file: {str(e)}")

    def get_total_market_value(self) -> float:
        """Calculate total market value of all positions."""
        if not self.portfolio:
            raise ValueError("No portfolio data loaded")
        return sum(position.market_value for position in self.portfolio.positions)

    def get_summary(self) -> dict:
        """Get a summary of the portfolio."""
        if not self.portfolio:
            return {"error": "No portfolio data loaded"}

        return {
            "total_positions": self.portfolio.total_positions,
            "total_value_by_currency": self.portfolio.total_market_value_by_currency,
            "position_count_by_currency": {
                currency: len(self.portfolio.get_positions_by_currency(currency))
                for currency in {pos.currency for pos in self.portfolio.positions}
            },
        }
