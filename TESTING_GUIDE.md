# Testing Guide: Compliance & Action Orchestrator Agent

## 🌐 Access the Application

**URL:** http://172.31.42.229:8501

---

## 📋 How to Test the Compliance Agent

### Test Case 1: Valid Applicant (Should Proceed)

**Steps:**
1. Open http://172.31.42.229:8501
2. Click **"📝 Submit Application"** in the sidebar
3. Fill in the form with:
   - **First Name:** John
   - **Last Name:** Doe
   - **Age:** 30
   - **Email:** john.doe@example.com
   - **Phone:** +1-555-123-4567
   - **Address:** 123 Main Street
   - **City:** New York
   - **State:** NY
   - **ZIP Code:** 10001
   - **Employment Type:** full-time
   - **Years Employed:** 5
   - **Annual Income:** $80,000
   - **Credit Score:** 750
   - **Loan Amount:** $150,000
   - **Loan Tenure:** 60 months
   - **Existing Liabilities:** $20,000

4. Click **"Submit Application"**
5. Copy the **Application ID**
6. Wait 5-10 seconds for processing

**Expected Results:**
- ✅ Application submitted successfully
- ✅ Compliance checks passed (no flags)
- ✅ Decision generated (APPROVED or REQUIRES_REVIEW)
- ✅ Case ID assigned in backend

---

### Test Case 2: Check Application Status

**Steps:**
1. Click **"📊 Application Status"** in the sidebar
2. Paste the Application ID from Test Case 1
3. Click **"Check Status"**

**Expected Results:**
- ✅ Status shows: "submitted" → "approved" or "manual_review"
- ✅ Decision classification displayed
- ✅ Risk score shown
- ✅ Confidence level displayed
- ✅ Explanation text visible
- ✅ Key factors listed
- ✅ Recent events/audit trail shown

**In the Decision Details, you'll see:**
```
Classification: APPROVED or REQUIRES_REVIEW
Risk Score: 15.0 - 85.0
Confidence: 65.0% - 95.0%
Key Factors: List of factors that influenced decision
Explanation: Natural language explanation
```

---

### Test Case 3: Invalid Applicant (Should Trigger Compliance Flags)

**Steps:**
1. Click **"📝 Submit Application"**
2. Fill with INVALID data:
   - **First Name:** (leave empty)
   - **Last Name:** (leave empty)
   - **Age:** 16 (under 18)
   - **Email:** invalid-email (no @)
   - **Phone:** 123 (too short)
   - **Address:** (leave empty)
   - **City:** (leave empty)
   - **State:** (leave empty)
   - **ZIP Code:** (leave empty)
   - **Other fields:** Fill with valid data

3. Click **"Submit Application"**
4. Check status as in Test Case 2

**Expected Results:**
- ✅ Application submitted
- ✅ Compliance checks detect issues:
  - Applicant under 18
  - Invalid email
  - Invalid phone
  - Incomplete address
  - Missing name
- ✅ Status: "manual_review"
- ✅ Case ID assigned for review
- ✅ Manual review queue triggered

---

### Test Case 4: High-Risk Application (Should Require Review)

**Steps:**
1. Click **"📝 Submit Application"**
2. Fill with HIGH-RISK data:
   - **Credit Score:** 550 (very low)
   - **Annual Income:** $25,000 (low)
   - **Loan Amount:** $300,000 (high)
   - **Existing Liabilities:** $150,000 (high)
   - **Years Employed:** 0.5 (recent employment)
   - **Employment Type:** part-time

3. Fill other fields with valid data
4. Submit and check status

**Expected Results:**
- ✅ Financial risk agent flags issues
- ✅ Decision: "REQUIRES_REVIEW" or "REJECTED"
- ✅ Risk Score: High (60-85)
- ✅ Confidence: Lower (<70%)
- ✅ Manual review case created
- ✅ Case ID tracked in audit trail

---

### Test Case 5: Check Dashboard

**Steps:**
1. Click **"📈 Dashboard"** in the sidebar
2. View system statistics

**Expected Results:**
- ✅ Total Applications: Incremented with your tests
- ✅ Total Applicants: Count updated
- ✅ Total Decisions: Incremented
- ✅ Audit Logs: Updated with compliance records
- ✅ System Health: "healthy" status

**In the health data, look for:**
- Storage statistics
- Application counts
- Decision records
- Audit log entries

---

## 🔍 How Compliance Agent Works (Behind the Scenes)

### When You Submit an Application:

```
1. Application Submitted
   ↓
2. COMPLIANCE AGENT RUNS:
   ├─ PII Validation (email, phone, address, name)
   ├─ Age Verification (18+ check)
   ├─ Application Completeness
   ├─ Protected Attributes Logging
   └─ Case ID Generated (CASE-XXXXXXXX)
   ↓
3. Financial & Profile Agents Analyze
   ↓
4. Decision Synthesized
   ↓
5. COMPLIANCE ACTIONS EXECUTED:
   ├─ APPROVED: Generate letter, send email, create docs
   ├─ REJECTED: Generate denial, send notification
   └─ REQUIRES_REVIEW: Assign to manual review queue
   ↓
6. Case Tracked in Audit Trail
```

---

## 📊 What to Look For in Status Page

### For APPROVED Applications:
- ✅ Status: "approved"
- ✅ Decision: "APPROVED"
- ✅ Risk Score: Low (0-30)
- ✅ Confidence: High (80-100%)
- ✅ Explanation: Positive factors highlighted

