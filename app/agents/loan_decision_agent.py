from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from datetime import datetime
from typing import Dict, Any, List


class LoanDecisionAgent(BaseAgent):
    """Synthesizes decisions from other agents and provides final recommendation."""

    def __init__(self):
        super().__init__("LoanDecisionAgent")

    async def analyze(self, agent_input: AgentInput) -> AgentOutput:
        """Synthesize analysis from other agents."""

        # For now, this will be a placeholder that will receive input from orchestrator
        # The actual decision logic will be implemented in the orchestration layer

        analysis = {
            "decision_synthesis": "Pending orchestrator input",
            "pending_agents": [
                "ApplicantProfileAgent",
                "FinancialRiskAgent",
            ],
        }

        return AgentOutput(
            agent_name=self.agent_name,
            analysis=analysis,
            recommendation="PENDING",
            confidence_score=0.0,
            risk_factors=[],
            timestamp=datetime.now(),
        )

    async def synthesize_decision(
        self,
        application_id: str,
        agent_outputs: List[AgentOutput],
        applicant_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Synthesize final decision from multiple agent outputs."""

        recommendations = [output.recommendation for output in agent_outputs]
        confidence_scores = [output.confidence_score for output in agent_outputs]
        all_risk_factors = []
        for output in agent_outputs:
            all_risk_factors.extend(output.risk_factors)

        # Decision Logic
        decision = "REQUIRES_REVIEW"
        confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0

        reject_count = recommendations.count("REJECT") + recommendations.count("FLAG")
        approve_count = recommendations.count("APPROVE")
        review_count = recommendations.count("REVIEW")

        if reject_count > 0:
            decision = "REJECTED"
            confidence = max(confidence_scores) if confidence_scores else 0
        elif review_count > 0 or (confidence < 70 and approve_count == 0):
            decision = "REQUIRES_REVIEW"
        elif approve_count >= len(agent_outputs) - 1 and confidence >= 70:
            decision = "APPROVED"

        # Risk Score (0-100)
        risk_score = 100 - confidence

        # Key Decision Factors
        key_factors = []
        for i, output in enumerate(agent_outputs):
            if output.risk_factors:
                key_factors.extend(output.risk_factors[:2])

        # Generate Explanation
        explanation = self._generate_explanation(
            decision,
            agent_outputs,
            confidence,
            risk_score,
        )

        final_decision = {
            "application_id": application_id,
            "classification": decision,
            "risk_score": round(risk_score, 2),
            "confidence_level": round(confidence, 2),
            "key_factors": list(set(key_factors))[:5],  # Top 5 unique factors
            "explanation": explanation,
            "agent_outputs": [output.dict() for output in agent_outputs],
            "decided_at": datetime.now().isoformat(),
        }

        return final_decision

    def _generate_explanation(
        self,
        decision: str,
        agent_outputs: List[AgentOutput],
        confidence: float,
        risk_score: float,
    ) -> str:
        """Generate human-readable explanation of decision."""

        explanations = []

        for output in agent_outputs:
            if "credit_score_risk_level" in output.analysis:
                risk_level = output.analysis.get("credit_score_risk_level", "Unknown")
                dti = output.analysis.get("debt_to_income_ratio", 0)
                explanations.append(
                    f"Financial risk assessment shows {risk_level} credit score risk with DTI ratio of {dti}%."
                )

            if "employment_risk" in output.analysis:
                emp_risk = output.analysis.get("employment_risk", "Unknown")
                explanations.append(f"Employment risk level is {emp_risk}.")

        if decision == "APPROVED":
            base_text = f"Application APPROVED. Confidence level: {confidence:.1f}%."
        elif decision == "REJECTED":
            base_text = f"Application REJECTED. Risk score: {risk_score:.1f}."
        else:
            base_text = f"Application requires MANUAL REVIEW. Confidence: {confidence:.1f}%, Risk Score: {risk_score:.1f}."

        full_explanation = base_text + " " + " ".join(explanations)
        return full_explanation
