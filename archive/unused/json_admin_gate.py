#!/usr/bin/env python3
"""
JSON-Gated System - Single Authority Pattern

PRINCIPLE: JSON is the admin. Nothing happens without JSON approval.

All operations (code generation, testing, review, approval, implementation)
go through JSON validation first. JSON contains:
- Approval rules
- Test requirements
- Implementation gates
- Training data
- Complete audit trail

No part of the system works around JSON. All paths lead through JSON.
"""

import json
from pathlib import Path
from datetime import datetime
from enum import Enum
from typing import Optional, Any, Dict, List
from dataclasses import dataclass, asdict


class OperationType(Enum):
    """All operations that require JSON approval."""
    CODE_GENERATION = "code_generation"
    TEST_EXECUTION = "test_execution"
    TEST_VALIDATION = "test_validation"
    CODE_REVIEW = "code_review"
    USER_APPROVAL = "user_approval"
    IMPLEMENTATION = "implementation"
    DOCUMENTATION_UPDATE = "documentation_update"
    MODEL_TRAINING = "model_training"
    FILE_CREATION = "file_creation"
    CONFIG_CHANGE = "config_change"


class ApprovalStatus(Enum):
    """Approval states in JSON."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    BLOCKED = "blocked"
    REVOKED = "revoked"


@dataclass
class OperationGate:
    """Gate that JSON uses to approve/reject operations."""
    operation_id: str
    operation_type: str
    status: str  # pending, approved, rejected, blocked
    timestamp: str
    description: str
    requirements: Dict[str, Any]  # What must be true
    checks: Dict[str, bool]  # What passed/failed
    approval_reason: Optional[str] = None
    blocked_reason: Optional[str] = None
    user_decision: Optional[str] = None  # approved/denied
    metadata: Optional[Dict] = None


class JSONAdminGate:
    """
    Central authority pattern - JSON gates all operations.
    
    NOTHING executes without JSON approval.
    EVERYTHING flows through JSON.
    JSON is the single source of truth.
    """

    def __init__(self):
        self.memory_path = Path("/Users/shawnfrahm/hungry/local-agent-vscode/ipc/agent_memory.json")
        self.ensure_memory_exists()

    def ensure_memory_exists(self):
        """Initialize JSON with gate structure if missing."""
        if not self.memory_path.exists():
            initial_structure = {
                "version": "3.0",
                "initialized": datetime.now().isoformat(),
                "admin_authority": True,
                "system_rules": {
                    "all_operations_require_gate": True,
                    "json_is_single_authority": True,
                    "no_bypassing_json": True,
                    "complete_audit_trail": True,
                },
                "operation_gates": {},
                "approval_rules": {
                    "code_generation": {
                        "requires_tests": True,
                        "tests_must_pass": True,
                        "requires_review": True,
                        "requires_user_approval": True,
                        "requires_documentation": True,
                    },
                    "test_execution": {
                        "auto_run": True,
                        "failure_blocks_review": True,
                        "results_recorded": True,
                    },
                    "code_review": {
                        "requires_user_approval": True,
                        "approval_recorded": True,
                        "feedback_required_for_denial": True,
                    },
                    "implementation": {
                        "requires_approval": True,
                        "requires_tests_pass": True,
                        "requires_review_pass": True,
                        "auto_updates_documentation": True,
                        "updates_memory": True,
                    },
                    "model_training": {
                        "requires_min_examples": 10,
                        "uses_approval_data": True,
                        "recorded_in_memory": True,
                    },
                },
                "conversation_history": [],
                "operation_history": [],
                "approval_history": {},
                "training_data": [],
                "config": {
                    "strict_mode": True,
                    "audit_all_operations": True,
                    "block_unauthorized": True,
                },
            }

            self.memory_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.memory_path, 'w') as f:
                json.dump(initial_structure, f, indent=2)

    def load_memory(self) -> dict:
        """Load the authoritative JSON state."""
        with open(self.memory_path, 'r') as f:
            return json.load(f)

    def save_memory(self, memory: dict) -> None:
        """Save back to authoritative JSON - this is the only write path."""
        with open(self.memory_path, 'w') as f:
            json.dump(memory, f, indent=2)

    def create_gate(self, operation_type: str, description: str, requirements: dict) -> str:
        """
        Create a new operation gate. Returns operation_id.
        
        This is where operations START. Every operation must go through JSON first.
        """
        memory = self.load_memory()
        
        operation_id = f"op_{len(memory['operation_history'])}_{datetime.now().timestamp()}"
        
        gate = {
            "operation_id": operation_id,
            "operation_type": operation_type,
            "status": "pending",
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "requirements": requirements,
            "checks": {},
            "approval_reason": None,
            "blocked_reason": None,
            "user_decision": None,
            "metadata": {},
        }

        memory["operation_gates"][operation_id] = gate
        memory["operation_history"].append(operation_id)
        self.save_memory(memory)

        print(f"📋 Gate Created: {operation_id}")
        print(f"   Type: {operation_type}")
        print(f"   Description: {description}")
        print(f"   Status: PENDING (awaiting checks)")

        return operation_id

    def check_requirement(
        self,
        operation_id: str,
        requirement_name: str,
        passed: bool,
        details: str = "",
    ) -> bool:
        """
        Record a requirement check. JSON tracks everything.
        
        Returns: True if gate still might pass, False if already blocked.
        """
        memory = self.load_memory()
        
        if operation_id not in memory["operation_gates"]:
            print(f"❌ Gate not found: {operation_id}")
            return False

        gate = memory["operation_gates"][operation_id]
        gate["checks"][requirement_name] = {
            "passed": passed,
            "timestamp": datetime.now().isoformat(),
            "details": details,
        }

        # Check if we should block
        if not passed and gate["requirements"].get(requirement_name, {}).get("blocking", True):
            gate["status"] = "blocked"
            gate["blocked_reason"] = f"Failed: {requirement_name} - {details}"
            print(f"🚫 Gate BLOCKED: {operation_id}")
            print(f"   Reason: {gate['blocked_reason']}")

        self.save_memory(memory)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}: {requirement_name}")
        if details:
            print(f"         {details}")

        return gate["status"] != "blocked"

    def request_user_approval(
        self,
        operation_id: str,
        code_file: str = None,
        test_results: str = None,
        test_passed: bool = False,
    ) -> tuple[bool, Optional[str]]:
        """
        Request user approval. This is a gate point.
        User decision goes into JSON, becomes part of official record.
        """
        from macos_approver import process_approval_request

        memory = self.load_memory()
        gate = memory["operation_gates"][operation_id]

        # Check: Can we even ask for approval?
        if gate["status"] == "blocked":
            print(f"❌ Cannot request approval - gate is BLOCKED")
            print(f"   Reason: {gate['blocked_reason']}")
            return False, None

        # Ask user
        approval_data = {
            "type": "code_review",
            "operation_id": operation_id,
            "description": gate["description"],
            "code_file": code_file or "N/A",
            "test_results": "PASSED ✅" if test_passed else "FAILED ❌",
        }

        approved, feedback = process_approval_request(approval_data)

        # Record in JSON (this is the official record)
        gate["user_decision"] = "approved" if approved else "denied"
        gate["approval_reason"] = feedback
        gate["status"] = "approved" if approved else "rejected"
        gate["checks"]["user_approval"] = {
            "passed": approved,
            "timestamp": datetime.now().isoformat(),
            "decision": gate["user_decision"],
            "reason": feedback,
        }

        # Record in approval_history (for model training)
        if operation_id not in memory["approval_history"]:
            memory["approval_history"][operation_id] = gate["checks"]["user_approval"]

        self.save_memory(memory)

        return approved, feedback

    def is_gate_approved(self, operation_id: str) -> bool:
        """Check if gate is fully approved by JSON."""
        memory = self.load_memory()
        
        if operation_id not in memory["operation_gates"]:
            return False

        gate = memory["operation_gates"][operation_id]
        
        # Gate must be explicitly approved, not just not-blocked
        return gate["status"] == "approved"

    def is_gate_blocked(self, operation_id: str) -> bool:
        """Check if gate is blocked."""
        memory = self.load_memory()
        gate = memory["operation_gates"].get(operation_id)
        return gate and gate["status"] == "blocked"

    def implement_approved_operation(self, operation_id: str) -> bool:
        """
        ONLY called if gate is APPROVED.
        Implementation path: JSON says yes → code runs.
        
        No code executes unless JSON approves first.
        """
        memory = self.load_memory()
        gate = memory["operation_gates"].get(operation_id)

        if not gate:
            print(f"❌ Operation not found: {operation_id}")
            return False

        if not self.is_gate_approved(operation_id):
            print(f"❌ Cannot implement - gate not approved")
            print(f"   Status: {gate['status']}")
            return False

        # Implementation happens here (code runs)
        gate["status"] = "implemented"
        gate["implementation_timestamp"] = datetime.now().isoformat()

        # Record in memory for training
        if "implementation" not in gate["checks"]:
            gate["checks"]["implementation"] = {
                "passed": True,
                "timestamp": datetime.now().isoformat(),
            }

        self.save_memory(memory)

        print(f"✅ IMPLEMENTED: {operation_id}")
        print(f"   Type: {gate['operation_type']}")
        print(f"   Description: {gate['description']}")

        return True

    def get_operation_status(self, operation_id: str) -> dict:
        """Get complete status of an operation from JSON."""
        memory = self.load_memory()
        return memory["operation_gates"].get(operation_id, {})

    def get_all_operations(self, status: str = None) -> List[dict]:
        """Get all operations, optionally filtered by status."""
        memory = self.load_memory()
        gates = memory["operation_gates"]

        if status:
            return {k: v for k, v in gates.items() if v.get("status") == status}
        return gates

    def enforce_strict_mode(self, operation_id: str) -> bool:
        """
        Strict mode: JSON is UNCOMPROMISING.
        
        - No bypassing gates
        - No parallel execution
        - No implementation without approval
        - Every check must pass
        - Audit everything
        """
        memory = self.load_memory()
        
        if not memory["config"].get("strict_mode"):
            return False

        gate = memory["operation_gates"].get(operation_id)
        
        if not gate:
            print("❌ STRICT MODE: Operation doesn't exist in JSON")
            return False

        # ALL required checks must pass
        rules = memory["approval_rules"].get(gate["operation_type"], {})
        
        for requirement, value in rules.items():
            if requirement not in gate["checks"]:
                print(f"❌ STRICT MODE: Missing check: {requirement}")
                return False

            if not gate["checks"][requirement].get("passed"):
                print(f"❌ STRICT MODE: Check failed: {requirement}")
                return False

        # Gate must be approved
        if gate["status"] != "approved":
            print(f"❌ STRICT MODE: Gate not approved (status: {gate['status']})")
            return False

        return True


# Example workflow showing JSON as admin
def example_workflow():
    """
    Shows how JSON gates everything.
    """
    gate = JSONAdminGate()

    print("\n" + "=" * 70)
    print("📋 JSON-GATED WORKFLOW EXAMPLE")
    print("=" * 70)

    # STEP 1: Operation starts - create gate in JSON
    print("\n[1] OPERATION STARTS - Create gate in JSON")
    operation_id = gate.create_gate(
        operation_type="code_generation",
        description="Generate Swift JSON decoder",
        requirements={
            "has_tests": {"blocking": True},
            "tests_pass": {"blocking": True},
            "user_approval": {"blocking": True},
        },
    )

    # STEP 2: Check requirements against JSON rules
    print("\n[2] CHECKING REQUIREMENTS")
    print("Memory rules say:")
    memory = gate.load_memory()
    rules = memory["approval_rules"]["code_generation"]
    for rule, value in rules.items():
        print(f"   - {rule}: {value}")

    # STEP 3: Run tests, record in JSON
    print("\n[3] RUNNING TESTS - Results recorded in JSON")
    gate.check_requirement(
        operation_id,
        "has_tests",
        passed=True,
        details="test_JSONDecoder.py exists"
    )
    gate.check_requirement(
        operation_id,
        "tests_pass",
        passed=True,
        details="3/3 tests passed"
    )

    # STEP 4: User approval - recorded in JSON
    print("\n[4] REQUESTING USER APPROVAL")
    approved, feedback = gate.request_user_approval(
        operation_id,
        code_file="JSONDecoder.swift",
        test_results="✅ PASSED",
        test_passed=True,
    )

    # STEP 5: Check if approved in JSON
    print("\n[5] CHECKING JSON APPROVAL STATUS")
    if gate.is_gate_approved(operation_id):
        print("✅ Gate approved in JSON - safe to implement")
    elif gate.is_gate_blocked(operation_id):
        print("❌ Gate blocked in JSON - cannot implement")
    else:
        print("⏳ Gate pending - waiting")

    # STEP 6: Implement ONLY if JSON approves
    print("\n[6] IMPLEMENTING (only if JSON approves)")
    if gate.is_gate_approved(operation_id):
        gate.implement_approved_operation(operation_id)
        print("\n✅ CODE IMPLEMENTED")
        print("   • Files created")
        print("   • README updated")
        print("   • Memory recorded")
    else:
        print("❌ Cannot implement - JSON did not approve")

    # STEP 7: Show complete audit trail in JSON
    print("\n[7] COMPLETE OPERATION RECORD IN JSON")
    status = gate.get_operation_status(operation_id)
    print(f"Status: {status['status']}")
    print(f"Type: {status['operation_type']}")
    print(f"Checks passed:")
    for check, result in status['checks'].items():
        passed = "✅" if result.get('passed') else "❌"
        print(f"  {passed} {check}")


if __name__ == "__main__":
    gate = JSONAdminGate()
    example_workflow()
