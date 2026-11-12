import asyncio
from typing import Dict, Any, List
from datetime import datetime
from app.agents import (
    ApplicantProfileAgent,
    FinancialRiskAgent,
    LoanDecisionAgent,
    ComplianceActionOrchestratorAgent,
    AgentInput,
)
from app.utils import get_storage, get_logger


class LoanApplicationOrchestrator:
    """Orchestrates multi-agent workflow for loan approval."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.storage = get_storage()

        # Initialize agents
        self.applicant_agent = ApplicantProfileAgent()
        self.financial_agent = FinancialRiskAgent()
        self.decision_agent = LoanDecisionAgent()
        self.compliance_agent = ComplianceActionOrchestratorAgent()

    async def process_application(
        self,
        application_id: str,
        applicant_data: Dict[str, Any],
        financial_data: Dict[str, Any],
        loan_details: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Process loan application through multi-agent workflow."""

        self.logger.info(f"Starting orchestration for application {application_id}")

        try:
            # Create agent input
            agent_input = AgentInput(
                application_id=application_id,
                applicant_data=applicant_data,
                financial_data=financial_data,
                loan_details=loan_details,
            )

            # Log orchestration start
            self.storage.log_action({
                "application_id": application_id,
                "action": "Orchestration started",
                "details": {
                    "applicant_id": applicant_data.get("applicant_id"),
                    "loan_amount": loan_details.get("loan_amount"),
                },
            })

            # Run compliance checks
            self.logger.info(f"Executing compliance checks for {application_id}")
            compliance_output = await self.compliance_agent.execute(agent_input)

            # Run financial and profile agents in parallel
            self.logger.info(f"Invoking financial and profile agents for {application_id}")
            agent_outputs = await self._run_agents_parallel(agent_input)

            # Synthesize decision
            self.logger.info(f"Synthesizing decision for {application_id}")
            final_decision = await self.decision_agent.synthesize_decision(
                application_id,
                agent_outputs,
                applicant_data,
            )

            # Store decision
            decision_id = self.storage.create_decision(final_decision)
            self.logger.info(f"Decision {decision_id} created for {application_id}")

            # Execute compliance actions
            self.logger.info(f"Executing compliance actions for {application_id}")
            compliance_result = await self.compliance_agent.execute_actions(
                application_id,
                final_decision,
                applicant_data,
            )

            # Update application status
            status_map = {
                "APPROVED": "approved",
                "REJECTED": "rejected",
                "REQUIRES_REVIEW": "manual_review",
            }
            new_status = status_map.get(final_decision["classification"], "under_review")

            self.storage.update_application(
                application_id,
                {
                    "status": new_status,
                    "decision_id": decision_id,
                    "case_id": compliance_result.get("case_id"),
                    "decision_made_at": datetime.now().isoformat(),
                },
            )

            # Log completion
            self.storage.log_action({
                "application_id": application_id,
                "action": "Orchestration completed",
                "details": {
                    "classification": final_decision["classification"],
                    "risk_score": final_decision["risk_score"],
                    "decision_id": decision_id,
                    "case_id": compliance_result.get("case_id"),
                    "compliance_actions": compliance_result.get("actions_taken"),
                },
            })

            return {
                "success": True,
                "application_id": application_id,
                "decision_id": decision_id,
                "case_id": compliance_result.get("case_id"),
                "decision": final_decision,
                "compliance_actions": compliance_result,
            }

        except Exception as e:
            self.logger.error(f"Error in orchestration for {application_id}: {str(e)}")
            self.storage.log_action({
                "application_id": application_id,
                "action": "Orchestration error",
                "details": {"error": str(e)},
                "status": "error",
            })
            raise

    async def _run_agents_parallel(self, agent_input: AgentInput) -> List:
        """Run agents in parallel."""
        tasks = [
            self.applicant_agent.execute(agent_input),
            self.financial_agent.execute(agent_input),
        ]

        agent_outputs = await asyncio.gather(*tasks)
        return agent_outputs

    async def get_orchestration_status(self, application_id: str) -> Dict[str, Any]:
        """Get current orchestration status."""
        application = self.storage.get_application(application_id)
        if not application:
            return {"status": "not_found"}

        decision = self.storage.get_decision_by_application(application_id)
        audit_logs = self.storage.get_audit_logs(application_id)

        return {
            "application_id": application_id,
            "application_status": application.get("status"),
            "decision": decision,
            "orchestration_steps": len(audit_logs),
            "last_updated": application.get("updated_at"),
        }
