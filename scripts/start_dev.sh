#!/bin/bash

# Start Agentic Loan Approval System in development mode

echo "🚀 Starting Agentic Loan Approval System..."
echo ""

# Get the directory of this script and change to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Activate virtual environment
if [ -f app/venv/bin/activate ]; then
    source app/venv/bin/activate
else
    echo "❌ Virtual environment not found at app/venv. Please run: python3 -m venv app/venv && pip install -r requirements.txt"
    exit 1
fi

# Create necessary directories
mkdir -p logs
mkdir -p data

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
else
    echo "❌ .env file not found. Please run: cp .env.example .env"
    exit 1
fi

# Start FastAPI backend
echo "📡 Starting FastAPI server..."
uvicorn app.main:app --reload --port 8000 &
FASTAPI_PID=$!

# Wait for FastAPI to start
sleep 3

# Start MCP Servers
echo "🔗 Starting MCP Servers..."
python3 -m app.mcp_servers.run_all &
MCP_PID=$!

# Wait for MCP servers to start
sleep 2

# Start Streamlit UI
echo "🎨 Starting Streamlit UI..."
streamlit run app/ui/chatbot.py --logger.level=info &
STREAMLIT_PID=$!

echo ""
echo "✅ All services started!"
echo ""
echo "Services running:"
echo "  - FastAPI API:     http://localhost:8000"
echo "  - Streamlit UI:    http://localhost:8501"
echo "  - API Docs:        http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Trap Ctrl+C to kill all processes
trap "kill $FASTAPI_PID $MCP_PID $STREAMLIT_PID" INT TERM

# Wait for all processes
wait
