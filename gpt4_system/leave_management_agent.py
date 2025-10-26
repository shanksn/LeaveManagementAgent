"""
Leave Management Agentic AI System
Integrates with HR knowledge base and handles leave requests with approvals
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv("../shared/.env")


class LeaveManagementAgent:
    """AI Agent for managing leave requests and approvals"""

    def __init__(self, knowledge_base_path: str = "../shared/hr_knowledge_base.json"):
        """Initialize the agent with HR knowledge base"""
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.knowledge_base = self._load_knowledge_base(knowledge_base_path)
        self.leave_requests = []
        self.request_id_counter = 1

    def _load_knowledge_base(self, path: str) -> Dict:
        """Load HR policies from knowledge base"""
        with open(path, 'r') as f:
            return json.load(f)

    def _get_policy_info(self, leave_type: str) -> Optional[Dict]:
        """Retrieve policy information for a leave type"""
        return self.knowledge_base["leave_policies"].get(leave_type.lower().replace(" ", "_"))

    def analyze_leave_request(self, request: Dict) -> Dict:
        """
        Use AI to analyze leave request against HR policies
        Returns eligibility, recommendations, and approval requirements
        """
        leave_type = request['leave_type']
        duration = request['duration_days']
        policy = self._get_policy_info(leave_type)

        if not policy:
            return {
                "status": "rejected",
                "reason": f"Invalid leave type: {leave_type}",
                "eligible": False
            }

        # Create context for AI analysis
        context = f"""
You are an HR AI assistant analyzing a leave request.

Employee Information:
- Name: {request['employee_name']}
- Employee ID: {request['employee_id']}
- Role: {request['role']}

Leave Request:
- Leave Type: {leave_type}
- Duration: {duration} days
- Start Date: {request['start_date']}
- End Date: {request['end_date']}
- Reason: {request['reason']}
- Current Leave Balance: {request.get('current_balance', policy['annual_quota'])} days

Company Policy for {policy['name']}:
- Annual Quota: {policy['annual_quota']} days
- Max Consecutive Days: {policy['max_consecutive_days']} days
- Advance Notice Required: {policy['advance_notice_days']} days
- Approval Required From: {policy['approval_required']}

Task: Analyze if this leave request complies with company policy.
Provide:
1. Eligibility (yes/no)
2. Reason for decision
3. Required approvers
4. Any additional recommendations or warnings

Respond in JSON format with keys: eligible, reason, required_approvers, recommendations
"""

        # Call AI for analysis
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an HR policy expert AI. Analyze leave requests strictly according to company policies. Always respond in valid JSON format."},
                    {"role": "user", "content": context}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )

            analysis = json.loads(response.choices[0].message.content)
            analysis['policy'] = policy
            return analysis

        except Exception as e:
            return {
                "eligible": False,
                "reason": f"Error in AI analysis: {str(e)}",
                "required_approvers": [],
                "recommendations": []
            }

    def create_leave_request(self,
                            employee_name: str,
                            employee_id: str,
                            role: str,
                            leave_type: str,
                            start_date: str,
                            end_date: str,
                            reason: str,
                            current_balance: Optional[int] = None) -> Dict:
        """
        Create a new leave request and analyze it
        """
        # Calculate duration
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        duration = (end - start).days + 1

        # Build request
        request = {
            "request_id": f"LR-{self.request_id_counter:04d}",
            "employee_name": employee_name,
            "employee_id": employee_id,
            "role": role,
            "leave_type": leave_type,
            "start_date": start_date,
            "end_date": end_date,
            "duration_days": duration,
            "reason": reason,
            "current_balance": current_balance,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "approvals": []
        }

        # Analyze request using AI
        analysis = self.analyze_leave_request(request)
        request['analysis'] = analysis

        # Set initial status based on eligibility
        if not analysis.get('eligible', False):
            request['status'] = 'rejected'
            request['rejection_reason'] = analysis.get('reason', 'Policy violation')
        else:
            request['status'] = 'pending_approval'
            request['required_approvers'] = analysis.get('required_approvers', ['manager'])

        # Store request
        self.leave_requests.append(request)
        self.request_id_counter += 1

        return request

    def process_approval(self, request_id: str, approver_name: str, approver_role: str,
                        decision: str, comments: str = "") -> Dict:
        """
        Process an approval/rejection from an approver
        Uses AI to validate if approver has authority
        """
        # Find request
        request = None
        for req in self.leave_requests:
            if req['request_id'] == request_id:
                request = req
                break

        if not request:
            return {"success": False, "message": "Request not found"}

        if request['status'] not in ['pending_approval', 'pending']:
            return {"success": False, "message": f"Request is already {request['status']}"}

        # Use AI to validate approver authority
        validation_context = f"""
