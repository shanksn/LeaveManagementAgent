# Visual Flow: How ChatGPT Analyzes Leave Requests

## 🔄 Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    EMPLOYEE SUBMITS REQUEST                      │
│                                                                   │
│  agent.create_leave_request(                                     │
│      employee_name="John Doe",                                   │
│      leave_type="casual_leave",                                  │
│      start_date="2025-11-01",                                    │
│      end_date="2025-11-02",                                      │
│      reason="Family function"                                    │
│  )                                                               │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 1: LOAD HR KNOWLEDGE BASE                      │
│                                                                   │
│  {                                                               │
│    "casual_leave": {                                             │
│      "annual_quota": 12,                                         │
│      "max_consecutive_days": 3,                                  │
│      "advance_notice_days": 1,                                   │
│      "approval_required": "manager"                              │
│    }                                                             │
│  }                                                               │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│         STEP 2: BUILD CONTEXT PROMPT FOR CHATGPT                 │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ You are an HR AI assistant.                             │   │
│  │                                                          │   │
│  │ Employee: John Doe (EMP001)                             │   │
│  │ Leave Type: casual_leave                                │   │
│  │ Duration: 2 days (Nov 1-2)                              │   │
│  │ Balance: 12 days available                              │   │
│  │                                                          │   │
│  │ Policy Rules:                                           │   │
│  │ - Max consecutive: 3 days                               │   │
│  │ - Advance notice: 1 day                                 │   │
│  │ - Annual quota: 12 days                                 │   │
│  │                                                          │   │
│  │ Task: Analyze eligibility and provide recommendations   │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 3: SEND TO OPENAI API                          │
│                                                                   │
│  POST https://api.openai.com/v1/chat/completions                │
│  {                                                               │
│    "model": "gpt-4o-mini",                                       │
│    "temperature": 0,                                             │
│    "response_format": {"type": "json_object"},                  │
│    "messages": [                                                 │
│      {                                                           │
│        "role": "system",                                         │
│        "content": "You are an HR policy expert..."              │
│      },                                                          │
│      {                                                           │
│        "role": "user",                                           │
│        "content": "[Context prompt from Step 2]"                │
│      }                                                           │
│    ]                                                             │
│  }                                                               │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
        ╔═══════════════════════════════════════╗
        ║                                       ║
        ║        CHATGPT REASONING              ║
        ║                                       ║
        ║  1. Duration (2) < Max (3) ✓          ║
        ║  2. Balance (12) >= Duration (2) ✓    ║
        ║  3. Leave type valid ✓                ║
        ║  4. Needs manager approval            ║
        ║  5. Recommend handover tasks          ║
        ║                                       ║
        ╚═══════════════╦═══════════════════════╝
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│            STEP 4: CHATGPT RETURNS JSON RESPONSE                 │
│                                                                   │
│  {                                                               │
│    "eligible": true,                                             │
│    "reason": "Request complies with policy. Balance after:       │
│               10 days",                                          │
│    "required_approvers": ["manager"],                            │
│    "recommendations": [                                          │
│      "Ensure 1 day advance notice provided",                     │
│      "Handover pending work before leave"                        │
│    ]                                                             │
│  }                                                               │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│       STEP 5: SYSTEM PROCESSES AI RESPONSE                       │
│                                                                   │
│  request = {                                                     │
│    "request_id": "LR-0001",                                      │
│    "status": "pending_approval",  ← Set based on AI response    │
│    "analysis": {                                                 │
│      "eligible": true,            ← From ChatGPT                 │
│      "reason": "...",              ← From ChatGPT                 │
│      "required_approvers": [...],  ← From ChatGPT                 │
│      "recommendations": [...]      ← From ChatGPT                 │
│    }                                                             │
│  }                                                               │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 6: MANAGER APPROVES                            │
│                                                                   │
│  agent.process_approval(                                         │
│      request_id="LR-0001",                                       │
│      approver_name="Sarah Manager",                              │
│      approver_role="manager",                                    │
│      decision="approved"                                         │
│  )                                                               │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│    STEP 7: BUILD VALIDATION CONTEXT FOR CHATGPT                  │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Validate approver authority                             │   │
│  │                                                          │   │
│  │ Approver: Sarah Manager (role: manager)                 │   │
│  │ Request: LR-0001 (2 days casual leave)                  │   │
│  │ Required approvers: ["manager"]                          │   │
│  │                                                          │   │
│  │ Hierarchy:                                              │   │
│  │ - Manager: can approve employee requests up to 5 days   │   │
│  │ - HR: can approve all requests up to 180 days           │   │
│  │                                                          │   │
│  │ Task: Does this approver have authority?                │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│          STEP 8: SEND VALIDATION TO OPENAI API                   │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
        ╔═══════════════════════════════════════╗
        ║                                       ║
        ║     CHATGPT VALIDATION LOGIC          ║
        ║                                       ║
        ║  1. Approver role = "manager" ✓       ║
        ║  2. Required role = "manager" ✓       ║
        ║  3. Duration (2) < Max limit (5) ✓    ║
        ║  4. No additional approvals needed ✓  ║
        ║                                       ║
        ╚═══════════════╦═══════════════════════╝
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│       STEP 9: CHATGPT VALIDATES AUTHORITY                        │
│                                                                   │
│  {                                                               │
│    "has_authority": true,                                        │
│    "reason": "Manager has authority to approve 2-day             │
│               employee requests",                                │
│    "next_approver_required": false                               │
│  }                                                               │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│           STEP 10: FINAL STATUS UPDATE                           │
│                                                                   │
│  request = {                                                     │
│    "request_id": "LR-0001",                                      │
│    "status": "APPROVED",        ← Updated                        │
│    "approved_at": "2025-10-25T...",                              │
│    "approvals": [                                                │
│      {                                                           │
│        "approver_name": "Sarah Manager",                         │
│        "decision": "approved",                                   │
│        "timestamp": "..."                                        │
│      }                                                           │
│    ]                                                             │
│  }                                                               │
│                                                                   │
│  ✅ LEAVE APPROVED                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Example: Policy Violation Scenario

