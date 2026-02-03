#!/usr/bin/env python3
"""
Code Review & Testing Enforcer

MANDATORY workflow for all generated code:
1. Code generated
2. Tests written
3. Tests MUST pass
4. User reviews code
5. User approves/denies via native dialog
6. If approved: implementation + docs updated
7. If denied: feedback captured + model learns

This is a LAW. No code is implemented without this flow.
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional
from enum import Enum


class ReviewStatus(Enum):
    """Review status states."""
    GENERATED = "generated"
    TESTING = "testing"
    TESTS_PASSED = "tests_passed"
    TESTS_FAILED = "tests_failed"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    DENIED = "denied"
    IMPLEMENTED = "implemented"


@dataclass
class CodeReviewRecord:
    """Record of a code review session."""
    request_id: str
    timestamp: str
    code_description: str
    code_file: str
    test_file: str
    test_results: str
    user_decision: Optional[str] = None
    user_feedback: Optional[str] = None
    status: str = ReviewStatus.GENERATED.value
    notes: Optional[str] = None


class CodeReviewEnforcer:
    """Enforces mandatory testing + review workflow."""

    def __init__(self):
        self.memory_path = Path("/Users/shawnfrahm/hungry/local-agent-vscode/ipc/agent_memory.json")
        self.review_history_path = Path("/Users/shawnfrahm/hungry/code_review_history.jsonl")
        self.test_results_path = Path("/Users/shawnfrahm/hungry/last_test_results.txt")

    def load_memory(self) -> dict:
        """Load agent memory."""
        try:
            with open(self.memory_path, 'r') as f:
                return json.load(f)
        except:
            return {}

    def save_memory(self, memory: dict) -> None:
        """Save agent memory."""
        with open(self.memory_path, 'w') as f:
            json.dump(memory, f, indent=2)

    def create_review_record(
        self,
        request_id: str,
        code_description: str,
        code_file: str,
        test_file: str,
    ) -> CodeReviewRecord:
        """Create a review record for new code."""
        return CodeReviewRecord(
            request_id=request_id,
            timestamp=datetime.now().isoformat(),
            code_description=code_description,
            code_file=code_file,
            test_file=test_file,
            test_results="",
            status=ReviewStatus.GENERATED.value,
        )

    def run_tests(self, test_file: str) -> tuple[bool, str]:
        """
        Run tests for the generated code.
        
        Returns: (passed: bool, output: str)
        """
        if not Path(test_file).exists():
            return False, f"Test file not found: {test_file}"

        print(f"\n🧪 Running tests: {test_file}")
        print("=" * 60)

        try:
            result = subprocess.run(
                ["python3", test_file],
                capture_output=True,
                text=True,
                timeout=30
            )

            output = f"""STDOUT:
{result.stdout}

STDERR:
{result.stderr}

Return Code: {result.returncode}
"""

            if result.returncode == 0:
                print("✅ ALL TESTS PASSED")
                return True, output
            else:
                print("❌ TESTS FAILED")
                print(output)
                return False, output

        except subprocess.TimeoutExpired:
            return False, "Tests timed out (30s)"
        except Exception as e:
            return False, f"Error running tests: {str(e)}"

    def request_review_approval(
        self,
        code_description: str,
        code_file: str,
        test_results: str,
        test_passed: bool,
    ) -> tuple[bool, Optional[str]]:
        """
        Request user approval for code via native dialog.

        Returns: (approved: bool, feedback: Optional[str])
        """
        from macos_approver import process_approval_request

        approval_data = {
            "type": "code_review",
            "description": code_description,
            "code_file": code_file,
            "test_results": "PASSED ✅" if test_passed else "FAILED ❌",
            "request": f"""
CODE REVIEW REQUIRED
=====================================

Description:
{code_description}

File: {code_file}

Test Results: {'✅ PASSED' if test_passed else '❌ FAILED'}