You are validating if an approver has authority to approve/reject a leave request.

Approver:
- Name: {approver_name}
- Role: {approver_role}

Leave Request:
- Request ID: {request_id}
- Employee: {request['employee_name']}
- Leave Type: {request['leave_type']}
- Duration: {request['duration_days']} days
- Required Approvers: {request.get('required_approvers', [])}

Approval Hierarchy:
{json.dumps(self.knowledge_base['approval_hierarchy'], indent=2)}

Task: Determine if this approver has authority to approve this request.
Consider:
1. Does their role match required approvers?
2. Is the duration within their approval limit?
3. Are they at the right level in hierarchy?

Respond in JSON format with keys: has_authority, reason, next_approver_required
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an HR authorization validator. Strictly check approval authority. Respond in valid JSON format."},
                    {"role": "user", "content": validation_context}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )

            validation = json.loads(response.choices[0].message.content)

            if not validation.get('has_authority', False):
                return {
                    "success": False,
                    "message": f"Approver does not have authority: {validation.get('reason', 'Unknown reason')}"
                }

            # Record approval
            approval_record = {
                "approver_name": approver_name,
                "approver_role": approver_role,
                "decision": decision,
                "comments": comments,
                "timestamp": datetime.now().isoformat()
            }

            request['approvals'].append(approval_record)

            # Update request status
            if decision.lower() == 'rejected':
                request['status'] = 'rejected'
                request['rejection_reason'] = comments or "Rejected by approver"
            elif validation.get('next_approver_required'):
                request['status'] = 'pending_approval'
            else:
                request['status'] = 'approved'
                request['approved_at'] = datetime.now().isoformat()

            return {
                "success": True,
                "message": f"Approval processed by {approver_name}",
                "new_status": request['status'],
                "validation": validation
            }

        except Exception as e:
            return {"success": False, "message": f"Error processing approval: {str(e)}"}

    def get_leave_summary(self, employee_id: str) -> Dict:
        """Get summary of all leave requests for an employee"""
        employee_requests = [req for req in self.leave_requests if req['employee_id'] == employee_id]

        summary = {
            "employee_id": employee_id,
            "total_requests": len(employee_requests),
            "approved": len([r for r in employee_requests if r['status'] == 'approved']),
            "pending": len([r for r in employee_requests if r['status'] == 'pending_approval']),
            "rejected": len([r for r in employee_requests if r['status'] == 'rejected']),
            "requests": employee_requests
        }

        return summary

    def generate_leave_report(self, request: Dict) -> str:
        """Generate a formatted report for a leave request"""
        report = f"""
{'='*80}
LEAVE REQUEST REPORT
{'='*80}

Request ID: {request['request_id']}
Status: {request['status'].upper()}
Created: {request['created_at']}

EMPLOYEE DETAILS:
  Name: {request['employee_name']}
  Employee ID: {request['employee_id']}
  Role: {request['role']}

LEAVE DETAILS:
  Type: {request['leave_type']}
  Start Date: {request['start_date']}
  End Date: {request['end_date']}
  Duration: {request['duration_days']} days
  Reason: {request['reason']}

AI ANALYSIS:
  Eligible: {request['analysis'].get('eligible', False)}
  Reason: {request['analysis'].get('reason', 'N/A')}
  Required Approvers: {', '.join(request['analysis'].get('required_approvers', []))}
  Recommendations: {request['analysis'].get('recommendations', 'None')}

APPROVALS:
"""
        if request['approvals']:
            for approval in request['approvals']:
                report += f"""
  - {approval['approver_name']} ({approval['approver_role']})
    Decision: {approval['decision']}
    Comments: {approval['comments']}
    Time: {approval['timestamp']}
"""
        else:
            report += "  No approvals yet\n"

        if request['status'] == 'rejected':
            report += f"\nREJECTION REASON: {request.get('rejection_reason', 'N/A')}\n"

        if request['status'] == 'approved':
            report += f"\nAPPROVED AT: {request.get('approved_at', 'N/A')}\n"

        report += f"\n{'='*80}\n"

        return report
