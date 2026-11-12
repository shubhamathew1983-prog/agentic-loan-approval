# System Architecture

## Overview

The Agentic AI Intelligent Loan Approval System implements a distributed, microservices-based multi-agent architecture with Claude Haiku 4.5 LLM integration.

---

## Architecture Layers

### 1. Presentation Layer
```
┌─────────────────────────────┐
│     Streamlit UI            │
│  (app/ui/chatbot.py)        │
├─────────────────────────────┤
│ • Application Form          │
│ • Status Tracking           │
│ • Dashboard                 │
│ • Decision Display          │
└─────────────────────────────┘
```

**Responsibilities:**
- User interface for loan applications
- Real-time status tracking
- Dashboard with metrics
- Decision presentation

---

### 2. API Layer (FastAPI)
```
┌─────────────────────────────┐
│     FastAPI Server          │
│   (app/main.py)             │
├─────────────────────────────┤
│ app/api/routes.py           │
├─────────────────────────────┤
│ POST   /api/applications    │
│ GET    /api/applications    │
│ GET    /api/health          │
└─────────────────────────────┘
```

**Responsibilities:**
- HTTP request handling
- Request validation
- Response formatting
- CORS support
- OpenAPI documentation

---

### 3. Storage Layer (In-Memory)
```
┌─────────────────────────────┐
│  In-Memory Storage          │
│  (app/utils/storage.py)     │
├─────────────────────────────┤
│ • Applications              │
│ • Applicants                │
│ • Decisions                 │
│ • Audit Logs                │
│ • MCP Data                  │
└─────────────────────────────┘
```

**Features:**
- Thread-safe access
- Dictionary-based storage
- Optional JSON persistence
- Unique ID generation
- Data querying capabilities

---

### 4. Orchestration Layer (LangGraph)
```
┌─────────────────────────────┐
│   Orchestrator              │
│ (app/orchestration/)        │
├─────────────────────────────┤
│ • Workflow Coordination     │
│ • Agent Invocation          │
│ • Parallel Execution        │
│ • State Management          │
│ • Decision Synthesis        │
└─────────────────────────────┘
```

**Orchestration Flow:**
```
Application Submitted
        ↓
Create Agent Input
        ↓
┌─────────────────────────────┐
│ Run Agents in Parallel      │
├─────────────────────────────┤
│ ✓ Applicant Profile Agent   │
│ ✓ Financial Risk Agent      │
└─────────────────────────────┘
        ↓
Collect Agent Outputs
        ↓
Loan Decision Agent
(Synthesize Decision)
        ↓
Generate Explanation
        ↓
Log Decision & Update Status
```

---

### 5. Agent Layer

#### Architecture
```
┌─────────────────────────────────┐
│   BaseAgent (Abstract)          │
│  (app/agents/base_agent.py)     │
├─────────────────────────────────┤
│ • async analyze()               │
│ • async execute()               │
│ • _log_action()                 │
│ • _calculate_confidence()       │
└─────────────────────────────────┘
        ↑         ↑         ↑
    ┌───┴──┐  ┌──┴──┐  ┌──┴─────┐
    │      │  │     │  │        │
 [Agent1] [Agent2] [Agent3]
```

#### Agents

**1. Applicant Profile Agent**
```
Input:
├── Applicant ID
├── First/Last Name
├── Age, Email
├── Employment Type
├── Employer, Annual Income
└── Years Employed

Processing:
├── Calculate Income Stability Score
├── Assess Employment Risk
├── Evaluate Credit History
└── Flag Completeness Issues

Output:
├── Income Stability (0-100)
├── Employment Risk (Low/Med/High)
├── Credit History Summary
├── Completeness Flags
└── Recommendation (PROCEED/REVIEW/FLAG)
```

**2. Financial Risk Agent**
```
Input:
├── Credit Score
├── Annual Income
├── Existing Liabilities
├── Loan Amount
└── Loan Tenure

Processing:
├── Calculate Debt-to-Income Ratio
├── Assess Credit Score Risk
├── Evaluate Loan Amount Risk
└── Detect Anomalies

Output:
├── DTI Ratio (%)
├── Credit Score Risk Level
├── Loan Amount Risk
├── Anomalies Detected
├── Risk Factors
└── Recommendation (APPROVE/REVIEW/REJECT)
```

**3. Loan Decision Agent**
```
Input:
├── Agent Output 1 (Profile Analysis)
├── Agent Output 2 (Financial Analysis)
└── Applicant Data

Processing:
├── Synthesize Recommendations
├── Calculate Confidence Scores
├── Generate Explanation
├── Determine Final Classification
└── Calculate Risk Score

Output:
├── Classification (APPROVED/REJECTED/REQUIRES_REVIEW)
├── Risk Score (0-100)
├── Confidence Level (0-100)
├── Key Decision Factors
├── Detailed Explanation
└── Agent Outputs
```

---

### 6. MCP Server Layer

