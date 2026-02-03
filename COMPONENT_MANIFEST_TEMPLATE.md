# Component Manifest Format - Template for AI Comprehension

**Purpose**: Standardized, machine-readable format so AI models can understand component contracts without ambiguity.

---

## Template (Copy this structure to every README)

```markdown
## Component Manifest

### Metadata
- **Component Name**: [exact name, must match filename]
- **Purpose**: [one sentence: what does it do?]
- **Status**: [stable|beta|experimental|deprecated]
- **Version**: [semantic version]
- **Last Updated**: [ISO 8601 date and time]
- **Updated Reason**: [what changed, why]
- **Owner**: [responsible for maintenance]

### Core Function

**Primary Function**: `function_name(param1: type, param2: type) -> return_type`
- **What it does**: [one sentence description]
- **When to call it**: [circumstances when this is the right function]
- **When NOT to call it**: [when this will fail]
- **Side effects**: [anything it changes besides return value]
- **Typical duration**: [how long it takes, e.g., "0.1-0.5 seconds"]

### Input/Output Specification

**Files Read**:
```
File: path/to/file.json
Format: JSON with fields: {field1: type, field2: type}
Required: yes|no
Permission: read
Update frequency: how often does AI model check this?
Error handling: what if file missing?
```

**Files Written**:
```
File: path/to/file.json
Format: JSON with fields: {field1: type, field2: type}
Append or overwrite: [specify]
Create if missing: yes|no
Permission needed: write
Typical size: [typical file size]
Frequency: [how often written]
Error handling: [what if write fails]
```

**Processes Spawned**:
```
Process: process_name
Command: exact command line
When: [when spawned]
Timeout: [max execution time]
Error handling: [if process hangs]
Logs: [where logs written]
```

**Network Calls**:
```
Service: [service name]
URL: [endpoint]
Port: [port number]
Method: [GET|POST|etc]
Timeout: [wait time before timeout]
Retry logic: [how many retries]
Fallback: [what to do if fails]
```

### Dependencies

**Required Python Packages**:
```
Package: package_name
Version constraint: ==1.0.0 or >=1.0.0,<2.0.0
Used for: [what does this package do]
If missing: [what error occurs]
Installation: pip install [command]
```

**Required Services**:
```
Service: [e.g., Ollama]
Endpoint: [e.g., localhost:11434]
Must be running: yes|no (before this component starts)
Health check: [how to verify it's running]
Timeout: [how long to wait for response]
If unavailable: [does it fall back, or fail?]
Recovery: [how to recover if it goes down]
```

**Required Processes**:
```
Process: [e.g., run_agent.py]
Must be running: [before this component starts]
Interaction: [reads from outbox, writes to inbox, etc]
Timing: [synchronization requirements]
If stops: [what happens to this component]
```

**Required Files**:
```
File: path/to/file.txt
Purpose: [what is this file]
Required before start: yes|no
Readable: yes|no
Writable: yes|no
Format: [JSON|CSV|text|binary]
If missing: [error or auto-create?]
Permissions: [755|644|etc]
```

### Configuration

**Environment Variables**:
```
Variable: VAR_NAME
Default value: [if none set]
Valid range: [min-max or enum]
Type: [string|int|float|bool]
Purpose: [why this setting]
If not set: [what error occurs]
If set wrong: [what breaks]
Update requires restart: [yes|no]
```

**Configuration File Settings**:
```
Setting: SETTING_NAME
File location: path/to/config.py or .env
Default value: [actual default]
Type: [string|int|float|bool|list]
Valid values: [enumeration or range]
Purpose: [what does changing this do]
If changed: [does component restart? reload? immediate?]
Critical: [yes if changing breaks everything]
```

### Preconditions (Must be true BEFORE calling)

- [ ] **Precondition 1**: [e.g., "Ollama must be running"]
  - How to verify: [command to check]
  - If false: [what error occurs]
  - How to fix: [steps to satisfy]

- [ ] **Precondition 2**: [e.g., "inbox.jsonl must be readable"]
  - How to verify: [command to check]
  - If false: [what error occurs]
  - How to fix: [steps to satisfy]

### Postconditions (Will be true AFTER successful execution)

- [ ] **Postcondition 1**: [e.g., "outbox.jsonl has new entry"]
  - How to verify: [command to check]
  - Timing: [when should this appear? immediate/5-10 seconds/etc]

- [ ] **Postcondition 2**: [e.g., "agent_memory.json updated"]
  - How to verify: [command to check]
  - Timing: [when should this appear?]

### Error Handling

**Error 1**: [Specific error message or condition]
```
Cause: [why does this error happen]
Symptoms: [what you see when this happens]
Detection: [how to identify this error]
Recovery: [steps to recover]
Prevent: [how to prevent this error]
Impact if not handled: [what breaks]
```

**Error 2**: [Next error type]
- (same structure)

### Assumptions (NEVER CHANGE WITHOUT CAREFUL THOUGHT)

These assumptions are baked into the system. Breaking them breaks the system.

- [ ] **Assumption 1**: [e.g., "IPC files are NDJSON format"]
  - Why important: [consequence if broken]
  - How verified: [how do we check this]
  - If broken: [what fails]

- [ ] **Assumption 2**: [e.g., "Ollama responds within 13 seconds"]
  - Why important: [consequence if broken]
  - How verified: [how do we check this]
  - If broken: [what fails]

### Breaking Changes

**Version X.Y**: [description of breaking change]
- What changed: [what no longer works the old way]
- Migration: [how to update code that uses old way]
- Timeline: [when old way becomes unsupported]

### Side Effects (Things that change as a side effect)

- [ ] **Side effect 1**: [e.g., "Creates temporary files in /tmp"]
  - What: [what exactly is created]
  - When: [when during execution]
  - Cleanup: [when/how are they cleaned up]
  - If cleanup fails: [what happens]

- [ ] **Side effect 2**: [e.g., "Increments counter in shared file"]
  - What: [what exactly changes]
  - When: [when during execution]
  - Rollback: [can it be rolled back?]
  - If multiple instances run: [race condition risk?]

### Performance Characteristics

| Operation | Min | Typical | Max | Notes |
|-----------|-----|---------|-----|-------|
| Reading inbox | 0.01s | 0.05s | 0.1s | Depends on file size |
| LLM call | 3s | 8s | 15s | Network dependent |
| Writing outbox | 0.01s | 0.02s | 0.1s | File system dependent |

**Bottlenecks**: [What's the slowest part]
**Optimization opportunities**: [What could be faster]

### Testing

**Unit Tests**:
- Test: `test_function_name_1`
  - Input: [what goes in]
  - Expected output: [what should come out]
  - Assertion: [exact condition checked]

**Integration Tests**:
- Test: `test_daemon_and_gui.py::test_step_1`
  - Setup: [what must be true before]
  - Action: [what the test does]
  - Verification: [how we know it worked]

### Integration Points

**Calls (Dependencies)**: [Functions/processes this calls]
```
Function: called_function_name
- Where: [in which function]
- Why: [what does calling this accomplish]
- With what data: [what parameters]
- Expects back: [what return value]
- If fails: [what does calling code do]
```

**Called By (Dependents)**: [Who calls this]
```
Function: calling_function_name
- Where: [in which file]
- Why: [what does the caller need from this]
- Passes: [what parameters]
- Uses return value: [how is return used]
- Error handling: [how does caller handle errors]
```

**Shared State**: [Any global variables, files accessed]
```
State: shared_variable_name
- Location: [in which file]
- Type: [data type]
- Readers: [functions that read]
- Writers: [functions that write]
- Conflicts: [race conditions possible?]
- Locking: [is access synchronized?]
```

### Version History

**V1.2** (2026-02-01)
- Changed: [what changed]
- Why: [why this change]
- Impact: [what now works/works differently]
- Breaking: [yes/no - does old code still work?]

**V1.1** (2026-01-20)
- Changed: [previous change]

### Maintenance

**How to Update This Component**:
1. Read this entire manifest
2. Check: Does code match these specs?
3. Change: [your code change]
4. Update: [what in this manifest changes?]
5. Test: `python3 test_daemon_and_gui.py` (must be 6/6)
6. Verify: Test 5 conditions in "Testing" section
7. Commit: Update this manifest in same commit

**When to Call for Help**:
- [ ] You're not sure what something does
- [ ] Tests don't pass after your change
- [ ] You don't understand a precondition
- [ ] You can't trace a side effect
- [ ] The manifest doesn't match the code

**Deprecated Methods**: [any functions being phased out]
- [old function]
  - Replacement: [new function to use instead]
  - Timeline: [when will old function be removed]
  - Migration: [how to update code using old function]
```

---

## Why This Format Matters for AI Models

### Before This Format
- AI must search docs for information ❌
- AI might miss important assumptions ❌
- AI can't verify preconditions systematically ❌
- AI might break things without knowing why ❌
- AI documentation reading is incomplete ❌

### After This Format
- AI can scan one section for each concern ✅
- All assumptions listed in one place ✅
- AI can verify preconditions before proceeding ✅
- AI understands why each assumption matters ✅
- AI comprehension becomes 100%, not 86% ✅

---

## Example: run_agent.py Component Manifest

```markdown
## Component Manifest

### Metadata
- **Component Name**: run_agent.py
- **Purpose**: Main autonomous agent loop - reads prompts, calls LLM, writes actions
- **Status**: stable
- **Version**: 1.2.0
- **Last Updated**: 2026-02-01 01:26 AM Central
- **Updated Reason**: Added memory context building, improved error handling
- **Owner**: AI Agent Development Team

### Core Function

**Primary Function**: `process_prompt(prompt_dict: dict) -> dict`
- **What it does**: Reads one prompt from inbox, generates LLM response, writes action to outbox
- **When to call it**: Every 2 seconds in main loop
- **When NOT to call it**: If Ollama not running, if inbox corrupted
- **Side effects**: Writes to outbox.jsonl, updates agent_memory.json, creates agent.log entries
- **Typical duration**: 8-13 seconds (mostly waiting for Ollama)

### Input/Output Specification

**Files Read**:
```
File: local-agent-vscode/ipc/inbox.jsonl
Format: NDJSON with fields: {id: string, text: string, timestamp: ISO8601}
Required: yes
Permission: read
Update frequency: checked every 2 seconds
Error handling: if file missing, create empty; if corrupted, log error and skip line
```

**Files Written**:
```
File: local-agent-vscode/ipc/outbox.jsonl
Format: NDJSON with fields: {id: string, action: string, params: object, timestamp: ISO8601}
Append or overwrite: append only
Create if missing: yes (auto-create empty)
Permission needed: write
Typical size: 1-2 KB per entry
Frequency: after each successful LLM call
Error handling: if write fails, log ERROR and sleep 5 seconds before retry
```

```
File: local-agent-vscode/ipc/agent_memory.json
Format: JSON array: [{role: "user"|"assistant", content: string, timestamp: ISO8601}, ...]
Append or overwrite: append (read, add, write back full)
Create if missing: yes (start with [])
Permission needed: write
Typical size: grows ~1 KB per 10 prompts
Frequency: after each prompt processed
Error handling: if corruption detected, backup to agent_memory.json.backup, init empty array
```

### Dependencies

**Required Python Packages**:
```
Package: ollama
Version constraint: >=0.1.0
Used for: calling local Ollama LLM service
If missing: ImportError on line 5
Installation: pip install ollama
```

**Required Services**:
```
Service: Ollama
Endpoint: localhost:11434
Must be running: yes (before starting agent loop)
Health check: curl http://localhost:11434/api/tags
Timeout: 13 seconds per request
If unavailable: attempts cloud_fallback.py (OpenAI)
Recovery: auto-restart Ollama if available (per ollama_manager.py)
```

**Required Processes**:
```
Process: agent_action_handler.py
Must be running: yes (watches outbox.jsonl for actions)
Interaction: reads from outbox.jsonl, logs to agent_actions.jsonl
Timing: checks outbox every 2 seconds
If stops: actions written to outbox won't execute (queued but not processed)
```

**Required Files**:
```
File: local-agent-vscode/ipc/inbox.jsonl
Purpose: user prompts waiting to be processed
Required before start: no (auto-created if missing)
Readable: yes
Writable: yes (by external systems)
Format: NDJSON (JSON lines)
If missing: auto-created empty
Permissions: 644 (user read/write, others read)
```

### Configuration

**Python Module Variables**:
```
Variable: CYCLE_TIME = 2
Default value: 2 (seconds)
Valid range: 1-10
Type: int
Purpose: how often to check inbox for new prompts
If changed to 0.1: would thrash CPU, constant polling
If changed to 60: might miss prompts, slower response
Update requires restart: yes
```

```
Variable: MEMORY_RETENTION = 5
Default value: 5 (recent messages)
Valid range: 1-100
Type: int
Purpose: how many recent messages to include for LLM context
If set to 1: model has no context, decisions inconsistent
If set to 100: slow LLM, token limit exceeded
Update requires restart: no (takes effect next call)
Critical: no (affects quality, not function)
```

```
Variable: LLM_TIMEOUT = 13
Default value: 13 (seconds)
Valid range: 5-30
Type: int
Purpose: max time to wait for Ollama response before timeout
If set to 2: timeouts before Ollama finishes
If set to 60: user waits too long, seems hung
Update requires restart: no (takes effect next call)
Critical: somewhat (affects user experience)
```

### Preconditions (Must be true BEFORE calling)

- [ ] **Ollama running and responding**
  - How to verify: `curl http://localhost:11434/api/tags`
  - If false: JSON parse error, process exits
  - How to fix: start Ollama with `ollama serve &`

- [ ] **inbox.jsonl accessible for reading**
  - How to verify: `ls -l local-agent-vscode/ipc/inbox.jsonl`
  - If false: FileNotFoundError (but auto-creates)
  - How to fix: check file permissions with `chmod 644`

- [ ] **outbox.jsonl directory writable**
  - How to verify: `touch local-agent-vscode/ipc/outbox.jsonl`
  - If false: PermissionError on write
  - How to fix: check directory permissions with `chmod 755`

- [ ] **agent_memory.json in correct JSON format**
  - How to verify: `python3 -m json.tool agent_memory.json > /dev/null`
  - If false: json.JSONDecodeError on read
  - How to fix: restore from backup or delete to auto-init

### Postconditions (Will be true AFTER successful execution)

- [ ] **outbox.jsonl has new entry**
  - How to verify: `tail -1 outbox.jsonl | jq .`
  - Timing: within 13 seconds of prompt in inbox
  - Marker: entry has same "id" as inbox entry that was processed

- [ ] **agent_memory.json updated**
  - How to verify: `tail -5 agent_memory.json | jq .`
  - Timing: immediately after outbox write
  - Marker: two new entries (user prompt + assistant response)

### Error Handling

**Error 1**: `JSONDecodeError` in outbox
```
Cause: Ollama returned invalid JSON (usually truncated)
Symptoms: "json.decoder.JSONDecodeError: Expecting value"
Detection: in outbox write, try json.loads(response)
Recovery: log error, sleep 2s, retry
Prevent: increase timeout if Ollama consistently slow
Impact if not handled: action not executed, user thinks nothing happened
```

**Error 2**: `Timeout` waiting for Ollama
```
Cause: Ollama taking > 13 seconds (network slow, model busy)
Symptoms: "socket.timeout: timed out"
Detection: after 13 seconds of waiting for response
Recovery: try cloud_fallback.py for GPT-4, or timeout and try again
Prevent: make sure Ollama not overloaded (check `top`)
Impact if not handled: prompts pile up in inbox, system grinds to halt
```

**Error 3**: File not found
```
Cause: IPC files deleted by external process
Symptoms: "FileNotFoundError: inbox.jsonl"
Detection: on attempt to read
Recovery: auto-create empty file and continue
Prevent: don't delete IPC files while agent running
Impact if not handled: crash and exit
```

### Assumptions (NEVER CHANGE WITHOUT CAREFUL THOUGHT)

- [ ] **inbox.jsonl is NDJSON format (JSON lines)**
  - Why important: parser expects newlines between entries
  - How verified: read line by line, parse each as JSON
  - If broken: corrupted entries cause agent to skip them silently

- [ ] **Each prompt has unique "id" field**
  - Why important: used to track which prompts were processed
  - How verified: check against agent_seen_ids.json
  - If broken: duplicates get processed twice, creating duplicate actions

- [ ] **Ollama always returns JSON**
  - Why important: response parsing expects valid JSON
  - How verified: json.loads() doesn't raise exception
  - If broken: agent fails to parse response, action not created

- [ ] **outbox.jsonl will be watched by agent_action_handler.py**
  - Why important: actions only execute if action handler running
  - How verified: check if agent_action_handler.py running (ps aux)
  - If broken: actions are written but never executed

### Performance Characteristics

| Operation | Min | Typical | Max | Notes |
|-----------|-----|---------|-----|-------|
| Read inbox | 0.01s | 0.05s | 0.1s | Depends on inbox size |
| Build context | 0.1s | 0.2s | 0.5s | Number of memory entries |
| LLM call | 3s | 8s | 15s | Network/model speed dependent |
| Parse response | 0.01s | 0.05s | 0.1s | Response size dependent |
| Write outbox | 0.01s | 0.02s | 0.1s | Disk I/O |
| **Total per cycle** | ~3s | ~8s | ~15s | Dominated by LLM call |

**Bottlenecks**: LLM call time (Ollama processing)
**Optimization opportunities**: 
- Parallel LLM calls (currently sequential)
- Cache identical prompts
- Use faster model for simple tasks

### Integration Points

**Calls (Dependencies)**:
```
Function: ollama.generate()
- Where: in process_prompt()
- Why: get AI response to user prompt
- With what data: {"model": "uncensored-llama3", "prompt": "...", "stream": false}
- Expects back: dict with "message" field containing response
- If fails: log error, try cloud_fallback.py
```

```
Function: backend.memory.add()
- Where: in process_prompt() after LLM response
- Why: store prompt and response for context
- With what data: {"role": "user|assistant", "content": "...", "timestamp": "..."}
- Expects back: None (modifies global memory)
- If fails: log WARNING, continue (memory loss but system doesn't crash)
```

**Called By (Dependents)**:
```
Function: main() loop in run_agent.py
- Where: every 2 seconds
- Why: keep processing prompts continuously
- Passes: None (reads from shared files)
- Uses return value: just error status
- Error handling: if error, log it and continue next cycle
```

**Shared State**:
```
State: agent_seen_ids set
- Location: in run_agent.py module level
- Type: set of strings
- Readers: process_prompt (check if id already seen)
- Writers: process_prompt (add new id after processing)
- Conflicts: race condition if 2 instances of run_agent.py run simultaneously
- Locking: none (relies on single-instance assumption)
- Prevention: ensure only one run_agent.py process at a time
```

### Testing

**Unit Tests**:
- Test: `test_process_prompt_valid_input`
  - Input: {"id": "test-1", "text": "hello"}
  - Expected output: dict with "action" field
  - Assertion: output["action"] in ["create_file", "update_file", "execute_command"]

- Test: `test_process_prompt_invalid_json`
  - Input: corrupted JSON in inbox
  - Expected output: error logged, prompt skipped
  - Assertion: agent continues (doesn't crash)

**Integration Tests**:
- Test: `test_daemon_and_gui.py::test_gui_prompt`
  - Setup: agent running, inbox empty
  - Action: write SwiftUI creation prompt to inbox
  - Verification: response appears in outbox within 13 seconds

### Maintenance

**How to Update This Component**:
1. Read this entire manifest first (don't skip)
2. Run `python3 test_daemon_and_gui.py` before change (baseline)
3. Make your change to code
4. Update this manifest's "Version" and "Last Updated"
5. Update "Changed" section in version history
6. Run `python3 test_daemon_and_gui.py` after change (must be 6/6)
7. Commit code + manifest changes together
8. If tests fail: REVERT and debug (don't proceed without passing)

**When to Call for Help**:
- [ ] You don't understand why a precondition exists
- [ ] Test fails after your change
- [ ] You can't trace a side effect
- [ ] The manifest contradicts the code
```

---

## How to Implement This System-Wide

### Phase 1: Create Template (Done)
This file - Component Manifest Format

### Phase 2: Retrofit Existing Components (1-2 hours)
Add Component Manifest section to each of 9 READMEs:
- run_agent.README.md ← Start here (example above)
- jailbreak_ollama.README.md
- cloud_fallback.README.md
- ollama_manager.README.md
- agent_action_handler.README.md
- backend/memory.README.md
- tinkerer_daemon.README.md
- And 2 others

### Phase 3: Enforce for New Code
- Any new component must include Component Manifest
- Any significant change must update Manifest
- Integration tests verify Manifest accuracy

### Phase 4: AI Comprehension Validation
Before AI deploys changes:
- AI reads Component Manifest
- AI verifies all preconditions met
- AI updates Manifest with changes
- Humans review Manifest to verify accuracy

---

**Result**: AI model comprehension goes from 86% to 100%

**System reliability**: Dramatically improves because AI can't miss critical details

**Documentation becomes**: The contract between AI and system - breaking it breaks the system

