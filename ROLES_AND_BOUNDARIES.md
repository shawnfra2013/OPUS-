# Roles and Boundaries - Hungry System Authority

## Principle
**Each component has ONE clear responsibility. No overreach. No ambiguity.**

---

## 1. BACKEND AGENT (run_agent.py)

### Authority
- **OWNS**: Agent logic, model calls, memory management, decision-making
- **READS FROM**: `ipc/inbox.jsonl` (prompts from extension/shell)
- **WRITES TO**: `ipc/outbox.jsonl` (responses)
- **MANAGES**: `ipc/agent_memory.json` (persistent memory, decisions history)

### Responsibilities
✅ Read next prompt from inbox
✅ Call Ollama via jailbreak_ollama.py
✅ Generate response
✅ Write response to outbox with proper NDJSON format
✅ Update agent memory
✅ Record all decisions for training

### CANNOT DO
❌ Directly execute user's computer (system calls)
❌ Modify files outside ipc/
❌ Bypass jailbreak_ollama.py wrapper
❌ Start/stop itself (controlled by API)
❌ Read from outbox (reads only from inbox)
❌ Write to inbox (reads only)
❌ Make approval decisions (leaves JSON gate decision to extension/GUI)

### Depends On
- `jailbreak_ollama.py` — Prompt wrapping
- Ollama service running with `uncensored-llama3` model
- `ipc/inbox.jsonl` exists and readable

### Controlled By
- `agent_api.py` (start/stop/status)
- `STOP_AGENT` flag in root

---

## 2. EXTENSION (local-agent-vscode/src/)

### Authority
- **OWNS**: User interface in VS Code, prompt submission, response display
- **WRITES TO**: `ipc/inbox.jsonl` (prompts)
- **READS FROM**: `ipc/outbox.jsonl` (responses)
- **MANAGES**: Webview streaming, user interactions

### Responsibilities
✅ Show user the chat interface
✅ Capture user prompt
✅ Format prompt (timestamp, id) and write to inbox
✅ Poll outbox for responses
✅ Stream responses to webview
✅ Display agent responses to user
✅ Show approval/rejection UI for agent actions

### CANNOT DO
❌ Call Ollama directly (goes through backend only)
❌ Execute code/commands (backend handles execution)
❌ Modify agent memory directly
❌ Approve actions without user interaction
❌ Bypass JSON gates
❌ Write to outbox (writes only to inbox)
❌ Start/stop backend (API controls that)

### Depends On
- Backend running
- `ipc/inbox.jsonl` writable
- `ipc/outbox.jsonl` readable
- User interaction

### Controls
- What the user sees
- When actions get user approval

---

## 3. AGENT GUI (agent_gui.py)

### Authority
- **OWNS**: Tkinter GUI, direct user interaction for testing/demo
- **CALLS**: Ollama directly (for quick responses, independent of backend)
- **READS FROM**: `ipc/agent_memory.json` (reference only)

### Responsibilities
✅ Provide Tkinter interface for testing
✅ Call Ollama directly (separate from backend loop)
✅ Display memory for reference
✅ Show recent actions
✅ Allow quick model testing

### CANNOT DO
❌ Make backend decisions
❌ Write to inbox/outbox (talks directly to Ollama, not through IPC)
❌ Modify agent_memory.json directly (read-only)
❌ Approve actions for backend (GUI is separate)
❌ Start/stop backend
❌ Control resources (RESOURCE_FOCUS flag)

### Depends On
- Ollama running
- `ipc/agent_memory.json` readable
- Tkinter available

### Is Independent From
- Backend loop
- Extension
- Agent API
- Can run simultaneously without conflict

---

## 4. AGENT API (agent_api.py)

### Authority
- **OWNS**: System control (start/stop/status)
- **CONTROLS**: `STOP_AGENT` flag (root level)
- **CONTROLS**: `RESOURCE_FOCUS` flag (root level)
- **REPORTS STATUS**: Agent running/stopped, last activity

### Responsibilities
✅ Start backend
✅ Stop backend  
✅ Report backend status
✅ Handle RESOURCE_FOCUS flag
✅ Provide HTTP control surface

### CANNOT DO
❌ Make decisions about what agent does
❌ Modify prompts
❌ Approve actions
❌ Access agent memory directly
❌ Call Ollama (only backend does that)
❌ Modify inbox/outbox directly
❌ Bypass agent logic

### Controls
- Backend lifecycle

