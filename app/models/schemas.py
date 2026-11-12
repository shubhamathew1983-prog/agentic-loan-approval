from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ApplicationStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    MANUAL_REVIEW = "manual_review"


class DecisionType(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"


# Applicant Schemas
class ApplicantProfile(BaseModel):
    applicant_id: str
    first_name: str
    last_name: str
    age: int
    email: EmailStr
    phone: str
    address: str
    city: str
    state: str
    zip_code: str
    employment_type: str  # full-time, part-time, self-employed
    employer: str
    annual_income: float
    years_employed: int


# Loan Application Schemas
class LoanApplicationRequest(BaseModel):
    applicant_id: str
    applicant_profile: ApplicantProfile
    credit_score: int = Field(..., ge=300, le=850)
    loan_amount: float = Field(..., gt=0)
    loan_tenure_months: int = Field(..., gt=0)
    existing_liabilities: float = Field(default=0, ge=0)
    location: str
    application_timestamp: Optional[datetime] = Field(default_factory=datetime.now)


class LoanApplicationResponse(BaseModel):
    application_id: str
    status: ApplicationStatus
    submitted_at: datetime
    decision: Optional[str] = None
    confidence: Optional[float] = None
    reasoning: Optional[str] = None


# Financial Analysis Schemas
class FinancialMetrics(BaseModel):
    credit_score: int
    annual_income: float
    existing_liabilities: float
    loan_amount: float
    debt_to_income_ratio: float
    credit_score_risk_level: str
    loan_amount_risk: str
    anomalies_detected: bool


# Agent Decision Schemas
class AgentDecision(BaseModel):
    agent_name: str
    analysis: Dict[str, Any]
    recommendation: str
    confidence_score: float
    timestamp: datetime


class FinalDecision(BaseModel):
    application_id: str
    classification: DecisionType
    risk_score: float
    confidence_level: float
    key_factors: List[str]
    explanation: str
    decision_agents: List[AgentDecision]
    decided_at: datetime


# Audit Log Schemas
class AuditLogEntry(BaseModel):
    log_id: str
    application_id: str
    action: str
    agent_name: Optional[str] = None
    details: Dict[str, Any]
    timestamp: datetime
    status: str = "success"
