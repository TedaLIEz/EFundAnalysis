"""Customer data models for KYC workflow."""

from enum import Enum

from pydantic import BaseModel, Field


class MaritalStatus(str, Enum):
    """Marital status options."""

    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"
    OTHER = "other"


class EmploymentStatus(str, Enum):
    """Employment status options."""

    EMPLOYED = "employed"
    SELF_EMPLOYED = "self_employed"
    UNEMPLOYED = "unemployed"
    RETIRED = "retired"
    STUDENT = "student"
    OTHER = "other"


class RiskTolerance(str, Enum):
    """Risk tolerance levels."""

    CONSERVATIVE = "conservative"  # 保守型
    MODERATE = "moderate"  # 稳健型
    BALANCED = "balanced"  # 平衡型
    AGGRESSIVE = "aggressive"  # 激进型


class BasicInfo(BaseModel):
    """Basic customer information."""

    age: int = Field(..., ge=18, le=100, description="Customer age")
    city: str = Field(..., min_length=1, description="City of residence")
    marital_status: MaritalStatus = Field(..., description="Marital status")
    employment_status: EmploymentStatus = Field(..., description="Employment status")
    annual_income: float | None = Field(None, ge=0, description="Annual income in local currency")
    education_level: str | None = Field(None, description="Education level")
    dependents: int = Field(0, ge=0, description="Number of dependents")


class InvestmentPreference(BaseModel):
    """Investment preferences and constraints."""

    investable_assets: float = Field(..., ge=0, description="Total investable assets in local currency")
    max_loss_tolerance: float = Field(..., ge=0, le=100, description="Maximum acceptable loss percentage (0-100)")
    investment_horizon_years: int = Field(..., ge=1, description="Investment time horizon in years")
    risk_tolerance: RiskTolerance = Field(..., description="Risk tolerance level")
    investment_goals: list[str] = Field(default_factory=list, description="Investment goals")
    preferred_investment_types: list[str] = Field(
        default_factory=list, description="Preferred investment types (e.g., stocks, bonds, funds)"
    )
    liquidity_needs: str | None = Field(None, description="Liquidity needs description")


class RiskProfile(BaseModel):
    """Risk assessment profile."""

    risk_score: float = Field(..., ge=0, le=100, description="Overall risk score (0-100)")
    risk_level: RiskTolerance = Field(..., description="Assessed risk level")
    risk_factors: list[str] = Field(default_factory=list, description="Key risk factors identified")
    suitability_notes: str | None = Field(None, description="Suitability assessment notes")


class CustomerProfile(BaseModel):
    """Complete customer profile combining all information."""

    customer_id: str | None = Field(None, description="Unique customer identifier")
    basic_info: BasicInfo
    investment_preference: InvestmentPreference
    risk_profile: RiskProfile | None = None
    additional_notes: str | None = Field(None, description="Additional relevant information")
    collected_at: str | None = Field(None, description="Timestamp when profile was collected")
