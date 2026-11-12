from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from datetime import datetime
from typing import Dict, Any


class ApplicantProfileAgent(BaseAgent):
    """Analyzes applicant profile, employment, and income stability."""

    def __init__(self):
        super().__init__("ApplicantProfileAgent")

    async def analyze(self, agent_input: AgentInput) -> AgentOutput:
        """Analyze applicant profile data."""

        applicant = agent_input.applicant_data
        employment_years = applicant.get("years_employed", 0)
        annual_income = applicant.get("annual_income", 0)
        employment_type = applicant.get("employment_type", "unknown")

        # Calculate Income Stability Score
        income_stability_factors = {
            "stable_employment": 80 if employment_years >= 2 else 40,
            "adequate_income": 80 if annual_income >= 30000 else 50,
            "employment_type": 100 if employment_type == "full-time" else 60,
        }
        income_stability_score = sum(income_stability_factors.values()) / len(income_stability_factors)

        # Determine Employment Risk
        employment_risk = "Low"
        if employment_years < 0.5:
            employment_risk = "High"
        elif employment_years < 2:
            employment_risk = "Medium"

        # Credit History Summary (placeholder)
        credit_history_summary = {
            "years_of_history": employment_years,
            "employment_stability": employment_type,
        }

        # Application Completeness Flags
        completeness_flags = []
        if not applicant.get("first_name") or not applicant.get("last_name"):
            completeness_flags.append("Missing name information")
        if not applicant.get("email"):
            completeness_flags.append("Missing email")
        if annual_income == 0:
            completeness_flags.append("Missing income information")

        # Generate recommendation
        recommendation = "PROCEED"
        if employment_risk == "High" or income_stability_score < 50:
            recommendation = "REVIEW"
        if employment_years < 0.5 and annual_income < 20000:
            recommendation = "FLAG"

        confidence = self._calculate_confidence(income_stability_factors)

        risk_factors = []
        if employment_years < 2:
            risk_factors.append("Recent employment")
        if annual_income < 30000:
            risk_factors.append("Lower income")
        if employment_type != "full-time":
            risk_factors.append("Non-standard employment")

        return AgentOutput(
            agent_name=self.agent_name,
            analysis={
                "income_stability_score": income_stability_score,
                "employment_risk": employment_risk,
                "credit_history_summary": credit_history_summary,
                "completeness_flags": completeness_flags,
            },
            recommendation=recommendation,
            confidence_score=confidence,
            risk_factors=risk_factors,
            timestamp=datetime.now(),
        )
