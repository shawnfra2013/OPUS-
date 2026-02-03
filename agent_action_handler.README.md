# Agent Action Handler

**Owner**: Agent execution layer | **Responsibility**: Execute all agent-requested actions atomically

## Purpose

The Action Handler is the **execution layer** between agent reasoning and actual system changes. When the agent outputs JSON actions, this module intercepts and executes them immediately without requiring human approval or feedback.

**Core Philosophy**: Autonomous execution - no prompt-back, no "here's how to do it", just do it.

# Agent Action Handler: Atomic Execution & Audit

**Owner**: Agent execution layer, audit, and journaling
**Responsibility**: Execute all agent-requested actions atomically, log every action and error, maintain audit trail, and support system coherence and advancement

## Purpose
The Action Handler is the **atomic execution layer** between agent reasoning and actual system changes. It:
- Executes all agent-requested actions (create/update/read files, execute commands) immediately and atomically.
- Logs every action and error to `agent_actions.jsonl` and `agent_debug.log` for full traceability.
- Maintains an audit trail for all actions, supporting transparency and debugging.
- Filters out demo/template actions unless explicitly requested, ensuring only relevant actions are executed.
- Surfaces all errors in the GUI/status bar for user awareness (no silent failures).
- Supports journaling and system advancement by providing a reliable execution and feedback loop.

**Core Philosophy**: Autonomous, auditable execution—no prompt-back, no "here's how to do it", just do it, log it, and surface all results.

## Architecture

```
Agent Output (outbox.jsonl)
    ↓
Action Handler (daemon thread)
    ↓ Parses JSON actions
    ↓
Execute actions (create_file, update_file, execute_command, etc.)
    ↓
Log to agent_actions.jsonl
    ↓
Status reported back to agent
```

## Architecture & Control

```
Agent Output (outbox.jsonl)
    ↓
Action Handler (daemon thread)
    ↓ Parses JSON actions
    ↓
Execute actions (create_file, update_file, execute_command, etc.)
    ↓
Log to agent_actions.jsonl and agent_debug.log
    ↓
Surface errors in GUI/status bar
    ↓
Status and audit trail reported back to agent and journaling system
```

## Files


## Files & Logging
- **Location**: `agent_action_handler.py`
- **Runs As**: Daemon thread in `run_agent.py`
- **Monitoring**: Checks outbox every 0.5 seconds for new actions
- **Logging**: Writes to `agent_actions.jsonl` (audit), `agent_debug.log` (errors), and surfaces errors in GUI/status bar

## Supported Actions

| Action Type | Parameters | Effect |
|------------|-----------|--------|
| `create_file` | `filepath`, `content`, `reason` | Creates file with content at path |
| `update_file` | `filepath`, `content`, `reason` | Overwrites file with new content |
| `update_readme` | `reason` | Appends entry to README.md auto-update log |
| `execute_command` | `filepath` (bash/sh), `content` (command), `reason` | Runs shell command |

## Supported Actions

| Action Type      | Parameters                        | Effect                                 |
|------------------|-----------------------------------|----------------------------------------|
| `create_file`    | `filepath`, `content`, `reason`   | Creates file with content at path      |
| `update_file`    | `filepath`, `content`, `reason`   | Overwrites file with new content       |
| `update_readme`  | `reason`                          | Appends entry to README.md auto-update |
| `execute_command`| `filepath` (bash/sh), `content` (command), `reason` | Runs shell command |
| `read_file`      | `filepath`, `reason`              | Reads file and logs content            |

## How It Works

### Step 1: Monitoring (monitor_loop)
```python
# Runs continuously in background thread
while True:
    process_outbox(processed_set)
    time.sleep(0.5)  # Check every 500ms
```

## How It Works

### Step 1: Monitoring (monitor_loop)
Runs continuously in a background thread, checking outbox every 0.5 seconds for new actions.
Tracks processed actions to prevent re-execution.

### Step 2: Parsing (process_outbox)
Reads outbox, parses each new line as JSON, and extracts the "actions" array.

### Step 3: Atomic Execution & Logging
Executes each action atomically, logs all actions and errors, and updates the audit trail and error log.
All errors are surfaced in the GUI/status bar for user awareness.

### Step 4: Journaling & Advancement
Provides a reliable execution and feedback loop for the journaling and self-improvement system, supporting continuous advancement.

## Advancement Goal
To ensure all agent actions are executed atomically, logged, and surfaced for full transparency, supporting system coherence, journaling, and continuous advancement.

**Key Detail**: Uses `processed` set to track which lines have been handled. This prevents re-executing the same action if outbox is re-read.

### Step 2: Parsing (process_outbox)
```python
# Read entire outbox file
for each line in outbox.jsonl:
    if line not yet in processed:
        parse as JSON
        extract "actions" array
        for each action:
            execute_action(action)
```

**Important**: Reads entire file each time. This is intentional - allows for new actions to appear even if agent crashed and restarted.

