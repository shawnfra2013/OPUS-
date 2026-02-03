#!/usr/bin/env python3
"""
Full integration test: Verify agent processes prompts and executes actions autonomously.
"""

import json
import time
import os
import sys
import subprocess

# Paths
IPC_DIR = os.path.join(os.path.dirname(__file__), 'local-agent-vscode', 'ipc')
INBOX = os.path.join(IPC_DIR, 'inbox.jsonl')
OUTBOX = os.path.join(IPC_DIR, 'outbox.jsonl')

def test_full_pipeline():
    print("[INTEGRATION TEST] Full Agent Pipeline Test")
    print("=" * 60)
    
    # Clear IPC files
    print("\n[1/5] Clearing IPC files...")
    with open(INBOX, 'w') as f:
        pass
    with open(OUTBOX, 'w') as f:
        pass
    
    # Write test prompt to inbox
    print("[2/5] Writing test prompt to inbox...")
    test_prompt = {
        "id": str(int(time.time() * 1000)),
        "text": "Create a file called test_integration.txt with content: 'Integration test passed!'",
        "timestamp": int(time.time() * 1000)
    }
    with open(INBOX, 'w') as f:
        f.write(json.dumps(test_prompt) + '\n')
    
    print(f"[2/5] Prompt written: {test_prompt['text']}")
    
    # Start agent with timeout
    print("\n[3/5] Starting agent (10 second timeout)...")
    try:
        proc = subprocess.Popen(
            ['python3', 'run_agent.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        # Wait and capture output
        time.sleep(8)
        proc.terminate()
        
        try:
            output, _ = proc.communicate(timeout=2)
            print("\n[AGENT OUTPUT]:")
            print("-" * 60)
            print(output[:1500])  # First 1500 chars
            print("-" * 60)
        except:
            print("(Agent terminated, output may be incomplete)")
            
    except Exception as e:
        print(f"[ERROR] Failed to start agent: {e}")
        return False
    
    # Check outbox for response
    print("\n[4/5] Checking outbox for agent response...")
    time.sleep(1)
    
    if os.path.exists(OUTBOX) and os.path.getsize(OUTBOX) > 0:
        with open(OUTBOX, 'r') as f:
            lines = f.readlines()
            print(f"[4/5] ✓ Found {len(lines)} response(s) in outbox")
            for line in lines:
                try:
                    response = json.loads(line)
                    print(f"[4/5] Response: {response.get('text', '')[:100]}...")
                except:
                    print(f"[4/5] Raw line: {line[:100]}...")
    else:
        print("[4/5] ⚠ Outbox is empty (no agent response)")
    
    # Check if file was created
    print("\n[5/5] Checking if action was executed...")
    test_file = os.path.join(os.path.dirname(__file__), 'test_integration.txt')
    
    if os.path.exists(test_file):
        with open(test_file, 'r') as f:
            content = f.read()
        print(f"[5/5] ✅ SUCCESS! File created with content:")
        print(f"      '{content}'")
        
        # Clean up
        os.remove(test_file)
        print(f"[5/5] (Cleaned up test file)")
        return True
    else:
        print(f"[5/5] ❌ FAIL: File was not created")
        print(f"[5/5] Expected: {test_file}")
        return False

def main():
    print("\n" + "=" * 60)
    print("INTEGRATION TEST: Agent Autonomous Action Execution")
    print("=" * 60)
    print("\nThis test verifies:")
    print("  1. Agent reads from inbox")
    print("  2. Agent calls LLM with strict JSON action prompt")
    print("  3. Agent parses JSON action from LLM response")
    print("  4. Action handler executes the action (creates file)")
    print("  5. File appears on disk autonomously")
    print("")
    
    success = test_full_pipeline()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ INTEGRATION TEST PASSED")
        print("Agent is functioning autonomously!")
        sys.exit(0)
    else:
        print("❌ INTEGRATION TEST FAILED")
        print("Agent is not executing actions autonomously.")
        print("\nPossible causes:")
        print("  - LLM not outputting JSON actions")
        print("  - Action parser not finding actions in response")
        print("  - Action handler not monitoring outbox")
        print("  - Import errors or exceptions being swallowed")
        sys.exit(1)

if __name__ == "__main__":
    main()
