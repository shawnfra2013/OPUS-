#!/usr/bin/env python3
"""
Diagnostic Monitor - Watch agent logic flow and catch issues
Monitors: inbox, outbox, action execution, threading, recursion
"""
import os
import time
import json
import sys
from collections import defaultdict

IPC_DIR = 'local-agent-vscode/ipc'
INBOX = os.path.join(IPC_DIR, 'inbox.jsonl')
OUTBOX = os.path.join(IPC_DIR, 'outbox.jsonl')
ACTION_LOG = 'agent_actions.jsonl'

class DiagnosticMonitor:
    def __init__(self):
        self.seen_prompts = set()
        self.seen_actions = set()
        self.recursion_depth = defaultdict(int)
        self.start_time = time.time()
        self.stats = {
            'prompts_processed': 0,
            'actions_executed': 0,
            'errors': 0,
            'recursion_detected': 0
        }
    
    def check_recursion(self, prompt_id, text):
        """Detect if same prompt is being processed multiple times"""
        key = f"{prompt_id}:{hash(text)}"
        self.recursion_depth[key] += 1
        if self.recursion_depth[key] > 2:
            print(f"⚠️  RECURSION DETECTED: Prompt {prompt_id} processed {self.recursion_depth[key]} times")
            print(f"   Text: {text[:80]}...")
            self.stats['recursion_detected'] += 1
            return True
        return False
    
    def watch_inbox(self):
        """Monitor inbox for new prompts"""
        if not os.path.exists(INBOX):
            return []
        
        with open(INBOX, 'r') as f:
            lines = f.readlines()
        
        new_prompts = []
        for line in lines:
            try:
                msg = json.loads(line)
                msg_id = msg.get('id')
                if msg_id and msg_id not in self.seen_prompts:
                    self.seen_prompts.add(msg_id)
                    self.stats['prompts_processed'] += 1
                    new_prompts.append(msg)
                    
                    # Check for recursion
                    text = msg.get('text', '')
                    if self.check_recursion(msg_id, text):
                        print(f"   ⚠️  Consider clearing inbox to break recursion")
            except:
                pass
        
        return new_prompts
    
    def watch_outbox(self):
        """Monitor outbox for responses"""
        if not os.path.exists(OUTBOX):
            return []
        
        with open(OUTBOX, 'r') as f:
            lines = f.readlines()
        
        return [json.loads(line) for line in lines if line.strip()]
    
    def watch_actions(self):
        """Monitor action execution log"""
        if not os.path.exists(ACTION_LOG):
            return []
        
        with open(ACTION_LOG, 'r') as f:
            lines = f.readlines()
        
        new_actions = []
        for line in lines:
            try:
                action = json.loads(line)
                action_id = f"{action.get('action_type')}:{action.get('filepath')}"
                if action_id not in self.seen_actions:
                    self.seen_actions.add(action_id)
                    self.stats['actions_executed'] += 1
                    new_actions.append(action)
            except:
                pass
        
        return new_actions
    
    def check_logic_gates(self):
        """Verify all critical paths exist and are accessible"""
        checks = {
            'run_agent.py': os.path.exists('run_agent.py'),
            'agent_action_handler.py': os.path.exists('agent_action_handler.py'),
            'jailbreak_ollama.py': os.path.exists('jailbreak_ollama.py'),
            'inbox': os.path.exists(INBOX),
            'outbox': os.path.exists(OUTBOX),
            'backend/memory.py': os.path.exists('backend/memory.py'),
        }
        
        print("\n🔍 LOGIC GATES CHECK:")
        all_good = True
        for path, exists in checks.items():
            status = "✓" if exists else "✗"
            print(f"  {status} {path}")
            if not exists:
                all_good = False
        
        return all_good
    
    def check_syntax(self):
        """Check Python files for syntax errors"""
        import subprocess
        files = ['run_agent.py', 'agent_action_handler.py', 'tinkerer_daemon.py', 'backend/memory.py']
        
        print("\n🔍 SYNTAX CHECK:")
        errors = []
        for f in files:
            if not os.path.exists(f):
                continue
            result = subprocess.run(['python3', '-m', 'py_compile', f], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print(f"  ✗ {f}: {result.stderr.split('File')[1] if 'File' in result.stderr else result.stderr}")
                errors.append(f)
            else:
                print(f"  ✓ {f}")
        
        return len(errors) == 0
    
    def watch_loop(self, duration=30):
        """Watch all components for specified duration"""
        print(f"\n{'='*60}")
        print(f"DIAGNOSTIC MONITOR - Watching for {duration}s")
        print(f"{'='*60}")
        
        # Pre-checks
        if not self.check_logic_gates():
            print("\n❌ Logic gate check failed - missing files!")
            return False
        
        if not self.check_syntax():
            print("\n❌ Syntax errors detected!")
            return False
        
        print("\n✓ Pre-checks passed. Starting watch...\n")
        
        end_time = time.time() + duration
        last_check = 0
        
        while time.time() < end_time:
            elapsed = time.time() - self.start_time
            
            # Check every second
            if time.time() - last_check >= 1:
                # Watch for new prompts
                new_prompts = self.watch_inbox()
                for p in new_prompts:
                    print(f"[{elapsed:.1f}s] 📥 INBOX: {p.get('text', '')[:60]}...")
                
                # Watch for responses
                responses = self.watch_outbox()
                if responses:
                    latest = responses[-1]
                    print(f"[{elapsed:.1f}s] 📤 OUTBOX: {latest.get('text', '')[:60]}...")
                
                # Watch for actions
                new_actions = self.watch_actions()
                for a in new_actions:
                    print(f"[{elapsed:.1f}s] ⚡ ACTION: {a.get('action_type')} → {a.get('filepath')}")
                
                last_check = time.time()
            
            time.sleep(0.5)
        
        # Final stats
        print(f"\n{'='*60}")
        print("DIAGNOSTIC SUMMARY")
        print(f"{'='*60}")
        print(f"Prompts processed: {self.stats['prompts_processed']}")
        print(f"Actions executed: {self.stats['actions_executed']}")
        print(f"Recursion warnings: {self.stats['recursion_detected']}")
        print(f"Errors: {self.stats['errors']}")
        
        return True

def test_with_monitor():
    """Run a test with monitoring"""
    monitor = DiagnosticMonitor()
    
    # Clear IPC
    for f in [INBOX, OUTBOX, ACTION_LOG]:
        if os.path.exists(f):
            open(f, 'w').close()
    
    # Write test prompt
    test_prompt = {
        'id': 'monitor_test',
        'text': 'Create monitor_test_output.txt with content: Monitor test passed!',
        'timestamp': int(time.time() * 1000)
    }
    with open(INBOX, 'w') as f:
        f.write(json.dumps(test_prompt) + '\n')
    
    print("\n✓ Test prompt written to inbox")
    print("  Starting agent in background...")
    
    import subprocess
    agent_proc = subprocess.Popen(
        ['python3', 'run_agent.py'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    print(f"  Agent PID: {agent_proc.pid}\n")
    
    # Monitor for 20 seconds
    success = monitor.watch_loop(duration=20)
    
    # Kill agent
    agent_proc.terminate()
    agent_proc.wait(timeout=2)
    
    # Check if file was created
    if os.path.exists('monitor_test_output.txt'):
        with open('monitor_test_output.txt') as f:
            content = f.read()
        print(f"\n✅ SUCCESS! File created: {content}")
        os.remove('monitor_test_output.txt')
        return True
    else:
        print("\n❌ FAIL: File not created")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        success = test_with_monitor()
        sys.exit(0 if success else 1)
    else:
        # Just run checks
        monitor = DiagnosticMonitor()
        monitor.check_logic_gates()
        monitor.check_syntax()
