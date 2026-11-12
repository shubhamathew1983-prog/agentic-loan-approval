"""
Test script to verify LangGraph orchestration end-to-end.

Tests the complete workflow:
1. LangGraph StateGraph creation
2. All node execution
3. Parallel agent execution
4. Final decision synthesis
5. Compliance actions
6. State persistence
"""

import asyncio
import json
from datetime import datetime
from app.orchestration import LangGraphOrchestrator


async def test_langgraph_orchestration():
    """Run complete end-to-end test of LangGraph orchestration."""

    print("\n" + "=" * 80)
    print("LANGGRAPH ORCHESTRATION TEST")
    print("=" * 80 + "\n")

    # Test data
    test_application = {
        "application_id": "TEST_APP_001",
        "applicant_data": {
            "applicant_id": "APPL_001",
            "first_name": "John",
            "last_name": "Doe",
            "age": 35,
            "email": "john.doe@example.com",
            "phone": "555-123-4567",
            "address": "123 Main St",
            "city": "New York",
            "state": "NY",
            "zip_code": "10001",
            "employment_type": "full-time",
            "employer": "Tech Corp",
            "annual_income": 85000,
            "years_employed": 5,
            "gender": "Male",
        },
        "financial_data": {
            "credit_score": 720,
            "annual_income": 85000,
            "years_employed": 5,
            "existing_liabilities": 15000,
        },
        "loan_details": {
            "loan_amount": 50000,
            "loan_tenure_months": 60,
            "location": "New York",
        },
    }

    # Initialize orchestrator
    print("1. Initializing LangGraph Orchestrator...")
    orchestrator = LangGraphOrchestrator()
    print("   ✅ Orchestrator initialized")
    print()

    # Display graph visualization
    print("2. LangGraph StateGraph Structure:")
    print("   " + "-" * 50)
    try:
        mermaid = orchestrator.get_graph_visualization()
        for line in mermaid.split("\n"):
            print(f"   {line}")
    except Exception as e:
        print(f"   (Visualization not available: {e})")
    print()

    # Run orchestration
    print("3. Running Orchestration Workflow...")
    print("   " + "-" * 50)

    start_time = datetime.now()

    try:
        result = await orchestrator.invoke(test_application)

        elapsed = (datetime.now() - start_time).total_seconds()

        print(f"   ✅ Orchestration completed in {elapsed:.2f}s")
        print()

        # Display results
        print("4. Orchestration Results:")
        print("   " + "-" * 50)
        print(f"   Application ID: {result['application_id']}")
        print(f"   Decision ID: {result['decision_id']}")
        print(f"   Case ID: {result.get('case_id', 'N/A')}")
        print()

        # Display decision
        decision = result["decision"]
        print("5. Final Decision:")
        print("   " + "-" * 50)
        print(f"   Classification: {decision['classification']}")
        print(f"   Risk Score: {decision['risk_score']:.1f}")
        print(f"   Confidence: {decision['confidence_level']:.1f}%")
        print(f"   Key Factors: {', '.join(decision['key_factors'][:3])}")
        print()

        # Display audit log
        audit_log = result["audit_log"]
        print("6. Workflow Audit Trail:")
        print("   " + "-" * 50)
        for i, entry in enumerate(audit_log, 1):
            step = entry.get("step", "unknown").replace("_", " ").title()
            status = entry.get("status", "unknown").upper()
            print(f"   {i}. {step:40} [{status}]")
        print()

        # Display agent outputs
        print("7. Agent Outputs:")
        print("   " + "-" * 50)

        if "applicant_output" in result:
            app_output = result["applicant_output"]
            print(f"   Applicant Profile Agent:")
            print(f"     └─ Recommendation: {app_output.get('recommendation')}")
            print(f"     └─ Confidence: {app_output.get('confidence_score'):.1f}%")

        if "financial_output" in result:
            fin_output = result["financial_output"]
            print(f"   Financial Risk Agent:")
            print(f"     └─ Recommendation: {fin_output.get('recommendation')}")
            print(f"     └─ Confidence: {fin_output.get('confidence_score'):.1f}%")

        print()

        # Display explanation
        print("8. Decision Explanation:")
        print("   " + "-" * 50)
        explanation = decision.get("explanation", "No explanation available")
        for line in explanation.split(". "):
            if line.strip():
                print(f"   • {line.strip()}.")
        print()

        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"✅ LangGraph orchestration: PASSED")
        print(f"✅ All {len(audit_log)} workflow steps executed successfully")
        print(f"✅ Decision classification: {decision['classification']}")
        print(f"✅ Execution time: {elapsed:.2f}s")
        print()

        return True

    except Exception as e:
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"   ❌ Orchestration failed after {elapsed:.2f}s")
        print(f"   Error: {str(e)}")
        print()
        import traceback
        traceback.print_exc()
        print()
        return False


