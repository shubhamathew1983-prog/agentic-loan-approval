from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from typing import List
from datetime import datetime
from app.models import (
    LoanApplicationRequest,
    LoanApplicationResponse,
    ApplicationStatus,
)
from app.utils import get_storage, get_logger
from app.orchestration import LangGraphOrchestrator
import asyncio

router = APIRouter(prefix="/api", tags=["applications"])
logger = get_logger(__name__)
storage = get_storage()
orchestrator = LangGraphOrchestrator()


@router.post("/applications", response_model=LoanApplicationResponse)
async def submit_application(request: LoanApplicationRequest, background_tasks: BackgroundTasks) -> LoanApplicationResponse:
    """Submit a new loan application."""
    try:
        app_data = {
            "applicant_id": request.applicant_id,
            "applicant_profile": request.applicant_profile.dict(),
            "credit_score": request.credit_score,
            "loan_amount": request.loan_amount,
            "loan_tenure_months": request.loan_tenure_months,
            "existing_liabilities": request.existing_liabilities,
            "location": request.location,
            "application_timestamp": request.application_timestamp or datetime.now(),
            "status": ApplicationStatus.SUBMITTED,
        }

        app_id = storage.create_application(app_data)
        storage.log_action({
            "application_id": app_id,
            "action": "Application submitted",
            "details": {"applicant_id": request.applicant_id},
        })

        logger.info(f"Application {app_id} submitted by {request.applicant_id}")

        # Trigger orchestration in background
        applicant_data = request.applicant_profile.dict()
        financial_data = {
            "credit_score": request.credit_score,
            "annual_income": applicant_data.get("annual_income"),
            "years_employed": applicant_data.get("years_employed"),
            "existing_liabilities": request.existing_liabilities,
        }
        loan_details = {
            "loan_amount": request.loan_amount,
            "loan_tenure_months": request.loan_tenure_months,
            "location": request.location,
        }

        async def run_orchestration():
            """Run LangGraph orchestration asynchronously."""
            try:
                await orchestrator.invoke({
                    "application_id": app_id,
                    "applicant_data": applicant_data,
                    "financial_data": financial_data,
                    "loan_details": loan_details,
                })
            except Exception as e:
                logger.error(f"Orchestration failed for {app_id}: {str(e)}")
                storage.log_action({
                    "application_id": app_id,
                    "action": "Orchestration error",
                    "details": {"error": str(e)},
                    "status": "error",
                })

        background_tasks.add_task(asyncio.run, run_orchestration())

        return LoanApplicationResponse(
            application_id=app_id,
            status=ApplicationStatus.SUBMITTED,
            submitted_at=datetime.now(),
        )

    except Exception as e:
        logger.error(f"Error submitting application: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing application: {str(e)}",
        )


@router.get("/applications/{application_id}", response_model=LoanApplicationResponse)
async def get_application(application_id: str) -> LoanApplicationResponse:
    """Get application details."""
    try:
        app = storage.get_application(application_id)
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application {application_id} not found",
            )

        decision = storage.get_decision_by_application(application_id)

        return LoanApplicationResponse(
            application_id=app_id,
            status=app.get("status", ApplicationStatus.SUBMITTED),
            submitted_at=app.get("application_timestamp", datetime.now()),
            decision=decision.get("classification") if decision else None,
            confidence=decision.get("confidence_level") if decision else None,
            reasoning=decision.get("explanation") if decision else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving application: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving application: {str(e)}",
        )


@router.get("/applications")
async def list_applications(skip: int = 0, limit: int = 10):
    """List all applications."""
    try:
        all_apps = storage.get_all_applications()
        total = len(all_apps)
        apps = all_apps[skip : skip + limit]

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "applications": apps,
        }

    except Exception as e:
        logger.error(f"Error listing applications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing applications: {str(e)}",
        )


@router.get("/applications/{application_id}/status")
async def get_application_status(application_id: str):
    """Get application status."""
    try:
        app = storage.get_application(application_id)
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application {application_id} not found",
            )

        decision = storage.get_decision_by_application(application_id)
        audit_logs = storage.get_audit_logs(application_id)

        return {
            "application_id": application_id,
            "status": app.get("status"),
            "submitted_at": app.get("application_timestamp"),
            "updated_at": app.get("updated_at"),
            "decision": decision,
            "recent_events": audit_logs[-5:] if audit_logs else [],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting application status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting application status: {str(e)}",
        )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    storage_summary = storage.get_storage_summary()
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "storage": storage_summary,
    }
