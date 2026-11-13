#!/usr/bin/env python
"""Live demonstration of LangGraph orchestration and MCP servers."""

import asyncio
import sys
from datetime import datetime
from app.orchestration import LangGraphOrchestrator
from app.utils import get_storage

async def demo():
    print("\n" + "="*90)
    print(" " * 20 + "LANGGRAPH ORCHESTRATION & MCP SERVER DEMONSTRATION")
    print("="*90 + "\n")

    # 1. Show workflow diagram
    print("1️⃣  WORKFLOW ARCHITECTURE")
    print("-" * 90)
    orchestrator = LangGraphOrchestrator()
    diagram = orchestrator.get_graph_visualization()
    print(diagram)

    # 2. Create test application
    print("\n2️⃣  SUBMITTING TEST APPLICATION")
    print("-" * 90)
    storage = get_storage()

    app_data = {
        "applicant_id": "appl_demo_001",
        "applicant_profile": {
            "applicant_id": "appl_demo_001",
            "first_name": "John",
            "last_name": "Demo",
            "age": 35,
            "email": "john@example.com",
            "phone": "+1-234-567-8900",
            "address": "123 Main St",
            "city": "Boston",
            "state": "MA",
            "zip_code": "02101",
            "employment_type": "full-time",
            "employer": "Tech Corp",
            "annual_income": 75000,
            "years_employed": 5,
        },
        "credit_score": 720,
        "loan_amount": 50000,
        "loan_tenure_months": 60,
        "existing_liabilities": 15000,
        "location": "Boston, MA",
    }

    app_id = storage.create_application(app_data)
    storage.create_applicant(app_data["applicant_profile"])
    print(f"✓ Application created: {app_id}\n")

    # 3. Run orchestration
    print("3️⃣  RUNNING LANGGRAPH ORCHESTRATION")
    print("-" * 90)
    print("Watch for log messages showing:")
    print("  • [NODE] entries for each orchestration step")
    print("  • [MCP] entries for microservice calls")
    print("  • [LLM] entries for Claude API calls\n")

    input_data = {
        "application_id": app_id,
        "applicant_data": app_data["applicant_profile"],
        "financial_data": {
            "credit_score": app_data["credit_score"],
            "annual_income": app_data["applicant_profile"]["annual_income"],
            "years_employed": app_data["applicant_profile"]["years_employed"],
            "existing_liabilities": app_data["existing_liabilities"],
        },
        "loan_details": {
            "loan_amount": app_data["loan_amount"],
            "loan_tenure_months": app_data["loan_tenure_months"],
            "location": app_data["location"],
        },
    }

    try:
        print("📊 Invoking orchestrator...")
        result = await orchestrator.invoke(input_data)

        print("\n✓ Orchestration completed successfully!\n")

    except Exception as e:
        print(f"\n❌ Orchestration failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # 4. Show decision results
    print("4️⃣  DECISION RESULTS")
    print("-" * 90)
    decision = result["decision"]
    print(f"Application ID:     {result['application_id']}")
    print(f"Case ID:            {result['case_id']}")
    print(f"Classification:     {decision['classification']}")
    print(f"Risk Score:         {decision['risk_score']}/100")
    print(f"Confidence Level:   {decision['confidence_level']}%")
    print(f"Key Decision Factors:")
    for i, factor in enumerate(decision['key_factors'], 1):
        print(f"  {i}. {factor}")

    # 5. Show explanation
    print("\n5️⃣  CLAUDE-GENERATED EXPLANATION")
    print("-" * 90)
    print(f"{decision['explanation']}\n")

    # 6. Show audit trail
    print("6️⃣  COMPLETE EXECUTION TRACE & AUDIT LOG")
    print("-" * 90)
    logs = storage.get_audit_logs(app_id)

    print(f"Total audit entries: {len(logs)}\n")
    print("📋 AUDIT LOG TIMELINE:\n")

    for i, log in enumerate(logs, 1):
        timestamp = log.get("timestamp", "")
        action = log.get("action", "")
        agent = log.get("agent_name", "system")
        status = log.get("status", "success")

        status_icon = "✓" if status == "success" else "⚠"
        print(f"{i:2}. [{timestamp}] {status_icon} {agent:35} {action}")

    # 7. Show agent outputs
    print("\n7️⃣  DETAILED AGENT OUTPUTS")
    print("-" * 90)

    for agent_output in decision.get('agent_outputs', []):
        agent_name = agent_output.get('agent_name', 'Unknown')
        recommendation = agent_output.get('recommendation', 'N/A')
        confidence = agent_output.get('confidence_score', 0)

        print(f"\n{agent_name}:")
        print(f"  Recommendation: {recommendation}")
        print(f"  Confidence:     {confidence:.1f}%")

        # Show analysis details
        analysis = agent_output.get('analysis', {})
        if analysis:
            for key, value in analysis.items():
                if not key.startswith('_'):
                    print(f"  {key}: {value}")

    # 8. Summary
    print("\n" + "="*90)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*90)
    print("\n📊 WHAT YOU JUST SAW:")
    print("  1. LangGraph StateGraph workflow diagram (architecture)")
    print("  2. Application submission and validation")
    print("  3. Parallel agent execution (Applicant + Financial agents)")
    print("  4. MCP server calls for data lookup and risk assessment")
    print("  5. Claude LLM generation of credit narrative")
    print("  6. Claude LLM generation of decision explanation")
    print("  7. Decision synthesis with confidence scoring")
    print("  8. Complete audit trail with all steps traced")
    print("\n✨ KEY TECHNOLOGIES DEMONSTRATED:")
    print("  • LangGraph StateGraph orchestration")
    print("  • Parallel agent execution")
    print("  • MCP (Model Context Protocol) microservices")
    print("  • Claude LLM integration via AsyncAnthropic")
    print("  • Comprehensive audit logging")
    print("="*90 + "\n")

if __name__ == "__main__":
    asyncio.run(demo())
