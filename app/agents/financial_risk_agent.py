from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from datetime import datetime
from typing import Dict, Any


class FinancialRiskAgent(BaseAgent):
    """Analyzes financial metrics and risk assessment."""

    def __init__(self):
        super().__init__("FinancialRiskAgent")

    async def analyze(self, agent_input: AgentInput) -> AgentOutput:
        """Analyze financial risk factors."""

        credit_score = agent_input.financial_data.get("credit_score", 600)
        annual_income = agent_input.applicant_data.get("annual_income", 0)
        existing_liabilities = agent_input.financial_data.get("existing_liabilities", 0)
        loan_amount = agent_input.loan_details.get("loan_amount", 0)

        # Calculate Debt-to-Income Ratio
        monthly_income = annual_income / 12
        monthly_liabilities = existing_liabilities / 12 if existing_liabilities > 0 else 0
        monthly_loan_payment = (loan_amount / 60) if loan_amount > 0 else 0  # Assuming 60-month tenure
        total_monthly_debt = monthly_liabilities + monthly_loan_payment
        dti_ratio = (total_monthly_debt / monthly_income * 100) if monthly_income > 0 else 100

        # Credit Score Risk Level
        credit_score_risk = "Low"
        credit_score_factor = 80
        if credit_score < 550:
            credit_score_risk = "High"
            credit_score_factor = 20
        elif credit_score < 650:
            credit_score_risk = "Medium"
            credit_score_factor = 50
        elif credit_score < 700:
            credit_score_risk = "Medium-Low"
            credit_score_factor = 70

        # Loan Amount Risk
        loan_amount_risk = "Low"
        loan_amount_factor = 80
        max_loan = annual_income * 3  # Max loan is 3x annual income
        if loan_amount > max_loan:
            loan_amount_risk = "High"
            loan_amount_factor = 30
        elif loan_amount > annual_income * 2:
            loan_amount_risk = "Medium"
            loan_amount_factor = 60

        # DTI Risk Assessment
        dti_risk_factor = 80
        if dti_ratio > 60:
            dti_risk_factor = 20
        elif dti_ratio > 35:
            dti_risk_factor = 50
        elif dti_ratio <= 35:
            dti_risk_factor = 90

        # Detect Anomalies
        anomalies_detected = False
        anomalies = []
        if credit_score < 550:
            anomalies.append("Very low credit score")
            anomalies_detected = True
        if dti_ratio > 60:
            anomalies.append("Extremely high debt-to-income ratio")
            anomalies_detected = True
        if loan_amount > annual_income * 5:
            anomalies.append("Loan amount exceeds reasonable limits")
            anomalies_detected = True

        # Calculate confidence
        confidence_factors = {
            "credit_score": credit_score_factor,
            "dti_ratio": dti_risk_factor,
            "loan_amount": loan_amount_factor,
        }
        confidence = self._calculate_confidence(confidence_factors)

        # Generate recommendation
        recommendation = "APPROVE"
        if anomalies_detected or dti_ratio > 50 or credit_score < 600:
            recommendation = "REVIEW"
        if credit_score < 550 or dti_ratio > 60:
            recommendation = "REJECT"

        risk_factors = []
        if credit_score < 650:
            risk_factors.append(f"Credit score: {credit_score}")
        if dti_ratio > 35:
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
            },
            recommendation=recommendation,
            confidence_score=confidence,
            risk_factors=risk_factors,
            timestamp=datetime.now(),
        )
