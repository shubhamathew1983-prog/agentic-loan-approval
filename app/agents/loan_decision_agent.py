from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.utils.llm_client import get_llm_client
from datetime import datetime
from typing import Dict, Any, List


class LoanDecisionAgent(BaseAgent):
    """Synthesizes decisions from other agents and provides final recommendation."""

    def __init__(self):
        super().__init__("LoanDecisionAgent")

    async def analyze(self, agent_input: AgentInput) -> AgentOutput:
        """Placeholder — real logic lives in synthesize_decision()."""
        return AgentOutput(
            agent_name=self.agent_name,
            analysis={
                "decision_synthesis": "Pending orchestrator input",
                "pending_agents": ["ApplicantProfileAgent", "FinancialRiskAgent"],
            },
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
        all_risk_factors: List[str] = []
        for output in agent_outputs:
            all_risk_factors.extend(output.risk_factors)

        # ── Decision logic ────────────────────────────────────────────────────
        confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        reject_count = recommendations.count("REJECT") + recommendations.count("FLAG")
        approve_count = recommendations.count("APPROVE")
        review_count = recommendations.count("REVIEW")

        decision = "REQUIRES_REVIEW"
        if reject_count > 0:
            decision = "REJECTED"
            confidence = max(confidence_scores) if confidence_scores else confidence
        elif review_count > 0 or (confidence < 70 and approve_count == 0):
            decision = "REQUIRES_REVIEW"
        elif approve_count >= len(agent_outputs) - 1 and confidence >= 70:
            decision = "APPROVED"

        risk_score = 100 - confidence

        key_factors: List[str] = []
        for output in agent_outputs:
            if output.risk_factors:
                key_factors.extend(output.risk_factors[:2])
        key_factors = list(set(key_factors))[:5]

        # ── LLM-generated explanation ─────────────────────────────────────────
        explanation = await self._generate_explanation_llm(
            decision, agent_outputs, confidence, risk_score, key_factors
        )
        if not explanation:
            explanation = self._generate_explanation_fallback(
                decision, agent_outputs, confidence, risk_score
            )

        return {
            "application_id": application_id,
            "classification": decision,
            "risk_score": round(risk_score, 2),
            "confidence_level": round(confidence, 2),
            "key_factors": key_factors,
            "explanation": explanation,
            "agent_outputs": [output.dict() for output in agent_outputs],
            "decided_at": datetime.now().isoformat(),
        }

    async def _generate_explanation_llm(
        self,
        decision: str,
        agent_outputs: List[AgentOutput],
        confidence: float,
        risk_score: float,
        key_factors: List[str],
    ) -> str:
        """Call Claude to produce a natural-language loan decision explanation."""
        llm = get_llm_client()

        # Build a compact summary of agent findings for the prompt
        agent_findings = []
        for output in agent_outputs:
            analysis = output.analysis
            if "credit_score_risk_level" in analysis:
                agent_findings.append(
                    f"Financial Risk Agent: credit risk={analysis['credit_score_risk_level']}, "
                    f"DTI={analysis.get('debt_to_income_ratio', 'N/A')}%, "
                    f"anomalies={analysis.get('anomalies_detected', False)}"
                )
            if "employment_risk" in analysis:
                agent_findings.append(
                    f"Applicant Profile Agent: employment risk={analysis['employment_risk']}, "
                    f"income stability={analysis.get('income_stability_score', 'N/A'):.0f}/100"
                    if isinstance(analysis.get('income_stability_score'), (int, float))
                    else f"Applicant Profile Agent: employment risk={analysis['employment_risk']}"
                )

        prompt = (
            "You are an AI loan officer. Write a clear, professional 3-sentence explanation "
            "for the following loan application decision. Address the applicant directly. "
            "Reference the key risk factors and be empathetic but precise.\n\n"
            f"Decision: {decision}\n"
            f"Risk Score: {risk_score:.1f}/100 (higher = riskier)\n"
            f"Confidence Level: {confidence:.1f}%\n"
            f"Key Risk Factors: {', '.join(key_factors) if key_factors else 'None identified'}\n"
            f"Agent Findings:\n" + "\n".join(f"  - {f}" for f in agent_findings) + "\n\n"
            "Provide only the explanation text, no headers or bullet points."
        )

        self.logger.info(f"[LLM] Requesting explanation for decision={decision}")
        return await llm.generate(prompt)

    def _generate_explanation_fallback(
        self,
        decision: str,
        agent_outputs: List[AgentOutput],
        confidence: float,
        risk_score: float,
    ) -> str:
        """Template-based fallback explanation when LLM is unavailable."""
        parts = []
        for output in agent_outputs:
            if "credit_score_risk_level" in output.analysis:
                risk_level = output.analysis.get("credit_score_risk_level", "Unknown")
                dti = output.analysis.get("debt_to_income_ratio", 0)
                parts.append(
                    f"Financial risk assessment shows {risk_level} credit score risk "
                    f"with DTI ratio of {dti}%."
                )
            if "employment_risk" in output.analysis:
                emp_risk = output.analysis.get("employment_risk", "Unknown")
                parts.append(f"Employment risk level is {emp_risk}.")

        if decision == "APPROVED":
            base = f"Application APPROVED. Confidence level: {confidence:.1f}%."
        elif decision == "REJECTED":
            base = f"Application REJECTED. Risk score: {risk_score:.1f}."
        else:
            base = (
                f"Application requires MANUAL REVIEW. "
                f"Confidence: {confidence:.1f}%, Risk Score: {risk_score:.1f}."
            )

        return base + " " + " ".join(parts)
