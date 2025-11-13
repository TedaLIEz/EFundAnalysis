"""Test cases for the data provider module."""

from unittest.mock import patch

import pandas as pd
import pytest

from data_provider import get_fund_info


@pytest.fixture
def mock_fund_data():
    """Fixture to create mock fund data."""
    return pd.DataFrame(
        {
            "item": [
                "基金代码",
                "基金名称",
                "基金全称",
                "成立时间",
                "最新规模",
                "基金公司",
                "基金经理",
                "托管银行",
                "基金类型",
                "评级机构",
                "基金评级",
                "投资策略",
                "投资目标",
                "业绩比较基准",
            ],
            "value": [
                "000001",
                "华夏成长混合",
                "华夏成长前收费",
                "2001-12-18",
                "27.30亿",
                "华夏基金管理有限公司",
                "王泽实 万方方",
                "中国建设银行股份有限公司",
                "混合型-偏股",
                "晨星评级",
                "一星基金",
                "在股票投资方面，本基金重点投资于预期利润或收入具有良好增长潜力的成长型上市公司发行的股票，从...",
                "本基金属成长型基金，主要通过投资于具有良好成长性的上市公司的股票，在保持基金资产安全性和流动...",
                "本基金暂不设业绩比较基准",
            ],
        }
    )


def test_get_fund_info_success(mock_fund_data):
    """Test successful retrieval of fund information."""
    with patch("akshare.fund_individual_basic_info_xq", return_value=mock_fund_data):
        result = get_fund_info("000001")

        assert result is not None
        assert result["基金代码"] == "000001"
        assert result["基金名称"] == "华夏成长混合"
        assert result["基金全称"] == "华夏成长前收费"
        assert result["成立时间"] == "2001-12-18"
        assert result["最新规模"] == "27.30亿"
        assert result["基金公司"] == "华夏基金管理有限公司"
        assert result["基金经理"] == "王泽实 万方方"
        assert result["托管银行"] == "中国建设银行股份有限公司"
        assert result["基金类型"] == "混合型-偏股"
        assert result["评级机构"] == "晨星评级"
        assert result["基金评级"] == "一星基金"
        assert "投资策略" in result
        assert "投资目标" in result
        assert result["业绩比较基准"] == "本基金暂不设业绩比较基准"


def test_get_fund_info_empty_result():
    """Test handling of empty DataFrame result."""
    with patch("akshare.fund_individual_basic_info_xq", return_value=pd.DataFrame()):
        result = get_fund_info("000001")
        assert result is None


def test_get_fund_info_api_error():
    """Test handling of API errors."""
    with patch("akshare.fund_individual_basic_info_xq", side_effect=Exception("API Error")):
        result = get_fund_info("000001")
        assert result is None


def test_get_fund_info_invalid_code():
    """Test handling of invalid fund code."""
    # Testing with a non-existent fund code
    with patch("akshare.fund_individual_basic_info_xq", return_value=pd.DataFrame()):
        result = get_fund_info("999999")
        assert result is None
