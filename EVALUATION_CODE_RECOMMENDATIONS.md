# Code-Level Recommendations for Shubha Mathew's Submission

## Priority 1: Implement Missing Compliance Agent

### Problem
The case study requires 4 agents:
1. ✅ Applicant Profile Agent
2. ✅ Financial Risk Analysis Agent
3. ✅ Loan Decision Agent
4. ❌ **Compliance & Action Orchestrator Agent** - MISSING

### Recommended Implementation

```python
# app/agents/compliance_orchestrator_agent.py

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
        if applicant.get("age", 0) < 18:
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
        if not phone or len(phone.replace("-", "")) < 10:
            compliance_flags.append("Invalid phone number")
        
        # Address validation
        address = applicant.get("address", "")
        city = applicant.get("city", "")
        state = applicant.get("state", "")
        if not all([address, city, state]):
            compliance_flags.append("Incomplete address information")
        
        # Generate Case ID for manual reviews
        case_id = f"CASE-{str(uuid.uuid4())[:8].upper()}"
        
        recommendation = "PROCEED"
        if compliance_flags:
            recommendation = "REVIEW"
        
        return AgentOutput(
            agent_name=self.agent_name,
            analysis={
                "compliance_flags": compliance_flags,
                "protected_attributes": protected_attributes_found,
                "case_id": case_id,
                "pii_validation": {
                    "email_valid": bool(email and "@" in email),
                    "phone_valid": bool(phone and len(phone.replace("-", "")) >= 10),
                    "address_complete": bool(all([address, city, state])),
                },
                "fair_lending_check": {
                    "protected_attributes_logged": protected_attributes_found,
                    "requires_manual_review": len(protected_attributes_found) > 0,
                },
            },
            recommendation=recommendation,
            confidence_score=95.0 if not compliance_flags else 70.0,
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
            
        elif decision_class == "REJECTED":
            action_type = "REJECTION_NOTIFICATION"
            notification_template = "rejection"
            actions_taken.append(f"Generate denial letter - {case_id}")
            actions_taken.append("Send rejection email notification")
            actions_taken.append("Log rejection reason for audit")
            
        else:  # REQUIRES_REVIEW
            action_type = "MANUAL_REVIEW_ASSIGNMENT"
            notification_template = "manual_review"
            actions_taken.append(f"Create manual review case - {case_id}")
            actions_taken.append("Assign to loan officer review queue")
            actions_taken.append("Send case assignment notification")
        
        # Log compliance action
        self._log_action(
            application_id,
            "Compliance actions executed",
            {
                "case_id": case_id,
                "decision_type": decision_class,
                "actions": actions_taken,
                "notification_template": notification_template,
            },
        )
        
        return {
            "case_id": case_id,
            "action_type": action_type,
            "actions_taken": actions_taken,
            "notification_template": notification_template,
            "executed_at": datetime.now().isoformat(),
        }
```

### Integration into Orchestrator

```python
# app/orchestration/orchestrator.py - Add to imports

from app.agents import (
    ApplicantProfileAgent,
    FinancialRiskAgent,
    LoanDecisionAgent,
    ComplianceActionOrchestratorAgent,  # ADD THIS
    AgentInput,
)

class LoanApplicationOrchestrator:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.storage = get_storage()

        # Initialize agents
        self.applicant_agent = ApplicantProfileAgent()
        self.financial_agent = FinancialRiskAgent()
        self.decision_agent = LoanDecisionAgent()
        self.compliance_agent = ComplianceActionOrchestratorAgent()  # ADD THIS

    async def process_application(self, ...):
        # ... existing code ...
        
        # After decision synthesis, execute compliance actions
        compliance_result = await self.compliance_agent.execute_actions(
            application_id,
            final_decision,
            applicant_data,
        )
        
        # Store compliance action
        self.storage.log_action({
            "application_id": application_id,
            "action": "Compliance actions completed",
            "details": compliance_result,
        })
        
        return {
            "success": True,
            "application_id": application_id,
            "decision": final_decision,
            "compliance_case_id": compliance_result["case_id"],  # ADD THIS
        }
```

**Impact:** +10% score improvement, meets case study requirements

---

## Priority 2: Integrate Claude LLM for Decision Reasoning

### Problem
Current explanations are template-based:
```
"Application APPROVED. Confidence level: 85.0%. Employment risk level is Low. 
Financial risk assessment shows Low credit score risk with DTI ratio of 32.5%."
```

Should be natural language generated by Claude.

### Recommended Implementation

