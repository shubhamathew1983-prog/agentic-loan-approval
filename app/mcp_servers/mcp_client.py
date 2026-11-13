"""
HTTP client for calling the mounted MCP sub-applications.

Agents use this client to delegate data lookups and notifications to the
appropriate MCP server instead of computing everything inline. Each method
returns None on failure so callers can fall back to local computation.

MCP servers are mounted on the main FastAPI app at:
  /mcp/applicant  → ApplicantDBMCP
  /mcp/risk       → RiskRulesDBMCP
  /mcp/notification → NotificationSystemMCP
"""

import logging
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)

_DEFAULT_BASE_URL = "http://localhost:8000"


class MCPClient:
    """Async HTTP client for the three MCP microservices."""

    def __init__(self, base_url: str = _DEFAULT_BASE_URL):
        self._base_url = base_url.rstrip("/")

    # ------------------------------------------------------------------
    # ApplicantDB MCP  (port prefix: /mcp/applicant)
    # ------------------------------------------------------------------

    async def get_income_stability(self, applicant_id: str) -> Optional[Dict[str, Any]]:
        """Fetch income stability score from ApplicantDB MCP."""
        url = f"{self._base_url}/mcp/applicant/applicant/{applicant_id}/income-stability"
        return await self._get(url, "get_income_stability")

    async def get_employment_risk(self, applicant_id: str) -> Optional[Dict[str, Any]]:
        """Fetch employment risk level from ApplicantDB MCP."""
        url = f"{self._base_url}/mcp/applicant/applicant/{applicant_id}/employment-risk"
        return await self._get(url, "get_employment_risk")

    # ------------------------------------------------------------------
    # RiskRulesDB MCP  (port prefix: /mcp/risk)
    # ------------------------------------------------------------------

    async def assess_risk(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fetch risk assessment from RiskRulesDB MCP."""
        url = f"{self._base_url}/mcp/risk/risk/assess"
        return await self._post(url, data, "assess_risk")

    async def get_risk_thresholds(self) -> Optional[Dict[str, Any]]:
        """Fetch current risk thresholds from RiskRulesDB MCP."""
        url = f"{self._base_url}/mcp/risk/rules/thresholds"
        return await self._get(url, "get_risk_thresholds")

    # ------------------------------------------------------------------
    # NotificationSystem MCP  (port prefix: /mcp/notification)
    # ------------------------------------------------------------------

    async def notify_decision(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a decision notification via NotificationSystem MCP."""
        url = f"{self._base_url}/mcp/notification/notify/decision"
        return await self._post(url, data, "notify_decision")

    async def log_compliance(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Log a decision to the compliance audit trail via NotificationSystem MCP."""
        url = f"{self._base_url}/mcp/notification/compliance/log-decision"
        return await self._post(url, data, "log_compliance")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _get(self, url: str, operation: str) -> Optional[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                logger.info(f"[MCP] {operation} → {response.status_code}")
                return response.json()
        except httpx.ConnectError:
            logger.warning(f"[MCP] {operation} — server unreachable, using local fallback")
            return None
        except Exception as exc:
            logger.warning(f"[MCP] {operation} failed: {exc} — using local fallback")
            return None

    async def _post(self, url: str, payload: Dict[str, Any], operation: str) -> Optional[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                logger.info(f"[MCP] {operation} → {response.status_code}")
                return response.json()
        except httpx.ConnectError:
            logger.warning(f"[MCP] {operation} — server unreachable, using local fallback")
            return None
        except Exception as exc:
            logger.warning(f"[MCP] {operation} failed: {exc} — using local fallback")
            return None


_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client
