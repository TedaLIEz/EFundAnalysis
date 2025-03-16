"""
Unit tests for the PortfolioAnalyzer class.
"""
import pytest
from datetime import datetime
from pathlib import Path
from analyzer.portfolio_analyzer import PortfolioAnalyzer, DividendMethod


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


def test_load_data_success(portfolio_analyzer):
    """Test that data is loaded successfully."""
    assert len(portfolio_analyzer.positions) > 0
    
    # Test the first position has correct attributes
    first_position = portfolio_analyzer.positions[0]
    assert len(first_position.fund_code) == 6  # Should be 6 digits
    assert isinstance(first_position.dividend_method, DividendMethod)
    assert first_position.currency in ["CNY", "USD", "HKD"]
    assert isinstance(first_position.nav_date, datetime)
    assert isinstance(first_position.shares, float)
    assert isinstance(first_position.nav, float)
    assert isinstance(first_position.market_value, float)


def test_get_position_by_fund_code(portfolio_analyzer):
    """Test retrieving a position by fund code."""
    # Get the first position's fund code to test with
    test_fund_code = portfolio_analyzer.positions[0].fund_code
    
    # Test finding existing position
    position = portfolio_analyzer.get_position_by_fund_code(test_fund_code)
    assert position is not None
    assert position.fund_code == test_fund_code
    
    # Test with non-existent fund code
    position = portfolio_analyzer.get_position_by_fund_code("999999")
    assert position is None


def test_get_positions_by_currency(portfolio_analyzer):
    """Test filtering positions by currency."""
    for currency in ["CNY", "USD", "HKD"]:
        positions = portfolio_analyzer.get_positions_by_currency(currency)
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
    
    assert "latest_nav_date" in summary
    assert "earliest_nav_date" in summary
    assert summary["latest_nav_date"] >= summary["earliest_nav_date"]


def test_empty_portfolio():
    """Test behavior with no positions loaded."""
    analyzer = PortfolioAnalyzer("nonexistent.xlsx")
    summary = analyzer.get_summary()
    assert summary == {"error": "No positions loaded"}


def test_market_value_calculation(portfolio_analyzer):
    """Test market value calculations."""
    for position in portfolio_analyzer.positions:
        expected_value = position.shares * position.nav
        assert position.market_value == expected_value
        assert position.market_value >= 0 