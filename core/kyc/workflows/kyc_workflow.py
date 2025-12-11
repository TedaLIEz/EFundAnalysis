"""Main KYC workflow for collecting customer information and generating investment recommendations."""

import logging

from llama_index.core.llms.function_calling import FunctionCallingLLM
from llama_index.core.workflow import (
    Context,
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)

from core.kyc.models.customer import (
    BasicInfo,
    CustomerProfile,
    EmploymentStatus,
    InvestmentPreference,
    MaritalStatus,
    RiskProfile,
    RiskTolerance,
)
from core.llm.model import create_llm
from core.llm.prompt.prompt_loader import PromptLoader
from core.util.json_util import extract_json_from_response

logger = logging.getLogger(__name__)


class BasicInfoEvent(Event):
    """Event containing basic customer information."""

    basic_info: BasicInfo
    customer_id: str | None = None
    user_input: str = ""


class InvestmentPreferenceEvent(Event):
    """Event containing investment preferences and basic info."""

    basic_info: BasicInfo
    investment_preference: InvestmentPreference
    customer_id: str | None = None
    user_input: str = ""


class RiskAssessmentEvent(Event):
    """Event containing risk assessment results and all previous data."""

    basic_info: BasicInfo
    investment_preference: InvestmentPreference
    risk_profile: RiskProfile
    customer_id: str | None = None


class StreamingChunkEvent(Event):
    """Event containing a streaming chunk of LLM output."""

    chunk: str
    step_name: str
    is_complete: bool = False


