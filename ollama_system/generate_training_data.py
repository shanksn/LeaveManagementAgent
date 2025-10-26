"""
Generate Training Data for Fine-Tuning Llama 3.2
Creates comprehensive examples for HR leave policy analysis
"""

import json
from itertools import product
from datetime import datetime, timedelta


def generate_training_examples():
    """Generate comprehensive training dataset"""

    training_data = []

    # Policy definitions
    policies = {
        "casual_leave": {
            "name": "Casual Leave",
            "max_consecutive": 3,
            "annual_quota": 12,
            "advance_notice": 1,
            "approver": "manager"
        },
        "sick_leave": {
            "name": "Sick Leave",
            "max_consecutive": 5,
            "annual_quota": 12,
            "advance_notice": 0,
            "approver": "manager"
        },
        "annual_leave": {
            "name": "Annual Leave",
            "max_consecutive": 15,
            "annual_quota": 21,
            "advance_notice": 7,
            "approver": "manager_and_hr"
        },
        "maternity_leave": {
            "name": "Maternity Leave",
            "max_consecutive": 180,
            "annual_quota": 180,
            "advance_notice": 30,
            "approver": "manager_and_hr"
        },
        "compensatory_leave": {
            "name": "Compensatory Off",
            "max_consecutive": 2,
            "annual_quota": 24,
            "advance_notice": 1,
            "approver": "manager"
        }
    }

    # Generate examples for each leave type
    for leave_type, policy in policies.items():
        # Valid requests (within limits)
        for duration in [1, 2, policy["max_consecutive"]]:
            for balance in [policy["annual_quota"], policy["annual_quota"] - 5]:
                if balance >= duration:
                    training_data.append(create_example(
                        leave_type=leave_type,
                        policy=policy,
                        duration=duration,
                        balance=balance,
                        eligible=True
                    ))

        # Policy violations - exceeds max consecutive days
        if policy["max_consecutive"] < 180:  # Skip for maternity
            for duration in [policy["max_consecutive"] + 1, policy["max_consecutive"] + 3]:
                training_data.append(create_example(
                    leave_type=leave_type,
                    policy=policy,
                    duration=duration,
                    balance=policy["annual_quota"],
                    eligible=False,
                    violation="max_consecutive"
                ))

        # Policy violations - insufficient balance
        for duration in [3, 5]:
            if duration > 0:
                balance = duration - 1  # Balance less than duration
                if balance >= 0:
                    training_data.append(create_example(
                        leave_type=leave_type,
                        policy=policy,
                        duration=duration,
                        balance=balance,
                        eligible=False,
                        violation="insufficient_balance"
                    ))

    # Edge cases
    training_data.extend(generate_edge_cases(policies))

    return training_data


def create_example(leave_type, policy, duration, balance, eligible, violation=None):
    """Create a single training example"""

    # Determine approvers
    if policy["approver"] == "manager":
        approvers = ["manager"]
    elif policy["approver"] == "manager_and_hr":
        approvers = ["manager", "hr"] if duration > 7 else ["manager"]
    else:
        approvers = ["manager"]

    # Create prompt
    prompt = f"""Analyze this leave request:

=== EMPLOYEE ===
Name: Employee Name
ID: EMP001
Role: employee

=== LEAVE REQUEST ===
Type: {leave_type} ({policy['name']})
Duration: {duration} days
Balance: {balance} days

=== POLICY CONSTRAINTS ===
Annual Quota: {policy['annual_quota']} days
Max Consecutive Days: {policy['max_consecutive']} days
Advance Notice Required: {policy['advance_notice']} days
Approval Chain: {policy['approver']}

=== ANALYSIS CHECKLIST ===
[ ] Duration ({duration} days) ≤ Max Consecutive ({policy['max_consecutive']} days)?
[ ] Duration ({duration} days) ≤ Current Balance ({balance} days)?
[ ] Balance after ({balance - duration} days) ≥ 0?"""

    # Create response based on eligibility
    if eligible:
        response = {
            "eligible": True,
            "reason": f"Request complies with {policy['name']} policy. Duration: {duration} days, Balance after approval: {balance - duration} days",
            "required_approvers": approvers,
            "recommendations": [
                f"Ensure {policy['advance_notice']} days advance notice is provided",
                "Handover pending work before leave starts"
            ]
        }
    else:
        if violation == "max_consecutive":
            response = {
                "eligible": False,
                "reason": f"Request exceeds maximum consecutive days. Max allowed: {policy['max_consecutive']} days, Requested: {duration} days",
                "required_approvers": [],
                "recommendations": [
                    f"Split the request into multiple applications of max {policy['max_consecutive']} days each",
                    "For medical emergencies, provide medical certificate for exception approval"
                ]
            }
        elif violation == "insufficient_balance":
            response = {
                "eligible": False,
                "reason": f"Insufficient leave balance. Current balance: {balance} days, Requested: {duration} days",
                "required_approvers": [],
                "recommendations": [
                    "Apply for unpaid leave or wait until next quota refresh",
                    "Check if compensatory off is available"
                ]
            }
        else:
            response = {
                "eligible": False,
                "reason": "Policy violation detected",
                "required_approvers": [],
                "recommendations": ["Review company leave policy"]
            }

    return {
        "prompt": prompt,
        "response": json.dumps(response, indent=2)
    }


