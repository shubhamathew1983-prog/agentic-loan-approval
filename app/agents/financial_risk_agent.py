from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.mcp_servers.mcp_client import get_mcp_client
from datetime import datetime
from typing import Dict, Any


class FinancialRiskAgent(BaseAgent):
    """Analyzes financial metrics and risk assessment."""

    def __init__(self):
        super().__init__("FinancialRiskAgent")

    async def analyze(self, agent_input: AgentInput) -> AgentOutput:
        """Analyze financial risk factors, delegating risk rules to RiskRulesDB MCP."""

        credit_score = agent_input.financial_data.get("credit_score", 600)
        annual_income = agent_input.applicant_data.get("annual_income", 0)
        existing_liabilities = agent_input.financial_data.get("existing_liabilities", 0)
        loan_amount = agent_input.loan_details.get("loan_amount", 0)

        # ── Fetch externalized thresholds from RiskRulesDB MCP ──────────────
        mcp = get_mcp_client()
        thresholds = await mcp.get_risk_thresholds()
        if thresholds:
            self.logger.info(
                f"[MCP] Risk thresholds loaded from RiskRulesDB: "
                f"credit critical={thresholds['credit_score']['critical']}, "
                f"dti critical={thresholds['dti_ratio']['critical']}"
            )
            cs_thresholds = thresholds["credit_score"]
            dti_thresholds = thresholds["dti_ratio"]
        else:
            # Local fallback defaults
            cs_thresholds = {"critical": 550, "high": 650, "medium": 700}
            dti_thresholds = {"critical": 60, "high": 50, "medium": 35}

        # ── Local financial calculations ─────────────────────────────────────
        monthly_income = annual_income / 12
        monthly_liabilities = existing_liabilities / 12 if existing_liabilities > 0 else 0
        monthly_loan_payment = (loan_amount / 60) if loan_amount > 0 else 0
        total_monthly_debt = monthly_liabilities + monthly_loan_payment
        dti_ratio = (total_monthly_debt / monthly_income * 100) if monthly_income > 0 else 100

        # Credit score risk (using MCP-sourced thresholds)
        credit_score_risk = "Low"
        credit_score_factor = 80
        if credit_score < cs_thresholds["critical"]:
            credit_score_risk = "High"
            credit_score_factor = 20
        elif credit_score < cs_thresholds["high"]:
            credit_score_risk = "Medium"
            credit_score_factor = 50
        elif credit_score < cs_thresholds["medium"]:
            credit_score_risk = "Medium-Low"
            credit_score_factor = 70

        # Loan amount risk
        loan_amount_risk = "Low"
        loan_amount_factor = 80
        max_loan = annual_income * 3
        if loan_amount > max_loan:
            loan_amount_risk = "High"
            loan_amount_factor = 30
        elif loan_amount > annual_income * 2:
            loan_amount_risk = "Medium"
            loan_amount_factor = 60

        # DTI risk factor (using MCP-sourced thresholds)
        dti_risk_factor = 80
        if dti_ratio > dti_thresholds["critical"]:
            dti_risk_factor = 20
        elif dti_ratio > dti_thresholds["medium"]:
            dti_risk_factor = 50
        else:
            dti_risk_factor = 90

        # ── Delegate risk assessment to RiskRulesDB MCP ─────────────────────
        mcp_risk = await mcp.assess_risk({
            "credit_score": credit_score,
            "dti_ratio": round(dti_ratio, 2),
            "annual_income": annual_income,
            "loan_amount": loan_amount,
        })
        if mcp_risk:
            self.logger.info(
                f"[MCP] Risk assessment from RiskRulesDB: "
                f"level={mcp_risk['risk_level']}, score={mcp_risk['risk_score']}"
            )
            # Override local credit risk with MCP-validated level
            credit_score_risk = mcp_risk["credit_score_risk"].capitalize()

        # ── Anomaly detection ────────────────────────────────────────────────
        anomalies_detected = False
        anomalies = []
        if credit_score < cs_thresholds["critical"]:
            anomalies.append("Very low credit score")
            anomalies_detected = True
        if dti_ratio > dti_thresholds["critical"]:
            anomalies.append("Extremely high debt-to-income ratio")
            anomalies_detected = True
        if loan_amount > annual_income * 5:
            anomalies.append("Loan amount exceeds reasonable limits")
            anomalies_detected = True

        # ── Confidence & recommendation ──────────────────────────────────────
        confidence_factors = {
            "credit_score": credit_score_factor,
            "dti_ratio": dti_risk_factor,
            "loan_amount": loan_amount_factor,
        }
        confidence = self._calculate_confidence(confidence_factors)

        recommendation = "APPROVE"
        if anomalies_detected or dti_ratio > 50 or credit_score < 600:
            recommendation = "REVIEW"
        if credit_score < cs_thresholds["critical"] or dti_ratio > dti_thresholds["critical"]:
            recommendation = "REJECT"

        risk_factors = []
        if credit_score < cs_thresholds["high"]:
            risk_factors.append(f"Credit score: {credit_score}")
        if dti_ratio > dti_thresholds["medium"]:
            risk_factors.append(f"DTI ratio: {dti_ratio:.1f}%")
        if loan_amount > annual_income:
            risk_factors.append("High loan-to-income ratio")

        return AgentOutput(
            agent_name=self.agent_name,
            analysis={
                "credit_score": credit_score,
                "credit_score_risk_level": credit_score_risk,
                "debt_to_income_ratio": round(dti_ratio, 2),
                "loan_amount_risk": loan_amount_risk,
                "monthly_income": round(monthly_income, 2),
                "total_monthly_debt": round(total_monthly_debt, 2),
                "anomalies_detected": anomalies_detected,
                "anomalies": anomalies,
                "mcp_risk_assessment": mcp_risk,
            },
            recommendation=recommendation,
            confidence_score=confidence,
            risk_factors=risk_factors,
            timestamp=datetime.now(),
        )