class KYCWorkflow(Workflow):
    """KYC workflow for collecting customer information and assessing investment suitability.

    This workflow collects:
    1. Basic information (age, city, family status, etc.)
    2. Investment preferences (investable assets, risk tolerance, etc.)
    3. Performs risk assessment
    4. Generates investment suitability profile
    """

    llm: FunctionCallingLLM = create_llm()
    prompt_loader: PromptLoader = PromptLoader()

    async def __stream_llm_response__(self, prompt: str, step_name: str, ctx: Context) -> str:
        """Stream LLM response chunk by chunk."""
        response_text = ""
        async for token in await self.llm.astream_complete(prompt):
            # Extract chunk text from token (handles different token formats)
            chunk = token.delta if hasattr(token, "delta") and token.delta else ""
            if chunk:
                response_text += chunk
                ctx.write_event_to_stream(
                    StreamingChunkEvent(
                        chunk=chunk,
                        step_name=step_name,
                        is_complete=False,
                    )
                )
        # Emit completion event with newline to separate from log messages
        ctx.write_event_to_stream(
            StreamingChunkEvent(
                chunk="\n",
                step_name=step_name,
                is_complete=True,
            )
        )
        return response_text.strip()

    @step
    async def collect_basic_info(self, ev: StartEvent, ctx: Context) -> BasicInfoEvent:
        """Step 1: Collect basic customer information using LLM.

        Extracts basic information from the start event which may contain
        unstructured text or structured data.
        """
        try:
            # Get input data from start event
            # StartEvent accepts arbitrary kwargs, accessible as attributes
            user_input = getattr(ev, "user_input", "") or getattr(ev, "data", "")
            customer_id = getattr(ev, "customer_id", None)

            # Use LLM to extract structured information from user input
            prompt = self.prompt_loader.load_prompt_with_context("kyc.liquid", {"user_context": user_input})

            # Stream LLM response chunk by chunk
            response_text = await self.__stream_llm_response__(prompt, "collect_basic_info", ctx)

            # Parse JSON response using robust extraction
            data = extract_json_from_response(response_text)

            # Create BasicInfo model
            basic_info = BasicInfo(
                age=data.get("age", 30),
                city=data.get("city", "Unknown"),
                marital_status=MaritalStatus(data.get("marital_status", "single")),
                employment_status=EmploymentStatus(data.get("employment_status", "employed")),
                annual_income=data.get("annual_income"),
                education_level=data.get("education_level"),
                dependents=data.get("dependents", 0),
            )

            # Completion event already emitted by __stream_llm_response__
            logger.info(f"Collected basic info for customer: {customer_id}")
            return BasicInfoEvent(
                basic_info=basic_info,
                customer_id=customer_id,
                user_input=user_input,
            )

        except Exception as e:
            logger.error(f"Error collecting basic info: {e}", exc_info=True)
            # Return default values on error
            basic_info = BasicInfo(
                age=30,
                city="Unknown",
                marital_status=MaritalStatus.SINGLE,
                employment_status=EmploymentStatus.EMPLOYED,
                annual_income=None,
                education_level=None,
                dependents=0,
            )
            return BasicInfoEvent(
                basic_info=basic_info,
                customer_id=customer_id,
                user_input=user_input,
            )

    @step
    async def collect_investment_preferences(self, ev: BasicInfoEvent, ctx: Context) -> InvestmentPreferenceEvent:
        """Step 2: Collect investment preferences and constraints.

        Uses the basic info to ask relevant follow-up questions or extract
        investment preferences from the original input.
        """
        try:
            basic_info = ev.basic_info
            user_input = ev.user_input
            customer_id = ev.customer_id

            # Load prompt template with context
            # Convert BasicInfo to dict with enum values as strings
            basic_info_dict = {
                "age": basic_info.age,
                "city": basic_info.city,
                "marital_status": basic_info.marital_status.value,
                "employment_status": basic_info.employment_status.value,
                "annual_income": basic_info.annual_income,
                "dependents": basic_info.dependents,
            }
            prompt = self.prompt_loader.load_prompt_with_context(
                "investment_preference.liquid",
                {
                    "basic_info": basic_info_dict,
                    "user_input": user_input,
                },
            )

            # Stream LLM response chunk by chunk
            response_text = await self.__stream_llm_response__(prompt, "collect_investment_preferences", ctx)

            # Parse JSON response using robust extraction
            data = extract_json_from_response(response_text)

            # Create InvestmentPreference model
            investment_preference = InvestmentPreference(
                investable_assets=data.get("investable_assets", 100000),
                max_loss_tolerance=data.get("max_loss_tolerance", 10),
                investment_horizon_years=data.get("investment_horizon_years", 5),
                risk_tolerance=RiskTolerance(data.get("risk_tolerance", "moderate")),
                investment_goals=data.get("investment_goals", []),
                preferred_investment_types=data.get("preferred_investment_types", []),
                liquidity_needs=data.get("liquidity_needs"),
            )

            # Completion event already emitted by __stream_llm_response__
            logger.info("Collected investment preferences for customer")
            return InvestmentPreferenceEvent(
                basic_info=basic_info,
                investment_preference=investment_preference,
                customer_id=customer_id,
                user_input=user_input,
            )

        except Exception as e:
            logger.error(f"Error collecting investment preferences: {e}", exc_info=True)
            # Return default values on error
            basic_info = ev.basic_info
            investment_preference = InvestmentPreference(
                investable_assets=100000,
                max_loss_tolerance=10,
                investment_horizon_years=5,
                risk_tolerance=RiskTolerance.MODERATE,
                liquidity_needs=None,
            )
            return InvestmentPreferenceEvent(
                basic_info=basic_info,
                investment_preference=investment_preference,
                customer_id=ev.customer_id,
                user_input=ev.user_input,
            )

    @step
    async def assess_risk_profile(self, ev: InvestmentPreferenceEvent, ctx: Context) -> RiskAssessmentEvent:
        """Step 3: Assess customer risk profile based on collected information.

        Analyzes the customer's risk tolerance, financial situation, and
        investment preferences to generate a comprehensive risk profile.
        """
        try:
            # Get previous events' data
            basic_info = ev.basic_info
            investment_preference = ev.investment_preference
            customer_id = ev.customer_id

            # Convert BasicInfo to dict with enum values as strings
            basic_info_dict = {
                "age": basic_info.age if basic_info else None,
                "city": basic_info.city if basic_info else None,
                "marital_status": basic_info.marital_status.value if basic_info else None,
                "employment_status": basic_info.employment_status.value if basic_info else None,
                "annual_income": basic_info.annual_income if basic_info and basic_info.annual_income else None,
                "dependents": basic_info.dependents if basic_info else 0,
            }

            # Convert InvestmentPreference to dict with enum values as strings
            investment_preference_dict = {
                "investable_assets": investment_preference.investable_assets,
                "max_loss_tolerance": investment_preference.max_loss_tolerance,
                "investment_horizon_years": investment_preference.investment_horizon_years,
                "risk_tolerance": investment_preference.risk_tolerance.value,
                "investment_goals": investment_preference.investment_goals or [],
                "preferred_investment_types": investment_preference.preferred_investment_types or [],
            }

            # Load prompt template with context
            prompt = self.prompt_loader.load_prompt_with_context(
                "risk_assessment.liquid",
                {
                    "basic_info": basic_info_dict,
                    "investment_preference": investment_preference_dict,
                },
            )

            # Stream LLM response chunk by chunk
            response_text = await self.__stream_llm_response__(prompt, "assess_risk_profile", ctx)

            # Parse JSON response using robust extraction
            data = extract_json_from_response(response_text)
            # Create RiskProfile model
            risk_profile = RiskProfile(
                risk_score=float(data.get("risk_score", 50)),
                risk_level=RiskTolerance(data.get("risk_level", "moderate")),
                risk_factors=data.get("risk_factors", []),
                suitability_notes=data.get("suitability_notes"),
            )

            # Completion event already emitted by __stream_llm_response__
            logger.info(
                f"Assessed risk profile: risk_score={risk_profile.risk_score}, risk_level={risk_profile.risk_level}"
            )
            return RiskAssessmentEvent(
                basic_info=basic_info,
                investment_preference=investment_preference,
                risk_profile=risk_profile,
                customer_id=customer_id,
            )

        except Exception as e:
            logger.error(f"Error assessing risk profile: {e}", exc_info=True)
            # Return default risk profile on error
            basic_info = ev.basic_info
            investment_preference = ev.investment_preference
            risk_profile = RiskProfile(
                risk_score=50.0,
                risk_level=RiskTolerance.MODERATE,
                risk_factors=["信息不足"],
                suitability_notes="由于信息不足，建议进行进一步咨询。",
            )
            return RiskAssessmentEvent(
                basic_info=basic_info,
                investment_preference=investment_preference,
                risk_profile=risk_profile,
                customer_id=ev.customer_id,
            )

    @step
    async def generate_customer_profile(self, ev: RiskAssessmentEvent, ctx: Context) -> StopEvent:
        """Step 4: Generate final customer profile and return results.

        Combines all collected information into a complete customer profile.
        """
        try:
            # Collect all information from previous steps
            basic_info = ev.basic_info
            investment_preference = ev.investment_preference
            risk_profile = ev.risk_profile
            customer_id = ev.customer_id

            # Create complete customer profile
            customer_profile = CustomerProfile(
                customer_id=customer_id,
                basic_info=basic_info,
                investment_preference=investment_preference,
                risk_profile=risk_profile,
                additional_notes=None,
                collected_at=None,
            )

            # Generate summary and recommendations
            # Convert models to dicts for template
            basic_info_dict = {
                "age": basic_info.age if basic_info else None,
                "city": basic_info.city if basic_info else None,
            }
            investment_preference_dict = {
                "investable_assets": investment_preference.investable_assets if investment_preference else None,
            }
            risk_profile_dict = {
                "risk_level": risk_profile.risk_level.value,
                "risk_score": risk_profile.risk_score,
            }

            # Load prompt template with context
            summary_prompt = self.prompt_loader.load_prompt_with_context(
                "investment_recommendation.liquid",
                {
                    "basic_info": basic_info_dict,
                    "investment_preference": investment_preference_dict,
                    "risk_profile": risk_profile_dict,
                },
            )

            # Stream LLM response chunk by chunk
            recommendation_text = await self.__stream_llm_response__(summary_prompt, "generate_customer_profile", ctx)

            # Prepare final result
            result = {
                "customer_profile": customer_profile.model_dump(),
                "recommendation": recommendation_text,
                "status": "completed",
            }

            logger.info(f"Generated customer profile for customer: {customer_profile.customer_id}")
            return StopEvent(result=result)

        except Exception as e:
            logger.error(f"Error generating customer profile: {e}", exc_info=True)
            return StopEvent(
                result={
                    "status": "error",
                    "error": str(e),
                    "message": "生成客户画像时发生错误",
                }
            )