```
┌────────────────────────────────────┐
│     MCP Servers (Model Context)    │
│     (app/mcp_servers/)             │
├────────────────────────────────────┤
│ ┌──────────────────────────┐       │
│ │ ApplicantDB MCP (8001)   │       │
│ ├──────────────────────────┤       │
│ │ • Get Applicant Profile  │       │
│ │ • Calculate Stability    │       │
│ │ • Assess Employment Risk │       │
│ └──────────────────────────┘       │
│                                    │
│ ┌──────────────────────────┐       │
│ │ RiskRulesDB MCP (8002)   │       │
│ ├──────────────────────────┤       │
│ │ • Assess Risk            │       │
│ │ • Apply Rules            │       │
│ │ • Get Thresholds         │       │
│ └──────────────────────────┘       │
│                                    │
│ ┌──────────────────────────┐       │
│ │ NotificationSystem (8003)│       │
│ ├──────────────────────────┤       │
│ │ • Send Notifications     │       │
│ │ • Log Compliance         │       │
│ │ • Audit Trail            │       │
│ └──────────────────────────┘       │
└────────────────────────────────────┘
```

---

## Data Flow

### Application Submission Flow

```
[User] (Streamlit)
   ↓
[Submit Application]
   ↓
POST /api/applications
   ↓
[FastAPI - routes.py]
   ├─ Validate Input
   ├─ Store Application
   ├─ Log Action
   └─ Return Application ID
   ↓
[User Receives Confirmation]
```

### Application Processing Flow

```
[Application Stored]
   ↓
[Trigger Orchestrator]
   ↓
[orchestrator.process_application()]
   ├─ Create Agent Input
   ├─ Run Agents in Parallel
   │  ├─ ApplicantProfileAgent.execute()
   │  │  └─ Send MCP: ApplicantDB
   │  │     └─ Query applicant data
   │  │        └─ Return analysis
   │  │
   │  └─ FinancialRiskAgent.execute()
   │     └─ Send MCP: RiskRulesDB
   │        └─ Assess financial risk
   │           └─ Return analysis
   │
   ├─ Collect Outputs
   ├─ LoanDecisionAgent.synthesize_decision()
   │  └─ Combine analyses
   │     └─ Apply decision logic
   │        └─ Generate explanation
   │
   ├─ Store Decision
   ├─ Update Application Status
   ├─ Send MCP: NotificationSystem
   │  ├─ Log Compliance
   │  ├─ Audit Trail
   │  └─ Send Notification
   │
   └─ Log Orchestration Complete
      ↓
   [Decision Ready]
      ↓
   [User Checks Status]
      ↓
   [GET /api/applications/{id}/status]
      ↓
   [Display Decision in Streamlit]
```

---

## Decision Classification Logic

```
All Agents Run
     ↓
Collect Recommendations & Scores
     ↓
┌─────────────────────────────┐
│ Decision Logic              │
├─────────────────────────────┤
│                             │
│ IF any agent = REJECT       │
│    Classification = REJECTED│
│    Confidence = High        │
│                             │
│ ELSE IF any agent = REVIEW  │
│    Classification = REQUIRES│
│    Confidence = Medium      │
│                             │
│ ELSE IF all APPROVE +       │
│        Confidence >= 70%    │
│    Classification = APPROVED│
│    Confidence = High        │
│                             │
│ ELSE                        │
│    Classification = REQUIRES│
│    Confidence = Low         │
│                             │
└─────────────────────────────┘
     ↓
Generate Explanation
     ↓
Calculate Risk Score
     ↓
Return Final Decision
```

---

## Storage Architecture

### In-Memory Data Structures

```python
{
  "applications": {
    "app_xxxxx": {
      "application_id": "app_xxxxx",
      "applicant_id": "appl_xxxxx",
      "status": "approved",
      "credit_score": 720,
      "loan_amount": 50000,
      "decision_id": "dec_xxxxx",
      "created_at": "2024-11-11T10:00:00",
      "updated_at": "2024-11-11T10:05:00"
    }
  },
  
  "applicants": {
    "appl_xxxxx": {
      "applicant_id": "appl_xxxxx",
      "first_name": "John",
      "annual_income": 75000,
      "years_employed": 3,
      "employment_type": "full-time"
    }
  },
  
  "decisions": {
    "dec_xxxxx": {
      "decision_id": "dec_xxxxx",
      "application_id": "app_xxxxx",
      "classification": "APPROVED",
      "risk_score": 25.5,
      "confidence_level": 85.0,
      "explanation": "..."
    }
  },
  
  "audit_logs": [
    {
      "log_id": "log_xxxxx",
      "application_id": "app_xxxxx",
      "action": "Application submitted",
      "timestamp": "2024-11-11T10:00:00"
    }
  ]
}
```

---

## Concurrency & Thread Safety

- **Storage**: Thread-safe with RLock
- **Agents**: Async execution with asyncio
- **API**: FastAPI handles concurrent requests
- **Logging**: Thread-safe logging handlers

---

## Error Handling

```
Try:
├─ Validate Input
├─ Process Request
└─ Store Result
Except:
├─ Log Error
├─ Update Status
├─ Notify User
└─ Return Error Response
```

---

## Performance Characteristics

| Operation | Time |
|-----------|------|
| Application Submission | < 100ms |
| Agent Execution (Parallel) | < 500ms |
| Decision Synthesis | < 200ms |
| Total Processing | < 1s |
| Status Query | < 50ms |

---

## Security Considerations

- Input validation on all endpoints
- Thread-safe access to shared data
- Audit logging of all decisions
- No sensitive data in logs
- CORS configuration
- Error messages don't expose internals

---

## Scalability

**Current State:**
- In-memory storage limited by available RAM
- Single-threaded async processing
- ~10,000 applications before memory concerns

**Future Enhancements:**
- PostgreSQL persistent storage
- Redis caching layer
- Distributed agents
- Load balancing
- Message queues for async processing

---

**Architecture Version**: 1.0  
**Last Updated**: November 2026
