#!/usr/bin/env python3
"""
Simple end-to-end test: Write a prompt, start agent, wait, check for file.
"""

import json
import time
import os
import sys
import subprocess
import signal

# Paths
IPC_DIR = os.path.join(os.path.dirname(__file__), 'local-agent-vscode', 'ipc')
INBOX = os.path.join(IPC_DIR, 'inbox.jsonl')
OUTBOX = os.path.join(IPC_DIR, 'outbox.jsonl')
TEST_FILE = os.path.join(os.path.dirname(__file__), 'agent_test_output.txt')

def main():
    print("\n" + "=" * 60)
    print("END-TO-END TEST: Agent Autonomous Execution")
    print("=" * 60)
    
    # Clean up from any previous run
    for f in [TEST_FILE]:
        if os.path.exists(f):
            os.remove(f)
    
    # Clear IPC
    print("\n[1] Clearing IPC files...")
    open(INBOX, 'w').close()
    open(OUTBOX, 'w').close()
    
    # Write test prompt
    print("[2] Writing test prompt to inbox...")
    prompt = {
        "id": str(int(time.time() * 1000)),
        "text": f"Create {TEST_FILE} with content: 'End-to-end test success!'",
        "timestamp": int(time.time() * 1000)
    }
    with open(INBOX, 'a') as f:
        f.write(json.dumps(prompt) + '\n')
    print(f"    Prompt: {prompt['text']}")
    
    # Start agent in background
    print("[3] Starting agent in background...")
    agent_proc = subprocess.Popen(
        ['python3', 'run_agent.py'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    print(f"    Agent PID: {agent_proc.pid}")
    print("[4] Waiting 10 seconds for agent to process...")
    
    # Wait for file to appear
    start_time = time.time()
    timeout = 10
    file_created = False
    
    while (time.time() - start_time) < timeout:
        if os.path.exists(TEST_FILE):
            file_created = True
            break
        time.sleep(0.5)
    
    # Kill agent
    print(f"\n[5] Stopping agent (PID {agent_proc.pid})...")
    try:
        os.kill(agent_proc.pid, signal.SIGTERM)
        agent_proc.wait(timeout=2)
    except:
        agent_proc.kill()
    
    # Check results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    if file_created:
        with open(TEST_FILE, 'r') as f:
            content = f.read()
        print(f"✅ SUCCESS!")
        print(f"   File: {TEST_FILE}")
        print(f"   Content: '{content}'")
        print(f"   Created in: {time.time() - start_time:.1f}s")
        
        # Clean up
        os.remove(TEST_FILE)
        
        print("\n✅ AGENT IS FUNCTIONING AUTONOMOUSLY!")
        return True
    else:
        print(f"❌ FAILED")
        print(f"   File was not created: {TEST_FILE}")
        
        # Show diagnostics
        if os.path.getsize(OUTBOX) > 0:
            print("\n   Outbox has content:")
            with open(OUTBOX, 'r') as f:
                for line in f:
                    print(f"   {line.strip()[:100]}...")
        else:
            print("\n   Outbox is empty (agent didn't write response)")
        
        print("\n❌ AGENT NOT FUNCTIONING AUTONOMOUSLY")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