def generate_edge_cases(policies):
    """Generate edge case examples"""

    edge_cases = []

    # Zero balance
    edge_cases.append({
        "prompt": """Analyze: casual_leave, 1 day, balance 0 days, max 3""",
        "response": json.dumps({
            "eligible": False,
            "reason": "Insufficient leave balance. Current balance: 0 days",
            "required_approvers": [],
            "recommendations": ["Wait for quota refresh", "Apply for unpaid leave"]
        })
    })

    # Exact limit
    edge_cases.append({
        "prompt": """Analyze: casual_leave, 3 days, balance 12 days, max 3 (EXACT LIMIT)""",
        "response": json.dumps({
            "eligible": True,
            "reason": "Request is at exact policy limit (3 days = max 3 days). This is acceptable.",
            "required_approvers": ["manager"],
            "recommendations": ["Ensure proper planning as this uses maximum consecutive days"]
        })
    })

    # Medical emergency
    edge_cases.append({
        "prompt": """Analyze: sick_leave, 8 days, balance 12, max 5, reason: emergency surgery""",
        "response": json.dumps({
            "eligible": False,
            "reason": "Duration exceeds max consecutive (5 days), but medical emergency may warrant exception",
            "required_approvers": [],
            "recommendations": [
                "Provide medical certificate from doctor",
                "Request HR for extended sick leave exception",
                "Consider medical leave policy for surgeries"
            ]
        })
    })

    return edge_cases


def save_training_data(training_data, filename="training_data.jsonl"):
    """Save training data in JSONL format"""

    with open(filename, 'w') as f:
        for example in training_data:
            f.write(json.dumps(example) + '\n')

    print(f"✓ Saved {len(training_data)} training examples to {filename}")


def save_for_ollama(training_data, filename="ollama_training.txt"):
    """Save in format optimized for Ollama fine-tuning"""

    with open(filename, 'w') as f:
        for example in training_data:
            f.write("### Instruction:\n")
            f.write(example['prompt'] + '\n\n')
            f.write("### Response:\n")
            f.write(example['response'] + '\n\n')
            f.write("---\n\n")

    print(f"✓ Saved Ollama format to {filename}")


def generate_statistics(training_data):
    """Print statistics about training data"""

    total = len(training_data)
    eligible_count = sum(1 for ex in training_data if '"eligible": true' in ex['response'].lower())
    ineligible_count = total - eligible_count

    print("\n📊 Training Data Statistics:")
    print(f"  Total examples: {total}")
    print(f"  Eligible (approved): {eligible_count} ({eligible_count/total*100:.1f}%)")
    print(f"  Ineligible (rejected): {ineligible_count} ({ineligible_count/total*100:.1f}%)")

    # Count by leave type
    leave_types = {}
    for ex in training_data:
        for leave_type in ["casual_leave", "sick_leave", "annual_leave", "maternity_leave", "compensatory_leave"]:
            if leave_type in ex['prompt']:
                leave_types[leave_type] = leave_types.get(leave_type, 0) + 1
                break

    print("\n  By leave type:")
    for leave_type, count in leave_types.items():
        print(f"    - {leave_type}: {count} examples")


def main():
    """Main function"""

    print("🔧 Generating training data for HR leave management...\n")

    # Generate training examples
    training_data = generate_training_examples()

    # Save in different formats
    save_training_data(training_data, "training_data.jsonl")
    save_for_ollama(training_data, "ollama_training.txt")

    # Print statistics
    generate_statistics(training_data)

    print("\n✅ Training data generation complete!")
    print("\nNext steps:")
    print("  1. Review training_data.jsonl to ensure quality")
    print("  2. Create Modelfile for Ollama")
    print("  3. Run: ollama create hr-assistant -f Modelfile")
    print("  4. Test: ollama run hr-assistant")
    print("\nSee FINE_TUNING_GUIDE.md for detailed instructions")


if __name__ == "__main__":
    main()
