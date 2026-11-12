"""
Microservices wrapper for independent loan approval agents.

This module encapsulates each agent as a "microservice" with a consistent
interface. Each agent service can be deployed independently, scaled separately,
or replaced with a remote REST service in the future.

Architecture:
    AgentService (abstract)
        ├── ApplicantProfileService
        ├── FinancialRiskService
        ├── LoanDecisionService
        └── ComplianceService
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

from app.agents import (
    BaseAgent,
    AgentInput,
    AgentOutput,
    ApplicantProfileAgent,
    FinancialRiskAgent,
    LoanDecisionAgent,
    ComplianceActionOrchestratorAgent,
)
from app.utils import get_logger


# ============================================================================
# Base Service Class
# ============================================================================

class AgentService(ABC):
    """
    Abstract base class for agent microservices.

    Defines standard interface for all agent services, enabling consistent
    service composition and potential replacement with remote services.
    """

    def __init__(self, service_name: str):
        """
        Initialize agent service.

        Args:
            service_name: Descriptive name for the service
        """
        self.service_name = service_name
        self.logger = get_logger(__name__)

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the service with provided input.

        Args:
            input_data: Service-specific input parameters

        Returns:
            Service output as dictionary
        """
        pass

    def _log_service_call(self, action: str, details: Dict[str, Any] = None):
        """
        Log service invocation for audit trail.

        Args:
            action: Action description
            details: Additional context
        """
        self.logger.info(
            f"[SERVICE:{self.service_name}] {action} - {details or {}}"
        )


# ============================================================================
# Individual Agent Services
# ============================================================================

class ApplicantProfileService(AgentService):
    """
    Microservice for applicant profile and employment stability analysis.

    Analyzes applicant data to assess:
    - Income stability score
    - Employment risk level
    - Credit history
    - Application completeness
    """

    def __init__(self):
        """Initialize applicant profile service."""
        super().__init__("ApplicantProfileService")
        self.agent = ApplicantProfileAgent()

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute applicant profile analysis.

        Args:
            input_data: Must contain:
                - application_id: Application identifier
                - applicant_data: Applicant profile information
                - financial_data: Financial information
                - loan_details: Loan request details

        Returns:
            Agent output dictionary with analysis results
        """
        try:
            self._log_service_call("execute", {
                "application_id": input_data.get("application_id"),
            })

            agent_input = AgentInput(
                application_id=input_data["application_id"],
                applicant_data=input_data["applicant_data"],
                financial_data=input_data["financial_data"],
                loan_details=input_data["loan_details"],
            )

            output = await self.agent.execute(agent_input)

            return {
                "success": True,
                "service": self.service_name,
                "output": output.dict(),
            }

        except Exception as e:
            self.logger.error(f"[SERVICE] Execution failed: {str(e)}")
            return {
                "success": False,
                "service": self.service_name,
                "error": str(e),
            }


class FinancialRiskService(AgentService):
    """
    Microservice for financial risk assessment.

    Analyzes financial metrics to assess:
    - Debt-to-income ratio
    - Credit score risk level
    - Loan amount risk
    - Financial anomalies
    """

    def __init__(self):
        """Initialize financial risk service."""
        super().__init__("FinancialRiskService")
        self.agent = FinancialRiskAgent()

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute financial risk analysis.

        Args:
            input_data: Must contain:
                - application_id: Application identifier
                - applicant_data: Applicant information (for income)
                - financial_data: Financial information (credit score, liabilities)
                - loan_details: Loan request details

        Returns:
            Agent output dictionary with risk analysis results
        """
        try:
            self._log_service_call("execute", {
                "application_id": input_data.get("application_id"),
            })

            agent_input = AgentInput(
                application_id=input_data["application_id"],
                applicant_data=input_data["applicant_data"],
                financial_data=input_data["financial_data"],
                loan_details=input_data["loan_details"],
            )

            output = await self.agent.execute(agent_input)

            return {
                "success": True,
                "service": self.service_name,
                "output": output.dict(),
            }

        except Exception as e:
            self.logger.error(f"[SERVICE] Execution failed: {str(e)}")
            return {
                "success": False,
                "service": self.service_name,
                "error": str(e),
            }