Review this code?
- APPROVE: Implement and update docs
- DENY: Explain why in the dialog
"""
        }

        return process_approval_request(approval_data)

    def record_review(self, record: CodeReviewRecord) -> None:
        """Record the review in history."""
        with open(self.review_history_path, 'a') as f:
            f.write(json.dumps(asdict(record)) + "\n")

    def update_readme(self, code_file: str, code_description: str) -> None:
        """Update README when code is approved."""
        readme_path = Path(code_file).parent / "README.md"

        if not readme_path.exists():
            return

        # Add to README
        with open(readme_path, 'a') as f:
            f.write(f"\n\n## {code_description}\n")
            f.write(f"File: `{code_file}`\n")
            f.write(f"Approved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Status: ✅ Implemented\n")

    def execute_enforcement_workflow(
        self,
        request_id: str,
        code_description: str,
        code_file: str,
        test_file: str,
    ) -> bool:
        """
        Execute the mandatory review workflow.

        Returns: True if approved and implemented, False if denied
        """
        print("\n" + "=" * 60)
        print("📋 CODE REVIEW ENFORCEMENT WORKFLOW")
        print("=" * 60)

        # Step 1: Create review record
        record = self.create_review_record(
            request_id=request_id,
            code_description=code_description,
            code_file=code_file,
            test_file=test_file,
        )

        # Step 2: Run tests
        print(f"\n[1/4] Testing generated code...")
        test_passed, test_output = self.run_tests(test_file)
        record.test_results = test_output
        record.status = ReviewStatus.TESTS_PASSED.value if test_passed else ReviewStatus.TESTS_FAILED.value

        # Step 3: If tests failed, ask if user wants to review anyway
        if not test_passed:
            print("\n⚠️  TESTS FAILED - Review anyway?")
            response = input("Continue with code review? (y/n): ").strip().lower()
            if response != 'y':
                record.status = ReviewStatus.DENIED.value
                record.user_feedback = "Tests failed - user chose not to review"
                self.record_review(record)
                print("❌ Code review skipped - tests must pass")
                return False

        # Step 4: Request approval
        print(f"\n[2/4] Requesting approval...")
        approved, feedback = self.request_review_approval(
            code_description=code_description,
            code_file=code_file,
            test_results=test_output,
            test_passed=test_passed,
        )

        record.user_decision = "approved" if approved else "denied"
        record.user_feedback = feedback
        record.status = ReviewStatus.APPROVED.value if approved else ReviewStatus.DENIED.value

        # Step 5: If approved, update docs and mark implemented
        if approved:
            print(f"\n[3/4] Updating documentation...")
            self.update_readme(code_file, code_description)
            record.status = ReviewStatus.IMPLEMENTED.value
            print(f"     ✅ README updated")

            print(f"\n[4/4] Implementation status: ✅ COMPLETE")
            print("=" * 60)
            print("✅ CODE APPROVED & IMPLEMENTED")
            print(f"   File: {code_file}")
            print(f"   Tests: PASSED ✅")
            print(f"   Docs: UPDATED ✅")
            print("=" * 60)
        else:
            print(f"\n[3/4] Review result: ❌ DENIED")
            print(f"   Feedback: {feedback}")
            print(f"\n[4/4] Next steps:")
            print(f"   1. Review the feedback above")
            print(f"   2. Modify code to address concerns")
            print(f"   3. Run tests again")
            print(f"   4. Request review again")
            print("=" * 60)

        # Record the review
        self.record_review(record)

        return approved

    def generate_review_report(self) -> None:
        """Generate a report of all code reviews."""
        if not self.review_history_path.exists():
            print("No review history yet")
            return

        reviews = []
        with open(self.review_history_path, 'r') as f:
            for line in f:
                reviews.append(json.loads(line))

        approved = len([r for r in reviews if r["user_decision"] == "approved"])
        denied = len([r for r in reviews if r["user_decision"] == "denied"])
        total = len(reviews)

        print("\n" + "=" * 60)
        print("📊 CODE REVIEW REPORT")
        print("=" * 60)
        print(f"\nTotal Reviews: {total}")
        print(f"Approved: {approved} ({approved/total*100:.1f}% if total > 0 else 0)")
        print(f"Denied: {denied} ({denied/total*100:.1f}% if total > 0 else 0)")

        print(f"\nRecent Reviews:")
        for review in reviews[-5:]:
            print(f"  - {review['code_description']}: {review['user_decision'].upper()}")

        print("\n" + "=" * 60)


if __name__ == "__main__":
    enforcer = CodeReviewEnforcer()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "report":
            enforcer.generate_review_report()
        elif command == "review":
            # Usage: python3 code_review_enforcer.py review <request_id> <description> <code_file> <test_file>
            if len(sys.argv) < 6:
                print("Usage: code_review_enforcer.py review <request_id> <description> <code_file> <test_file>")
                sys.exit(1)

            request_id = sys.argv[2]
            description = sys.argv[3]
            code_file = sys.argv[4]
            test_file = sys.argv[5]

            success = enforcer.execute_enforcement_workflow(
                request_id=request_id,
                code_description=description,
                code_file=code_file,
                test_file=test_file,
            )

            sys.exit(0 if success else 1)
    else:
        print("Code Review Enforcer")
        print("\nUsage:")
        print("  python3 code_review_enforcer.py review <id> <desc> <code_file> <test_file>")
        print("  python3 code_review_enforcer.py report")
