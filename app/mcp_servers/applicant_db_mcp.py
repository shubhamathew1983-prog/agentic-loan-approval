from app.mcp_servers.base_mcp import BaseMCPServer
from app.utils import get_storage
from fastapi import HTTPException


class ApplicantDBMCP(BaseMCPServer):
    """MCP Server for Applicant Profile Data."""

    def __init__(self, port: int = 8001):
        super().__init__("ApplicantDB", port)
        self.storage = get_storage()
        self._setup_applicant_routes()

    def _setup_applicant_routes(self):
        @self.app.get("/applicant/{applicant_id}")
        async def get_applicant(applicant_id: str):
            """Get applicant profile data."""
            applicant = self.storage.get_applicant(applicant_id)
            if not applicant:
                raise HTTPException(status_code=404, detail="Applicant not found")
            return applicant

        @self.app.post("/applicant")
        async def create_applicant(data: dict):
            """Create or update applicant profile."""
            applicant_id = self.storage.create_applicant(data)
            return {
                "applicant_id": applicant_id,
                "status": "created",
            }

        @self.app.get("/applicant/{applicant_id}/income-stability")
        async def get_income_stability(applicant_id: str):
            """Calculate income stability score."""
            applicant = self.storage.get_applicant(applicant_id)
            if not applicant:
                raise HTTPException(status_code=404, detail="Applicant not found")

            annual_income = applicant.get("annual_income", 0)
            years_employed = applicant.get("years_employed", 0)
            employment_type = applicant.get("employment_type", "unknown")

            # Calculate stability score
            stability_score = 0
            if years_employed >= 2:
                stability_score += 35
            elif years_employed >= 1:
                stability_score += 20
            elif years_employed >= 0.5:
                stability_score += 10

            if employment_type == "full-time":
                stability_score += 40
            elif employment_type == "part-time":
                stability_score += 20
            else:
                stability_score += 10

            if annual_income >= 50000:
                stability_score += 25
            elif annual_income >= 30000:
                stability_score += 15
            elif annual_income >= 20000:
                stability_score += 8

            return {
                "applicant_id": applicant_id,
                "income_stability_score": min(stability_score, 100),
                "annual_income": annual_income,
                "years_employed": years_employed,
                "employment_type": employment_type,
            }

        @self.app.get("/applicant/{applicant_id}/employment-risk")
        async def get_employment_risk(applicant_id: str):
            """Assess employment risk."""
            applicant = self.storage.get_applicant(applicant_id)
            if not applicant:
                raise HTTPException(status_code=404, detail="Applicant not found")

            years_employed = applicant.get("years_employed", 0)

            if years_employed < 0.5:
                risk = "HIGH"
            elif years_employed < 2:
                risk = "MEDIUM"
            else:
                risk = "LOW"

            return {
                "applicant_id": applicant_id,
                "employment_risk": risk,
                "years_employed": years_employed,
            }
