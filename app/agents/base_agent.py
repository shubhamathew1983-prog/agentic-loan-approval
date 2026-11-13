from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
from app.utils import get_storage, get_logger
from pydantic import BaseModel


class AgentInput(BaseModel):
    application_id: str
    applicant_data: Dict[str, Any]
    financial_data: Dict[str, Any]
    loan_details: Dict[str, Any]


class AgentOutput(BaseModel):
    agent_name: str
    analysis: Dict[str, Any]
    recommendation: str
    confidence_score: float
    risk_factors: list = []
    timestamp: datetime


class BaseAgent(ABC):
    """Base class for all loan evaluation agents."""

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = get_logger(self.__class__.__name__)
        self.storage = get_storage()

    @abstractmethod
    async def analyze(self, agent_input: AgentInput) -> AgentOutput:
        """Analyze applicant data and return recommendations."""
        pass

    def _log_action(
        self,
        app_id: str,
        action: str,
        details: Dict[str, Any],
    ) -> str:
        """Log agent action to audit trail."""
        return self.storage.log_action({
            "application_id": app_id,
            "agent_name": self.agent_name,
            "action": action,
            "details": details,
            "status": "success",
        })

    def _calculate_confidence(self, factors: Dict[str, float]) -> float:
        """Calculate confidence score based on factors already on a 0-100 scale."""
        if not factors:
            return 0.0
        return sum(factors.values()) / len(factors)

    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute agent analysis with logging."""
        try:
            self.logger.info(f"Agent {self.agent_name} started analyzing application {agent_input.application_id}")

            output = await self.analyze(agent_input)

            self._log_action(
                agent_input.application_id,
                f"Analysis completed by {self.agent_name}",
                {
                    "recommendation": output.recommendation,
                    "confidence": output.confidence_score,
                    "risk_factors": output.risk_factors,
                },
            )

            self.logger.info(f"Agent {self.agent_name} completed analysis for {agent_input.application_id}")
            return output

        except Exception as e:
            self.logger.error(f"Error in agent {self.agent_name}: {str(e)}")
            self._log_action(
                agent_input.application_id,
                f"Error in {self.agent_name}",
                {"error": str(e)},
            )
            raise
