"""
Leave Management System - Mock Demo (No API Required)
Shows how the system works with simulated AI responses
"""

import json
from datetime import datetime, timedelta


class MockLeaveManagementAgent:
    """Mock agent that simulates AI responses without API calls"""

    def __init__(self):
        """Initialize with HR knowledge base"""
        with open("hr_knowledge_base.json", 'r') as f:
            self.knowledge_base = json.load(f)
        self.leave_requests = []
        self.request_id_counter = 1

    def _get_policy_info(self, leave_type):
        """Retrieve policy information"""
        return self.knowledge_base["leave_policies"].get(leave_type.lower().replace(" ", "_"))

    def _mock_ai_analysis(self, request, policy):
        """Simulate AI analysis without API call"""
        duration = request['duration_days']
        current_balance = request.get('current_balance', policy['annual_quota'])

        # Rule-based simulation of AI analysis
        if current_balance <= 0:
            return {
                "eligible": False,
                "reason": f"Insufficient leave balance. Current balance: {current_balance} days, Requested: {duration} days",
                "required_approvers": [],
                "recommendations": ["Apply for unpaid leave or wait until next quota refresh"]
            }

        if duration > policy['max_consecutive_days']:
            return {
                "eligible": False,
                "reason": f"Request exceeds maximum consecutive days. Max allowed: {policy['max_consecutive_days']} days, Requested: {duration} days",
                "required_approvers": [],
                "recommendations": [
                    f"Split the request into multiple applications of max {policy['max_consecutive_days']} days each",
                    "For medical emergencies, provide medical certificate for exception approval"
                ]
            }

        if duration > current_balance:
            return {
                "eligible": False,
                "reason": f"Insufficient leave balance. Available: {current_balance} days, Requested: {duration} days",
                "required_approvers": [],
                "recommendations": ["Reduce the number of days or check if unpaid leave is an option"]
            }

        # Determine required approvers based on policy
        approval_req = policy['approval_required']
        if approval_req == "manager":
            required_approvers = ["manager"]
        elif approval_req == "manager_and_hr":
            required_approvers = ["manager", "hr"] if duration > 7 else ["manager"]
        else:
            required_approvers = ["manager"]

        return {
            "eligible": True,
            "reason": f"Request complies with {policy['name']} policy. Duration: {duration} days, Balance after approval: {current_balance - duration} days",
            "required_approvers": required_approvers,
            "recommendations": [
                f"Ensure {policy['advance_notice_days']} days advance notice is provided",
                "Handover pending work before leave starts"
            ]
        }

    def create_leave_request(self, employee_name, employee_id, role, leave_type,
                            start_date, end_date, reason, current_balance=None):
        """Create and analyze leave request"""
        # Calculate duration
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        duration = (end - start).days + 1

        policy = self._get_policy_info(leave_type)
        if not policy:
            return {
                "request_id": f"LR-{self.request_id_counter:04d}",
                "status": "rejected",
                "error": f"Invalid leave type: {leave_type}"
            }

        if current_balance is None:
            current_balance = policy['annual_quota']

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

        # Mock AI analysis
        analysis = self._mock_ai_analysis(request, policy)
        request['analysis'] = analysis
        request['policy'] = policy

        # Set status
        if not analysis['eligible']:
            request['status'] = 'rejected'
            request['rejection_reason'] = analysis['reason']
        else:
            request['status'] = 'pending_approval'
            request['required_approvers'] = analysis['required_approvers']

        self.leave_requests.append(request)
        self.request_id_counter += 1

        return request

    def process_approval(self, request_id, approver_name, approver_role, decision, comments=""):
        """Process approval"""
        request = None
        for req in self.leave_requests:
            if req['request_id'] == request_id:
                request = req
                break

        if not request:
            return {"success": False, "message": "Request not found"}

        if request['status'] not in ['pending_approval', 'pending']:
            return {"success": False, "message": f"Request is already {request['status']}"}

        # Mock validation of approver authority
        hierarchy = self.knowledge_base['approval_hierarchy']
        approver_info = hierarchy.get(approver_role)

        if not approver_info:
            return {"success": False, "message": f"Invalid approver role: {approver_role}"}

        # Check if approver is in required list
        required = request.get('required_approvers', [])
        if approver_role not in required:
            return {
                "success": False,
                "message": f"Approver role '{approver_role}' not in required approvers: {required}"
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

        # Update status
        if decision.lower() == 'rejected':
            request['status'] = 'rejected'
            request['rejection_reason'] = comments or "Rejected by approver"
            next_approver_required = False
        else:
            # Remove this approver from required list
            required.remove(approver_role)
            request['required_approvers'] = required

            if len(required) == 0:
                request['status'] = 'approved'
                request['approved_at'] = datetime.now().isoformat()
                next_approver_required = False
            else:
                request['status'] = 'pending_approval'
                next_approver_required = True

        return {
            "success": True,
            "message": f"Approval processed by {approver_name}",
            "new_status": request['status'],
            "validation": {
                "has_authority": True,
                "reason": f"{approver_role} has authority to approve requests",
                "next_approver_required": next_approver_required
            }
        }

    def generate_leave_report(self, request):
        """Generate formatted report"""
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
  Current Balance: {request.get('current_balance', 'N/A')} days

POLICY INFORMATION:
  Leave Type: {request.get('policy', {}).get('name', 'N/A')}
  Annual Quota: {request.get('policy', {}).get('annual_quota', 'N/A')} days
  Max Consecutive: {request.get('policy', {}).get('max_consecutive_days', 'N/A')} days
  Advance Notice: {request.get('policy', {}).get('advance_notice_days', 'N/A')} days

AI ANALYSIS:
  Eligible: {request['analysis'].get('eligible', False)}
  Reason: {request['analysis'].get('reason', 'N/A')}
  Required Approvers: {', '.join(request['analysis'].get('required_approvers', []))}
  Recommendations:
"""
        for rec in request['analysis'].get('recommendations', []):
            report += f"    - {rec}\n"

        report += "\nAPPROVALS:\n"
        if request['approvals']:
            for approval in request['approvals']:
                report += f"""
  ✓ {approval['approver_name']} ({approval['approver_role']})
    Decision: {approval['decision'].upper()}
    Comments: {approval['comments']}
    Time: {approval['timestamp']}
"""
        else:
            report += "  No approvals yet\n"

        if request['status'] == 'rejected':
            report += f"\n❌ REJECTION REASON: {request.get('rejection_reason', 'N/A')}\n"

        if request['status'] == 'approved':
            report += f"\n✓ APPROVED AT: {request.get('approved_at', 'N/A')}\n"

        report += f"\n{'='*80}\n"
        return report

    def get_leave_summary(self, employee_id):
        """Get employee leave summary"""
        employee_requests = [req for req in self.leave_requests if req['employee_id'] == employee_id]
        return {
            "employee_id": employee_id,
            "total_requests": len(employee_requests),
            "approved": len([r for r in employee_requests if r['status'] == 'approved']),
            "pending": len([r for r in employee_requests if r['status'] == 'pending_approval']),
            "rejected": len([r for r in employee_requests if r['status'] == 'rejected']),
            "requests": employee_requests
        }


def print_section(title):
    """Print formatted section"""
    print(f"\n{'='*80}")
    print(f"{title:^80}")
    print(f"{'='*80}\n")


def main():
    print_section("LEAVE MANAGEMENT AI SYSTEM - MOCK DEMO")
    print("✓ Running without API calls - using simulated AI responses\n")

    print("📌 Initializing agent...")
    agent = MockLeaveManagementAgent()
    print("✓ Agent initialized\n")

    # Scenario 1: Valid casual leave
    print_section("SCENARIO 1: Valid Casual Leave Request ✓")

    print("📌 METHOD CALL: agent.create_leave_request()")
    print("   Parameters:")
    print("     - employee_name: 'John Doe'")
    print("     - employee_id: 'EMP001'")
    print("     - role: 'employee'")
    print("     - leave_type: 'casual_leave'")
    print("     - start_date: '2025-11-01'")
    print("     - end_date: '2025-11-02'")
    print("     - reason: 'Family function to attend'")
    print("     - current_balance: 12")
    print()

    request1 = agent.create_leave_request(
        employee_name="John Doe",
        employee_id="EMP001",
        role="employee",
        leave_type="casual_leave",
        start_date="2025-11-01",
        end_date="2025-11-02",
        reason="Family function to attend",
        current_balance=12
    )

    print(f"✓ Request created: {request1['request_id']}\n")
    print("📌 METHOD CALL: agent.generate_leave_report(request1)")
    print()
    print(agent.generate_leave_report(request1))

    if request1['status'] == 'pending_approval':
        print("🔄 Processing manager approval...")
        print("\n📌 METHOD CALL: agent.process_approval()")
        print("   Parameters:")
        print(f"     - request_id: '{request1['request_id']}'")
        print("     - approver_name: 'Sarah Manager'")
        print("     - approver_role: 'manager'")
        print("     - decision: 'approved'")
        print("     - comments: 'Approved. Enjoy your time off!'")
        print()

        approval1 = agent.process_approval(
            request_id=request1['request_id'],
            approver_name="Sarah Manager",
            approver_role="manager",
            decision="approved",
            comments="Approved. Enjoy your time off!"
        )
        print(f"✓ {approval1['message']}")
        print(f"  New Status: {approval1['new_status']}\n")

    # Scenario 2: Policy violation
    print_section("SCENARIO 2: Sick Leave Exceeding Policy Limit ❌")

    print("📌 METHOD CALL: agent.create_leave_request()")
    print("   Parameters:")
    print("     - employee_name: 'Jane Smith'")
    print("     - employee_id: 'EMP002'")
    print("     - leave_type: 'sick_leave'")
    print("     - start_date: '2025-11-05'")
    print("     - end_date: '2025-11-12' (8 days - EXCEEDS MAX OF 5)")
    print()

    request2 = agent.create_leave_request(
        employee_name="Jane Smith",
        employee_id="EMP002",
        role="employee",
        leave_type="sick_leave",
        start_date="2025-11-05",
        end_date="2025-11-12",  # 8 days - exceeds max of 5
        reason="Recovering from surgery",
        current_balance=12
    )

    print(f"✓ Request created: {request2['request_id']} (Auto-rejected due to policy violation)\n")
    print("📌 METHOD CALL: agent.generate_leave_report(request2)")
    print()
    print(agent.generate_leave_report(request2))

    # Scenario 3: Multi-level approval
    print_section("SCENARIO 3: Annual Leave - Multiple Approvals Required 🔄")

    print("📌 METHOD CALL: agent.create_leave_request()")
    print("   Parameters:")
    print("     - employee_name: 'Mike Johnson'")
    print("     - employee_id: 'EMP003'")
    print("     - role: 'manager'")
    print("     - leave_type: 'annual_leave'")
    print("     - duration: 8 days (Requires MANAGER + HR approval)")
    print()

    request3 = agent.create_leave_request(
        employee_name="Mike Johnson",
        employee_id="EMP003",
        role="manager",
        leave_type="annual_leave",
        start_date="2025-12-20",
        end_date="2025-12-27",  # 8 days
        reason="Year-end vacation with family",
        current_balance=21
    )

    print(f"✓ Request created: {request3['request_id']}\n")
    print("📌 METHOD CALL: agent.generate_leave_report(request3)")
    print()
    print(agent.generate_leave_report(request3))

    if request3['status'] == 'pending_approval':
        print("🔄 Step 1: Processing manager approval...")
        print("\n📌 METHOD CALL: agent.process_approval() [MANAGER]")
        print("   Parameters:")
        print(f"     - request_id: '{request3['request_id']}'")
        print("     - approver_name: 'David Senior'")
        print("     - approver_role: 'manager'")
        print("     - decision: 'approved'")
        print()

        approval3a = agent.process_approval(
            request_id=request3['request_id'],
            approver_name="David Senior",
            approver_role="manager",
            decision="approved",
            comments="Approved. Have a great vacation!"
        )
        print(f"✓ {approval3a['message']}")
        print(f"  New Status: {approval3a['new_status']}")

        if approval3a['validation'].get('next_approver_required'):
            print("\n🔄 Step 2: Processing HR approval...")
            print("\n📌 METHOD CALL: agent.process_approval() [HR]")
            print("   Parameters:")
            print(f"     - request_id: '{request3['request_id']}'")
            print("     - approver_name: 'Lisa HR'")
            print("     - approver_role: 'hr'")
            print("     - decision: 'approved'")
            print()

            approval3b = agent.process_approval(
                request_id=request3['request_id'],
                approver_name="Lisa HR",
                approver_role="hr",
                decision="approved",
                comments="HR approved. All documentation complete."
            )
            print(f"✓ {approval3b['message']}")
            print(f"  New Status: {approval3b['new_status']}\n")

    # Scenario 4: Insufficient balance
    print_section("SCENARIO 4: Insufficient Leave Balance ❌")

    print("📌 METHOD CALL: agent.create_leave_request()")
    print("   Parameters:")
    print("     - employee_name: 'Tom Brown'")
    print("     - current_balance: 0 (NO QUOTA LEFT)")
    print()

    request4 = agent.create_leave_request(
        employee_name="Tom Brown",
        employee_id="EMP004",
        role="employee",
        leave_type="casual_leave",
        start_date="2025-11-03",
        end_date="2025-11-03",
        reason="Need day off",
        current_balance=0
    )

    print(f"✓ Request created: {request4['request_id']} (Auto-rejected - insufficient balance)\n")
    print("📌 METHOD CALL: agent.generate_leave_report(request4)")
    print()
    print(agent.generate_leave_report(request4))

    # Scenario 5: Compensatory leave
    print_section("SCENARIO 5: Compensatory Leave Request ✓")

    print("📌 METHOD CALL: agent.create_leave_request()")
    print("   Parameters:")
    print("     - employee_name: 'Amy Wilson'")
    print("     - leave_type: 'compensatory_leave'")
    print("     - reason: 'Worked during weekend for project delivery'")
    print()

    request5 = agent.create_leave_request(
        employee_name="Amy Wilson",
        employee_id="EMP005",
        role="employee",
        leave_type="compensatory_leave",
        start_date="2025-11-10",
        end_date="2025-11-10",
        reason="Worked during weekend for project delivery",
        current_balance=2
    )

    print(f"✓ Request created: {request5['request_id']}\n")
    print("📌 METHOD CALL: agent.generate_leave_report(request5)")
    print()
    print(agent.generate_leave_report(request5))

    if request5['status'] == 'pending_approval':
        print("🔄 Processing manager approval...")
        print("\n📌 METHOD CALL: agent.process_approval()")
        print("   Parameters:")
        print(f"     - request_id: '{request5['request_id']}'")
        print("     - approver_name: 'Sarah Manager'")
        print("     - approver_role: 'manager'")
        print("     - decision: 'approved'")
        print()

        approval5 = agent.process_approval(
            request_id=request5['request_id'],
            approver_name="Sarah Manager",
            approver_role="manager",
            decision="approved",
            comments="Approved. Thank you for your weekend work!"
        )
        print(f"✓ {approval5['message']}")
        print(f"  New Status: {approval5['new_status']}\n")

    # Summary
    print_section("EMPLOYEE LEAVE SUMMARY 📊")

    print("📌 METHOD CALL: agent.get_leave_summary() for each employee\n")

    for emp_id in ["EMP001", "EMP002", "EMP003", "EMP004", "EMP005"]:
        print(f"   → agent.get_leave_summary('{emp_id}')")
        summary = agent.get_leave_summary(emp_id)
        print(f"     Employee ID: {summary['employee_id']}")
        print(f"       Total Requests: {summary['total_requests']}")
        print(f"       ✓ Approved: {summary['approved']}")
        print(f"       🔄 Pending: {summary['pending']}")
        print(f"       ❌ Rejected: {summary['rejected']}")
        print()

    print_section("DEMO COMPLETE!")
    print("This mock demo shows the system working without API calls.")
    print("The real system uses GPT-4o-mini for intelligent policy analysis.")
    print("\nKey Features Demonstrated:")
    print("  ✓ Policy-compliant requests are approved")
    print("  ❌ Policy violations are auto-rejected with reasons")
    print("  🔄 Multi-level approvals work correctly")
    print("  📊 Complete audit trail maintained")
    print("\n✓ System is ready for production use with valid API key!")


if __name__ == "__main__":
    main()
