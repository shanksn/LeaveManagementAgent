"""
Leave Management System - Demo Application
Shows how to use the Leave Management Agent
"""

from leave_management_agent import LeaveManagementAgent
import time


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f"{title:^80}")
    print(f"{'='*80}\n")


def main():
    # Initialize the agent
    print_section("LEAVE MANAGEMENT AGENTIC AI SYSTEM")
    print("Initializing agent with HR knowledge base...")
    agent = LeaveManagementAgent()
    print("✓ Agent initialized successfully!\n")

    # Demo 1: Valid casual leave request
    print_section("SCENARIO 1: Valid Casual Leave Request")

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

    print(agent.generate_leave_report(request1))

    # Process approval from manager
    if request1['status'] == 'pending_approval':
        print("Processing manager approval...")
        time.sleep(1)
        approval1 = agent.process_approval(
            request_id=request1['request_id'],
            approver_name="Sarah Manager",
            approver_role="manager",
            decision="approved",
            comments="Approved. Enjoy your time off!"
        )
        print(f"✓ {approval1['message']}")
        print(f"  New Status: {approval1['new_status']}\n")

    # Demo 2: Sick leave exceeding policy
    print_section("SCENARIO 2: Sick Leave Exceeding Policy Limit")

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

    print(agent.generate_leave_report(request2))

    # Demo 3: Annual leave requiring multiple approvals
    print_section("SCENARIO 3: Annual Leave - Multiple Approvals Required")

    request3 = agent.create_leave_request(
        employee_name="Mike Johnson",
        employee_id="EMP003",
        role="manager",
        leave_type="annual_leave",
        start_date="2025-12-20",
        end_date="2025-12-31",  # 12 days
        reason="Year-end vacation with family",
        current_balance=21
    )

    print(agent.generate_leave_report(request3))

    if request3['status'] == 'pending_approval':
        # Manager approval
        print("Step 1: Processing manager approval...")
        time.sleep(1)
        approval3a = agent.process_approval(
            request_id=request3['request_id'],
            approver_name="David Senior",
            approver_role="senior_manager",
            decision="approved",
            comments="Approved by senior management. Have a great vacation!"
        )
        print(f"✓ {approval3a['message']}")
        print(f"  New Status: {approval3a['new_status']}\n")

        # Check if HR approval needed
        if approval3a.get('validation', {}).get('next_approver_required'):
            print("Step 2: Processing HR approval...")
            time.sleep(1)
            approval3b = agent.process_approval(
                request_id=request3['request_id'],
                approver_name="Lisa HR",
                approver_role="hr",
                decision="approved",
                comments="HR approved. All documentation complete."
            )
            print(f"✓ {approval3b['message']}")
            print(f"  New Status: {approval3b['new_status']}\n")

    # Demo 4: Rejection scenario
    print_section("SCENARIO 4: Leave Request Rejected")

    request4 = agent.create_leave_request(
        employee_name="Tom Brown",
        employee_id="EMP004",
        role="employee",
        leave_type="casual_leave",
        start_date="2025-11-03",
        end_date="2025-11-03",
        reason="Need day off",
        current_balance=0  # No leave balance
    )

    print(agent.generate_leave_report(request4))

    # Demo 5: Compensatory leave
    print_section("SCENARIO 5: Compensatory Leave Request")

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

    print(agent.generate_leave_report(request5))

    if request5['status'] == 'pending_approval':
        print("Processing manager approval...")
        time.sleep(1)
        approval5 = agent.process_approval(
            request_id=request5['request_id'],
            approver_name="Sarah Manager",
            approver_role="manager",
            decision="approved",
            comments="Approved. Thank you for your weekend work!"
        )
        print(f"✓ {approval5['message']}")
        print(f"  New Status: {approval5['new_status']}\n")

    # Summary Report
    print_section("EMPLOYEE LEAVE SUMMARY")

    for emp_id in ["EMP001", "EMP002", "EMP003", "EMP004", "EMP005"]:
        summary = agent.get_leave_summary(emp_id)
        print(f"Employee ID: {summary['employee_id']}")
        print(f"  Total Requests: {summary['total_requests']}")
        print(f"  Approved: {summary['approved']}")
        print(f"  Pending: {summary['pending']}")
        print(f"  Rejected: {summary['rejected']}")
        print()

    # Interactive mode
    print_section("INTERACTIVE MODE")
    print("The system is now ready for interactive use!")
    print("\nYou can:")
    print("  1. Create new leave requests")
    print("  2. Process approvals")
    print("  3. Generate reports")
    print("  4. Check employee summaries")
    print("\nFor a full demo, run this script again!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSystem terminated by user.")
    except Exception as e:
        print(f"\n\nError: {str(e)}")
        print("Make sure you have:")
        print("  1. Set OPENAI_API_KEY in .env file")
        print("  2. Installed required packages: pip install openai python-dotenv")
        print("  3. hr_knowledge_base.json file exists")
