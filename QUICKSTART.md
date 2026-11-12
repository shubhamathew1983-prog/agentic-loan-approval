# Quick Start Guide

## Prerequisites
- Python 3.9+
- pip or conda
- Anthropic API Key

## Installation

### 1. Clone and Setup Environment
```bash
cd agentic-loan-approval

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env

# Edit .env and add your Anthropic API key
# ANTHROPIC_API_KEY=your_key_here
```

### 3. Create Logs and Data Directories
```bash
mkdir -p logs data
```

## Running the Application

### Option 1: Using Start Script (Linux/Mac)
```bash
chmod +x scripts/start_dev.sh
./scripts/start_dev.sh
```

### Option 2: Manual Start (All Terminals)

**Terminal 1 - FastAPI Backend:**
```bash
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - MCP Servers:**
```bash
source venv/bin/activate
python app/mcp_servers/run_all.py
```

**Terminal 3 - Streamlit UI:**
```bash
source venv/bin/activate
streamlit run app/ui/chatbot.py
```

## Access Services

- **Streamlit UI**: http://localhost:8501
- **FastAPI Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## MCP Servers

Once running, MCP servers are available at:
- **ApplicantDB**: http://localhost:8001
- **RiskRulesDB**: http://localhost:8002
- **NotificationSystem**: http://localhost:8003

## Sample API Usage

### Submit Loan Application
```bash
curl -X POST "http://localhost:8000/api/applications" \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_id": "appl_123",
    "applicant_profile": {
      "applicant_id": "appl_123",
      "first_name": "John",
      "last_name": "Doe",
      "age": 35,
      "email": "john@example.com",
      "phone": "+1-234-567-8900",
      "address": "123 Main St",
      "city": "New York",
      "state": "NY",
      "zip_code": "10001",
      "employment_type": "full-time",
      "employer": "Tech Company",
      "annual_income": 75000,
      "years_employed": 3
    },
    "credit_score": 720,
    "loan_amount": 50000,
    "loan_tenure_months": 60,
    "existing_liabilities": 10000,
    "location": "New York, NY"
  }'
```

### Get Application Status
```bash
curl "http://localhost:8000/api/applications/{application_id}/status"
```

### Health Check
```bash
curl "http://localhost:8000/api/health"
```

## Troubleshooting

### Port Already in Use
```bash
# Find and kill process using port 8000
lsof -i :8000
kill -9 <PID>
```

### Module Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### API Connection Refused
Make sure FastAPI server is running:
```bash
ps aux | grep uvicorn
```

## Next Steps

1. Try submitting a loan application via the Streamlit UI
2. Check the application status
3. View the dashboard
4. Explore API documentation at `/docs`
5. Check logs in `logs/app.log`

## Project Structure

```
agentic-loan-approval/
├── app/
│   ├── agents/              # Agent implementations
│   ├── mcp_servers/         # MCP server implementations
│   ├── orchestration/       # LangGraph orchestrator
│   ├── api/                 # FastAPI routes
│   ├── models/              # Pydantic schemas
│   ├── ui/                  # Streamlit interface
│   ├── utils/               # Utilities
│   └── main.py              # FastAPI entry point
├── tests/                   # Test suite
├── scripts/                 # Utility scripts
└── requirements.txt         # Python dependencies
```

## Support

For issues or questions, check:
1. Logs in `logs/app.log`
2. API documentation at `http://localhost:8000/docs`
3. Health endpoint at `http://localhost:8000/api/health`
