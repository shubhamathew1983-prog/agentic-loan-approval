from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.config import get_settings
from app.api import router
from app.utils import setup_logging
from app.mcp_servers import ApplicantDBMCP, RiskRulesDBMCP, NotificationSystemMCP

# Setup logging
setup_logging()

# Initialize FastAPI
settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Multi-Agent Agentic AI Loan Approval System",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount MCP server sub-applications — agents call these via HTTP
_mcp_applicant = ApplicantDBMCP()
_mcp_risk = RiskRulesDBMCP()
_mcp_notification = NotificationSystemMCP()
app.mount("/mcp/applicant", _mcp_applicant.app)
app.mount("/mcp/risk", _mcp_risk.app)
app.mount("/mcp/notification", _mcp_notification.app)

# Include routes
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    print(f"Starting {settings.app_name}")
    print(f"Environment: {settings.app_env}")
    print(f"LLM Model: {settings.llm_model}")
    print(f"Storage Mode: {settings.storage_mode}")


@app.on_event("shutdown")
async def shutdown_event():
    print(f"Shutting down {settings.app_name}")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.app_name,
        version="1.0.0",
        description="Multi-Agent Agentic AI Loan Approval System API",
        routes=app.routes,
    )

    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
    )
