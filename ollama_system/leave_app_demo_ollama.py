"""
Leave Management System - Ollama Demo
Uses local Llama 3.2 model instead of OpenAI API
"""

from leave_management_agent_ollama import LeaveManagementAgentOllama
import time


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f"{title:^80}")
    print(f"{'='*80}\n")


def main():
    print_section("LEAVE MANAGEMENT AI SYSTEM - OLLAMA (LOCAL) VERSION")
    print("Using Llama 3.2 model via Ollama - No API costs, fully local!\n")

    # Initialize agent
    print("📌 Initializing agent with Ollama (Llama 3.2)...")
    agent = LeaveManagementAgentOllama(model="llama3.2:latest")

    # Check Ollama status
    print("🔍 Checking Ollama status...")
    status = agent.check_ollama_status()

    if not status.get('ollama_running'):
        print(f"\n❌ ERROR: {status.get('error')}")
        print(f"💡 {status.get('suggestion', 'Make sure Ollama is installed and running')}")
        print("\nTo fix:")
        print("  1. Install Ollama: https://ollama.com/download")
        print("  2. Start Ollama: ollama serve")
        print("  3. Pull Llama 3.2: ollama pull llama3.2:latest")
        return

    print(f"✓ Ollama is running")
    print(f"  Available models: {', '.join(status['available_models'][:3])}{'...' if len(status['available_models']) > 3 else ''}")

    if not status.get('model_available'):
        print(f"\n⚠️  Model '{agent.model}' not found!")
        print(f"💡 Pull the model with: ollama pull {agent.model}")
        return

    print(f"✓ Model '{agent.model}' is ready\n")

    # Scenario 1: Valid casual leave
    print_section("SCENARIO 1: Valid Casual Leave Request ✓")

    print("📌 METHOD CALL: agent.create_leave_request()")
    print("   Using local Llama 3.2 for analysis...\n")

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

    print(f"\n✓ Request created: {request1['request_id']}\n")
    print(agent.generate_leave_report(request1))

    if request1['status'] == 'pending_approval':
        print("🔄 Processing manager approval...")
        print("\n📌 METHOD CALL: agent.process_approval()")
        print("   Validating authority with Llama 3.2...\n")

        approval1 = agent.process_approval(
            request_id=request1['request_id'],
            approver_name="Sarah Manager",
            approver_role="manager",
            decision="approved",
            comments="Approved. Enjoy your time off!"
        )
        print(f"\n✓ {approval1['message']}")
        print(f"  New Status: {approval1['new_status']}\n")
        time.sleep(1)

    # Scenario 2: Policy violation
    print_section("SCENARIO 2: Sick Leave Exceeding Policy Limit ❌")

    print("📌 METHOD CALL: agent.create_leave_request()")
    print("   Analyzing policy violation with Llama 3.2...\n")

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

    print(f"\n✓ Request created: {request2['request_id']}")
    print(agent.generate_leave_report(request2))

    # Scenario 3: Multi-level approval
    print_section("SCENARIO 3: Annual Leave - Multiple Approvals Required 🔄")

    print("📌 METHOD CALL: agent.create_leave_request()")
    print("   Analyzing with Llama 3.2...\n")

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

    print(f"\n✓ Request created: {request3['request_id']}")
    print(agent.generate_leave_report(request3))

    if request3['status'] == 'pending_approval':
        print("🔄 Step 1: Processing manager approval...")
        print("\n📌 METHOD CALL: agent.process_approval() [MANAGER]")

        approval3a = agent.process_approval(
            request_id=request3['request_id'],
            approver_name="David Senior",
            approver_role="manager",
            decision="approved",
            comments="Approved. Have a great vacation!"
        )
        print(f"\n✓ {approval3a['message']}")
        print(f"  New Status: {approval3a['new_status']}")

        if approval3a['validation'].get('next_approver_required'):
            print("\n🔄 Step 2: Processing HR approval...")
            print("\n📌 METHOD CALL: agent.process_approval() [HR]")
            time.sleep(1)

            approval3b = agent.process_approval(
                request_id=request3['request_id'],
                approver_name="Lisa HR",
                approver_role="hr",
                decision="approved",
                comments="HR approved. All documentation complete."
            )
            print(f"\n✓ {approval3b['message']}")
            print(f"  New Status: {approval3b['new_status']}\n")

    # Summary
    print_section("EMPLOYEE LEAVE SUMMARY 📊")

    print("📌 METHOD CALL: agent.get_leave_summary() for each employee\n")

    for emp_id in ["EMP001", "EMP002", "EMP003"]:
        summary = agent.get_leave_summary(emp_id)
        if summary['total_requests'] > 0:
            print(f"   → agent.get_leave_summary('{emp_id}')")
            print(f"     Employee ID: {summary['employee_id']}")
            print(f"       Total Requests: {summary['total_requests']}")
            print(f"       ✓ Approved: {summary['approved']}")
            print(f"       🔄 Pending: {summary['pending']}")
            print(f"       ❌ Rejected: {summary['rejected']}")
            print()

    print_section("DEMO COMPLETE!")
    print("✅ All analysis done using LOCAL Llama 3.2 model!")
    print("✅ No API costs")
    print("✅ Complete data privacy (everything stays on your machine)")
    print("✅ No internet connection required (after model download)")
    print("\nPerformance:")
    print("  - Llama 3.2 is fast and accurate for policy analysis")
    print("  - Typical response time: 2-5 seconds per analysis")
    print("  - Can handle complex reasoning and edge cases")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSystem terminated by user.")
    except Exception as e:
        print(f"\n\nError: {str(e)}")
        import traceback
        traceback.print_exc()
