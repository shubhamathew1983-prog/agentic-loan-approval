from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
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

        # Compliance Checks
        compliance_flags = []
        protected_attributes_found = []

        # Age verification (must be 18+)
        age = applicant.get("age", 0)
        if age < 18:
            compliance_flags.append("Applicant under 18")

        # Identify protected attributes (for Fair Lending tracking)
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

        # Generate Case ID for manual reviews
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
                    "phone_valid": bool(phone and len(phone.replace("-", "").replace("+", "").replace(" ", "")) >= 10),
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
        """Execute compliance actions and trigger notifications."""

        actions_taken = []

        # Generate case ID if not present
        case_id = f"CASE-{str(uuid.uuid4())[:8].upper()}"

        # Determine notification type based on decision
        decision_class = decision.get("classification", "UNKNOWN")

        if decision_class == "APPROVED":
            action_type = "APPROVAL_NOTIFICATION"
            notification_template = "approval"
            actions_taken.append(f"Generate approval letter - {case_id}")
            actions_taken.append("Send approval email notification")
            actions_taken.append("Create loan document checklist")
            actions_taken.append("Schedule disbursement")

        elif decision_class == "REJECTED":
            action_type = "REJECTION_NOTIFICATION"
            notification_template = "rejection"
            actions_taken.append(f"Generate denial letter - {case_id}")
            actions_taken.append("Send rejection email notification")
            actions_taken.append("Log rejection reason for audit")
            actions_taken.append("Document compliance checks performed")

        else:  # REQUIRES_REVIEW
            action_type = "MANUAL_REVIEW_ASSIGNMENT"
            notification_template = "manual_review"
            actions_taken.append(f"Create manual review case - {case_id}")
            actions_taken.append("Assign to loan officer review queue")
            actions_taken.append("Send case assignment notification")
            actions_taken.append("Set escalation priority based on risk")

        # Log compliance action
        self._log_action(
            application_id,
            "Compliance actions executed",
            {
                "case_id": case_id,
                "decision_type": decision_class,
                "actions": actions_taken,
                "notification_template": notification_template,
                "risk_score": decision.get("risk_score"),
                "confidence": decision.get("confidence_level"),
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
            "executed_at": datetime.now().isoformat(),
        }