### Step 3: Execution (execute_action)
```python
action = {
    "action_type": "create_file",
    "filepath": "/Users/shawnfrahm/hungry/file.txt",
    "content": "file contents here",
    "reason": "Why this action accomplishes the user request"
}
# Route to appropriate handler based on action_type
_create_file(action)  # Creates directories, writes file, logs
```

### Step 4: Logging (_log_action)
Every executed action appended to `agent_actions.jsonl`:
```json
{
  "timestamp": 1738439400,
  "action_type": "create_file",
  "filepath": "/Users/shawnfrahm/hungry/file.txt",
  "reason": "...",
  "status": "success",
  "details": "File created successfully"
}
```

## Responsibility Matrix

| Responsibility | Who | How |
|----------------|-----|-----|
| **Parse JSON** | AgentActionHandler | Regex extraction + JSON parsing in `process_outbox()` |
| **Route actions** | AgentActionHandler | Switch on `action_type` field in `execute_action()` |
| **Create files** | `_create_file()` | mkdir -p + file write + error handling |
| **Update files** | `_update_file()` | Read-modify-write with backup |
| **Execute commands** | `_execute_command()` | subprocess.run() with timeout |
| **Audit trail** | `_log_action()` | Write to agent_actions.jsonl atomically |

## Error Handling

```python
# Every action execution is wrapped in try/except
try:
    _create_file(action)
except FileNotFoundError as e:
    # Log the error
    _log_action(action, status="failed", details=str(e))
    print(f"[ActionHandler] ✗ {action_type}: {e}")
except Exception as e:
    # Catch all other errors
    _log_action(action, status="error", details=str(e))
```

**Important**: Errors don't stop the loop. Handler continues processing subsequent actions. This allows partial success (some actions fail, others succeed).

## Known Behaviors

### ✅ Correct (Don't Change)

1. **Infinite monitor_loop** (line 20-24)
   - Loop never exits naturally, runs until process killed
   - Intentional: daemon threads should run forever

2. **Processed set not persisted** (line 21)
   - `processed = set()` created fresh each call to process_outbox
   - Intentional: allows re-processing if handler crashes
   - Only tracks within current execution session

3. **No outbox cleanup** (handler doesn't delete lines)
   - Agent responsible for clearing inbox (not outbox)
   - Outbox grows indefinitely
   - Intentional: complete audit trail
   - **Cleanup**: Must be done manually via script or operator

4. **File write immediately** (no batching)
   - Each action executes immediately, not queued
   - Intentional: responsive to agent requests

### ⚠️ Potential Issues (Monitored)

1. **Outbox file locks** 
   - Multiple readers could cause issues on some filesystems
   - Monitor: Check if files get corrupted with concurrent access
   - Mitigation: Use `.jsonl` format (line-delimited, atomic writes)

2. **Large outbox files**
   - Handler re-reads entire file every 0.5s
   - If outbox grows to 100k+ lines, performance degrades
   - Monitor: Track outbox file size in diagnostic_monitor.py
   - Mitigation: Implement cleanup or archiving

3. **Action failures silent to user**
   - Action failure logged but not reported back to user
   - By design: no real-time feedback channel yet
   - Future: Could write to response channel for user notification

## Testing

**Unit Test**: See `test_action_autonomy.py`
```bash
python3 test_action_autonomy.py
# Creates proof_of_autonomy.txt
# Verifies handler executes actions without agent involvement
```

**Integration Test**: See `test_e2e_simple.py`
```bash
python3 test_e2e_simple.py
# Writes prompt to inbox
# Agent processes and outputs JSON action
# Handler executes action
# File appears on disk
# Entire flow verified in ~8 seconds
```

## Transparency & Audit

Every action is logged to `agent_actions.jsonl`:
- **When**: Timestamp of execution
- **What**: Action type, filepath, content signature
- **Why**: Reason from agent
- **Status**: Success/failure with error details

This provides complete audit trail:
```bash
# View all actions
tail -100 agent_actions.jsonl | python3 -m json.tool

# Count by type
grep action_type agent_actions.jsonl | grep -o '"[^"]*"' | sort | uniq -c

# Find failures
grep '"status": "failed"' agent_actions.jsonl
```

## Configuration

No configuration file needed. Handler uses hardcoded paths:
- Reads from: `local-agent-vscode/ipc/outbox.jsonl`
- Logs to: `agent_actions.jsonl`
- Poll interval: 0.5 seconds (line 23)

To change poll interval, edit line 23:
```python
time.sleep(0.5)  # Change 0.5 to desired seconds
```

## Integration Points

- **Started by**: `run_agent.py` line 254
- **Input from**: `process_prompt()` output → `outbox.jsonl`
- **Output to**: File system + `agent_actions.jsonl`
- **No direct communication** with agent (only via IPC files)

## Daemon Responsibilities

The Tinkerer Daemon should:
1. Monitor `agent_actions.jsonl` for errors
2. Check if action handler thread is still running
3. Verify outbox doesn't grow unbounded
4. Report summary of action success rate
5. Alert if handler crashes
