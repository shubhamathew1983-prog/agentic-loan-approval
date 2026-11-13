# Demonstration Guide: LangGraph Orchestration & MCP Servers

This guide shows how to visualize and demonstrate the LangGraph orchestration and MCP server invocations in action.

---

## 1. View LangGraph Workflow Diagram

### Option A: Get Mermaid Diagram (Programmatic)

```python
from app.orchestration import LangGraphOrchestrator

orchestrator = LangGraphOrchestrator()
mermaid_diagram = orchestrator.get_graph_visualization()
print(mermaid_diagram)
```

This outputs a Mermaid diagram showing:
```
flowchart TD
    START --> compliance["Compliance Check"]
    compliance --> applicant["Applicant Profile Agent (ASYNC)"]
    compliance --> financial["Financial Risk Agent (ASYNC)"]
    applicant --> decision["Decision Synthesis"]
    financial --> decision
    decision --> actions["Compliance Actions"]
    actions --> END
```

### Option B: Render in Browser

Save the Mermaid output to an HTML file:

```python
from app.orchestration import LangGraphOrchestrator

orchestrator = LangGraphOrchestrator()
mermaid = orchestrator.get_graph_visualization()

html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
</head>
<body>
    <div class="mermaid">
{mermaid}
    </div>
</body>
</html>
"""

with open("langgraph_workflow.html", "w") as f:
    f.write(html)
```

Then open `langgraph_workflow.html` in a browser.

---

## 2. Monitor Live Log Output (Recommended)

The best way to see orchestration and MCP calls is through **structured logging**.

### Start the server with logging:

```bash
cd /home/ubuntu/agentic-loan-approval
export LOG_LEVEL=INFO
app/venv/bin/python -m uvicorn app.main:app --port 8000 --log-level debug
```

### In another terminal, tail the logs:

```bash
tail -f logs/app.log | grep -E "\[NODE\]|\[MCP\]|\[LLM\]|\[ORCHESTRATOR\]"
```

### Expected Log Output:

```
[ORCHESTRATOR] Starting workflow for app_a1b2c3d4e5f6
[NODE] Executing compliance check for app_a1b2c3d4e5f6
[NODE] Compliance check completed. Case ID: CASE-ABC12345
[NODE] Executing applicant profile analysis for app_a1b2c3d4e5f6
[NODE] Executing financial risk analysis for app_a1b2c3d4e5f6
[MCP] get_income_stability → 200
[MCP] get_employment_risk → 200
[MCP] assess_risk → 200
[MCP] get_risk_thresholds → 200
[LLM] Calling claude-haiku-5-5 (max_tokens=1024)
[LLM] Response received (127 chars)
[NODE] Applicant profile analysis completed
[NODE] Financial risk analysis completed
[NODE] Synthesizing decision for app_a1b2c3d4e5f6
[LLM] Calling claude-haiku-5-5 (max_tokens=1024)
[LLM] Response received (186 chars)
[NODE] Decision synthesized: APPROVED (Risk: 25.5, Confidence: 85.0%)
[NODE] Executing compliance actions for app_a1b2c3d4e5f6
[MCP] notify_decision → 200
[MCP] log_compliance → 200
[NODE] Compliance actions executed
[ORCHESTRATOR] Workflow completed for app_a1b2c3d4e5f6. Decision: APPROVED
```

---

## 3. Create a Detailed Execution Trace Endpoint

Add this to `app/api/routes.py`:

```python
@router.get("/applications/{application_id}/execution-trace")
async def get_execution_trace(application_id: str):
    """Get detailed execution trace for an application."""
    logs = storage.get_audit_logs(application_id)
    
    trace = {
        "application_id": application_id,
        "workflow_steps": [],
        "mcp_calls": [],
        "llm_calls": [],
        "total_duration_ms": 0,
    }
    
    for log in logs:
        step = {
            "timestamp": log.get("timestamp"),
            "action": log.get("action"),
            "agent": log.get("agent_name", "system"),
            "details": log.get("details", {}),
        }
        
        if "[MCP]" in log.get("action", ""):
            trace["mcp_calls"].append(step)
        elif "[LLM]" in log.get("action", ""):
            trace["llm_calls"].append(step)
        else:
            trace["workflow_steps"].append(step)
    
    return trace
```

### Usage:

```bash
curl http://localhost:8000/api/applications/app_xxxxx/execution-trace | jq
```

### Sample Response:

```json
{
  "application_id": "app_xxxxx",
  "workflow_steps": [
    {
      "timestamp": "2026-11-13T10:00:00.000",
      "action": "Compliance check completed",
      "agent": "ComplianceActionOrchestratorAgent",
      "details": {"case_id": "CASE-ABC123"}
    },
    {
      "timestamp": "2026-11-13T10:00:01.500",
      "action": "Decision synthesized",
      "agent": "LoanDecisionAgent",
      "details": {"classification": "APPROVED", "confidence": 85.0}
    }
  ],
  "mcp_calls": [
    {
      "timestamp": "2026-11-13T10:00:00.200",
      "action": "get_income_stability",
      "agent": "ApplicantProfileAgent"
    },
    {
      "timestamp": "2026-11-13T10:00:00.300",
      "action": "assess_risk",
      "agent": "FinancialRiskAgent"
    }
  ],
  "llm_calls": [
    {
      "timestamp": "2026-11-13T10:00:00.800",
      "action": "LLM credit narrative generation",
      "agent": "ApplicantProfileAgent"
    }
  ]
}
```

---

## 4. Add Visualization Dashboard

Create `app/ui/dashboard.py`:

```python
import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(page_title="Orchestration Dashboard", layout="wide")
st.title("🔄 LangGraph Orchestration Dashboard")

# Get execution trace
app_id = st.text_input("Application ID", "")

if app_id:
    try:
        response = requests.get(f"http://localhost:8000/api/applications/{app_id}/execution-trace")
        trace = response.json()
        
        # Display workflow steps
        st.subheader("🔗 Workflow Execution")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Steps", len(trace["workflow_steps"]))
        with col2:
            st.metric("MCP Calls", len(trace["mcp_calls"]))
        with col3:
            st.metric("LLM Calls", len(trace["llm_calls"]))
        
        # Timeline visualization
        st.subheader("📊 Execution Timeline")
        for step in trace["workflow_steps"]:
            with st.expander(f"{step['timestamp']} — {step['action']}"):
                st.json(step)
        
        # MCP calls
        st.subheader("🔌 MCP Server Invocations")
        for call in trace["mcp_calls"]:
            st.write(f"✓ {call['timestamp']} — {call['action']} ({call['agent']})")
        
        # LLM calls
        st.subheader("🤖 Claude LLM Calls")
        for call in trace["llm_calls"]:
            st.write(f"✓ {call['timestamp']} — {call['action']} ({call['agent']})")
            
    except Exception as e:
        st.error(f"Error loading trace: {e}")
```

### Run:

```bash
app/venv/bin/streamlit run app/ui/dashboard.py
```

---

## 5. Create a Live Demo Script

Create `demo_orchestration.py`:

```python
#!/usr/bin/env python
"""Live demonstration of LangGraph orchestration and MCP servers."""

import asyncio
import json
from datetime import datetime
from app.orchestration import LangGraphOrchestrator
from app.utils import get_storage

async def demo():
    print("\n" + "="*80)
    print("LANGGRAPH ORCHESTRATION & MCP SERVER DEMONSTRATION")
    print("="*80 + "\n")
    
    # 1. Show workflow diagram
    print("1️⃣  WORKFLOW ARCHITECTURE")
    print("-" * 80)
    orchestrator = LangGraphOrchestrator()
    diagram = orchestrator.get_graph_visualization()
    print(diagram)
    
    # 2. Create test application
    print("\n2️⃣  SUBMITTING TEST APPLICATION")
    print("-" * 80)
    storage = get_storage()
    app_data = {
        "applicant_id": "appl_demo_001",
        "applicant_profile": {
            "applicant_id": "appl_demo_001",
            "first_name": "John",
            "last_name": "Demo",
            "age": 35,
            "email": "john@example.com",
            "phone": "+1-234-567-8900",
            "address": "123 Main St",
            "city": "Boston",
            "state": "MA",
            "zip_code": "02101",
            "employment_type": "full-time",
            "employer": "Tech Corp",
            "annual_income": 75000,
            "years_employed": 5,
        },
        "credit_score": 720,
        "loan_amount": 50000,
        "loan_tenure_months": 60,
        "existing_liabilities": 15000,
        "location": "Boston, MA",
    }
    
    app_id = storage.create_application(app_data)
    storage.create_applicant(app_data["applicant_profile"])
    print(f"✓ Application created: {app_id}\n")
    
    # 3. Run orchestration
    print("3️⃣  RUNNING LANGGRAPH ORCHESTRATION")
    print("-" * 80)
    
    input_data = {
        "application_id": app_id,
        "applicant_data": app_data["applicant_profile"],
        "financial_data": {
            "credit_score": app_data["credit_score"],
            "annual_income": app_data["applicant_profile"]["annual_income"],
            "years_employed": app_data["applicant_profile"]["years_employed"],
            "existing_liabilities": app_data["existing_liabilities"],
        },
        "loan_details": {
            "loan_amount": app_data["loan_amount"],
            "loan_tenure_months": app_data["loan_tenure_months"],
            "location": app_data["location"],
        },
    }
    
    try:
        result = await orchestrator.invoke(input_data)
        
        print("✓ Orchestration completed successfully!\n")
        print("Decision:", result["decision"]["classification"])
        print("Risk Score:", result["decision"]["risk_score"])
        print("Confidence:", result["decision"]["confidence_level"], "%")
        print("Case ID:", result["case_id"])
        
    except Exception as e:
        print(f"❌ Orchestration failed: {e}")
        return
    
    # 4. Show execution trace
    print("\n4️⃣  EXECUTION TRACE & AUDIT LOG")
    print("-" * 80)
    logs = storage.get_audit_logs(app_id)
    
    mcp_calls = [l for l in logs if "MCP" in str(l.get("details", {}))]
    llm_calls = [l for l in logs if "LLM" in str(l.get("details", {}))]
    
    print(f"Total audit log entries: {len(logs)}")
    print(f"MCP server calls: {len(mcp_calls)}")
    print(f"LLM calls: {len(llm_calls)}\n")
    
    print("📋 AUDIT LOG:")
    for log in logs:
        timestamp = log.get("timestamp", "")
        action = log.get("action", "")
        agent = log.get("agent_name", "system")
        print(f"  [{timestamp}] {agent}: {action}")
    
    # 5. Show decision details
    print("\n5️⃣  DECISION DETAILS & EXPLANATION")
    print("-" * 80)
    decision = result["decision"]
    print(f"Classification: {decision['classification']}")
    print(f"Risk Score: {decision['risk_score']}/100")
    print(f"Confidence: {decision['confidence_level']}%")
    print(f"\nExplanation:\n{decision['explanation']}")
    
    print("\n" + "="*80)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(demo())
```