class LoanDecisionService(AgentService):
    """
    Microservice for loan decision synthesis.

    Synthesizes final loan decision by combining:
    - Applicant profile analysis
    - Financial risk analysis
    - Decision logic and confidence scoring
    - Explanation generation
    """

    def __init__(self):
        """Initialize loan decision service."""
        super().__init__("LoanDecisionService")
        self.agent = LoanDecisionAgent()

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize final loan decision.

        Args:
            input_data: Must contain:
                - application_id: Application identifier
                - agent_outputs: List of AgentOutput objects from previous agents
                - applicant_data: Applicant information
                - financial_data: Financial information

        Returns:
            Decision output dictionary with classification and reasoning
        """
        try:
            self._log_service_call("execute", {
                "application_id": input_data.get("application_id"),
            })

            # Reconstruct AgentOutput objects
            agent_outputs = input_data.get("agent_outputs", [])
            if agent_outputs and isinstance(agent_outputs[0], dict):
                agent_outputs = [AgentOutput(**ao) for ao in agent_outputs]

            output = await self.agent.synthesize_decision(
                application_id=input_data["application_id"],
                agent_outputs=agent_outputs,
                applicant_data=input_data["applicant_data"],
            )

            return {
                "success": True,
                "service": self.service_name,
                "decision": output,
            }

        except Exception as e:
            self.logger.error(f"[SERVICE] Decision synthesis failed: {str(e)}")
            return {
                "success": False,
                "service": self.service_name,
                "error": str(e),
            }


class ComplianceService(AgentService):
    """
    Microservice for compliance checks and action execution.

    Performs:
    - PII validation
    - Age verification
    - Protected attributes tracking (Fair Lending)
    - Case ID generation
    - Decision-based action execution
    """

    def __init__(self):
        """Initialize compliance service."""
        super().__init__("ComplianceService")
        self.agent = ComplianceActionOrchestratorAgent()

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute compliance checks (default execute method for interface compatibility).

        Args:
            input_data: Must contain required fields for compliance checks

        Returns:
            Compliance check results
        """
        return await self.execute_checks(input_data)

    async def execute_checks(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute compliance checks on applicant data.

        Args:
            input_data: Must contain:
                - application_id: Application identifier
                - applicant_data: Applicant information
                - financial_data: Financial information
                - loan_details: Loan request details

        Returns:
            Compliance check results with flags and case ID
        """
        try:
            self._log_service_call("execute_checks", {
                "application_id": input_data.get("application_id"),
            })

            agent_input = AgentInput(
                application_id=input_data["application_id"],
                applicant_data=input_data["applicant_data"],
                financial_data=input_data["financial_data"],
                loan_details=input_data["loan_details"],
            )

            output = await self.agent.execute(agent_input)

            return {
                "success": True,
                "service": self.service_name,
                "checks": output.dict(),
            }

        except Exception as e:
            self.logger.error(f"[SERVICE] Compliance checks failed: {str(e)}")
            return {
                "success": False,
                "service": self.service_name,
                "error": str(e),
            }

    async def execute_actions(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute compliance-based actions after decision.

        Args:
            input_data: Must contain:
                - application_id: Application identifier
                - decision: Final loan decision dictionary
                - applicant_data: Applicant information

        Returns:
            Compliance action results with case ID and actions taken
        """
        try:
            self._log_service_call("execute_actions", {
                "application_id": input_data.get("application_id"),
                "decision": input_data.get("decision", {}).get("classification"),
            })

            result = await self.agent.execute_actions(
                application_id=input_data["application_id"],
                decision=input_data["decision"],
                applicant_data=input_data["applicant_data"],
            )

            return {
                "success": True,
                "service": self.service_name,
                "actions": result,
            }

        except Exception as e:
            self.logger.error(f"[SERVICE] Compliance actions failed: {str(e)}")
            return {
                "success": False,
                "service": self.service_name,
                "error": str(e),
            }


# ============================================================================
# Service Factory
# ============================================================================

class AgentServiceFactory:
    """
    Factory for creating agent service instances.

    Enables centralized service instantiation with potential
    for service discovery, remote service routing, etc.
    """

    _services = {
        "applicant_profile": ApplicantProfileService,
        "financial_risk": FinancialRiskService,
        "loan_decision": LoanDecisionService,
        "compliance": ComplianceService,
    }

    @classmethod
    def get_service(cls, service_type: str) -> AgentService:
        """
        Get service instance by type.

        Args:
            service_type: Type of service ('applicant_profile', 'financial_risk', etc.)

        Returns:
            Service instance

        Raises:
            ValueError: If service_type is unknown
        """
        if service_type not in cls._services:
            raise ValueError(
                f"Unknown service type: {service_type}. "
                f"Available: {list(cls._services.keys())}"
            )

        return cls._services[service_type]()

    @classmethod
    def get_all_services(cls) -> Dict[str, AgentService]:
        """
        Get all available service instances.

        Returns:
            Dictionary mapping service type to service instance
        """
        return {name: service_class() for name, service_class in cls._services.items()}