### Depends On
- Root `STOP_AGENT` flag
- Root `RESOURCE_FOCUS` flag
- Backend implementation

---

## 5. JAILBREAK WRAPPER (jailbreak_ollama.py)

### Authority
- **OWNS**: Prompt wrapping and preprocessing
- **CALLED BY**: Backend only

### Responsibilities
✅ Wrap user prompts with safety jailbreak
✅ Apply model overrides
✅ Return wrapped prompt to backend

### CANNOT DO
❌ Make decisions (only wraps prompts)
❌ Call Ollama (backend calls after wrapping)
❌ Write to IPC files
❌ Approve/reject anything
❌ Access agent memory

### Called By
- `run_agent.py` only

### Controls
- How prompts are formatted before Ollama

---

## 6. SHELL WRAPPER (shell-wrapper/)

### Authority
- **OWNS**: CLI access from terminal
- **WRITES TO**: `local-agent-vscode/ipc/inbox.jsonl` (SAME as extension!)
- **READS FROM**: `local-agent-vscode/ipc/outbox.jsonl` (SAME as extension!)

### Responsibilities
✅ Provide `-` command in shell for quick agent access
✅ Write prompts to same inbox as extension
✅ Read from same outbox as extension
✅ Simple alternative to opening VS Code

### CANNOT DO
❌ Access backend directly
❌ Modify agent memory
❌ Approve actions (must use VS Code for approvals)
❌ Call Ollama

### Uses Same Door
- Uses SAME IPC as extension (`local-agent-vscode/ipc/`)
- Same agent loop
- Same responses
- Just different UI (CLI vs webview)

---

## Authority Chain (JSON Admin Pattern)

```
USER INPUT
    ↓
Extension/GUI captures input
    ↓
JSON GATE: Is input valid? (create_gate in JSON)
    ↓
Backend receives prompt
    ↓
Backend calls Ollama (via jailbreak_ollama.py)
    ↓
Backend gets response
    ↓
Backend writes to outbox
    ↓
JSON GATE: Should this be approved? (check_requirement in JSON)
    ↓
User sees action + approval request
    ↓
JSON GATE: User approved? (request_user_approval in JSON)
    ↓
IF approved: Extension shows result, backend implements
IF rejected: JSON records decision, model learns not to do this
```

---

## File Ownership

### Backend Owns
```
ipc/inbox.jsonl       - READS (primary consumer)
ipc/outbox.jsonl      - WRITES (primary producer)
ipc/agent_memory.json - MANAGES (reads + writes)
```

### Extension Owns
```
ipc/inbox.jsonl       - WRITES (user prompts)
ipc/outbox.jsonl      - READS (agent responses)
Webview UI            - MANAGES (displays everything)
```

### GUI Owns
```
ipc/agent_memory.json - READS (reference only)
Tkinter UI            - MANAGES
Direct Ollama calls   - MANAGES
```

### API Owns
```
STOP_AGENT flag       - MANAGES (root level)
RESOURCE_FOCUS flag   - MANAGES (root level)
Status reporting      - MANAGES
```

### Shell Wrapper Shares
```
local-agent-vscode/ipc/inbox.jsonl  - WRITES (same as extension)
local-agent-vscode/ipc/outbox.jsonl - READS (same as extension)
(Uses SAME IPC as extension - no separate door)
```

---

## No Overreach Rules

### Backend Cannot
```python
# ❌ WRONG - Backend executing without gate
subprocess.run("rm -rf /")  

# ✅ RIGHT - Backend asks extension to show action to user
gate.create_gate("execute_command", ...)
outbox.write({"action_type": "execute_command", ...})
# Extension shows user, user approves via JSON
```

### Extension Cannot
```python
# ❌ WRONG - Extension calling model
response = ollama.generate("prompt")

# ✅ RIGHT - Extension asking backend
inbox.write({"text": "prompt"})
response = outbox.read()
```

### API Cannot
```python
# ❌ WRONG - API making decisions
memory.approve_action(action)

# ✅ RIGHT - API just reporting status
return get_backend_status()
```

### GUI Cannot
```python
# ❌ WRONG - GUI modifying real memory
memory["training_data"].append(decision)

# ✅ RIGHT - GUI reading memory for display
display_memory(memory)
```

---

## Communication Matrix

