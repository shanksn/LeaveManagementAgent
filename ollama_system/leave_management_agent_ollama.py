"""
Leave Management Agentic AI System - Ollama Version
Uses local Llama 3.2 model via Ollama instead of OpenAI API
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
import requests


class LeaveManagementAgentOllama:
    """AI Agent for managing leave requests using Ollama (Llama 3.2)"""

    def __init__(self, knowledge_base_path: str = "../shared/hr_knowledge_base.json",
                 ollama_url: str = "http://localhost:11434",
                 model: str = "llama3.2:latest"):
        """Initialize the agent with HR knowledge base and Ollama config"""
        self.ollama_url = ollama_url
        self.model = model
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

    def _call_ollama(self, system_prompt: str, user_prompt: str, use_gpu: bool = True) -> Dict:
        """
        Call Ollama API with the given prompts
        Returns parsed JSON response

        Args:
            system_prompt: System instruction for the AI
            user_prompt: User query/task
            use_gpu: Whether to use GPU acceleration (default: True)
        """
        url = f"{self.ollama_url}/api/generate"

        # Improved prompt format for Llama 3.2
        full_prompt = f"""You are a helpful AI assistant specialized in HR policy analysis.

SYSTEM INSTRUCTIONS:
{system_prompt}

USER REQUEST:
{user_prompt}

IMPORTANT:
- Respond ONLY with valid JSON
- Do not include any explanatory text before or after the JSON
- Ensure all keys are present in the response
- Be precise and factual based only on the provided information

