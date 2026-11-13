from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.mcp_servers.mcp_client import get_mcp_client
from app.utils.llm_client import get_llm_client
from datetime import datetime
from typing import Dict, Any


class ApplicantProfileAgent(BaseAgent):
    """Analyzes applicant profile, employment, and income stability."""

    def __init__(self):
        super().__init__("ApplicantProfileAgent")

    async def analyze(self, agent_input: AgentInput) -> AgentOutput:
        """Analyze applicant profile data, delegating lookups to ApplicantDB MCP."""

        applicant = agent_input.applicant_data
        applicant_id = applicant.get("applicant_id", "")
        employment_years = applicant.get("years_employed", 0)
        annual_income = applicant.get("annual_income", 0)
        employment_type = applicant.get("employment_type", "unknown")

        # ── Local baseline calculations ───────────────────────────────────────
        income_stability_factors = {
            "stable_employment": 80 if employment_years >= 2 else 40,
            "adequate_income": 80 if annual_income >= 30000 else 50,
            "employment_type": 100 if employment_type == "full-time" else 60,
        }
        income_stability_score = sum(income_stability_factors.values()) / len(income_stability_factors)

        employment_risk = "Low"
        if employment_years < 0.5:
            employment_risk = "High"
        elif employment_years < 2:
            employment_risk = "Medium"

        # ── Delegate to ApplicantDB MCP ───────────────────────────────────────
        mcp = get_mcp_client()
        if applicant_id:
            mcp_stability = await mcp.get_income_stability(applicant_id)
            if mcp_stability:
                self.logger.info(
                    f"[MCP] Income stability from ApplicantDB: "
                    f"score={mcp_stability['income_stability_score']}"
                )
                income_stability_score = mcp_stability["income_stability_score"]

            mcp_employment = await mcp.get_employment_risk(applicant_id)
            if mcp_employment:
                self.logger.info(
                    f"[MCP] Employment risk from ApplicantDB: "
                    f"risk={mcp_employment['employment_risk']}"
                )
                employment_risk = mcp_employment["employment_risk"].capitalize()

        # ── LLM-generated credit history narrative ────────────────────────────
        llm = get_llm_client()
        credit_history_prompt = (
            f"You are a credit analyst. Write a 2-sentence professional credit risk narrative "
            f"for a loan applicant with the following profile:\n"
            f"- Annual income: ${annual_income:,.0f}\n"
            f"- Employment type: {employment_type}\n"
            f"- Years employed: {employment_years}\n"
            f"- Income stability score: {income_stability_score:.0f}/100\n"
            f"- Employment risk: {employment_risk}\n"
            f"Be objective and reference the key risk indicators."
        )
        credit_narrative = await llm.generate(credit_history_prompt)
        if not credit_narrative:
            credit_narrative = (
                f"Employment-based profile: {employment_type} for {employment_years} year(s). "
                f"Income stability score: {income_stability_score:.0f}/100."
            )
        self.logger.info(f"[LLM] Credit history narrative generated ({len(credit_narrative)} chars)")

        credit_history_summary = {
            "narrative": credit_narrative,
            "years_of_history": employment_years,
            "employment_stability": employment_type,
            "income_stability_score": round(income_stability_score, 1),
        }

        # ── Application completeness flags ────────────────────────────────────
        completeness_flags = []
        if not applicant.get("first_name") or not applicant.get("last_name"):
            completeness_flags.append("Missing name information")
        if not applicant.get("email"):
            completeness_flags.append("Missing email")
        if annual_income == 0:
            completeness_flags.append("Missing income information")

        # ── Recommendation ────────────────────────────────────────────────────
        recommendation = "PROCEED"
        if employment_risk in ("High", "HIGH") or income_stability_score < 50:
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