```
┌─────────────────────────────────────────────────────────────────┐
│              REQUEST: 8 Days Sick Leave (Max: 5)                 │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
        ╔═══════════════════════════════════════╗
        ║      CHATGPT INTELLIGENT ANALYSIS      ║
        ║                                       ║
        ║  Duration: 8 days                     ║
        ║  Policy max: 5 days                   ║
        ║  Violation detected! ❌                ║
        ║                                       ║
        ║  BUT... Context analysis:             ║
        ║  - Reason: "Recovering from surgery"  ║
        ║  - Medical emergency                  ║
        ║  - May need exception                 ║
        ║                                       ║
        ║  Smart recommendations:               ║
        ║  1. Split into 5+3 day requests       ║
        ║  2. Provide medical certificate       ║
        ║  3. Check extended sick leave policy  ║
        ╚═══════════════════════════════════════╝
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI RESPONSE                                   │
│                                                                   │
│  {                                                               │
│    "eligible": false,                                            │
│    "reason": "Exceeds max consecutive days (5). Requested: 8",   │
│    "required_approvers": [],                                     │
│    "recommendations": [                                          │
│      "Split into two requests: 5 days + 3 days",                 │
│      "For medical emergencies, provide medical certificate",     │
│      "Consider extended sick leave policy for surgeries"         │
│    ]                                                             │
│  }                                                               │
│                                                                   │
│  STATUS: REJECTED ❌                                             │
│  But with helpful recommendations! 💡                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Multi-Level Approval Example

```
REQUEST: 12 Days Annual Leave
├─ Duration: 12 days (within max 15)
└─ Requires: Manager + HR approval

        ╔═══════════════════════════════════════╗
        ║        CHATGPT ANALYSIS               ║
        ║                                       ║
        ║  12 days > 7 days                     ║
        ║  → Requires escalation                ║
        ║  → Manager first, then HR             ║
        ╚═══════════════════════════════════════╝
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Manager Approval                                        │
│  ├─ ChatGPT validates: ✓ Manager has authority                  │
│  ├─ Duration within manager limit? NO (max 5 days)               │
│  └─ Result: Approved, but needs HR                               │
│                                                                   │
│  STATUS: PENDING_APPROVAL (Next: HR)                             │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: HR Approval                                             │
│  ├─ ChatGPT validates: ✓ HR has authority                       │
│  ├─ Duration within HR limit? YES (max 180 days)                 │
│  └─ Result: Final approval                                       │
│                                                                   │
│  STATUS: APPROVED ✅                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Key Differences: AI vs Rules

### Traditional Rule-Based System
```python
def analyze_request(request, policy):
    if request.duration > policy.max_days:
        return {"eligible": False, "reason": "Exceeds max"}
    elif request.balance < request.duration:
        return {"eligible": False, "reason": "Insufficient balance"}
    else:
        return {"eligible": True, "reason": "Approved"}
```

**Result:** Binary yes/no, no context, no recommendations

---

### AI-Powered System
```python
def analyze_request(request, policy):
    # Build rich context
    context = build_context(request, policy)

    # Let ChatGPT reason about it
    response = chatgpt.analyze(context)

    # Get intelligent analysis with recommendations
    return response
```

**Result:** Contextual analysis, smart recommendations, flexible reasoning

---

## 🎯 Summary: Two ChatGPT Calls Per Request

| Call # | When | Purpose | Input | Output |
|--------|------|---------|-------|--------|
| **1** | Request created | Analyze eligibility | Request + Policy | Eligible? Required approvers? Recommendations |
| **2** | Approval processed | Validate authority | Approver + Hierarchy | Has authority? Next approver needed? |

**Total API calls for complete workflow:** 2-4 depending on approval chain

**Average cost:** $0.0003 - $0.0008 per complete request (less than 1 cent!)

---

## 💡 Why This Matters

Without AI:
- ❌ Rigid if/else logic
- ❌ Cannot handle edge cases
- ❌ No contextual understanding
- ❌ No helpful recommendations
- ❌ Hard to maintain as policies change

With AI:
- ✅ Intelligent reasoning
- ✅ Handles edge cases naturally
- ✅ Context-aware decisions
- ✅ Helpful recommendations
- ✅ Easy to update (just change prompts)

**The AI doesn't just apply rules—it REASONS about them!**
