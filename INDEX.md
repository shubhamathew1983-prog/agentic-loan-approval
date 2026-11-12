# 📑 Project Index - Agentic AI Loan Approval System

## 🎯 Start Here
- **[START_HERE.md](START_HERE.md)** ← Begin here! (5 min read)

## 📚 Documentation
- **[README.md](README.md)** - Full system specifications & requirements
- **[QUICKSTART.md](QUICKSTART.md)** - Installation & setup guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design & data flows
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Features & achievements

## 💻 Source Code

### Application Entry Point
- `app/main.py` - FastAPI application setup

### Configuration
- `app/config.py` - Environment & settings management

### Agent Layer (`app/agents/`)
- `base_agent.py` - Base agent abstract class
- `applicant_profile_agent.py` - Analyzes employment & income
- `financial_risk_agent.py` - Analyzes credit & financial risk
- `loan_decision_agent.py` - Synthesizes final decision
- `__init__.py` - Package exports

### Orchestration Layer (`app/orchestration/`)
- `orchestrator.py` - LangGraph-based multi-agent orchestrator
- `__init__.py` - Package exports

### API Layer (`app/api/`)
- `routes.py` - FastAPI endpoint definitions
- `__init__.py` - Package exports

### MCP Servers (`app/mcp_servers/`)
- `base_mcp.py` - Base MCP server class
- `applicant_db_mcp.py` - Applicant data MCP server (port 8001)
- `risk_rules_db_mcp.py` - Risk rules MCP server (port 8002)
- `notification_system_mcp.py` - Notifications MCP server (port 8003)
- `run_all.py` - Startup script for all MCP servers
- `__init__.py` - Package exports

### Data Models (`app/models/`)
- `schemas.py` - Pydantic data models & schemas
- `__init__.py` - Package exports

### User Interface (`app/ui/`)
- `chatbot.py` - Streamlit application
- `__init__.py` - Package exports

### Utilities (`app/utils/`)
- `storage.py` - In-memory storage manager (thread-safe)
- `logging_config.py` - Logging configuration
- `__init__.py` - Package exports

## 🔧 Configuration
- `.env.example` - Environment variables template
- `.gitignore` - Git ignore rules

## 📦 Dependencies
- `requirements.txt` - All Python package dependencies

## 🚀 Scripts
- `scripts/start_dev.sh` - Development startup script

## 🧪 Testing
- `tests/` - Test suite (unit and integration)
- `tests/unit/` - Unit tests
- `tests/integration/` - Integration tests

---

## 📊 File Statistics

- **Total Files**: 34
- **Project Size**: 256 KB
- **Python Files**: ~25
- **Documentation**: 5 comprehensive guides

---

## 🗂️ Architecture Components

### 1. **Presentation Layer**
- Streamlit UI (`app/ui/chatbot.py`)

### 2. **API Layer**
- FastAPI server (`app/main.py`)
- Routes (`app/api/routes.py`)

### 3. **Business Logic**
- Agents (`app/agents/`)
- Orchestration (`app/orchestration/`)

### 4. **Communication**
- MCP Servers (`app/mcp_servers/`)

### 5. **Data Layer**
- Models (`app/models/`)
- Storage (`app/utils/storage.py`)

### 6. **Configuration**
- Settings (`app/config.py`)
- Logging (`app/utils/logging_config.py`)

---

## 🎯 Quick File Lookup

### "I want to..."
- **...understand the system** → Read `START_HERE.md`
- **...set up the project** → Follow `QUICKSTART.md`
- **...see all requirements** → Read `README.md`
- **...understand architecture** → Read `ARCHITECTURE.md`
- **...know what was built** → Read `PROJECT_SUMMARY.md`
- **...modify an agent** → Edit `app/agents/*_agent.py`
- **...add an API endpoint** → Edit `app/api/routes.py`
- **...change storage** → Edit `app/utils/storage.py`
- **...run the system** → Execute `scripts/start_dev.sh`

---

## 📋 Project Features

✅ Multi-Agent Architecture (4 agents)  
✅ In-Memory Storage (thread-safe)  
✅ FastAPI Microservices  
✅ Streamlit Web UI  
✅ MCP Server Communication  
✅ LangGraph Orchestration  
✅ Claude Haiku 4.5 Integration  
✅ Decision Explainability  
✅ Audit Logging  
✅ Compliance Tracking  

---

## 🚀 Services & Ports

| Service | Port | URL |
|---------|------|-----|
| Streamlit UI | 8501 | http://localhost:8501 |
| FastAPI | 8000 | http://localhost:8000 |
| ApplicantDB MCP | 8001 | http://localhost:8001 |
| RiskRulesDB MCP | 8002 | http://localhost:8002 |
| NotificationSystem MCP | 8003 | http://localhost:8003 |

---

## 📞 Navigation Guide

```
Project Root (agentic-loan-approval/)
│
├─ 📖 Documentation
│  ├─ START_HERE.md ............ Quick overview (start here!)
│  ├─ README.md ............... Full specifications
│  ├─ QUICKSTART.md ........... Setup guide
│  ├─ ARCHITECTURE.md ......... System design
│  └─ PROJECT_SUMMARY.md ...... Features & status
│
├─ 💻 Source Code (app/)
│  ├─ main.py ................. FastAPI entry
│  ├─ config.py ............... Settings
│  ├─ agents/ ................. 4 AI agents
│  ├─ orchestration/ .......... Agent coordinator
│  ├─ api/ .................... REST endpoints
│  ├─ mcp_servers/ ............ Communication layer
│  ├─ models/ ................. Data schemas
│  ├─ ui/ ..................... Streamlit UI
│  └─ utils/ .................. Utilities
│
├─ 🔧 Configuration
│  ├─ .env.example ............ Environment template
│  ├─ requirements.txt ........ Dependencies
│  └─ .gitignore .............. Git rules
│
├─ 🚀 Scripts
│  └─ scripts/start_dev.sh .... Startup script
│
└─ 🧪 Testing
   └─ tests/ .................. Test suite
```

---

**Version**: 1.0  
**Status**: ✅ Complete & Ready  
**LLM**: Claude Haiku 4.5  
**Storage**: In-Memory (Thread-Safe)  
**Architecture**: Multi-Agent Microservices  

---

**Next Step**: Open `START_HERE.md` →
