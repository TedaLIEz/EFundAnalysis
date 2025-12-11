"""KYC data models for customer information and investment preferences."""

from .customer import (
    BasicInfo,
    CustomerProfile,
    InvestmentPreference,
    RiskProfile,
)

__all__ = [
    "BasicInfo",
    "InvestmentPreference",
    "RiskProfile",
    "CustomerProfile",
]
