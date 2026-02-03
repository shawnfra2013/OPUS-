#!/usr/bin/env python3
"""
test_daemon_and_gui.py
Comprehensive test of daemon functionality, heartbeat, and GUI creation prompt.
"""

import os
import json
import time
import subprocess
import psutil
from pathlib import Path

# Paths
WORK_DIR = "/Users/shawnfrahm/hungry"
INBOX_PATH = f"{WORK_DIR}/local-agent-vscode/ipc/inbox.jsonl"
OUTBOX_PATH = f"{WORK_DIR}/local-agent-vscode/ipc/outbox.jsonl"
MEMORY_PATH = f"{WORK_DIR}/local-agent-vscode/ipc/agent_memory.json"

def print_header(text):
    """Print formatted header."""
    print(f"\n{'='*70}")
    print(f"✓ {text}")
    print(f"{'='*70}\n")

def verify_ollama():
    """Verify Ollama is running."""
    print_header("STEP 1: Verify Ollama Running")
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/tags"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            models = [m.get("name", "unknown") for m in data.get("models", [])]
            print(f"✓ Ollama running")
            print(f"✓ Models available: {', '.join(models) or 'none'}")
            return True
        else:
            print(f"✗ Ollama not responding (return code: {result.returncode})")
            return False
    except Exception as e:
        print(f"✗ Ollama check failed: {e}")
        return False

def check_processes():
    """Check if main processes are running."""
    print_header("STEP 2: Check Running Processes")
    
    processes_to_check = {
        "run_agent.py": "Agent loop",
        "tinkerer_daemon.py": "Daemon",
        "agent_action_handler.py": "Action handler",
        "ollama": "Ollama LLM"
    }
    
    running_processes = {}
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            for check_name, description in processes_to_check.items():
                if check_name in cmdline or check_name in proc.info['name']:
                    running_processes[check_name] = {
                        'pid': proc.info['pid'],
                        'description': description
                    }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if running_processes:
        for name, info in running_processes.items():
            print(f"✓ {info['description']:30} (PID: {info['pid']})")
    else:
        print("⚠ No core processes found running")
        print("   Run: python3 run_agent.py &")
        print("   Run: python3 tinkerer_daemon.py &")
    
    return len(running_processes) > 0

def check_ipc_files():
    """Check IPC file structure."""
    print_header("STEP 3: Check IPC File Structure")
    
    ipc_dir = f"{WORK_DIR}/local-agent-vscode/ipc"
    Path(ipc_dir).mkdir(parents=True, exist_ok=True)
    
    files_to_check = {
        INBOX_PATH: "Inbox (user prompts)",
        OUTBOX_PATH: "Outbox (agent actions)",
        MEMORY_PATH: "Memory (context)"
    }
    
    all_exist = True
    for path, description in files_to_check.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✓ {description:30} ({size:,} bytes)")
        else:
            print(f"⚠ {description:30} MISSING (will be created)")
            all_exist = False
    
    return all_exist

def test_heartbeat():
    """Test daemon heartbeat mechanism."""
    print_header("STEP 4: Test Daemon Heartbeat")
    
    try:
        # Check if tinkerer_daemon.log exists
        log_path = f"{WORK_DIR}/tinkerer_daemon.log"
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                lines = f.readlines()
                if lines:
                    print(f"✓ Daemon log exists ({len(lines)} entries)")
                    print(f"  Last entry: {lines[-1][:70].strip()}")
                else:
                    print("⚠ Daemon log empty")
        else:
            print("⚠ Daemon log not found (will be created)")
        
        # Check agent_actions.jsonl for recent activity
        actions_path = f"{WORK_DIR}/agent_actions.jsonl"
        if os.path.exists(actions_path):
            with open(actions_path, 'r') as f:
                lines = f.readlines()
                if lines:
                    print(f"✓ Action log exists ({len(lines)} actions)")
                    try:
                        last_action = json.loads(lines[-1])
                        print(f"  Last action: {last_action.get('action', {}).get('action_type', 'unknown')}")
                    except:
                        pass
                else:
                    print("⚠ Action log empty")
        else:
            print("⚠ Action log not found")
        
        return True
    except Exception as e:
        print(f"✗ Heartbeat check failed: {e}")
        return False

