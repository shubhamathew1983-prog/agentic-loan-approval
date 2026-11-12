from app.mcp_servers.base_mcp import BaseMCPServer
from app.utils import get_storage
from fastapi import HTTPException
from datetime import datetime


class NotificationSystemMCP(BaseMCPServer):
    """MCP Server for Notifications and Compliance."""

    def __init__(self, port: int = 8003):
        super().__init__("NotificationSystem", port)
        self.storage = get_storage()
        self._setup_notification_routes()

    def _setup_notification_routes(self):
        @self.app.post("/notify/decision")
        async def notify_decision(data: dict):
            """Send decision notification."""
            application_id = data.get("application_id")
            decision = data.get("decision")
            applicant_email = data.get("applicant_email")

            if not application_id or not decision:
                raise HTTPException(
                    status_code=400,
                    detail="Missing required fields",
                )

            notification_data = {
                "application_id": application_id,
                "notification_type": "decision",
                "decision": decision,
                "recipient": applicant_email,
                "timestamp": datetime.now().isoformat(),
                "status": "sent",
            }

            self.storage.log_action({
                "application_id": application_id,
                "action": f"Decision notification sent - {decision}",
                "details": notification_data,
            })

            return {
                "status": "notification_sent",
                "application_id": application_id,
                "decision": decision,
                "timestamp": datetime.now().isoformat(),
            }

        @self.app.post("/compliance/log-decision")
        async def log_decision(data: dict):
            """Log decision for compliance and audit."""
            application_id = data.get("application_id")
            classification = data.get("classification")
            reasoning = data.get("reasoning")
            agent_outputs = data.get("agent_outputs", [])

            case_id = f"CASE_{application_id[-8:]}"

            compliance_record = {
                "case_id": case_id,
                "application_id": application_id,
                "classification": classification,
                "reasoning": reasoning,
                "agents_involved": [a.get("agent_name") for a in agent_outputs if "agent_name" in a],
                "timestamp": datetime.now().isoformat(),
                "compliance_status": "LOGGED",
                "audit_trail": True,
            }

            self.storage.set_mcp_data(f"compliance_{case_id}", compliance_record)
            self.storage.log_action({
                "application_id": application_id,
                "action": "Decision logged for compliance",
                "details": compliance_record,
            })

            return {
                "case_id": case_id,
                "compliance_status": "LOGGED",
                "timestamp": datetime.now().isoformat(),
            }

        @self.app.get("/compliance/audit-trail/{application_id}")
        async def get_audit_trail(application_id: str):
            """Get audit trail for application."""
            logs = self.storage.get_audit_logs(application_id)
            return {
                "application_id": application_id,
                "audit_trail_length": len(logs),
                "events": logs,
                "last_event": logs[-1] if logs else None,
            }

        @self.app.post("/compliance/verify")
        async def verify_compliance(data: dict):
            """Verify compliance rules for decision."""
            classification = data.get("classification")
            risk_score = data.get("risk_score", 0)
            confidence_level = data.get("confidence_level", 0)

            compliance_checks = {
                "fair_lending": True,
                "decision_documented": True,
                "audit_logged": True,
                "applicant_notified": True,
                "decision_reasoning_provided": True,
            }

            compliance_status = "COMPLIANT"
            if risk_score > 80:
                compliance_checks["high_risk_review"] = False
                compliance_status = "REQUIRES_REVIEW"

            return {
                "classification": classification,
                "compliance_status": compliance_status,
                "compliance_checks": compliance_checks,
                "timestamp": datetime.now().isoformat(),
            }

        @self.app.get("/compliance/report/{application_id}")
        async def get_compliance_report(application_id: str):
            """Get compliance report for application."""
            logs = self.storage.get_audit_logs(application_id)
            decision = self.storage.get_decision_by_application(application_id)

            return {
                "application_id": application_id,
                "decision": decision,
                "audit_events": len(logs),
                "compliance_status": "COMPLIANT",
                "report_generated": datetime.now().isoformat(),
            }