```python
# app/utils/llm_client.py - NEW FILE

from anthropic import AsyncAnthropic
import os
from app.utils import get_logger

logger = get_logger(__name__)
client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

async def generate_decision_explanation(
    decision: str,
    agents_analysis: list,
    applicant_info: dict,
    confidence: float,
    risk_score: float,
) -> str:
    """Generate natural language explanation using Claude."""
    
    analysis_text = "\n".join([
        f"- {agent.agent_name}: {agent.recommendation} (Confidence: {agent.confidence_score:.1f}%)"
        for agent in agents_analysis
    ])
    
    applicant_summary = f"{applicant_info.get('first_name')} {applicant_info.get('last_name')}"
    
    prompt = f"""
You are a loan approval specialist. Provide a clear, concise explanation for this loan decision.

Applicant: {applicant_summary}
Decision: {decision}
Overall Confidence: {confidence:.1f}%
Risk Score: {risk_score:.1f}

Agent Analysis:
{analysis_text}

Generate a professional, clear explanation suitable for:
1. The applicant to understand why the decision was made
2. Regulatory compliance documentation
3. Internal audit trails

Keep it to 2-3 sentences maximum. Be specific about the key factors.
"""

    message = await client.messages.create(
        model="claude-opus-5.5",
        max_tokens=256,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return message.content[0].text
```

### Integration into Loan Decision Agent

```python
# app/agents/loan_decision_agent.py - UPDATE _generate_explanation method

from app.utils.llm_client import generate_decision_explanation

async def _generate_explanation(
    self,
    decision: str,
    agent_outputs: List[AgentOutput],
    confidence: float,
    risk_score: float,
    applicant_data: Dict[str, Any],
) -> str:
    """Generate human-readable explanation using Claude LLM."""
    
    try:
        explanation = await generate_decision_explanation(
            decision,
            agent_outputs,
            applicant_data,
            confidence,
            risk_score,
        )
        return explanation
        
    except Exception as e:
        self.logger.warning(f"LLM explanation failed: {e}, using template fallback")
        # Fallback to template-based explanation
        return self._generate_template_explanation(
            decision, agent_outputs, confidence, risk_score
        )

async def synthesize_decision(
    self,
    application_id: str,
    agent_outputs: List[AgentOutput],
    applicant_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Synthesize final decision with LLM-generated explanation."""
    
    # ... existing decision logic ...
    
    # Generate LLM-based explanation
    explanation = await self._generate_explanation(
        decision,
        agent_outputs,
        confidence,
        risk_score,
        applicant_data,  # ADD THIS PARAMETER
    )
    
    final_decision = {
        # ... existing fields ...
        "explanation": explanation,  # Now LLM-generated
    }
```

**Environment Setup:**
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

**Impact:** +5-10% score improvement, significantly improves explanation quality

---

## Priority 3: Complete MCP Integration

### Problem
MCP servers exist but agents don't call them. Agents should query:
- **ApplicantDBMCP** for applicant history
- **RiskRulesDBMCP** for dynamic risk rules
- **NotificationSystemMCP** to send notifications

### Recommended Implementation

```python
# app/utils/mcp_client.py - NEW FILE

import httpx
from typing import Dict, Any
from app.utils import get_logger

logger = get_logger(__name__)

class MCPClient:
    """Client for interacting with MCP servers."""
    
    def __init__(self):
        self.applicant_db_url = "http://localhost:8001"
        self.risk_rules_url = "http://localhost:8002"
        self.notification_url = "http://localhost:8003"
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def get_applicant(self, applicant_id: str) -> Dict[str, Any]:
        """Get applicant profile from ApplicantDB MCP."""
        try:
            response = await self.client.get(
                f"{self.applicant_db_url}/applicants/{applicant_id}"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get applicant from MCP: {e}")
            return {}
    
    async def get_applicable_rules(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get applicable risk rules for profile."""
        try:
            response = await self.client.post(
                f"{self.risk_rules_url}/rules/evaluate",
                json=profile
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get rules from MCP: {e}")
            return {}
    
    async def send_notification(
        self,
        application_id: str,
        recipient_email: str,
        template: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Send notification via NotificationSystem MCP."""
        try:
            response = await self.client.post(
                f"{self.notification_url}/notifications/send",
                json={
                    "application_id": application_id,
                    "recipient_email": recipient_email,
                    "template": template,
                    "context": context,
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return {"status": "failed", "error": str(e)}

# Global client instance
mcp_client = MCPClient()
```

### Update Agents to Use MCP

```python
# app/agents/applicant_profile_agent.py - UPDATE

from app.utils.mcp_client import mcp_client

class ApplicantProfileAgent(BaseAgent):
    async def analyze(self, agent_input: AgentInput) -> AgentOutput:
        applicant = agent_input.applicant_data
        
        # Get applicant history from MCP
        try:
            applicant_history = await mcp_client.get_applicant(
                applicant.get("applicant_id")
            )
            # Use history for enhanced analysis
            previous_applications = applicant_history.get("previous_applications", 0)
        except Exception as e:
            self.logger.warning(f"Could not fetch applicant history: {e}")
            previous_applications = 0
        
        # ... rest of analysis using enhanced data ...
```

