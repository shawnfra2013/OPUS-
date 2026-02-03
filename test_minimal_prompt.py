#!/usr/bin/env python3
"""
Minimal test: Call process_prompt directly without starting full agent loop.
"""

import json
import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from jailbreak_ollama import NoGuardrailsOllama
from backend.memory import AgentMemory
from run_agent import process_prompt

# Paths
IPC_DIR = os.path.join(os.path.dirname(__file__), 'local-agent-vscode', 'ipc')
OUTBOX = os.path.join(IPC_DIR, 'outbox.jsonl')
TEST_FILE = os.path.join(os.path.dirname(__file__), 'minimal_test_output.txt')

def main():
    print("\n" + "=" * 60)
    print("MINIMAL TEST: Direct process_prompt() call")
    print("=" * 60)
    
    # Clean up
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    open(OUTBOX, 'w').close()
    
    # Initialize components
    print("\n[1] Initializing components...")
    memory = AgentMemory()
    bot = NoGuardrailsOllama()
    
    # Test message
    msg = {
        "id": "test_minimal",
        "text": f"Create {TEST_FILE} with content: 'Minimal test passed!'"
    }
    
    print(f"[2] Calling process_prompt()...")
    print(f"    Prompt: {msg['text']}")
    
    # Call process_prompt
    try:
        process_prompt(msg, memory, bot, OUTBOX)
        print(f"[3] process_prompt() returned successfully")
    except Exception as e:
        print(f"[3] process_prompt() raised exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Give action handler a moment
    print("[4] Waiting 2 seconds for action handler...")
    time.sleep(2)
    
    # Check results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    if os.path.exists(TEST_FILE):
        with open(TEST_FILE, 'r') as f:
            content = f.read()
        print(f"✅ SUCCESS!")
        print(f"   File: {TEST_FILE}")
        print(f"   Content: '{content}'")
        os.remove(TEST_FILE)
        return True
    else:
        print(f"❌ FAILED: File not created")
        
        # Diagnostics
        if os.path.getsize(OUTBOX) > 0:
            print("\n   Outbox content:")
            with open(OUTBOX, 'r') as f:
                for line in f:
                    print(f"   {line.strip()}")
        else:
            print("\n   Outbox is empty")
        
        return False

if __name__ == "__main__":
    # Disable refinement for faster test
    import run_agent
    run_agent.skip_refinement = True
    
    success = main()
    sys.exit(0 if success else 1)
