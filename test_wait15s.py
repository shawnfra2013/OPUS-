#!/usr/bin/env python3
"""Quick manual test with extended wait time."""
import sys, subprocess, time, json, os

inbox = 'local-agent-vscode/ipc/inbox.jsonl'
outbox = 'local-agent-vscode/ipc/outbox.jsonl'
test_file = 'test_wait15s.txt'

# Clean up
for f in [test_file]:
    if os.path.exists(f): os.remove(f)
for f in [inbox, outbox]:
    open(f, 'w').close()

# Write prompt
with open(inbox, 'w') as f:
    f.write(json.dumps({
        'id': 'wait15', 
        'text': f'Create {test_file} with content: Extended wait test passed!',
        'timestamp': int(time.time() * 1000)
    }) + '\n')

print(f'[TEST] Starting agent, waiting 15 seconds...')
proc = subprocess.Popen(['python3', '-u', 'run_agent.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

try:
    for i in range(15):
        time.sleep(1)
        if os.path.exists(test_file):
            print(f'\n✅ File created after {i+1}s!')
            with open(test_file) as f:
                print(f'Content: {f.read()}')
            os.remove(test_file)
            proc.terminate()
            raise SystemExit(0)  # Exit gracefully
        print(f'{i+1}s...', end=' ', flush=True)

    proc.terminate()
    output, _ = proc.communicate(timeout=2)
    print(f'\n❌ File not created. Agent output:\n{output[-300:]}')
    raise RuntimeError("Test failed: File not created within 15 seconds.")

except Exception as e:
    print(f"[ERROR] {e}")
    proc.terminate()
    raise