### For REJECTED Applications:
- ✅ Status: "rejected"
- ✅ Decision: "REJECTED"
- ✅ Risk Score: High (70-100)
- ✅ Confidence: Medium-High (60-85%)
- ✅ Key Factors: Why rejected (credit, DTI, etc.)

### For REQUIRES_REVIEW Applications:
- ✅ Status: "manual_review"
- ✅ Decision: "REQUIRES_REVIEW"
- ✅ Risk Score: Medium (30-70)
- ✅ Confidence: Medium (40-70%)
- ✅ Case ID: Assigned for manual review
- ✅ Recent Events: Compliance checks listed

---

## 🔐 Compliance Features You Can Observe

### In Application Submission:
- Form validates email format
- Phone number must be complete
- Address requires street, city, state, zip
- Name is required

### In Status Check:
- Audit log shows "Application submitted"
- Audit log shows "Orchestration started"
- Audit log shows each agent's analysis
- Audit log shows "Orchestration completed"
- Case ID visible in recent events

### In Decision Details:
- Risk factors directly from compliance checks
- Decision reasoning includes compliance status
- Explanation mentions employment risk, financial risk
- Key factors highlight critical decision drivers

---

## 🧪 Advanced Testing: Monitor Compliance Logs

### To See Full Audit Trail:

1. In "📊 Application Status" page
2. Scroll down to "Recent Events"
3. Click each expander to see:
   - "Application submitted" → Original data
   - "Orchestration started" → Application details
   - "ApplicantProfileAgent analysis" → Profile score, flags
   - "FinancialRiskAgent analysis" → DTI, credit risk
   - "LoanDecisionAgent synthesized" → Decision logic
   - "Orchestration completed" → Final result with case ID

### What Each Shows:
- **Compliance Flags:** Any PII or completeness issues
- **Case ID:** Unique identifier for this application
- **Decision Classification:** APPROVED/REJECTED/REQUIRES_REVIEW
- **Risk Score:** Calculated risk (0-100)
- **Confidence Level:** Decision confidence (0-100%)
- **Key Factors:** What influenced the decision

---

## 📱 API Testing (Advanced)

### Get Application Status via API:

```bash
curl -X GET "http://172.31.42.229:8000/api/applications/{app_id}/status"
```

**Response includes:**
```json
{
  "application_id": "app_xxx",
  "status": "approved",
  "decision": {
    "classification": "APPROVED",
    "risk_score": 15.0,
    "confidence_level": 85.0,
    "explanation": "...",
    "key_factors": [...]
  },
  "recent_events": [
    {
      "action": "Compliance actions executed",
      "case_id": "CASE-XXXXXXXX",
      "actions": ["Generate approval letter", ...]
    }
  ]
}
```

---

## 🎯 Expected Test Outcomes

### Test Summary Table:

| Test Case | Input | Expected Output | Passes? |
|-----------|-------|-----------------|---------|
| Valid Applicant | Clean data | APPROVED or REQUIRES_REVIEW | ✅ |
| Invalid Data | Missing/bad PII | REQUIRES_REVIEW + Compliance Flags | ✅ |
| High Risk | Low credit, high DTI | REQUIRES_REVIEW or REJECTED | ✅ |
| Check Status | Valid App ID | Full decision details + audit trail | ✅ |
| Dashboard | N/A | Updated statistics | ✅ |

---

## 🔧 Troubleshooting

### If Application Won't Submit:
1. Check all required fields are filled
2. Email must have @ symbol
3. Phone must have 10+ digits
4. Verify ages is between 18-100
5. Credit score between 300-850

### If Status Page Shows No Decision:
1. Wait 10-15 seconds (processing is happening)
2. Refresh the page
3. Check Application ID is correct
4. Look for "Orchestration started" in events

### If Audit Trail Doesn't Show Compliance:
1. Scroll down in status page to "Recent Events"
2. Look for "Orchestration started" entry
3. Expand each event to see details
4. Check for "case_id" in compliance actions

---

## 📈 What Success Looks Like

### Successful Compliance Processing:
```
✅ Application submitted → Stored
✅ Compliance checks executed → No errors
✅ Case ID generated → CASE-XXXXXXXX
✅ Financial analysis completed → DTI calculated
✅ Profile analysis completed → Income stability scored
✅ Decision synthesized → Classification determined
✅ Compliance actions executed → Case assigned/letter generated
✅ Audit trail logged → Full history captured
✅ Status updated → Reflects final decision
✅ Dashboard updated → Statistics incremented
```

---

## 🎓 Learning Outcomes

By testing the compliance agent, you'll see:

1. **Multi-Agent Orchestration:** How 4 agents work together
2. **Compliance Pipeline:** How compliance checks integrate
3. **Decision Flow:** How decisions are made step-by-step
4. **Audit Trails:** How every action is logged
5. **Case Management:** How cases are tracked (Case IDs)
6. **Risk Scoring:** How risk is calculated
7. **Confidence Levels:** How decisions are weighted
8. **Explainability:** How decisions are explained

---

## 📝 Test Report Template

Use this to document your testing:

```
Test Date: ___________
Tester: ___________

Test Case: ___________
Input Data: ___________
Expected Result: ___________
Actual Result: ___________
Status: PASS / FAIL

Observations:
___________

Case ID Generated: ___________
Decision Classification: ___________
Audit Trail Events: ___________

Notes:
___________
```

---

**Ready to Test!**

Visit: **http://172.31.42.229:8501**

The compliance agent is fully integrated and ready to handle your test applications. Try all 5 test cases to see the complete multi-agent orchestration in action!

Good luck! 🚀
