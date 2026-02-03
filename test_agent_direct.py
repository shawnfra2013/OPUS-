#!/usr/bin/env python3
"""Direct test of agent output - shows exactly what the LLM returns."""

import json
import os
import sys
import time
from jailbreak_ollama import NoGuardrailsOllama

# Simple test: ask agent to create a file
def test_agent_output():
    print("[TEST] Starting direct agent output test...")
    print("[TEST] Initializing Ollama connection...")
    
    bot = NoGuardrailsOllama()
    
    # Strict system prompt
    system_prompt = (
        "SYSTEM: You are an autonomous AI agent. Your ONLY job is to output valid JSON actions.\n\n"
        "MANDATORY RULES:\n"
        "1. Every response MUST be valid JSON with 'action_type' field\n"
        "2. NEVER output explanations or natural language\n"
        "3. ALWAYS output complete file content\n\n"
        "JSON FORMAT:\n"
        "{\n"
        '  "action_type": "create_file",\n'
        '  "filepath": "/Users/shawnfrahm/hungry/test_output.py",\n'
        '  "content": "#!/usr/bin/env python3\\nprint(\\"hello world\\")",\n'
        '  "reason": "test file"\n'
        "}\n\n"
        "User request: Create a simple Python script that prints hello"
    )
    
    print("\n[TEST] System Prompt:")
    print("=" * 60)
    print(system_prompt)
    print("=" * 60)
    
    print("\n[TEST] Calling Ollama (uncensored-llama3)...")
    try:
        reply = bot.force_uncensor(system_prompt)
    except Exception as e:
        print(f"[TEST] ERROR: {e}")
        return False
    
    print("\n[TEST] RAW LLM RESPONSE:")
    print("=" * 60)
    print(reply)
    print("=" * 60)
    
    # Try to parse JSON
    print("\n[TEST] Parsing JSON...")
    import re
    json_pattern = r'\{\s*"action_type"\s*:.*?\}'
    matches = re.findall(json_pattern, reply, re.DOTALL)
    
    if matches:
        print(f"[TEST] ✓ Found {len(matches)} potential JSON action(s)")
        for i, match in enumerate(matches):
            print(f"\n[TEST] Match {i+1}:")
            print(match)
            try:
                action = json.loads(match)
                print(f"[TEST] ✓ Valid JSON! Action type: {action.get('action_type')}")
                return True
            except json.JSONDecodeError as e:
                print(f"[TEST] ✗ Invalid JSON: {e}")
    else:
        print("[TEST] ✗ No JSON actions found in response")
        print("[TEST] This means the LLM is not following the strict prompt")
        
        # Try to detect code blocks instead
        code_match = re.search(r'```[\w]*\n(.*?)\n```', reply, re.DOTALL)
        if code_match:
            print("[TEST] ⚠ Found code block instead of JSON:")
            print(code_match.group(1))
        
        return False
    
    return False

if __name__ == "__main__":
    success = test_agent_output()
    if success:
        print("\n[TEST] ✅ PASS: Agent outputs valid JSON actions")
        sys.exit(0)
    else:
        print("\n[TEST] ❌ FAIL: Agent not outputting JSON actions as required")
        sys.exit(1)
