# Leave Management Agentic AI System

An intelligent leave management system that uses AI to process leave requests, validate against HR policies, and manage approval workflows.

## Features

- **AI-Powered Policy Analysis**: Uses GPT-4o-mini to analyze leave requests against company policies
- **Multi-Level Approval Workflow**: Supports manager, senior manager, and HR approvals
- **HR Knowledge Base Integration**: Reads from structured HR policy database
- **Smart Validation**: AI validates approver authority and policy compliance
- **Comprehensive Reporting**: Generates detailed reports for all requests
- **Multiple Leave Types**: Supports casual, sick, annual, maternity, paternity, and compensatory leave

## System Components

### 1. HR Knowledge Base (`hr_knowledge_base.json`)
Contains:
- Leave policies for different types
- Approval hierarchy and authority levels
- Business rules and constraints

### 2. Leave Management Agent (`leave_management_agent.py`)
Core AI agent that:
- Analyzes leave requests using LLM
- Validates policy compliance
- Manages approval workflows
- Generates reports

### 3. Demo Application (`leave_app_demo.py`)
Interactive demo showing:
- Valid leave requests
- Policy violations
- Multi-level approvals
- Rejection scenarios

## Installation

1. Install required packages:
```bash
pip install openai python-dotenv
```

2. Set up your environment:
```bash
# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

3. Ensure all files are in the same directory:
- `hr_knowledge_base.json`
- `leave_management_agent.py`
- `leave_app_demo.py`
- `.env`

## Usage

### Run the Demo
```bash
python leave_app_demo.py
```

This will demonstrate:
- Creating leave requests
- AI analyzing requests against policies
- Processing approvals
- Generating reports
- Employee summaries

### Use in Your Code

```python
from leave_management_agent import LeaveManagementAgent

# Initialize agent
agent = LeaveManagementAgent()

# Create a leave request
request = agent.create_leave_request(
    employee_name="John Doe",
    employee_id="EMP001",
    role="employee",
    leave_type="casual_leave",
    start_date="2025-11-01",
    end_date="2025-11-02",
    reason="Personal work",
    current_balance=12
)

# View AI analysis
print(f"Eligible: {request['analysis']['eligible']}")
print(f"Reason: {request['analysis']['reason']}")

# Process approval
if request['status'] == 'pending_approval':
    approval = agent.process_approval(
        request_id=request['request_id'],
        approver_name="Manager Name",
        approver_role="manager",
        decision="approved",
        comments="Approved!"
    )
    print(f"Status: {approval['new_status']}")

# Generate report
print(agent.generate_leave_report(request))

# Get employee summary
summary = agent.get_leave_summary("EMP001")
print(f"Total requests: {summary['total_requests']}")
print(f"Approved: {summary['approved']}")
```

## Leave Types Supported

| Leave Type | Annual Quota | Max Consecutive | Advance Notice | Approvers |
|------------|--------------|-----------------|----------------|-----------|
| Casual Leave | 12 days | 3 days | 1 day | Manager |
| Sick Leave | 12 days | 5 days | 0 days | Manager |
| Annual Leave | 21 days | 15 days | 7 days | Manager + HR |
| Maternity Leave | 180 days | 180 days | 30 days | Manager + HR |
| Paternity Leave | 15 days | 15 days | 7 days | Manager + HR |
| Compensatory Off | 24 days | 2 days | 1 day | Manager |

## Approval Hierarchy

1. **Employee** (Level 1): Can submit requests
2. **Manager** (Level 2): Can approve up to 5 days
3. **Senior Manager** (Level 3): Can approve up to 10 days
4. **HR** (Level 4): Can approve up to 180 days

## AI Decision Making

The system uses AI to:

1. **Analyze Eligibility**:
   - Check leave balance
   - Validate duration against policy
   - Verify advance notice requirements
   - Consider special circumstances

2. **Validate Approvers**:
   - Confirm approver authority level
   - Check if duration is within approval limit
   - Determine if additional approvals needed

3. **Provide Recommendations**:
   - Suggest alternative dates
   - Flag policy violations
   - Recommend documentation requirements

## Example Scenarios

### Scenario 1: Simple Approval
```
Employee requests 2 days casual leave
→ AI: Eligible, requires manager approval
→ Manager approves
→ Status: APPROVED
```

### Scenario 2: Multi-Level Approval
```
Manager requests 12 days annual leave
→ AI: Eligible, requires senior manager + HR approval
→ Senior Manager approves
→ HR approves
→ Status: APPROVED
```

### Scenario 3: Policy Violation
```
Employee requests 8 days sick leave (max 5 consecutive)
→ AI: Not eligible, exceeds policy limit
→ Status: REJECTED
→ Recommendation: Split into two requests or provide medical certificate
```

### Scenario 4: Insufficient Balance
```
Employee requests leave with 0 balance remaining
→ AI: Not eligible, insufficient leave balance
→ Status: REJECTED
```

## Customization

### Add New Leave Types
Edit `hr_knowledge_base.json`:
```json
{
  "leave_policies": {
    "study_leave": {
      "name": "Study Leave",
      "annual_quota": 10,
      "max_consecutive_days": 5,
      "advance_notice_days": 14,
      "approval_required": "manager_and_hr",
      "description": "Leave for education and training"
    }
  }
}
```

### Modify Approval Rules
Update the `approval_hierarchy` section in the knowledge base.

### Change AI Model
In `leave_management_agent.py`, modify:
```python
model="gpt-4o-mini"  # Change to gpt-4, gpt-4-turbo, etc.
```

## Benefits

1. **Automated Policy Enforcement**: AI ensures all requests comply with HR policies
2. **Consistent Decision Making**: Removes human bias from initial screening
3. **Time Savings**: Reduces manual policy checking by HR
4. **Audit Trail**: Complete history of all decisions and approvals
5. **Smart Recommendations**: AI suggests solutions for policy violations
6. **Scalable**: Handles multiple requests simultaneously

## Limitations

- Requires OpenAI API key and internet connection
- AI responses use tokens (costs associated)
- Does not integrate with calendar systems (can be extended)
- Does not send email notifications (can be extended)

## Future Enhancements

- [ ] Calendar integration for holiday/weekend detection
- [ ] Email notifications to employees and approvers
- [ ] Dashboard UI with web interface
- [ ] Integration with HRMS systems
- [ ] Mobile app support
- [ ] Advanced analytics and reporting
- [ ] Machine learning for leave pattern prediction

## Troubleshooting

**Error: "OPENAI_API_KEY not found"**
- Ensure `.env` file exists with valid API key

**Error: "hr_knowledge_base.json not found"**
- Verify the JSON file is in the same directory

**AI Analysis Failing**
- Check internet connection
- Verify API key has sufficient credits
- Confirm model name is correct

## License

This is a demo application for educational purposes.

## Support

For issues or questions, review the code comments or modify according to your organization's specific requirements.
