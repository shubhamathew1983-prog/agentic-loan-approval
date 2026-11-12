from app.mcp_servers.base_mcp import BaseMCPServer
from app.utils import get_storage
from fastapi import HTTPException


class RiskRulesDBMCP(BaseMCPServer):
    """MCP Server for Risk Assessment Rules."""

    def __init__(self, port: int = 8002):
        super().__init__("RiskRulesDB", port)
        self.storage = get_storage()
        self._setup_risk_routes()

    def _setup_risk_routes(self):
        @self.app.post("/risk/assess")
        async def assess_risk(data: dict):
            """Assess financial risk."""
            credit_score = data.get("credit_score", 600)
            dti_ratio = data.get("dti_ratio", 50)
            annual_income = data.get("annual_income", 0)
            loan_amount = data.get("loan_amount", 0)

            risk_level = "LOW"
            risk_score = 20

            # Credit score risk
            if credit_score < 550:
                risk_level = "CRITICAL"
                risk_score += 40
            elif credit_score < 650:
                risk_level = "HIGH"
                risk_score += 30
            elif credit_score < 700:
                risk_level = "MEDIUM"
                risk_score += 15
            else:
                risk_score += 5

            # DTI ratio risk
            if dti_ratio > 60:
                if risk_level == "LOW":
                    risk_level = "HIGH"
                risk_score += 30
            elif dti_ratio > 35:
                if risk_level in ["LOW", "MEDIUM"]:
                    risk_level = "MEDIUM"
                risk_score += 15
            else:
                risk_score += 5

            # Loan amount risk
            if annual_income > 0:
                loan_to_income = (loan_amount / annual_income) * 100
                if loan_to_income > 300:
                    risk_score += 20
                elif loan_to_income > 200:
                    risk_score += 10

            return {
                "risk_level": risk_level,
                "risk_score": min(risk_score, 100),
                "credit_score_risk": self._get_credit_risk(credit_score),
                "dti_ratio_risk": self._get_dti_risk(dti_ratio),
            }

        @self.app.post("/risk/rules")
        async def get_rules(data: dict):
            """Get applicable risk rules."""
            credit_score = data.get("credit_score", 600)
            dti_ratio = data.get("dti_ratio", 50)

            rules = []

            if credit_score < 550:
                rules.append({
                    "rule": "CRITICAL_CREDIT",
                    "message": "Credit score below 550 - HIGH RISK",
                    "action": "REJECT",
                })
            if dti_ratio > 60:
                rules.append({
                    "rule": "HIGH_DEBT_RATIO",
                    "message": f"DTI ratio {dti_ratio}% exceeds 60% limit",
                    "action": "REVIEW",
                })
            if credit_score >= 700 and dti_ratio <= 35:
                rules.append({
                    "rule": "APPROVED_CRITERIA_MET",
                    "message": "Meets automatic approval criteria",
                    "action": "APPROVE",
                })

            return {"applicable_rules": rules}

        @self.app.get("/rules/thresholds")
        async def get_thresholds():
            """Get risk thresholds."""
            return {
                "credit_score": {
                    "critical": 550,
                    "high": 650,
                    "medium": 700,
                    "low": 750,
                },
                "dti_ratio": {
                    "critical": 60,
                    "high": 50,
                    "medium": 35,
                    "acceptable": 35,
                },
                "income": {
                    "minimum": 15000,
                    "recommended": 30000,
                },
            }

    def _get_credit_risk(self, score: int) -> str:
        if score < 550:
            return "CRITICAL"
        elif score < 650:
            return "HIGH"
        elif score < 700:
            return "MEDIUM"
        else:
            return "LOW"

    def _get_dti_risk(self, ratio: float) -> str:
        if ratio > 60:
            return "CRITICAL"
        elif ratio > 50:
            return "HIGH"
        elif ratio > 35:
            return "MEDIUM"
        else:
            return "LOW"