### Update Compliance Agent to Send Notifications

```python
# app/agents/compliance_orchestrator_agent.py - ADD notification logic

from app.utils.mcp_client import mcp_client

async def execute_actions(
    self,
    application_id: str,
    decision: Dict[str, Any],
    applicant_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Execute compliance actions and send notifications via MCP."""
    
    # ... existing action logic ...
    
    # Send notification via MCP
    recipient_email = applicant_data.get("email")
    template_type = {
        "APPROVED": "approval",
        "REJECTED": "rejection",
        "REQUIRES_REVIEW": "manual_review",
    }.get(decision.get("classification"), "general")
    
    notification_result = await mcp_client.send_notification(
        application_id=application_id,
        recipient_email=recipient_email,
        template=template_type,
        context={
            "applicant_name": f"{applicant_data.get('first_name')} {applicant_data.get('last_name')}",
            "case_id": case_id,
            "decision": decision.get("classification"),
            "explanation": decision.get("explanation"),
        }
    )
    
    self._log_action(
        application_id,
        "Notification sent",
        notification_result,
    )
```

**Impact:** +5% score improvement, enables dynamic rule evaluation

---

## Priority 4: Add Persistence Layer

### Problem
In-memory storage loses data on restart.

### Recommended Implementation

```python
# requirements.txt - ADD
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
```

```python
# app/database.py - NEW FILE

from sqlalchemy import create_engine, Column, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost/loan_approval"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Application(Base):
    __tablename__ = "applications"
    
    application_id = Column(String, primary_key=True)
    applicant_id = Column(String)
    status = Column(String)
    applicant_profile = Column(JSON)
    credit_score = Column(Float)
    loan_amount = Column(Float)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Decision(Base):
    __tablename__ = "decisions"
    
    decision_id = Column(String, primary_key=True)
    application_id = Column(String)
    classification = Column(String)
    risk_score = Column(Float)
    confidence = Column(Float)
    explanation = Column(String)
    created_at = Column(DateTime, default=datetime.now)

Base.metadata.create_all(bind=engine)
```

**Impact:** +3% score improvement, enables production deployment

---

## Priority 5: Improve Test Coverage

```python
# tests/test_agents.py - NEW FILE

import pytest
from app.agents import ApplicantProfileAgent, FinancialRiskAgent, LoanDecisionAgent
from app.agents.base_agent import AgentInput

@pytest.mark.asyncio
async def test_applicant_profile_agent():
    agent = ApplicantProfileAgent()
    
    agent_input = AgentInput(
        application_id="test_001",
        applicant_data={
            "first_name": "John",
            "last_name": "Doe",
            "age": 35,
            "annual_income": 80000,
            "years_employed": 5,
            "employment_type": "full-time",
        },
        financial_data={},
        loan_details={},
    )
    
    output = await agent.analyze(agent_input)
    
    assert output.agent_name == "ApplicantProfileAgent"
    assert output.recommendation in ["PROCEED", "REVIEW", "FLAG"]
    assert 0 <= output.confidence_score <= 100

@pytest.mark.asyncio
async def test_financial_risk_agent():
    agent = FinancialRiskAgent()
    
    agent_input = AgentInput(
        application_id="test_002",
        applicant_data={"annual_income": 100000},
        financial_data={
            "credit_score": 700,
            "existing_liabilities": 20000,
        },
        loan_details={"loan_amount": 150000},
    )
    
    output = await agent.analyze(agent_input)
    
    assert output.analysis["debt_to_income_ratio"] > 0
    assert output.analysis["credit_score_risk_level"] in ["Low", "Medium", "High"]
```

**Impact:** +2-3% score improvement

---

## Summary of Improvements

| Priority | Item | Effort | Impact | Total Impact |
|---|---|---|---|---|
| 1 | Compliance Agent | 2-3h | +10% | 18/10 → Capped at 10 |
| 2 | LLM Integration | 2-3h | +5-10% | Included in #1 |
| 3 | MCP Integration | 2-3h | +5% | Same |
| 4 | Persistence Layer | 2-3h | +3% | Same |
| 5 | Test Coverage | 4-6h | +2-3% | Same |

**Final Score Projection with All Improvements:** 9-9.5/10

---

**Implementation Priority Timeline:**
- **Week 1:** Implement Compliance Agent (#1) + LLM Integration (#2)
- **Week 2:** Complete MCP Integration (#3) + Add Tests (#5)
- **Week 3:** Add Persistence Layer (#4) + Polish & Documentation

All code examples follow the existing patterns and can be integrated directly.
