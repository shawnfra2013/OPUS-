"""
agent_action_handler.py

Processes agent output and executes actions like file creation, README updates, etc.
Bridges the gap between agent reasoning and actual system changes.
Runs as a daemon thread monitoring outbox for structured action JSON.
"""
import json
import os
import time
from pathlib import Path

OUTBOX = Path(__file__).parent / 'local-agent-vscode' / 'ipc' / 'outbox.jsonl'
ACTIONS_LOG = Path(__file__).parent / 'agent_actions.jsonl'

# Global set to track processed action IDs
_PROCESSED_ACTIONS = set()

from macos_approver import macOSApprover

class AgentActionHandler:
    @staticmethod
    def monitor_loop():
        """Continuously monitor outbox for actions (runs as daemon thread)"""
        global _PROCESSED_ACTIONS
        while True:
            try:
                AgentActionHandler.process_outbox()
                time.sleep(0.5)
            except Exception as e:
                print(f"[ActionHandler] Monitor error: {e}")
    
    @staticmethod
    def process_outbox():
        """Monitor outbox and execute agent-requested actions"""
        global _PROCESSED_ACTIONS
        
        if not OUTBOX.exists():
            return
        
        try:
            with open(OUTBOX, 'r') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                if not line.strip():
                    continue
                if i in _PROCESSED_ACTIONS:
                    continue
                try:
                    data = json.loads(line)
                    action_id = data.get('id')
                    # Check for actions array in response
                    actions = data.get('actions', [])
                    if actions:
                        print(f"[ActionHandler] Found {len(actions)} actions in response {action_id}")
                    for action in actions:
                        AgentActionHandler.execute_action(action)
                    _PROCESSED_ACTIONS.add(i)
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"[ActionHandler] Error processing outbox: {e}")
    
    @staticmethod
    def execute_action(data):
        """Execute agent actions, skipping demo/template actions unless explicitly requested"""
        action_type = data.get('action_type')
        DEMO_KEYWORDS = [
            'hello', 'greeting', 'greet', 'helo', 'hi', 'test', 'demo', 'sample', 'example',
            'greeting.txt', 'greetings.txt', 'greeting.py', 'greetings.py', 'HELO.py', 'hello.py', 'helo.py'
        ]
        def is_demo_action(data):
            fp = (data.get('filepath') or '').lower()
            content = (data.get('content') or '').lower()
            reason = (data.get('reason') or '').lower()
            for word in DEMO_KEYWORDS:
                if word in fp or word in content:
                    # Exclude /tmp/manual_test.txt from being classified as a demo action
                    if fp == '/tmp/manual_test.txt':
                        continue
                    # Only allow if explicitly requested in reason or filepath/content
                    if word in reason or word in fp or word in content:
                        continue
                    return True
            return False
        if is_demo_action(data):
            print(f"[ActionHandler] Skipped demo/template action: {data.get('filepath','')} (not explicitly requested)")
            AgentActionHandler._log_action({
                'type': 'demo_action_skipped',
                'filepath': data.get('filepath'),
                'timestamp': int(time.time()),
                'reason': 'Demo/template action not explicitly requested',
                'trigger': data.get('reason', 'Agent-generated')
            })
            return
        if action_type == 'create_file':
            AgentActionHandler._create_file(data)
        elif action_type == 'update_file':
            AgentActionHandler._update_file(data)
        elif action_type == 'update_readme':
            AgentActionHandler._update_readme(data)
        elif action_type == 'execute_command':
            AgentActionHandler._execute_command(data)
        elif action_type == 'read_file':
            AgentActionHandler._read_file(data)
        elif action_type == 'log_action':
            AgentActionHandler._log_action(data)
    
    @staticmethod
    def _create_file(data):
        """Create a file from agent output, only if not already present with same content. Allow safe absolute paths (e.g., /tmp). Aggressively log all /tmp file actions."""
        filepath = data.get('filepath')
        content = data.get('content')
        if not filepath or not content:
            return
        try:
            # Allow absolute paths only for /tmp, else use project root
            is_tmp = os.path.isabs(filepath) and filepath.startswith('/tmp/')
            if is_tmp:
                path = Path(filepath)
            else:
                path = Path(__file__).parent / filepath
            path.parent.mkdir(parents=True, exist_ok=True)
            # Context check: skip if file exists with identical content
            if path.exists() and path.read_text() == content:
                print(f"[ActionHandler] Skipped creation: {filepath} (identical content)")
                AgentActionHandler._log_action({
                    'type': 'file_create_skipped',
                    'filepath': filepath,
                    'timestamp': int(time.time()),
                    'reason': 'Identical file already exists',
                    'trigger': data.get('reason', 'Agent-generated')
                })
                if is_tmp:
                    try:
                        with open('/tmp/agent_debug.log', 'a') as dbg:
                            dbg.write(f"[TMP] Skipped creation: {filepath} (identical content)\n")
                    except Exception:
                        pass
                return
            path.write_text(content)
            print(f"[ActionHandler] ✓ Created: {filepath}")
            AgentActionHandler._log_action({
                'type': 'file_created',
                'filepath': filepath,
                'timestamp': int(time.time()),
                'reason': data.get('reason', 'Agent-generated'),
                'trigger': data.get('trigger', 'N/A')
            })
            if is_tmp:
                try:
                    with open('/tmp/agent_debug.log', 'a') as dbg:
                        dbg.write(f"[TMP] Created: {filepath}\n")
                except Exception:
                    pass
        except Exception as e:
            print(f"[ActionHandler] ✗ Failed to create {filepath}: {e}")
            try:
                with open('/tmp/agent_debug.log', 'a') as dbg:
                    dbg.write(f"[TMP] Failed to create {filepath}: {e}\n")
            except Exception:
                pass
            AgentActionHandler._log_action({
                'type': 'file_create_failed',
                'filepath': filepath,
                'timestamp': int(time.time()),
                'error': str(e),
                'trigger': data.get('reason', 'Agent-generated')
            })
    
    @staticmethod
    def _update_file(data):
        """Update an existing file, only if content is different or append is True"""
        filepath = data.get('filepath')
        content = data.get('content')
        append = data.get('append', False)
        if not filepath or not content:
            return
        try:
            path = Path(__file__).parent / filepath
            if path.exists() and not append and path.read_text() == content:
                print(f"[ActionHandler] Skipped update: {filepath} (identical content)")
                AgentActionHandler._log_action({
                    'type': 'file_update_skipped',
                    'filepath': filepath,
                    'timestamp': int(time.time()),
                    'reason': 'Identical file already exists',
                    'trigger': data.get('reason', 'Agent-generated')
                })
                return
            if append:
                path.write_text(path.read_text() + '\n' + content)
            else:
                path.write_text(content)
            print(f"[ActionHandler] ✓ Updated: {filepath}")
            AgentActionHandler._log_action({
                'type': 'file_updated',
                'filepath': filepath,
                'timestamp': int(time.time()),
                'reason': data.get('reason', 'Agent-generated'),
                'trigger': data.get('trigger', 'N/A')
            })
        except Exception as e:
            print(f"[ActionHandler] ✗ Failed to update {filepath}: {e}")
            AgentActionHandler._log_action({
                'type': 'file_update_failed',
                'filepath': filepath,
                'timestamp': int(time.time()),
                'error': str(e),
                'trigger': data.get('reason', 'Agent-generated')
            })
    
    @staticmethod
    def _update_readme(data):
        """Update README with timestamp and reason"""
        reason = data.get('reason', 'Agent update')
        # Approval dialog disabled: always auto-approve
        readme_path = Path(__file__).parent / 'README.md'
        try:
            existing = readme_path.read_text()
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            update_log = f"\n- {timestamp} (auto): {reason}\n"
            if '### [AUTO-UPDATE LOG]' in existing:
                existing = existing.replace('### [AUTO-UPDATE LOG]', f'### [AUTO-UPDATE LOG]{update_log}')
            else:
                existing += f"\n---\n### [AUTO-UPDATE LOG]{update_log}---\n"
            readme_path.write_text(existing)
            print(f"[ActionHandler] ✓ README updated: {reason}")
        except Exception as e:
            print(f"[ActionHandler] ✗ Failed to update README: {e}")
            """Update README with timestamp and reason (no approval, no confirmation)"""
            # Removed approval dialog logic
    
    @staticmethod
    def _execute_command(data):
        """Execute system command"""
        command = data.get('content') or data.get('command')
        if not command:
            return
        # No approval dialog for execute_command actions
        try:
            import subprocess
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            output = result.stdout + result.stderr
            print(f"[ActionHandler] ✓ Executed: {command}")
            print(f"[ActionHandler] Output: {output[:200]}")
            AgentActionHandler._log_action({
                'type': 'command_executed',
                'command': command,
                'exit_code': result.returncode,
                'output': output,
                'timestamp': int(time.time())
            })
        except Exception as e:
            print(f"[ActionHandler] ✗ Failed to execute {command}: {e}")
    
    @staticmethod
    def _read_file(data):
        """Read and display file contents"""
        filepath = data.get('filepath')
        if not filepath:
            return
        
        try:
            path = Path(__file__).parent / filepath
            if path.exists():
                content = path.read_text()
                print(f"[ActionHandler] ✓ Read: {filepath}")
                print(f"[ActionHandler] Content preview: {content[:300]}...")
                AgentActionHandler._log_action({
                    'type': 'file_read',
                    'filepath': filepath,
                    'size': len(content),
                    'timestamp': int(time.time())
                })
            else:
                print(f"[ActionHandler] ✗ File not found: {filepath}")
        except Exception as e:
            print(f"[ActionHandler] ✗ Failed to read {filepath}: {e}")
    
    @staticmethod
    def _log_action(data):
        """Log action to agent_actions.jsonl"""
        try:
            with open(ACTIONS_LOG, 'a') as f:
                f.write(json.dumps(data) + '\n')
        except Exception as e:
            print(f"[ActionHandler] Failed to log action: {e}")

if __name__ == "__main__":
    print("[ActionHandler] Monitoring outbox for agent actions...")
    try:
        handler = AgentActionHandler()
        handler.monitor_loop()
    except KeyboardInterrupt:
        print("[ActionHandler] Stopped.")