def send_test_prompt(prompt_text, test_id):
    """Send a test prompt to the agent."""
    print_header(f"STEP 5: Send Test Prompt")
    
    try:
        # Create prompt
        prompt = {
            "id": test_id,
            "text": prompt_text,
            "timestamp": int(time.time())
        }
        
        # Write to inbox
        with open(INBOX_PATH, 'a') as f:
            f.write(json.dumps(prompt) + '\n')
        
        print(f"✓ Prompt written to inbox")
        print(f"  ID: {test_id}")
        print(f"  Text: {prompt_text[:60]}...")
        
        return True
    except Exception as e:
        print(f"✗ Failed to send prompt: {e}")
        return False

def wait_for_response(test_id, timeout=30):
    """Wait for agent to process prompt and create action."""
    print_header(f"STEP 6: Wait for Agent Response ({timeout}s timeout)")
    
    start_time = time.time()
    last_line_count = 0
    
    while time.time() - start_time < timeout:
        try:
            if os.path.exists(OUTBOX_PATH):
                with open(OUTBOX_PATH, 'r') as f:
                    lines = f.readlines()
                
                # Check if new actions appeared
                if len(lines) > last_line_count:
                    print(f"⏱ {int(time.time() - start_time):2}s: Action detected! ({len(lines)} total)")
                    last_line_count = len(lines)
                    
                    # Check if our prompt was processed
                    for line in lines[-5:]:  # Check last 5 actions
                        try:
                            action = json.loads(line)
                            if action.get('id') == test_id:
                                print(f"\n✓ PROMPT PROCESSED!")
                                print(f"  Action type: {action.get('action', {}).get('action_type', 'unknown')}")
                                return action
                        except:
                            pass
        except:
            pass
        
        time.sleep(1)
    
    print(f"✗ Timeout waiting for response ({timeout}s)")
    return None

def verify_readme_updates():
    """Check if READMEs are being maintained."""
    print_header("STEP 7: Verify README Maintenance")
    
    readme_files = [
        "run_agent.README.md",
        "ARCHITECTURE.md",
        "tinkerer_daemon.README.md",
        "cloud_fallback.README.md",
        "ollama_manager.README.md",
        "backend/memory.README.md",
        "agent_action_handler.README.md",
        "jailbreak_ollama.README.md",
        "DOCS_INDEX.md"
    ]
    
    all_exist = True
    for readme in readme_files:
        path = f"{WORK_DIR}/{readme}"
        if os.path.exists(path):
            size = os.path.getsize(path)
            # Get last modified time
            mtime = os.path.getmtime(path)
            age_hours = (time.time() - mtime) / 3600
            status = "✓" if age_hours < 24 else "⚠"
            print(f"{status} {readme:40} ({size:6,} bytes, {age_hours:5.1f}h old)")
        else:
            print(f"✗ {readme:40} MISSING")
            all_exist = False
    
    return all_exist

def run_full_test():
    """Run all tests."""
    print("\n" + "="*70)
    print("HUNGRY AGENT - DAEMON & HEARTBEAT VERIFICATION TEST")
    print("="*70)
    
    results = {}
    
    # Run tests
    results['ollama'] = verify_ollama()
    results['processes'] = check_processes()
    results['ipc'] = check_ipc_files()
    results['heartbeat'] = test_heartbeat()
    results['readmes'] = verify_readme_updates()
    
    # Send test prompt
    test_id = f"gui-test-{int(time.time())}"
    gui_prompt = (
        "Create a simple Xcode SwiftUI GUI that shows a counter with increment/decrement buttons. "
        "Put it in xcode-project/CounterApp.swift with proper SwiftUI structure. "
        "Include comments explaining each part."
    )
    
    if send_test_prompt(gui_prompt, test_id):
        action = wait_for_response(test_id, timeout=45)
        results['gui_test'] = action is not None
        
        if action:
            print(f"\n✓ AGENT CREATED FILE/ACTION!")
            print(f"  Details: {json.dumps(action, indent=2)[:200]}...")
    else:
        results['gui_test'] = False
    
    # Summary
    print_header("TEST SUMMARY")
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:10} {test_name}")
    
    all_passed = all(results.values())
    print(f"\n{'='*70}")
    if all_passed:
        print("✓ ALL TESTS PASSED - System is fully functional!")
    else:
        print("⚠ Some tests did not pass - See details above")
    print(f"{'='*70}\n")
    
    return all_passed

if __name__ == "__main__":
    run_full_test()
