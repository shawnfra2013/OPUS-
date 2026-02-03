#!/usr/bin/env python3
"""
test_action_autonomy.py

Simple, direct proof that the agent can output actions and the action handler executes them autonomously.
No LLM calls needed—just demonstrates the core autonomy loop.
"""
import json
import time
from pathlib import Path
from agent_action_handler import AgentActionHandler

print("=" * 80)
print("PROOF: Agent Action → Handler Execution (No Prompt-Back)")
print("=" * 80)

# Simulate agent output with structured actions
print("\n[DEMO] Step 1: Simulating agent output with action_type JSON...")
agent_output = {
    "id": "demo-1",
    "text": "Creating test file autonomously",
    "actions": [
        {
            "action_type": "create_file",
            "filepath": "proof_of_autonomy.txt",
            "content": "This file was created by the autonomous action handler.\nAgent output → Action Handler → File Created.\nNo prompt-back. Pure autonomous execution.",
            "reason": "Proof of autonomous agent action"
        }
    ],
    "timestamp": int(time.time() * 1000)
}

print(f"✓ Simulated agent output:")
print(f"  Text: {agent_output['text']}")
print(f"  Actions: {len(agent_output['actions'])} action(s)")
print(f"  Action type: {agent_output['actions'][0]['action_type']}")

# Step 2: Extract and execute action
print("\n[DEMO] Step 2: Agent would output this JSON to outbox...")
print(json.dumps(agent_output, indent=2))

# Step 3: Action handler executes (no waiting, no approval request)
print("\n[DEMO] Step 3: Action handler intercepts and executes immediately...")
action = agent_output['actions'][0]
print(f"✓ Executing action: {action['action_type']}")
print(f"  filepath: {action['filepath']}")
print(f"  reason: {action['reason']}")

AgentActionHandler.execute_action(action)

# Step 4: Verify execution
print("\n[DEMO] Step 4: Verifying autonomous execution...")
test_file = Path(__file__).parent / action['filepath']
if test_file.exists():
    content = test_file.read_text()
    print(f"\n✅ SUCCESS: File created autonomously")
    print(f"   Path: {test_file}")
    print(f"   Content:\n{content}")
    
    # Verify action was logged
    actions_log = Path(__file__).parent / 'agent_actions.jsonl'
    if actions_log.exists():
        print(f"\n✅ Action logged to: {actions_log}")
        log_entry = actions_log.read_text().strip().split('\n')[-1]
        print(f"   Log entry: {log_entry}")
    
    print("\n" + "=" * 80)
    print("PROOF COMPLETE:")
    print("  1. Agent outputs structured action JSON (no text response)")
    print("  2. Action handler intercepts and executes immediately")
    print("  3. File is created autonomously")
    print("  4. Action is logged for audit trail")
    print("  5. NO prompt-back, NO confirmation requests, NO instructions given back")
    print("=" * 80)
else:
    print(f"\n❌ FAILED: File was not created")
    print(f"   Expected: {test_file}")
    exit(1)