Your JSON response:"""

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "format": "json",  # Force JSON output
            "options": {
                "temperature": 0.0,  # Deterministic for consistency
                "top_p": 0.95,       # Nucleus sampling for quality
                "top_k": 40,         # Limit token choices
                "num_predict": 800,  # Allow longer responses
                "repeat_penalty": 1.1,  # Reduce repetition
                "num_gpu": -1 if use_gpu else 0,  # Use all GPU layers if available
                "num_thread": 8      # Multi-threading for CPU
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()

            result = response.json()
            response_text = result.get('response', '{}')

            # Parse JSON response
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from text
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    return {"error": "Could not parse JSON response", "raw": response_text}

        except requests.exceptions.ConnectionError:
            return {
                "error": "Cannot connect to Ollama. Make sure Ollama is running on localhost:11434",
                "suggestion": "Run: ollama serve"
            }
        except Exception as e:
            return {"error": str(e)}

    def analyze_leave_request(self, request: Dict) -> Dict:
        """
        Use Ollama (Llama 3.2) to analyze leave request against HR policies
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

        # Enhanced prompts for better accuracy
        system_prompt = """You are an expert HR policy analyst AI. Your role is to:
1. Strictly evaluate leave requests against company policies
2. Check ALL policy constraints (quota, duration, balance, advance notice)
3. Provide clear, actionable recommendations
4. Be conservative - reject if ANY policy violation exists

You must respond in EXACT JSON format with these keys:
- "eligible": boolean (true/false)
- "reason": string (detailed explanation)
- "required_approvers": array of strings (roles that must approve)
- "recommendations": array of strings (helpful suggestions)

Rules for analysis:
- If duration > max_consecutive_days → REJECT with clear reason
- If duration > current_balance → REJECT (insufficient quota)
- If balance < 0 after approval → REJECT
- Consider the leave type when determining approvers
- For long durations (>7 days), typically need manager AND hr approval"""

        current_balance = request.get('current_balance', policy['annual_quota'])

        user_prompt = f"""Analyze this leave request:

=== EMPLOYEE ===
Name: {request['employee_name']}
ID: {request['employee_id']}
Role: {request['role']}

=== LEAVE REQUEST ===
Type: {leave_type} ({policy['name']})
Duration: {duration} days
Dates: {request['start_date']} to {request['end_date']}
Reason: {request['reason']}

=== CURRENT STATUS ===
Available Balance: {current_balance} days
Balance After Approval: {current_balance - duration} days

=== POLICY CONSTRAINTS ===
Annual Quota: {policy['annual_quota']} days
Max Consecutive Days: {policy['max_consecutive_days']} days
Advance Notice Required: {policy['advance_notice_days']} days
Approval Chain: {policy['approval_required']}

=== ANALYSIS CHECKLIST ===
[ ] Duration ({duration} days) ≤ Max Consecutive ({policy['max_consecutive_days']} days)?
[ ] Duration ({duration} days) ≤ Current Balance ({current_balance} days)?
[ ] Balance after ({current_balance - duration} days) ≥ 0?
[ ] Appropriate approver chain for {policy['approval_required']}?

Perform strict policy compliance check. Respond with JSON only."""

        analysis = self._call_ollama(system_prompt, user_prompt)

        # Add policy to response
        if 'error' not in analysis:
            analysis['policy'] = policy

        return analysis

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
        Create a new leave request and analyze it using Ollama
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

        # Analyze request using Ollama
        print(f"🤖 Analyzing request with Llama 3.2 (Ollama)...")
        analysis = self.analyze_leave_request(request)
        request['analysis'] = analysis

        # Check for errors
        if 'error' in analysis:
            request['status'] = 'error'
            request['error_message'] = analysis['error']
            if 'suggestion' in analysis:
                request['suggestion'] = analysis['suggestion']
        # Set initial status based on eligibility
        elif not analysis.get('eligible', False):
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
        Uses Ollama to validate if approver has authority
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

        # Enhanced approval validation prompt
        system_prompt = """You are an HR authorization validator. Your job is to:
1. Verify if an approver has the authority to approve/reject leave requests
2. Check role matches, approval limits, and hierarchy levels
3. Determine if additional approvers are needed in the chain

Respond in EXACT JSON format with these keys:
- "has_authority": boolean (true/false)
- "reason": string (explanation of decision)
- "next_approver_required": boolean (true if more approvals needed)

Validation rules:
- Approver's role MUST be in required_approvers list
- Duration MUST be within approver's max_days_approval limit
- If duration > approver's limit, deny even if role matches
- If multiple approvers required, set next_approver_required = true after first approval"""

        required_approvers = request.get('required_approvers', [])
        duration = request['duration_days']
        hierarchy = self.knowledge_base['approval_hierarchy']
        approver_info = hierarchy.get(approver_role, {})

        user_prompt = f"""Validate approver authority:

=== APPROVER ===
Name: {approver_name}
Role: {approver_role}
Max Days Approval: {approver_info.get('max_days_approval', 'N/A')} days
Level: {approver_info.get('level', 'N/A')}
Can Approve: {approver_info.get('can_approve', [])}

=== LEAVE REQUEST ===
Request ID: {request_id}
Employee: {request['employee_name']} ({request['role']})
Leave Type: {request['leave_type']}
Duration: {duration} days
Required Approvers (remaining): {required_approvers}

=== APPROVAL HIERARCHY ===
{json.dumps(hierarchy, indent=2)}

=== VALIDATION CHECKLIST ===
[ ] Is "{approver_role}" in required approvers {required_approvers}?
[ ] Duration ({duration} days) ≤ Max approval limit ({approver_info.get('max_days_approval', 'N/A')} days)?
[ ] Employee role "{request['role']}" in approver's can_approve list {approver_info.get('can_approve', [])}?
[ ] After this approval, are more approvers needed from {required_approvers}?

Perform strict validation. Respond with JSON only."""

        print(f"🤖 Validating approver authority with Llama 3.2...")
        validation = self._call_ollama(system_prompt, user_prompt)

        if 'error' in validation:
            return {"success": False, "message": f"Validation error: {validation['error']}"}

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
LEAVE REQUEST REPORT (Analyzed by Llama 3.2 via Ollama)
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

AI ANALYSIS (Llama 3.2):
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

        if request['status'] == 'error':
            report += f"\n❌ ERROR: {request.get('error_message', 'Unknown error')}\n"
            if 'suggestion' in request:
                report += f"   Suggestion: {request['suggestion']}\n"

        report += f"\n{'='*80}\n"

        return report

    def check_ollama_status(self) -> Dict:
        """Check if Ollama is running and model is available"""
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            response.raise_for_status()

            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]

            return {
                "ollama_running": True,
                "available_models": model_names,
                "target_model": self.model,
                "model_available": self.model in model_names
            }
        except requests.exceptions.ConnectionError:
            return {
                "ollama_running": False,
                "error": "Cannot connect to Ollama",
                "suggestion": "Start Ollama with: ollama serve"
            }
        except Exception as e:
            return {
                "ollama_running": False,
                "error": str(e)
            }