### Run:

```bash
cd /home/ubuntu/agentic-loan-approval
app/venv/bin/python demo_orchestration.py
```

---

## 6. Use Streamlit UI to Show Live Flow

The existing Streamlit app shows:
1. **Submit Application** — Triggers orchestration
2. **Application Status** — Shows decision & case ID
3. **Dashboard** — Shows overall metrics

### Run Streamlit:

```bash
app/venv/bin/streamlit run app/ui/chatbot.py
```

Then:
1. Go to "Submit Application"
2. Submit a test application
3. Note the Application ID
4. Go to "Application Status"
5. Enter the Application ID
6. See the decision with Claude-generated explanation

---

## 7. Check MCP Endpoints Directly

### Test ApplicantDB MCP:

```bash
curl http://localhost:8000/mcp/applicant/applicant/appl_xxx/income-stability
```

Response:
```json
{
  "applicant_id": "appl_xxx",
  "income_stability_score": 85.0,
  "annual_income": 75000,
  "years_employed": 5,
  "employment_type": "full-time"
}
```

### Test RiskRulesDB MCP:

```bash
curl http://localhost:8000/mcp/risk/rules/thresholds
```

Response:
```json
{
  "credit_score": {
    "critical": 550,
    "high": 650,
    "medium": 700,
    "low": 750
  },
  "dti_ratio": {
    "critical": 60,
    "high": 50,
    "medium": 35,
    "acceptable": 35
  }
}
```

---

## 8. Docker-Based Full Stack Demo

Create `docker-compose.demo.yml`:

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - LOG_LEVEL=DEBUG
    volumes:
      - ./logs:/app/logs
  
  streamlit:
    build: .
    command: streamlit run app/ui/chatbot.py
    ports:
      - "8501:8501"
    depends_on:
      - app
```

### Run:

```bash
docker-compose -f docker-compose.demo.yml up
```

Access:
- API: `http://localhost:8000`
- Streamlit: `http://localhost:8501`

---

## Summary: Best Ways to Demonstrate

| Method | Best For | Difficulty |
|--------|----------|-----------|
| **Logs** | Seeing real-time execution flow | ⭐ Easy |
| **Demo Script** | Complete end-to-end walkthrough | ⭐ Easy |
| **Streamlit UI** | Interactive user-friendly demo | ⭐⭐ Medium |
| **Execution Trace API** | Programmatic analysis | ⭐⭐ Medium |
| **Mermaid Diagram** | Architecture visualization | ⭐⭐⭐ Hard |
| **Docker Compose** | Full stack deployment | ⭐⭐⭐ Hard |

---

## Recommended Demo Flow

1. **Show architecture:** Run the demo script to show workflow diagram
2. **Live execution:** Submit an application via Streamlit UI
3. **Monitor logs:** Watch `[NODE]`, `[MCP]`, `[LLM]` log entries
4. **Check results:** See decision with Claude-generated explanation
5. **Test MCP:** Call MCP endpoints directly to show they're working

This demonstrates:
- ✅ LangGraph orchestration (nodes, parallel execution, state management)
- ✅ MCP servers operational (HTTP calls working)
- ✅ Claude LLM integration (narrative & explanation generation)
- ✅ Audit trail (complete trace of all steps)
