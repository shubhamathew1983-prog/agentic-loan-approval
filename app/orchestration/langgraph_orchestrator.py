"""
LangGraph-based orchestration for multi-agent loan approval workflow.

This module implements a StateGraph-based orchestrator that coordinates
independent agents through a defined state machine. Each agent runs as an
independent node, communicating only through the shared state.

Architecture:
- Compliance checks execute first (sequential)
- Applicant Profile and Financial Risk agents run in parallel
- Decision synthesis consumes both agent outputs
- Compliance actions execute based on final decision
- All state transitions are logged for auditability
"""

from typing import TypedDict, List, Dict, Any, Optional, Annotated
from datetime import datetime
import asyncio
import logging

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.agents import (
    AgentInput,
    AgentOutput,
    ApplicantProfileAgent,
    FinancialRiskAgent,
    LoanDecisionAgent,
    ComplianceActionOrchestratorAgent,
)
from app.utils import get_storage, get_logger


# ============================================================================
# Helper Functions
# ============================================================================

def _combine_audit_logs(logs1: List[Dict[str, Any]], logs2: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Reducer function for combining audit logs from parallel nodes.

    Args:
        logs1: First list of audit log entries
        logs2: Second list of audit log entries to append

    Returns:
        Combined list of audit log entries
    """
    if not isinstance(logs1, list):
        logs1 = []
    if not isinstance(logs2, list):
        logs2 = []
    return logs1 + logs2


# ============================================================================
# State Definition
# ============================================================================

class LoanState(TypedDict, total=False):
    """
    Complete state for loan approval workflow.

    All fields are optional (total=False) to support incremental state updates
    during graph execution. Fields are populated as each node executes.

    The `audit_log` field uses an `Annotated` type with a reducer function
    to handle concurrent updates from parallel nodes.
    """

    # Input data
    application_id: str
    applicant_data: Dict[str, Any]
    financial_data: Dict[str, Any]
    loan_details: Dict[str, Any]

    # Agent outputs
    compliance_output: Dict[str, Any]
    applicant_output: Dict[str, Any]
    financial_output: Dict[str, Any]

    # Final decision
    decision: Dict[str, Any]
    case_id: str

    # Metadata
    # audit_log uses Annotated with reducer for parallel updates
    audit_log: Annotated[List[Dict[str, Any]], _combine_audit_logs]
    started_at: str
    completed_at: Optional[str]
    status: str


# ============================================================================
# Node Functions
# ============================================================================

async def compliance_check_node(state: LoanState) -> Dict[str, Any]:
    """
    Execute compliance checks on applicant data.

    This node runs first to ensure data quality and regulatory compliance
    before engaging other agents. Generates a case ID for tracking.

    Args:
        state: Current workflow state

    Returns:
        Dictionary with only the updated fields (not full state)
    """
    logger = get_logger(__name__)
    logger.info(f"[NODE] Executing compliance check for {state['application_id']}")

    try:
        compliance_agent = ComplianceActionOrchestratorAgent()
        agent_input = AgentInput(
            application_id=state["application_id"],
            applicant_data=state["applicant_data"],
            financial_data=state["financial_data"],
            loan_details=state["loan_details"],
        )

        output = await compliance_agent.execute(agent_input)

        # Extract case ID from compliance output
        case_id = output.analysis.get("case_id", "CASE-UNKNOWN")

        # Get current audit log and append new entry
        audit_log = state.get("audit_log", [])
        audit_log.append({
            "step": "compliance_check",
            "status": "completed",
            "agent": "ComplianceActionOrchestratorAgent",
            "recommendation": output.recommendation,
            "confidence": output.confidence_score,
            "timestamp": datetime.now().isoformat(),
        })

        logger.info(f"[NODE] Compliance check completed. Case ID: {case_id}")

        # Return only the updated fields
        return {
            "compliance_output": output.dict(),
            "case_id": case_id,
            "audit_log": audit_log,
        }

    except Exception as e:
        logger.error(f"[NODE] Compliance check failed: {str(e)}")
        audit_log = state.get("audit_log", [])
        audit_log.append({
            "step": "compliance_check",
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        })
        raise


async def applicant_profile_node(state: LoanState) -> Dict[str, Any]:
    """
    Analyze applicant profile and employment stability.

    Independent agent that evaluates applicant's employment history,
    income stability, and completeness of application data.

    Args:
        state: Current workflow state

    Returns:
        Dictionary with only the updated fields (not full state)
    """
    logger = get_logger(__name__)
    logger.info(f"[NODE] Executing applicant profile analysis for {state['application_id']}")

    try:
        applicant_agent = ApplicantProfileAgent()
        agent_input = AgentInput(
            application_id=state["application_id"],
            applicant_data=state["applicant_data"],
            financial_data=state["financial_data"],
            loan_details=state["loan_details"],
        )

        output = await applicant_agent.execute(agent_input)

        audit_log = state.get("audit_log", [])
        audit_log.append({
            "step": "applicant_profile_analysis",
            "status": "completed",
            "agent": "ApplicantProfileAgent",
            "recommendation": output.recommendation,
            "confidence": output.confidence_score,
            "timestamp": datetime.now().isoformat(),
        })

        logger.info(f"[NODE] Applicant profile analysis completed")

        return {
            "applicant_output": output.dict(),
            "audit_log": audit_log,
        }

    except Exception as e:
        logger.error(f"[NODE] Applicant profile analysis failed: {str(e)}")
        audit_log = state.get("audit_log", [])
        audit_log.append({
            "step": "applicant_profile_analysis",
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        })
        raise


async def financial_risk_node(state: LoanState) -> Dict[str, Any]:
    """
    Analyze financial risk metrics.

    Independent agent that evaluates credit score, debt-to-income ratio,
    loan amount risk, and anomalies.

    Args:
        state: Current workflow state

    Returns:
        Dictionary with only the updated fields (not full state)
    """
    logger = get_logger(__name__)
    logger.info(f"[NODE] Executing financial risk analysis for {state['application_id']}")

    try:
        financial_agent = FinancialRiskAgent()
        agent_input = AgentInput(
            application_id=state["application_id"],
            applicant_data=state["applicant_data"],
            financial_data=state["financial_data"],
            loan_details=state["loan_details"],
        )

        output = await financial_agent.execute(agent_input)

        audit_log = state.get("audit_log", [])
        audit_log.append({
            "step": "financial_risk_analysis",
            "status": "completed",
            "agent": "FinancialRiskAgent",
            "recommendation": output.recommendation,
            "confidence": output.confidence_score,
            "timestamp": datetime.now().isoformat(),
        })

        logger.info(f"[NODE] Financial risk analysis completed")

        return {
            "financial_output": output.dict(),
            "audit_log": audit_log,
        }

    except Exception as e:
        logger.error(f"[NODE] Financial risk analysis failed: {str(e)}")
        audit_log = state.get("audit_log", [])
        audit_log.append({
            "step": "financial_risk_analysis",
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        })
        raise


async def decision_synthesis_node(state: LoanState) -> Dict[str, Any]:
    """
    Synthesize final loan decision from all agent outputs.

    Combines recommendations from all previous agents, calculates
    confidence scores, and generates human-readable explanation.

    Args:
        state: Current workflow state (must include applicant_output and financial_output)

    Returns:
        Dictionary with only the updated fields (not full state)
    """
    logger = get_logger(__name__)
    logger.info(f"[NODE] Synthesizing decision for {state['application_id']}")

    try:
        decision_agent = LoanDecisionAgent()

        # Reconstruct AgentOutput objects from state dictionaries
        applicant_output = AgentOutput(**state.get("applicant_output", {}))
        financial_output = AgentOutput(**state.get("financial_output", {}))

        agent_outputs = [applicant_output, financial_output]

        # Synthesize final decision
        final_decision = await decision_agent.synthesize_decision(
            application_id=state["application_id"],
            agent_outputs=agent_outputs,
            applicant_data=state["applicant_data"],
        )

        audit_log = state.get("audit_log", [])
        audit_log.append({
            "step": "decision_synthesis",
            "status": "completed",
            "agent": "LoanDecisionAgent",
            "classification": final_decision["classification"],
            "risk_score": final_decision["risk_score"],
            "confidence": final_decision["confidence_level"],
            "timestamp": datetime.now().isoformat(),
        })

        logger.info(
            f"[NODE] Decision synthesized: {final_decision['classification']} "
            f"(Risk: {final_decision['risk_score']}, Confidence: {final_decision['confidence_level']}%)"
        )

        return {
            "decision": final_decision,
            "audit_log": audit_log,
        }

    except Exception as e:
        logger.error(f"[NODE] Decision synthesis failed: {str(e)}")
        audit_log = state.get("audit_log", [])
        audit_log.append({
            "step": "decision_synthesis",
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        })
        raise


async def compliance_actions_node(state: LoanState) -> Dict[str, Any]:
    """
    Execute compliance-based actions after decision is made.

    Triggers notifications, generates letters, and manages case assignment
    based on the final decision classification.

    Args:
        state: Current workflow state (must include decision)

    Returns:
        Dictionary with only the updated fields (not full state)
    """
    logger = get_logger(__name__)
    logger.info(f"[NODE] Executing compliance actions for {state['application_id']}")

    try:
        compliance_agent = ComplianceActionOrchestratorAgent()

        # Execute decision-specific actions
        compliance_result = await compliance_agent.execute_actions(
            application_id=state["application_id"],
            decision=state["decision"],
            applicant_data=state["applicant_data"],
        )

        audit_log = state.get("audit_log", [])
        audit_log.append({
            "step": "compliance_actions",
            "status": "completed",
            "agent": "ComplianceActionOrchestratorAgent",
            "case_id": compliance_result.get("case_id"),
            "action_type": compliance_result.get("action_type"),
            "actions_count": len(compliance_result.get("actions_taken", [])),
            "timestamp": datetime.now().isoformat(),
        })

        logger.info(
            f"[NODE] Compliance actions executed. "
            f"Actions: {len(compliance_result.get('actions_taken', []))}, "
            f"Case: {compliance_result.get('case_id')}"
        )

        updates = {
            "audit_log": audit_log,
        }

        # Update case ID if new one was generated
        if "case_id" in compliance_result:
            updates["case_id"] = compliance_result["case_id"]

        return updates

    except Exception as e:
        logger.error(f"[NODE] Compliance actions failed: {str(e)}")
        audit_log = state.get("audit_log", [])
        audit_log.append({
            "step": "compliance_actions",
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        })
        raise


# ============================================================================
# LangGraph Orchestrator
# ============================================================================

class LangGraphOrchestrator:
    """
    LangGraph-based orchestrator for multi-agent loan approval workflow.

    Uses LangGraph's StateGraph to coordinate independent agents with:
    - Parallel execution support (Applicant + Financial agents run together)
    - State persistence via checkpointing
    - Clear routing logic based on state
    - Audit trail of all steps

    Architecture:
        Compliance → (Applicant || Financial) → Decision → Actions → End
    """

    def __init__(self):
        """Initialize orchestrator with compiled graph."""
        self.logger = get_logger(__name__)
        self.storage = get_storage()
        self._graph = self._build_graph()

    def _build_graph(self):
        """
        Build and compile the LangGraph StateGraph.

        Returns:
            Compiled graph ready for execution
        """
        self.logger.info("[GRAPH] Building LangGraph StateGraph")

        # Create state graph
        graph = StateGraph(LoanState)

        # Add all nodes
        graph.add_node("compliance", compliance_check_node)
        graph.add_node("applicant", applicant_profile_node)
        graph.add_node("financial", financial_risk_node)
        graph.add_node("decision", decision_synthesis_node)
        graph.add_node("actions", compliance_actions_node)

        # Define flow: Compliance → Parallel Agents → Decision → Actions → End
        graph.add_edge(START, "compliance")

        # After compliance, run both agents in parallel
        graph.add_edge("compliance", "applicant")
        graph.add_edge("compliance", "financial")

        # Both agents converge to decision
        graph.add_edge("applicant", "decision")
        graph.add_edge("financial", "decision")

        # Decision leads to compliance actions
        graph.add_edge("decision", "actions")

        # Compliance actions end the workflow
        graph.add_edge("actions", END)

        # Compile with memory checkpointer for state persistence
        compiled_graph = graph.compile(checkpointer=MemorySaver())

        self.logger.info("[GRAPH] StateGraph compiled successfully")
        return compiled_graph

    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the workflow for a loan application.

        Runs the compiled state graph with the provided input data,
        managing state through all nodes with full audit logging.

        Args:
            input_data: Dictionary with keys:
                - application_id: Unique application identifier
                - applicant_data: Applicant profile information
                - financial_data: Financial metrics
                - loan_details: Loan request details

        Returns:
            Final state dictionary with:
                - decision: Final loan decision with classification
                - case_id: Generated case ID for tracking
                - audit_log: Complete execution trace
                - All intermediate agent outputs
        """
        application_id = input_data["application_id"]
        self.logger.info(f"[ORCHESTRATOR] Starting workflow for {application_id}")

        try:
            # Initialize state
            initial_state: LoanState = {
                "application_id": application_id,
                "applicant_data": input_data["applicant_data"],
                "financial_data": input_data["financial_data"],
                "loan_details": input_data["loan_details"],
                "audit_log": [],
                "started_at": datetime.now().isoformat(),
                "status": "started",
            }

            self.storage.log_action({
                "application_id": application_id,
                "action": "Orchestration started",
                "agent": "LangGraphOrchestrator",
                "details": {
                    "workflow": "LangGraph StateGraph",
                    "timestamp": datetime.now().isoformat(),
                },
            })

            # Execute graph - synchronous wrapper for async graph
            final_state = await self._run_async_graph(initial_state)

            final_state["completed_at"] = datetime.now().isoformat()
            final_state["status"] = "completed"

            # Store decision
            decision_id = self.storage.create_decision(final_state["decision"])

            # Log completion
            self.storage.log_action({
                "application_id": application_id,
                "action": "Orchestration completed",
                "agent": "LangGraphOrchestrator",
                "details": {
                    "decision_id": decision_id,
                    "classification": final_state["decision"]["classification"],
                    "case_id": final_state.get("case_id"),
                    "audit_steps": len(final_state["audit_log"]),
                },
            })

            # Update application status
            status_map = {
                "APPROVED": "approved",
                "REJECTED": "rejected",
                "REQUIRES_REVIEW": "manual_review",
            }
            new_status = status_map.get(
                final_state["decision"]["classification"], "under_review"
            )

            self.storage.update_application(
                application_id,
                {
                    "status": new_status,
                    "decision_id": decision_id,
                    "case_id": final_state.get("case_id"),
                    "decision_made_at": datetime.now().isoformat(),
                },
            )

            self.logger.info(
                f"[ORCHESTRATOR] Workflow completed for {application_id}. "
                f"Decision: {final_state['decision']['classification']}"
            )

            return {
                "success": True,
                "application_id": application_id,
                "decision_id": decision_id,
                "case_id": final_state.get("case_id"),
                "decision": final_state["decision"],
                "audit_log": final_state["audit_log"],
            }

        except Exception as e:
            self.logger.error(
                f"[ORCHESTRATOR] Workflow failed for {application_id}: {str(e)}"
            )
            self.storage.log_action({
                "application_id": application_id,
                "action": "Orchestration error",
                "agent": "LangGraphOrchestrator",
                "details": {"error": str(e)},
                "status": "error",
            })
            raise

    async def _run_async_graph(self, initial_state: LoanState) -> LoanState:
        """
        Execute the graph asynchronously.

        Uses LangGraph's ainvoke() to properly handle async node functions.

        Args:
            initial_state: Initial state for graph execution

        Returns:
            Final state after all nodes complete
        """
        # Use ainvoke for async graph execution
        result = await self._graph.ainvoke(
            initial_state,
            config={"configurable": {"thread_id": initial_state["application_id"]}},
        )
        return result

    def get_graph_visualization(self) -> str:
        """
        Get Mermaid diagram of the workflow graph.

        Useful for documentation and debugging.

        Returns:
            Mermaid diagram as string
        """
        return self._graph.get_graph().draw_mermaid()