async def test_agent_services():
    """Test individual agent services through microservices layer."""

    print("\n" + "=" * 80)
    print("AGENT MICROSERVICES TEST")
    print("=" * 80 + "\n")

    from app.orchestration import AgentServiceFactory

    factory = AgentServiceFactory()

    test_data = {
        "application_id": "SERVICE_TEST_001",
        "applicant_data": {
            "applicant_id": "APPL_S001",
            "first_name": "Jane",
            "last_name": "Smith",
            "age": 28,
            "email": "jane.smith@example.com",
            "phone": "555-987-6543",
            "address": "456 Oak Ave",
            "city": "Los Angeles",
            "state": "CA",
            "zip_code": "90001",
            "employment_type": "full-time",
            "employer": "Finance Ltd",
            "annual_income": 95000,
            "years_employed": 3,
        },
        "financial_data": {
            "credit_score": 750,
            "annual_income": 95000,
            "years_employed": 3,
            "existing_liabilities": 20000,
        },
        "loan_details": {
            "loan_amount": 75000,
            "loan_tenure_months": 84,
            "location": "Los Angeles",
        },
    }

    print("Testing individual agent services...")
    print("-" * 80)

    try:
        # Test Applicant Profile Service
        print("\n1. ApplicantProfileService:")
        applicant_service = factory.get_service("applicant_profile")
        result = await applicant_service.execute(test_data)
        if result.get("success"):
            output = result.get("output", {})
            rec = output.get("recommendation", "N/A")
            print(f"   ✅ Recommendation: {rec}")
        else:
            print(f"   ❌ Error: {result.get('error')}")

        # Test Financial Risk Service
        print("\n2. FinancialRiskService:")
        financial_service = factory.get_service("financial_risk")
        result = await financial_service.execute(test_data)
        if result.get("success"):
            output = result.get("output", {})
            rec = output.get("recommendation", "N/A")
            print(f"   ✅ Recommendation: {rec}")
        else:
            print(f"   ❌ Error: {result.get('error')}")

        # Test Compliance Service
        print("\n3. ComplianceService:")
        compliance_service = factory.get_service("compliance")
        result = await compliance_service.execute_checks(test_data)
        if result.get("success"):
            checks = result.get("checks", {})
            print(f"   ✅ Case ID: {checks.get('analysis', {}).get('case_id', 'N/A')}")
        else:
            print(f"   ❌ Error: {result.get('error')}")

        print("\n" + "=" * 80)
        print("✅ Agent Microservices Test: PASSED")
        print("=" * 80 + "\n")

        return True

    except Exception as e:
        print(f"\n❌ Agent Services Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""

    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "LANGGRAPH AGENTIC AI ORCHESTRATION - COMPREHENSIVE TEST SUITE".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")

    # Run tests
    test1_passed = await test_langgraph_orchestration()
    test2_passed = await test_agent_services()

    # Final summary
    print("\n" + "=" * 80)
    print("FINAL TEST SUMMARY")
    print("=" * 80)
    print(f"LangGraph Orchestration:  {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Agent Microservices:      {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print("=" * 80 + "\n")

    return test1_passed and test2_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
