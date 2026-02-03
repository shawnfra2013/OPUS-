#!/usr/bin/env python3
"""
Agent Approval Workflow System
Implements VS Code-style approval gates for agent-generated code

Flow:
1. User sends prompt
2. Agent generates code
3. Agent creates APPROVAL_REQUEST.json with:
   - What was created
   - Where it will be saved
   - How to test it
   - Risk assessment
4. User reviews via CLI or GUI
5. User approves/denies
6. If approved: auto-run tests
7. Display results
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

class ApprovalWorkflow:
    """Manages approval requests and workflow execution"""
    
    APPROVAL_DIR = Path("/Users/shawnfrahm/hungry/approval_requests")
    EXECUTED_DIR = Path("/Users/shawnfrahm/hungry/executed_approvals")
    
    def __init__(self):
        self.APPROVAL_DIR.mkdir(exist_ok=True)
        self.EXECUTED_DIR.mkdir(exist_ok=True)
    
    def create_approval_request(
        self,
        request_id: str,
        description: str,
        files_to_create: dict,  # {filepath: content}
        commands_to_run: list,  # [{cmd: "...", description: "...", test: True/False}]
        risk_level: str,  # "low", "medium", "high"
        verification_steps: list,  # ["step 1", "step 2"]
    ) -> str:
        """
        Create an approval request for user review
        
        Args:
            request_id: Unique ID for this request
            description: What the AI is proposing to do
            files_to_create: Files that will be created
            commands_to_run: Commands that will execute
            risk_level: "low" | "medium" | "high"
            verification_steps: Steps user can run to verify
        
        Returns:
            Path to approval request file
        """
        
        approval_request = {
            "id": request_id,
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "risk_level": risk_level,
            "files": {
                "to_create": list(files_to_create.keys()),
                "count": len(files_to_create),
                "total_lines": sum(len(c.split('\n')) for c in files_to_create.values())
            },
            "commands": {
                "to_run": commands_to_run,
                "count": len(commands_to_run)
            },
            "verification_steps": verification_steps,
            "status": "pending_approval",
            "user_decision": None,
            "decision_timestamp": None
        }
        
        request_path = self.APPROVAL_DIR / f"{request_id}.json"
        
        with open(request_path, 'w') as f:
            json.dump(approval_request, f, indent=2)
        
        # Also store the actual files separately
        files_path = self.APPROVAL_DIR / f"{request_id}_files.json"
        with open(files_path, 'w') as f:
            json.dump(files_to_create, f, indent=2)
        
        return str(request_path)
    
    def display_approval_request(self, request_id: str) -> None:
        """Display approval request in readable format"""
        request_path = self.APPROVAL_DIR / f"{request_id}.json"
        
        if not request_path.exists():
            print(f"❌ Approval request not found: {request_id}")
            return
        
        with open(request_path) as f:
            request = json.load(f)
        
        print("\n" + "="*80)
        print("🤖 AGENT APPROVAL REQUEST")
        print("="*80)
        
        print(f"\n📋 ID: {request['id']}")
        print(f"⏰ Created: {request['timestamp']}")
        print(f"⚠️  Risk Level: {request['risk_level'].upper()}")
        
        print(f"\n📝 WHAT THE AGENT IS PROPOSING:")
        print(f"   {request['description']}")
        
        print(f"\n📁 FILES TO CREATE ({request['files']['count']}):")
        for filepath in request['files']['to_create']:
            print(f"   • {filepath}")
        print(f"   Total lines: {request['files']['total_lines']}")
        
        print(f"\n⚡ COMMANDS TO RUN ({request['commands']['count']}):")
        for cmd_info in request['commands']['to_run']:
            marker = "🧪" if cmd_info.get('test') else "▶️"
            print(f"   {marker} {cmd_info['description']}")
            print(f"       $ {cmd_info['cmd']}")
        
        print(f"\n✅ HOW TO VERIFY (Run these to check):")
        for i, step in enumerate(request['verification_steps'], 1):
            print(f"   {i}. {step}")
        
        print(f"\n{'='*80}")
        print("APPROVE? [y/n/review]: ", end="", flush=True)
        choice = input().lower().strip()
        
        if choice == 'y':
            self.approve_request(request_id)
        elif choice == 'n':
            self.deny_request(request_id)
        elif choice == 'review':
            self.show_files(request_id)
            # Ask again after review
            print("\nAPPROVE NOW? [y/n]: ", end="", flush=True)
            if input().lower().strip() == 'y':
                self.approve_request(request_id)
            else:
                self.deny_request(request_id)
    
    def show_files(self, request_id: str) -> None:
        """Display the actual files that would be created"""
        files_path = self.APPROVAL_DIR / f"{request_id}_files.json"
        
        if not files_path.exists():
            print("❌ Files not found")
            return
        
        with open(files_path) as f:
            files = json.load(f)
        
        print("\n" + "="*80)
        print("📂 FILES PREVIEW")
        print("="*80)
        
        for filepath, content in files.items():
            print(f"\n📄 {filepath}")
            print("-" * 80)
            lines = content.split('\n')
            preview_lines = lines[:30]  # Show first 30 lines
            print('\n'.join(preview_lines))
            if len(lines) > 30:
                print(f"\n... [{len(lines) - 30} more lines]")
            print("-" * 80)
    
    def approve_request(self, request_id: str) -> bool:
        """Approve and execute the request"""
        print(f"\n✅ APPROVED: {request_id}")
        
        request_path = self.APPROVAL_DIR / f"{request_id}.json"
        files_path = self.APPROVAL_DIR / f"{request_id}_files.json"
        
        # Load request and files
        with open(request_path) as f:
            request = json.load(f)
        
        with open(files_path) as f:
            files = json.load(f)
        
        # Execute: Create files
        print("\n📁 Creating files...")
        for filepath, content in files.items():
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            print(f"   ✓ {filepath}")
        
        # Execute: Run commands
        print("\n⚡ Running commands...")
        results = []
        for cmd_info in request['commands']['to_run']:
            cmd = cmd_info['cmd']
            print(f"   ▶️ {cmd_info['description']}")
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                results.append({
                    "command": cmd,
                    "status": "success" if result.returncode == 0 else "failed",
                    "returncode": result.returncode,
                    "stdout": result.stdout[:500],  # First 500 chars
                    "stderr": result.stderr[:500]
                })
                status = "✓" if result.returncode == 0 else "✗"
                print(f"      {status} Exit code: {result.returncode}")
            except subprocess.TimeoutExpired:
                print(f"      ✗ TIMEOUT")
                results.append({"command": cmd, "status": "timeout"})
            except Exception as e:
                print(f"      ✗ ERROR: {e}")
                results.append({"command": cmd, "status": "error", "error": str(e)})
        
        # Mark as executed
        request['status'] = 'approved_executed'
        request['user_decision'] = 'approve'
        request['decision_timestamp'] = datetime.now().isoformat()
        request['execution_results'] = results
        
        executed_path = self.EXECUTED_DIR / f"{request_id}.json"
        with open(executed_path, 'w') as f:
            json.dump(request, f, indent=2)
        
        print(f"\n✅ EXECUTION COMPLETE")
        print(f"📊 Log saved: {executed_path}")
        
        return all(r.get('status') == 'success' for r in results)
    
    def deny_request(self, request_id: str) -> None:
        """Deny and discard the request"""
        print(f"\n❌ DENIED: {request_id}")
        
        request_path = self.APPROVAL_DIR / f"{request_id}.json"
        
        with open(request_path) as f:
            request = json.load(f)
        
        request['status'] = 'denied'
        request['user_decision'] = 'deny'
        request['decision_timestamp'] = datetime.now().isoformat()
        
        with open(request_path, 'w') as f:
            json.dump(request, f, indent=2)
        
        print(f"Request marked as denied and archived.")
    
    def list_pending(self) -> None:
        """List all pending approval requests"""
        pending = []
        for req_file in self.APPROVAL_DIR.glob("*.json"):
            if "_files.json" in str(req_file):
                continue
            with open(req_file) as f:
                req = json.load(f)
                if req['status'] == 'pending_approval':
                    pending.append(req)
        
        if not pending:
            print("✅ No pending approvals")
            return
        
        print(f"\n⏳ {len(pending)} PENDING APPROVALS:\n")
        for req in pending:
            risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(req['risk_level'], "⚪")
            print(f"{risk_emoji} [{req['id']}] {req['description'][:60]}")
            print(f"   Files: {req['files']['count']} | Commands: {req['commands']['count']}")
            print()

# CLI Interface
if __name__ == "__main__":
    workflow = ApprovalWorkflow()
    
    if len(sys.argv) < 2:
        workflow.list_pending()
    else:
        command = sys.argv[1]
        
        if command == "list":
            workflow.list_pending()
        elif command == "review":
            request_id = sys.argv[2] if len(sys.argv) > 2 else None
            if not request_id:
                workflow.list_pending()
            else:
                workflow.display_approval_request(request_id)
        elif command == "approve":
            request_id = sys.argv[2]
            workflow.approve_request(request_id)
        elif command == "deny":
            request_id = sys.argv[2]
            workflow.deny_request(request_id)
        else:
            print("Usage:")
            print("  python3 approval_workflow.py list              # List pending")
            print("  python3 approval_workflow.py review [id]       # Review & approve/deny")
            print("  python3 approval_workflow.py approve [id]      # Auto-approve")
            print("  python3 approval_workflow.py deny [id]         # Auto-deny")