|  From  | To  | Method | What |
|--------|-----|--------|------|
| User | Extension | UI | Type prompt |
| User | Shell CLI | `-` command | Type prompt (same inbox!) |
| Extension/CLI | Backend | `ipc/inbox.jsonl` | Submit prompt |
| Backend | Ollama | HTTP API | Request completion |
| Ollama | Backend | HTTP Response | Return generation |
| Backend | Extension/CLI | `ipc/outbox.jsonl` | Write response |
| Extension | User | Webview | Display response |
| CLI | User | Terminal | Display response |
| Backend | Memory | Direct file I/O | Record decision |
| API | Backend | Flag + subprocess | Control lifecycle |
| GUI | Ollama | HTTP API | Direct testing (independent) |
| GUI | Memory | File read | Display reference |

**Rule**: Communication goes through specified channels only. No direct calls except where explicitly allowed (like GUI→Ollama for testing).

---

## Conflict Resolution

When two components might do the same thing:

### Issue: Backend writes to outbox, Extension reads from outbox
**Solution**: Backend is primary producer (owns writing). Extension is primary consumer (owns reading). No conflict.

### Issue: GUI calls Ollama, Backend calls Ollama
**Solution**: 
- GUI calls for quick testing (independent, doesn't affect main loop)
- Backend calls for actual agent decisions (primary path)
- No conflict because they're separate purposes

### Issue: Shell wrapper and Extension both want to submit prompts
**Solution**: 
- Both use SAME inbox: `local-agent-vscode/ipc/inbox.jsonl`
- Both read SAME outbox: `local-agent-vscode/ipc/outbox.jsonl`
- CLI is just alternative UI - same backend, same responses
- Use CLI for quick questions, use extension for approvals/actions

### Issue: API starts backend, something else tries to start it
**Solution**: API is sole authority for start/stop. All start/stop requests go through API only.

---

## Decision Authority (JSON Gates)

| Decision | Authority | Records In |
|----------|-----------|------------|
| Run code generation? | JSON gate + Backend | `ipc/agent_memory.json` |
| User approve action? | User via Extension | `ipc/agent_memory.json` |
| Implement approved action? | JSON gate + Backend | `ipc/agent_memory.json` |
| Start/stop agent? | API (via flags) | Logs |
| What to display user? | Extension (UI) | Webview state |
| Wrap prompt safely? | jailbreak_ollama.py | Via returned prompt |
| Train model? | Separate trainer | `ipc/agent_memory.json` approval data |

---

## Clear Ownership Summary

```
┌─────────────────────────────────────────────────────────┐
│                    BACKEND AGENT                         │
│  Owns: Agent logic, model calls, memory, decisions      │
│  In:   ipc/inbox.jsonl                                  │
│  Out:  ipc/outbox.jsonl                                 │
│  Mem:  ipc/agent_memory.json                            │
└─────────────────────────────────────────────────────────┘
              ↑                                    ↓
              │                                    │
     ┌────────┴────────┐              ┌──────────┴──────────┐
     │  EXTENSION      │              │  IPC FILES          │
     │  Owns: UI, UX   │              │  (Communication)    │
     │  In:  inbox     │              └─────────────────────┘
     │  Out: outbox    │                         ↑
     └────────────────┘                          │
              ↑                      ┌────────────┴───────────┐
              │                      │                        │
              └──────────┬───────────┘                   ┌─────┴──────┐
                         │                              │  AGENT API │
                         │                              │  Owns:     │
                   ┌─────┴────┐                        │  start/    │
                   │    GUI    │                        │  stop/     │
                   │  (test)   │                        │  status    │
                   │  Direct   │                        └────────────┘
                   │  Ollama   │
                   └───────────┘
```

---

## Verification Checklist

Before changes, ask:

1. **Is this component's responsibility?**
   - [ ] Does it match the "Responsibilities" list?
   - [ ] Does the CANNOT DO list say it's forbidden?

2. **Is it the right channel?**
   - [ ] Using ipc/inbox.jsonl, ipc/outbox.jsonl, flags, or direct API calls?
   - [ ] Not creating new back-channels?

3. **Is authority clear?**
   - [ ] Only one component owns this decision?
   - [ ] No other component tries to do the same thing?

4. **Is it recorded?**
   - [ ] Decisions go through JSON gate?
   - [ ] Memory records this?
   - [ ] Audit trail exists?

5. **Is overreach impossible?**
   - [ ] Component can't bypass the system?
   - [ ] Can't skip JSON gate?
   - [ ] Can't execute without approval?

---

## Implementation Rule

**If you can't answer all 5 verification questions with YES, redesign it.**

