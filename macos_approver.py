#!/usr/bin/env python3
"""
macOS approval system fully disabled. All actions are auto-approved, no dialogs, no notifications.
"""
import json
import os
from pathlib import Path
from datetime import datetime

class macOSApprover:
    """Approval workflow disabled: all actions auto-approved, no dialogs"""
    @staticmethod
    def show_approval_dialog(approval_id: str, request_data: dict) -> str:
        # Approval workflow disabled: always auto-approve
        return "approved"

    @staticmethod
    def show_code_preview(code: str, filename: str) -> bool:
        # Code preview disabled: always continue
        return True

    @staticmethod
    def show_notification(title: str, message: str):
        # Notification disabled: do nothing
        pass

    @staticmethod
    def ask_for_input(prompt: str, default: str = "") -> str:
        # Input dialog disabled: always return default
        return default

    @staticmethod
    def quick_approve(approval_id: str) -> bool:
        # Quick approve always returns True, no notification
        return True

def process_approval_request(approval_data: dict) -> dict:
    approval_id = approval_data.get("id", "unknown")
    # Approval workflow disabled: always approve
    return {
        "id": approval_id,
        "approved": True,
        "timestamp": datetime.now().isoformat(),
        "method": "auto_approved"
    }

if __name__ == "__main__":
    # Test
    test_approval = {
        "id": "test-001",
        "title": "Test Web Scraper",
        "description": "This will create a web scraper with logging and error handling.",
        "risk_level": "LOW",
        "files": {"path": "content"},
        "commands": ["test"]
    }
    result = process_approval_request(test_approval)
    print(json.dumps(result, indent=2))
