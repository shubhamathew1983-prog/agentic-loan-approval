# Quick Start: Demonstrating LangGraph Orchestration & MCP Servers

**Goal:** Show LangGraph orchestration, MCP servers, and Claude LLM integration in action.

**Time:** ~5 minutes setup + 2-5 seconds execution

---

## The Easiest Way: Demo Script

```bash
# Terminal 1: Start API server
cd /home/ubuntu/agentic-loan-approval
app/venv/bin/python -m uvicorn app.main:app --port 8000

# Terminal 2: Run demo (in new terminal)
cd /home/ubuntu/agentic-loan-approval
app/venv/bin/python demo_orchestration.py
```

**What you'll see:**
- LangGraph workflow diagram
- Test application submitted
- Full orchestration executed
- Decision with Claude-generated explanation
- Complete execution trace with all [NODE], [MCP], [LLM] calls

---

## Real-time Log Monitoring

```bash
# Terminal 1: API server
app/venv/bin/python -m uvicorn app.main:app --port 8000

# Terminal 2: Watch logs
tail -f logs/app.log | grep -E "\[NODE\]|\[MCP\]|\[LLM\]"

# Terminal 3: Submit test application
app/venv/bin/python demo_orchestration.py
```

**Watch for:**
- `[NODE]` entries showing orchestration steps
- `[MCP]` entries showing microservice calls
- `[LLM]` entries showing Claude API calls

---

## Interactive UI Demo

```bash
# Terminal 1: API server
app/venv/bin/python -m uvicorn app.main:app --port 8000

# Terminal 2: Streamlit UI
app/venv/bin/streamlit run app/ui/chatbot.py
```

Then in browser:
1. Go to `http://localhost:8501`
2. Fill out "Submit Application" form
3. Get Application ID from confirmation
4. Go to "Application Status" tab
5. Paste Application ID
6. See decision + Claude-generated explanation

---

## Test MCP Endpoints Directly

With API server running:

```bash
# Get risk thresholds
curl http://localhost:8000/mcp/risk/rules/thresholds | jq

# Get applicant income stability
curl http://localhost:8000/mcp/applicant/applicant/appl_demo_001/income-stability | jq

# Get risk assessment
curl -X POST http://localhost:8000/mcp/risk/risk/assess \
  -H "Content-Type: application/json" \
  -d '{
    "credit_score": 720,
    "dti_ratio": 40,
    "annual_income": 75000,
    "loan_amount": 50000
  }' | jq
```

---

## What's Actually Happening

### LangGraph Orchestration Flow:
```
START
  ↓
Compliance Check (Sequential)
  ↓
├─ Applicant Profile Agent (Parallel) 
│  ├─ [MCP] get_income_stability
│  ├─ [MCP] get_employment_risk
│  └─ [LLM] Generate credit narrative
│
└─ Financial Risk Agent (Parallel)
   ├─ [MCP] assess_risk
   ├─ [MCP] get_risk_thresholds
   └─ [LLM] Generate risk explanation
      ↓
Decision Synthesis (Sequential)
  ├─ Combine all agent outputs
  └─ [LLM] Generate decision explanation
     ↓
Compliance Actions (Sequential)
  ├─ [MCP] notify_decision
  └─ [MCP] log_compliance
     ↓
END
```

### MCP Servers Being Called:
1. **ApplicantDBMCP** (port 8001 → mounted at /mcp/applicant)
   - `get_income_stability()`
   - `get_employment_risk()`

2. **RiskRulesDBMCP** (port 8002 → mounted at /mcp/risk)
   - `assess_risk()`
   - `get_risk_thresholds()`

3. **NotificationSystemMCP** (port 8003 → mounted at /mcp/notification)
   - `notify_decision()`
   - `log_compliance()`

### Claude LLM Being Called:
1. **ApplicantProfileAgent**: Generate credit risk narrative
2. **LoanDecisionAgent**: Generate decision explanation

---

## Expected Log Output

When you run the demo, you'll see logs like:

```
[ORCHESTRATOR] Starting workflow for app_a1b2c3d4e5f6
[NODE] Executing compliance check for app_a1b2c3d4e5f6
[NODE] Executing applicant profile analysis for app_a1b2c3d4e5f6
[NODE] Executing financial risk analysis for app_a1b2c3d4e5f6
[MCP] get_income_stability → 200
[MCP] get_employment_risk → 200
[LLM] Calling claude-haiku-5-5 (max_tokens=1024)
[LLM] Response received (127 chars)
[MCP] assess_risk → 200
[MCP] get_risk_thresholds → 200
[NODE] Applicant profile analysis completed
[NODE] Financial risk analysis completed
[NODE] Synthesizing decision for app_a1b2c3d4e5f6
[LLM] Calling claude-haiku-5-5 (max_tokens=1024)
[LLM] Response received (186 chars)
[NODE] Decision synthesized: APPROVED (Risk: 25.5, Confidence: 85.0%)
[MCP] notify_decision → 200
[MCP] log_compliance → 200
[NODE] Compliance actions executed
[ORCHESTRATOR] Workflow completed for app_a1b2c3d4e5f6. Decision: APPROVED
```

---

## Key Files to Explore

- **demo_orchestration.py** — Runnable demo script
- **app/orchestration/langgraph_orchestrator.py** — StateGraph implementation
- **app/mcp_servers/mcp_client.py** — MCP HTTP client
- **app/utils/llm_client.py** — Claude API wrapper
- **app/agents/** — All 4 agent implementations
- **DEMO_GUIDE.md** — 8 different demonstration approaches

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `[MCP] get_income_stability → 404` | MCP servers not mounted | Restart API server |
| `[LLM] Authentication failed` | API key not set | `export ANTHROPIC_API_KEY=...` |
| `Connection refused` | API server not running | Start server in Terminal 1 |
| No `[NODE]` logs | Log level too high | Set `export LOG_LEVEL=DEBUG` |

---

## Performance

| Component | Time |
|-----------|------|
| Compliance Check | ~100ms |
| Applicant Profile Agent | ~500ms (includes LLM) |
| Financial Risk Agent | ~500ms (includes MCP calls) |
| Decision Synthesis | ~200ms (includes LLM) |
| Compliance Actions | ~100ms |
| **Total** | **~1-2 seconds** |

---

Ready to demo? Run this:

```bash
app/venv/bin/python demo_orchestration.py
```
