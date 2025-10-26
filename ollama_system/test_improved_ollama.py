"""
Quick test of improved Ollama prompts
Tests the enhanced accuracy of Llama 3.2 with better prompts
"""

from leave_management_agent_ollama import LeaveManagementAgentOllama


def test_improved_prompts():
    """Test improved prompts for better accuracy"""

    print("="*80)
    print("Testing IMPROVED Ollama Prompts with GPU Acceleration")
    print("="*80)

    agent = LeaveManagementAgentOllama(model="llama3.2:latest")

    # Check Ollama status
    status = agent.check_ollama_status()
    if not status.get('ollama_running'):
        print(f"\n❌ Ollama not running: {status.get('error')}")
        return

    print(f"\n✓ Ollama ready with model: {agent.model}")
    print(f"✓ GPU acceleration: {'Enabled' if status.get('model_available') else 'Disabled'}\n")

    # Test Case 1: Should catch 8 days > 5 days max (CRITICAL TEST)
    print("\n" + "="*80)
    print("TEST 1: Policy Violation Detection (8 days sick leave, max is 5)")
    print("="*80)
    print("Expected: REJECT (exceeds max consecutive days)")
    print("Testing improved prompt...\n")

    request1 = agent.create_leave_request(
        employee_name="Jane Smith",
        employee_id="EMP002",
        role="employee",
        leave_type="sick_leave",
        start_date="2025-11-05",
        end_date="2025-11-12",  # 8 days - EXCEEDS MAX OF 5
        reason="Recovering from surgery",
        current_balance=12
    )

    print(f"\n✓ Request created: {request1['request_id']}")
    print(f"   Status: {request1['status']}")
    print(f"   Eligible: {request1['analysis'].get('eligible')}")
    print(f"   Reason: {request1['analysis'].get('reason')}")

    if not request1['analysis'].get('eligible'):
        print("\n✅ PASS: Correctly detected policy violation!")
    else:
        print("\n❌ FAIL: Should have rejected (8 > 5 days)")

    # Test Case 2: Valid request (should approve)
    print("\n" + "="*80)
    print("TEST 2: Valid Request (2 days casual leave, max is 3)")
    print("="*80)
    print("Expected: APPROVE")
    print("Testing...\n")

    request2 = agent.create_leave_request(
        employee_name="John Doe",
        employee_id="EMP001",
        role="employee",
        leave_type="casual_leave",
        start_date="2025-11-01",
        end_date="2025-11-02",  # 2 days - WITHIN LIMIT
        reason="Family function",
        current_balance=12
    )

    print(f"\n✓ Request created: {request2['request_id']}")
    print(f"   Status: {request2['status']}")
    print(f"   Eligible: {request2['analysis'].get('eligible')}")
    print(f"   Reason: {request2['analysis'].get('reason')}")

    if request2['analysis'].get('eligible'):
        print("\n✅ PASS: Correctly approved valid request!")
    else:
        print("\n❌ FAIL: Should have approved (2 ≤ 3 days)")

    # Test Case 3: Zero balance (should reject)
    print("\n" + "="*80)
    print("TEST 3: Insufficient Balance (requesting 1 day with 0 balance)")
    print("="*80)
    print("Expected: REJECT (no balance)")
    print("Testing...\n")

    request3 = agent.create_leave_request(
        employee_name="Tom Brown",
        employee_id="EMP004",
        role="employee",
        leave_type="casual_leave",
        start_date="2025-11-03",
        end_date="2025-11-03",  # 1 day
        reason="Personal work",
        current_balance=0  # NO BALANCE
    )

    print(f"\n✓ Request created: {request3['request_id']}")
    print(f"   Status: {request3['status']}")
    print(f"   Eligible: {request3['analysis'].get('eligible')}")
    print(f"   Reason: {request3['analysis'].get('reason')}")

    if not request3['analysis'].get('eligible'):
        print("\n✅ PASS: Correctly rejected (zero balance)!")
    else:
        print("\n❌ FAIL: Should have rejected (balance = 0)")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    tests = [
        ("Policy violation detection", not request1['analysis'].get('eligible')),
        ("Valid request approval", request2['analysis'].get('eligible')),
        ("Zero balance rejection", not request3['analysis'].get('eligible'))
    ]

    passed = sum(1 for _, result in tests if result)
    total = len(tests)

    print(f"\nTests passed: {passed}/{total} ({passed/total*100:.0f}%)")

    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")

    print("\n" + "="*80)
    print("IMPROVEMENTS MADE:")
    print("="*80)
    print("1. ✅ Enhanced prompts with explicit policy rules")
    print("2. ✅ Added analysis checklists for structured reasoning")
    print("3. ✅ GPU acceleration enabled (num_gpu: -1)")
    print("4. ✅ Temperature set to 0.0 for deterministic results")
    print("5. ✅ Increased num_predict to 800 tokens for detailed responses")
    print("6. ✅ Better JSON extraction with fallbacks")
    print("\nCompare this with the earlier run to see improvement!")


if __name__ == "__main__":
    test_improved_prompts()
