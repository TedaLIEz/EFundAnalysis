"""
Unit tests for the PortfolioAnalyzer class.
"""
import pytest
from datetime import datetime
from pathlib import Path
from src.analyzer.portfolio_analyzer import PortfolioAnalyzer, DividendMethod, Portfolio, FundPosition


@pytest.fixture
def test_data_path():
    """Fixture to provide the path to test data file."""
    return str(Path(__file__).parent.parent / "data" / "test_data.xlsx")


@pytest.fixture
def portfolio_analyzer(test_data_path):
    """Fixture to provide an initialized PortfolioAnalyzer instance."""
    analyzer = PortfolioAnalyzer(test_data_path)
    analyzer.load_data()
    return analyzer


@pytest.fixture
def sample_portfolio():
    """Fixture to provide a sample portfolio with test data."""
    positions = [
        FundPosition(
            fund_code="000001",
            fund_name="Test Fund 1",
            shares=100.0,
            nav=1.5,
            nav_date=datetime(2024, 1, 1),
            currency="CNY",
            dividend_method=DividendMethod.CASH
        ),
        FundPosition(
            fund_code="000002",
            fund_name="Test Fund 2",
            shares=200.0,
            nav=2.0,
            nav_date=datetime(2024, 1, 2),
            currency="USD",
            dividend_method=DividendMethod.REINVEST
        )
    ]
    return Portfolio(positions=positions)


def test_load_data_success(portfolio_analyzer):
    """Test that data is loaded successfully."""
    assert portfolio_analyzer.portfolio is not None
    assert len(portfolio_analyzer.portfolio.positions) > 0
    
    # Test the first position has correct attributes
    first_position = portfolio_analyzer.portfolio.positions[0]
    assert len(first_position.fund_code) == 6  # Should be 6 digits
    assert isinstance(first_position.dividend_method, DividendMethod)
    assert first_position.currency in ["CNY", "USD", "HKD"]
    assert isinstance(first_position.nav_date, datetime)
    assert isinstance(first_position.shares, float)
    assert isinstance(first_position.nav, float)
    assert isinstance(first_position.market_value, float)




def test_portfolio_empty():
    """Test Portfolio behavior with no positions."""
    empty_portfolio = Portfolio(positions=[])
    assert empty_portfolio.total_positions == 0
    assert empty_portfolio.total_market_value_by_currency == {}
    


def test_get_position_by_fund_code(portfolio_analyzer):
    """Test retrieving a position by fund code."""
    # Get the first position's fund code to test with
    test_fund_code = portfolio_analyzer.portfolio.positions[0].fund_code
    
    # Test finding existing position
    position = portfolio_analyzer.portfolio.get_position_by_fund_code(test_fund_code)
    assert position is not None
    assert position.fund_code == test_fund_code
    
    # Test with non-existent fund code
    position = portfolio_analyzer.portfolio.get_position_by_fund_code("999999")
    assert position is None


def test_get_positions_by_currency(portfolio_analyzer):
    """Test filtering positions by currency."""
    for currency in ["CNY", "USD", "HKD"]:
        positions = portfolio_analyzer.portfolio.get_positions_by_currency(currency)
        # Verify all returned positions have the correct currency
        assert all(pos.currency == currency for pos in positions)


def test_get_summary(portfolio_analyzer):
    """Test portfolio summary generation."""
    summary = portfolio_analyzer.get_summary()
    
    assert "total_positions" in summary
    assert summary["total_positions"] > 0
    
    assert "total_value_by_currency" in summary
    for currency, value in summary["total_value_by_currency"].items():
        assert currency in ["CNY", "USD", "HKD"]
        assert isinstance(value, float)
        assert value >= 0
    
    assert "position_count_by_currency" in summary
    for currency, count in summary["position_count_by_currency"].items():
        assert currency in ["CNY", "USD", "HKD"]
        assert isinstance(count, int)
        assert count > 0


def test_empty_portfolio_analyzer():
    """Test behavior with no positions loaded."""
    analyzer = PortfolioAnalyzer("nonexistent.xlsx")
    summary = analyzer.get_summary()
    assert summary == {"error": "No portfolio data loaded"}


def test_market_value_calculation(sample_portfolio):
    """Test market value calculations."""
    for position in sample_portfolio.positions:
        expected_value = position.shares * position.nav
        assert position.market_value == expected_value
        assert position.market_value >= 0 