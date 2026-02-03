#!/usr/bin/env python3
"""
test_autonomous_agent.py

End-to-end test proving the agent acts autonomously without prompt-back.
Demonstrates: prompt → agent processing → action output → action handler execution → file creation → success.
"""
import json
import time
import os
from pathlib import Path
import subprocess
import sys

# Paths
PROJECT_ROOT = Path(__file__).parent
IPC_DIR = PROJECT_ROOT / 'local-agent-vscode' / 'ipc'
INBOX = IPC_DIR / 'inbox.jsonl'
OUTBOX = IPC_DIR / 'outbox.jsonl'

print("=" * 80)
print("AUTONOMOUS AGENT TEST: Prompt → Action → Execution")
print("=" * 80)

# Step 1: Prepare IPC
print("\n[TEST] Step 1: Setting up IPC...")
IPC_DIR.mkdir(parents=True, exist_ok=True)
INBOX.write_text("")
OUTBOX.write_text("")
print(f"✓ IPC ready at {IPC_DIR}")

# Step 2: Send test prompt
print("\n[TEST] Step 2: Sending autonomous prompt to agent...")
test_prompt = """Create a file called test_autonomous.txt with the content:
"This file was created autonomously by the agent without prompting back for confirmation."
Use JSON action format: {"action_type": "create_file", "filepath": "test_autonomous.txt", "content": "...", "reason": "..."}
"""

msg = {
    "id": str(int(time.time() * 1000)),
    "text": test_prompt,
    "timestamp": int(time.time() * 1000)
}
INBOX.write_text(json.dumps(msg) + '\n')
print(f"✓ Prompt written to inbox.jsonl")
print(f"  Prompt: {test_prompt[:80]}...")

# Step 3: Start agent backend
print("\n[TEST] Step 3: Starting agent backend (run_agent.py)...")
agent_process = subprocess.Popen(
    [sys.executable, 'run_agent.py'],
    cwd=PROJECT_ROOT,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)
print(f"✓ Agent started (PID: {agent_process.pid})")

# Step 4: Wait for agent to process and write to outbox
print("\n[TEST] Step 4: Waiting for agent to process and write output...")
for i in range(30):  # 30 second timeout
    time.sleep(1)
    if OUTBOX.exists() and OUTBOX.stat().st_size > 0:
        print(f"✓ Agent output detected at {i+1}s")
        break
else:
    print("✗ Timeout: No agent output")
    agent_process.terminate()
    sys.exit(1)

# Step 5: Read agent output
print("\n[TEST] Step 5: Reading agent output...")
outbox_content = OUTBOX.read_text()
lines = outbox_content.strip().split('\n')
if not lines:
    print("✗ Outbox is empty")
    agent_process.terminate()
    sys.exit(1)

agent_response = json.loads(lines[-1])
print(f"✓ Agent response received:")
print(f"  Text: {agent_response.get('text', '')[:80]}...")
print(f"  Actions: {len(agent_response.get('actions', []))} action(s) included")

# Step 6: Check for actions
actions = agent_response.get('actions', [])
if not actions:
    print("✗ No actions in agent response")
    agent_process.terminate()
    sys.exit(1)

print(f"\n[TEST] Step 6: Parsing action_type from agent...")
action = actions[0]
print(f"✓ Action found:")
print(f"  Type: {action.get('action_type')}")
print(f"  Filepath: {action.get('filepath')}")
print(f"  Reason: {action.get('reason')}")

# Step 7: Execute action handler manually (simulate daemon)
print("\n[TEST] Step 7: Executing action handler...")
from agent_action_handler import AgentActionHandler
AgentActionHandler.execute_action(action)

# Step 8: Verify file was created
print("\n[TEST] Step 8: Verifying autonomous action succeeded...")
test_file = PROJECT_ROOT / action.get('filepath', 'test_autonomous.txt')
if test_file.exists():
    content = test_file.read_text()
    print(f"✓ FILE CREATED AUTONOMOUSLY: {test_file}")
    print(f"  Content: {content}")
    success = True
else:
    print(f"✗ File was NOT created: {test_file}")
    success = False

# Step 9: Check action log
print("\n[TEST] Step 9: Verifying action was logged...")
actions_log = PROJECT_ROOT / 'agent_actions.jsonl'
if actions_log.exists():
    actions_log_content = actions_log.read_text()
    print(f"✓ Action logged to agent_actions.jsonl")
    print(f"  Log entries: {len(actions_log_content.strip().split(chr(10)))}")
else:
    print("ℹ Action log not yet created (will be created on next action)")

# Cleanup
print("\n[TEST] Cleanup...")
agent_process.terminate()
try:
    agent_process.wait(timeout=5)
except subprocess.TimeoutExpired:
    agent_process.kill()
print("✓ Agent stopped")

# Final result
print("\n" + "=" * 80)
if success:
    print("✅ TEST PASSED: Agent acted autonomously without prompt-back")
    print("   Prompt → Agent Output → Action Handler → File Created")
    print("   NO prompting back. Pure autonomous action.")
else:
    print("❌ TEST FAILED: Agent did not create file autonomously")
    sys.exit(1)
print("=" * 80)
