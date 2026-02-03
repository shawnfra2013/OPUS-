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
            # Handle content that might be a list or string
            content_raw = data.get('content') or ''
            content = content_raw.lower() if isinstance(content_raw, str) else str(content_raw).lower()
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
        elif action_type == 'insert_code':
            AgentActionHandler._insert_code(data)
        elif action_type == 'list_directory':
            AgentActionHandler._list_directory(data)
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
    
    # Critical files that require special protection
    CRITICAL_FILES = [
        'agent_action_handler.py', 'run_agent.py', 'agent_gui.py', 
        'jailbreak_ollama.py', 'scripts/dev.sh'
    ]
    
    # Placeholder patterns that indicate incomplete/bad content
    PLACEHOLDER_PATTERNS = [
        'FULL_NEW_FILE_CONTENT_HERE', 'TODO_REPLACE', 'PLACEHOLDER',
        'INSERT_CODE_HERE', '...(truncated)', 'CONTENT_GOES_HERE'
    ]
    
    @staticmethod
    def _update_file(data):
        """Update an existing file, with safety checks for critical files"""
        filepath = data.get('filepath')
        content = data.get('content')
        append = data.get('append', False)
        if not filepath or not content:
            return
        
        # SAFETY CHECK 1: Block placeholder content
        for pattern in AgentActionHandler.PLACEHOLDER_PATTERNS:
            if pattern in content:
                print(f"[ActionHandler] ⚠️ BLOCKED update to {filepath}: Contains placeholder '{pattern}'")
                AgentActionHandler._log_action({
                    'type': 'file_update_blocked',
                    'filepath': filepath,
                    'timestamp': int(time.time()),
                    'reason': f'Content contains placeholder: {pattern}'
                })
                return
        
        try:
            path = Path(__file__).parent / filepath
            
            # SAFETY CHECK 2: For critical files, ensure new content is substantial
            basename = os.path.basename(filepath)
            if basename in AgentActionHandler.CRITICAL_FILES:
                if path.exists():
                    original_size = len(path.read_text())
                    new_size = len(content)
                    # Block if new content is less than 50% of original
                    if new_size < original_size * 0.5:
                        print(f"[ActionHandler] ⚠️ BLOCKED update to {filepath}: New content ({new_size} bytes) is too small vs original ({original_size} bytes)")
                        AgentActionHandler._log_action({
                            'type': 'file_update_blocked',
                            'filepath': filepath,
                            'timestamp': int(time.time()),
                            'reason': f'New content too small: {new_size} < {original_size * 0.5}'
                        })
                        return
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
    def _insert_code(data):
        """Insert code into a file at a specific location (after a matching line)"""
        filepath = data.get('filepath')
        after_line = data.get('after_line', '')
        code = data.get('code', '')
        reason = data.get('reason', 'Insert code')
        
        if not filepath or not code:
            print(f"[ActionHandler] ✗ insert_code missing filepath or code")
            return
        
        try:
            path = Path(filepath) if filepath.startswith('/') else Path(__file__).parent / filepath
            
            if not path.exists():
                print(f"[ActionHandler] ✗ insert_code: file not found: {filepath}")
                return
            
            original_content = path.read_text()
            lines = original_content.split('\n')
            
            # Find the line to insert after
            insert_index = None
            after_line_clean = after_line.strip()
            
            for i, line in enumerate(lines):
                if after_line_clean in line:
                    insert_index = i + 1
                    break
            
            if insert_index is None:
                # Fallback: insert after the class definition
                for i, line in enumerate(lines):
                    if 'class AgentActionHandler' in line:
                        # Find the end of this method/start of next
                        for j in range(i + 1, len(lines)):
                            if lines[j].strip().startswith('@staticmethod') or lines[j].strip().startswith('def '):
                                insert_index = j
                                break
                        break
            
            if insert_index is None:
                # Last resort: append at end of file
                insert_index = len(lines)
            
            # Insert the code
            code_lines = code.split('\n')
            new_lines = lines[:insert_index] + [''] + code_lines + [''] + lines[insert_index:]
            new_content = '\n'.join(new_lines)
            
            # Write the modified file
            path.write_text(new_content)
            
            print(f"[ActionHandler] ✓ Inserted code into {filepath} (after line {insert_index})")
            
            # Write result to outbox for GUI display
            result_msg = {
                "id": f"insert-code-{int(time.time())}",
                "agent": "actionHandler",
                "text": f"✅ **Inserted code into {filepath}**\n\nCode added:\n```python\n{code[:500]}{'...' if len(code) > 500 else ''}\n```\n\nReason: {reason}",
                "actions": [],
                "timestamp": int(time.time() * 1000)
            }
            with open(OUTBOX, 'a') as f:
                f.write(json.dumps(result_msg) + '\n')
            
            AgentActionHandler._log_action({
                'type': 'code_inserted',
                'filepath': filepath,
                'timestamp': int(time.time()),
                'reason': reason,
                'lines_added': len(code_lines)
            })
            
        except Exception as e:
            print(f"[ActionHandler] ✗ Failed to insert code into {filepath}: {e}")
            AgentActionHandler._log_action({
                'type': 'code_insert_failed',
                'filepath': filepath,
                'timestamp': int(time.time()),
                'error': str(e)
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
        """Read and display file contents, writing result to outbox for GUI display"""
        filepath = data.get('filepath')
        if not filepath:
            return
        
        try:
            # Support both relative and absolute paths
            if os.path.isabs(filepath):
                path = Path(filepath)
            else:
                path = Path(__file__).parent / filepath
            
            if path.exists():
                content = path.read_text()
                print(f"[ActionHandler] ✓ Read: {filepath} ({len(content)} bytes)")
                
                # Write content to outbox so GUI displays it
                outbox_entry = {
                    'id': f'file-read-{int(time.time())}',
                    'agent': 'actionHandler',
                    'text': f'📄 **{filepath}** ({len(content)} bytes):\n\n```\n{content[:2000]}{"...(truncated)" if len(content) > 2000 else ""}\n```',
                    'actions': [],
                    'timestamp': int(time.time() * 1000)
                }
                with open(OUTBOX, 'a') as f:
                    f.write(json.dumps(outbox_entry) + '\n')
                
                AgentActionHandler._log_action({
                    'type': 'file_read',
                    'filepath': filepath,
                    'size': len(content),
                    'timestamp': int(time.time())
                })
            else:
                print(f"[ActionHandler] ✗ File not found: {filepath}")
                # Write error to outbox
                outbox_entry = {
                    'id': f'file-read-error-{int(time.time())}',
                    'agent': 'actionHandler',
                    'text': f'❌ File not found: {filepath}',
                    'actions': [],
                    'timestamp': int(time.time() * 1000)
                }
                with open(OUTBOX, 'a') as f:
                    f.write(json.dumps(outbox_entry) + '\n')
        except Exception as e:
            print(f"[ActionHandler] ✗ Failed to read {filepath}: {e}")

    @staticmethod
    def _list_directory(data):
        """List files and folders in a directory"""
        # Support multiple field names that the LLM might use
        directory_path = data.get('directory_path') or data.get('filepath') or data.get('path', '.')
        
        try:
            from pathlib import Path
            path = Path(directory_path)
            
            if not path.exists():
                print(f"[ActionHandler] ✗ list_directory: path not found: {directory_path}")
                return
            
            items = []
            for item in path.iterdir():
                item_type = 'dir' if item.is_dir() else 'file'
                items.append({'name': item.name, 'type': item_type})
            
            # Write result to outbox for GUI display
            result_msg = {
                "id": f"list-dir-{int(time.time())}",
                "agent": "actionHandler",
                "text": f"📁 **{directory_path}**:\n" + "\n".join([f"  {'📂' if i['type']=='dir' else '📄'} {i['name']}" for i in sorted(items, key=lambda x: (x['type']!='dir', x['name']))]),
                "actions": [],
                "timestamp": int(time.time() * 1000)
            }
            with open(OUTBOX, 'a') as f:
                f.write(json.dumps(result_msg) + '\n')
            
            print(f"[ActionHandler] ✓ Listed {len(items)} items in {directory_path}")
            AgentActionHandler._log_action({
                'type': 'directory_listed',
                'path': directory_path,
                'timestamp': int(time.time()),
                'item_count': len(items)
            })
            
        except Exception as e:
            print(f"[ActionHandler] ✗ Failed to list directory {directory_path}: {e}")
    
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
