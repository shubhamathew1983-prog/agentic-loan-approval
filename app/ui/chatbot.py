import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, Any

# Page config
st.set_page_config(
    page_title="Agentic Loan Approval System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

st.title("💰 Agentic AI Loan Approval System")
st.markdown("Submit loan applications and get instant decisions powered by multi-agent AI")

# Sidebar Navigation
page = st.sidebar.radio(
    "Navigation",
    ["📝 Submit Application", "📊 Application Status", "📈 Dashboard"],
)

# Extract page name (remove emoji prefix)
page_name = page.split(" ", 1)[1] if " " in page else page

if page_name == "Submit Application":
    st.header("Submit Loan Application")

    with st.form("loan_application_form"):
        # Personal Information
        st.subheader("Personal Information")
        col1, col2 = st.columns(2)

        with col1:
            first_name = st.text_input("First Name", placeholder="John")
            age = st.number_input("Age", min_value=18, max_value=100, value=30)
            employment_type = st.selectbox(
                "Employment Type",
                ["full-time", "part-time", "self-employed"],
            )

        with col2:
            last_name = st.text_input("Last Name", placeholder="Doe")
            email = st.text_input("Email", placeholder="john@example.com")
            phone = st.text_input("Phone", placeholder="+1-234-567-8900")

        # Financial Information
        st.subheader("Financial Information")
        col3, col4 = st.columns(2)

        with col3:
            annual_income = st.number_input(
                "Annual Income ($)",
                min_value=0,
                step=1000,
                value=50000,
            )
            credit_score = st.number_input(
                "Credit Score",
                min_value=300,
                max_value=850,
                value=700,
            )

        with col4:
            years_employed = st.number_input(
                "Years Employed",
                min_value=0.0,
                max_value=50.0,
                step=0.5,
                value=3.0,
            )
            existing_liabilities = st.number_input(
                "Existing Liabilities ($)",
                min_value=0,
                step=1000,
                value=0,
            )

        # Loan Details
        st.subheader("Loan Details")
        col5, col6 = st.columns(2)

        with col5:
            loan_amount = st.number_input(
                "Loan Amount ($)",
                min_value=1000,
                step=1000,
                value=50000,
            )

        with col6:
            loan_tenure = st.number_input(
                "Loan Tenure (months)",
                min_value=6,
                max_value=360,
                step=6,
                value=60,
            )

        address = st.text_input("Address", placeholder="123 Main St")
        col7, col8, col9 = st.columns(3)
        with col7:
            city = st.text_input("City", placeholder="New York")
        with col8:
            state = st.text_input("State", placeholder="NY", max_chars=2)
        with col9:
            zip_code = st.text_input("ZIP Code", placeholder="10001")

        # Submit Button
        submitted = st.form_submit_button("Submit Application", use_container_width=True)

    if submitted:
        # Prepare application data
        applicant_profile = {
            "applicant_id": f"appl_{datetime.now().timestamp()}",
            "first_name": first_name,
            "last_name": last_name,
            "age": age,
            "email": email,
            "phone": phone,
            "address": address,
            "city": city,
            "state": state,
            "zip_code": zip_code,
            "employment_type": employment_type,
            "employer": "Current Employer",
            "annual_income": annual_income,
            "years_employed": years_employed,
        }

        application_request = {
            "applicant_id": applicant_profile["applicant_id"],
            "applicant_profile": applicant_profile,
            "credit_score": credit_score,
            "loan_amount": loan_amount,
            "loan_tenure_months": loan_tenure,
            "existing_liabilities": existing_liabilities,
            "location": f"{city}, {state}",
        }

        try:
            with st.spinner("Processing application..."):
                # Submit application
                response = requests.post(
                    f"{API_BASE_URL}/api/applications",
                    json=application_request,
                    timeout=30,
                )

                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Application submitted successfully!")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**Application ID:** {result['application_id']}")
                    with col2:
                        st.info(f"**Status:** {result['status']}")

                    st.session_state.last_app_id = result["application_id"]
                else:
                    st.error(f"Error: {response.text}")

        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {str(e)}")

elif page_name == "Application Status":
    st.header("Check Application Status")

    col1, col2 = st.columns([3, 1])
    with col1:
        app_id = st.text_input(
            "Enter Application ID",
            value=st.session_state.get("last_app_id", ""),
            placeholder="app_xxxxx",
        )
    with col2:
        check_btn = st.button("Check Status", use_container_width=True)

    if check_btn and app_id:
        try:
            with st.spinner("Fetching application details..."):
                response = requests.get(
                    f"{API_BASE_URL}/api/applications/{app_id}/status",
                    timeout=10,
                )

                if response.status_code == 200:
                    status_data = response.json()

                    # Display status
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Application ID", app_id)
                    with col2:
                        st.metric("Status", status_data["status"].upper())
                    with col3:
                        if status_data.get("decision"):
                            st.metric(
                                "Decision",
                                status_data["decision"].get("classification", "PENDING"),
                            )

                    # Decision Details
                    if status_data.get("decision"):
                        st.subheader("Decision Details")
                        decision = status_data["decision"]

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Risk Score", f"{decision['risk_score']:.1f}")
                        with col2:
                            st.metric("Confidence", f"{decision['confidence_level']:.1f}%")
                        with col3:
                            st.metric("Decision", decision["classification"])

                        st.info(f"**Explanation:** {decision['explanation']}")

                        if decision.get("key_factors"):
                            st.subheader("Key Factors")
                            for i, factor in enumerate(decision["key_factors"], 1):
                                st.write(f"{i}. {factor}")

                    # Recent Events
                    if status_data.get("recent_events"):
                        st.subheader("Recent Events")
                        for event in status_data["recent_events"]:
                            with st.expander(f"{event.get('action')} - {event.get('timestamp')}"):
                                st.json(event)

                else:
                    st.error(f"Application not found: {app_id}")

        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {str(e)}")

elif page_name == "Dashboard":
    st.header("System Dashboard")

    try:
        with st.spinner("Loading dashboard..."):
            response = requests.get(f"{API_BASE_URL}/api/health", timeout=10)

            if response.status_code == 200:
                health_data = response.json()
                storage = health_data.get("storage", {})

                # Display statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Applications", storage.get("total_applications", 0))
                with col2:
                    st.metric("Total Applicants", storage.get("total_applicants", 0))
                with col3:
                    st.metric("Total Decisions", storage.get("total_decisions", 0))
                with col4:
                    st.metric("Audit Logs", storage.get("total_audit_logs", 0))

                st.success("System is healthy! ✅")
                st.json(health_data)

            else:
                st.error("System health check failed")

    except requests.exceptions.RequestException as e:
        st.error(f"Cannot connect to API: {str(e)}")
        st.info("Make sure the FastAPI server is running on http://localhost:8000")

# Footer
st.divider()
st.markdown(
    """
    ---
    **Agentic AI Intelligent Loan Approval System**

    Powered by Multi-Agent Architecture | Claude Haiku 4.5 | LangGraph Orchestration
    """
)
