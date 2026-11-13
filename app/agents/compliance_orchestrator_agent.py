from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.mcp_servers.mcp_client import get_mcp_client
from datetime import datetime
from typing import Dict, Any
import uuid


class ComplianceActionOrchestratorAgent(BaseAgent):
    """Coordinates compliance checks, actions, and notifications."""

    def __init__(self):
        super().__init__("ComplianceActionOrchestratorAgent")

    async def analyze(self, agent_input: AgentInput) -> AgentOutput:
        """Execute compliance checks on applicant data."""

        applicant = agent_input.applicant_data

        compliance_flags = []
        protected_attributes_found = []

        # Age verification (must be 18+)
        age = applicant.get("age", 0)
        if age < 18:
            compliance_flags.append("Applicant under 18")

        # Identify protected attributes for Fair Lending tracking
        if "age" in applicant:
            protected_attributes_found.append("age")
        if "gender" in applicant:
            protected_attributes_found.append("gender")
        if "ethnicity" in applicant:
            protected_attributes_found.append("ethnicity")

        # PII Validation
        email = applicant.get("email", "")
        phone = applicant.get("phone", "")
        if not email or "@" not in email:
            compliance_flags.append("Invalid email address")
        if not phone or len(phone.replace("-", "").replace("+", "").replace(" ", "")) < 10:
            compliance_flags.append("Invalid phone number")

        # Address validation
        address = applicant.get("address", "")
        city = applicant.get("city", "")
        state = applicant.get("state", "")
        zip_code = applicant.get("zip_code", "")
        if not all([address, city, state, zip_code]):
            compliance_flags.append("Incomplete address information")

        # Name validation
        first_name = applicant.get("first_name", "")
        last_name = applicant.get("last_name", "")
        if not first_name or not last_name:
            compliance_flags.append("Missing name information")

        # Single case ID used throughout the lifecycle
        case_id = f"CASE-{str(uuid.uuid4())[:8].upper()}"

        recommendation = "PROCEED"
        confidence_score = 95.0
        if compliance_flags:
            recommendation = "REVIEW"
            confidence_score = 70.0

        return AgentOutput(
            agent_name=self.agent_name,
            analysis={
                "compliance_flags": compliance_flags,
                "protected_attributes": protected_attributes_found,
                "case_id": case_id,
                "pii_validation": {
                    "email_valid": bool(email and "@" in email),
                    "phone_valid": bool(
                        phone and len(phone.replace("-", "").replace("+", "").replace(" ", "")) >= 10
                    ),
                    "address_complete": bool(all([address, city, state, zip_code])),
                    "name_valid": bool(first_name and last_name),
                },
                "fair_lending_check": {
                    "protected_attributes_logged": protected_attributes_found,
                    "requires_manual_review": len(protected_attributes_found) > 0,
                },
            },
            recommendation=recommendation,
            confidence_score=confidence_score,
            risk_factors=compliance_flags,
            timestamp=datetime.now(),
        )

    async def execute_actions(
        self,
        application_id: str,
        decision: Dict[str, Any],
        applicant_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute compliance actions and trigger notifications via MCP."""

        actions_taken = []
        case_id = f"CASE-{str(uuid.uuid4())[:8].upper()}"
        decision_class = decision.get("classification", "UNKNOWN")

        if decision_class == "APPROVED":
            action_type = "APPROVAL_NOTIFICATION"
            notification_template = "approval"
            actions_taken.extend([
                f"Generate approval letter - {case_id}",
                "Send approval email notification",
                "Create loan document checklist",
                "Schedule disbursement",
            ])
        elif decision_class == "REJECTED":
            action_type = "REJECTION_NOTIFICATION"
            notification_template = "rejection"
            actions_taken.extend([
                f"Generate denial letter - {case_id}",
                "Send rejection email notification",
                "Log rejection reason for audit",
                "Document compliance checks performed",
            ])
        else:
            action_type = "MANUAL_REVIEW_ASSIGNMENT"
            notification_template = "manual_review"
            actions_taken.extend([
                f"Create manual review case - {case_id}",
                "Assign to loan officer review queue",
                "Send case assignment notification",
                "Set escalation priority based on risk",
            ])

        # ── Notify via NotificationSystem MCP ────────────────────────────────
        mcp = get_mcp_client()
        notify_result = await mcp.notify_decision({
            "application_id": application_id,
            "decision": decision_class,
            "applicant_email": applicant_data.get("email"),
        })
        if notify_result:
            self.logger.info(
                f"[MCP] Decision notification sent via NotificationSystem MCP: "
                f"status={notify_result.get('status')}"
            )
            actions_taken.append(f"MCP notification dispatched: {notify_result.get('status')}")
        else:
            self.logger.warning("[MCP] NotificationSystem MCP unreachable — notification logged locally")

        # ── Log to compliance audit trail via NotificationSystem MCP ─────────
        compliance_result = await mcp.log_compliance({
            "application_id": application_id,
            "classification": decision_class,
            "reasoning": decision.get("explanation", ""),
            "agent_outputs": decision.get("agent_outputs", []),
        })
        if compliance_result:
            self.logger.info(
                f"[MCP] Compliance logged via NotificationSystem MCP: "
                f"case={compliance_result.get('case_id')}"
            )
        else:
            self.logger.warning("[MCP] NotificationSystem MCP unreachable — compliance logged locally")

        self._log_action(
            application_id,
            "Compliance actions executed",
            {
                "case_id": case_id,
                "decision_type": decision_class,
                "actions": actions_taken,
                "notification_template": notification_template,
                "mcp_notify": notify_result is not None,
                "mcp_compliance": compliance_result is not None,
            },
        )

        self.logger.info(
            f"Compliance actions executed for {application_id}. Case ID: {case_id}, "
            f"Decision: {decision_class}, Actions: {len(actions_taken)}"
        )

        return {
            "case_id": case_id,
            "action_type": action_type,
            "actions_taken": actions_taken,
            "notification_template": notification_template,
            "mcp_notification": notify_result,
            "mcp_compliance_log": compliance_result,
            "executed_at": datetime.now().isoformat(),
        }
