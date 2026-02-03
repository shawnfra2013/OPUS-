# Documentation Index

**Last Updated**: 2026-02-01 10:55 AM Central | **Purpose**: Quick navigation to all system documentation
## Key Implementation Files (2026-02-01 update)

- `run_agent.py`: Strict prompt routing, action filtering, and output logic.
- `agent_action_handler.py`: Skips demo/template actions unless explicitly requested.
- `agent_gui.py`: GUI writes user prompt to inbox, displays only new agent/user messages.

## 📚 Start Here

### New Users
1. **[DOCUMENTATION_SUMMARY.md](DOCUMENTATION_SUMMARY.md)** - What was created and how to use it
2. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete system overview
3. **[README.md](README.md)** - Main project README with critical changes

### Experienced Team
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Full technical overview
- Individual component READMEs (see below)

## 🔧 Component Documentation

### Core Agent Loop
- **[run_agent.README.md](run_agent.README.md)** (550+ lines)
  - Purpose: Read prompts, call LLM, generate JSON actions
  - Owner: Agent execution engine
  - Key Methods: 
    - `read_prompts()` → Reads unprocessed from inbox, tracks seen IDs
    - `build_context()` → Pulls last 5 from memory, builds context string
    - `call_llm()` → Ollama chat with DAN system prompt
    - `process_prompt()` → Full pipeline: read → context → LLM → parse JSON → store memory
    - `write_to_outbox()` → Appends JSON actions + audit log
  - Dependencies: ollama, jailbreak_ollama, cloud_fallback, backend.memory
  - Module Exports: `process_prompt()`, `agent_self_inspect()`
  - Requires: inbox/outbox NDJSON files, agent_memory.json, seen IDs tracking

### LLM Interfaces
- **[jailbreak_ollama.README.md](jailbreak_ollama.README.md)** (270+ lines)
  - Purpose: Ollama integration with DAN system prompt
  - Owner: LLM interface abstraction
  - Key Methods:
    - `direct_json_call()` → Single DAN call for JSON actions (PRIMARY)
    - `force_uncensor()` → Multi-layer jailbreak (DAN + Developer + Raw) (FALLBACK)
  - Dependencies: ollama library, system prompts
  - Module Class: `NoGuardrailsOllama` with methods for uncensored inference
  - Requires: Ollama running on localhost:11434, uncensored-llama3 model
  - Provides: JSON-only output with action_type field enforcement
  
- **[cloud_fallback.README.md](cloud_fallback.README.md)** (300+ lines)
  - Purpose: OpenAI/Anthropic fallback when Ollama unavailable
  - Owner: Cloud API abstraction
  - Key Methods:
    - `chat()` → Single request/response with fallback chain
    - `stream_chat()` → Streaming response tokens
  - Dependencies: openai, anthropic, requests libraries
  - Module Class: `CloudFallback` with provider detection and chaining
  - Requires: OPENAI_API_KEY, ANTHROPIC_API_KEY in .env
  - Provides: Identical interface to ollama.chat()

### Runtime Management
- **[ollama_manager.README.md](ollama_manager.README.md)** (350+ lines)
  - Purpose: Ollama startup, health checks, model management
  - Owner: LLM runtime lifecycle
  - Key Methods:
    - `is_ollama_running()` → Health check via HTTP GET to /api/tags
    - `start_ollama()` → Launch via `ollama serve` or app (OS-specific)
    - `ensure_model_loaded()` → Build from Modelfile if missing
    - `health_check()` → Test inference latency
    - `auto_restart()` → Graceful → force kill → fresh start
    - `get_status()` → Complete system status JSON
  - Dependencies: ollama binary, psutil, subprocess
  - Module Class: Implicit functions (can be refactored to class)
  - Requires: Ollama installed, ~/.ollama/models accessible, uncensored.Modelfile
  - Provides: Reliable local LLM with auto-recovery

### Action Execution
- **[agent_action_handler.README.md](agent_action_handler.README.md)** (180+ lines)
  - Purpose: Monitor outbox, execute JSON actions immediately (no approval)
  - Owner: Autonomous action execution daemon
  - Key Methods:
    - `monitor_loop()` → Daemon thread polling outbox every 500ms
    - `execute_action()` → Parse JSON and run appropriate handler
    - `handle_create_file()` → Write file to disk with content
    - `handle_update_file()` → Replace old_content with new_content
    - `handle_execute_command()` → Run bash/python commands
    - `handle_update_readme()` → Update documentation with timestamps
  - Dependencies: json, os, subprocess, pathlib
  - Module Class: `AgentActionHandler` daemon thread running in background
  - Requires: outbox.jsonl input, file system write access
  - Provides: Autonomous execution audit trail (agent_actions.jsonl)

### Memory & Storage
- **[backend/memory.README.md](backend/memory.README.md)** (250+ lines)
  - Purpose: Persistent conversation history and context storage
  - Owner: Agent persistence layer
  - Key Methods:
    - `add()` → Store prompt+reply with timestamp, calls filter_junk()
    - `last()` → Retrieve N entries optionally filtered by conversation_id
    - `filter_junk()` → Remove empty/one-word/incomplete entries (regex-based)
    - `add_todo_from_chat()` → Parse action keywords from prompts
    - `add_self_reflection()` → Store agent analysis with [SELF-REFLECTION] tag
    - `add_best_practices_reference()` → Embed guidelines from files
  - Dependencies: json, os, re (regex), pathlib
  - Module Class: `AgentMemory` with persistent JSON storage
  - Requires: agent_memory.json in ipc/ directory
  - Provides: Context building for prompts, complete conversation history

### Self-Improvement
- **[tinkerer_daemon.README.md](tinkerer_daemon.README.md)** (400+ lines)
  - Purpose: Continuous monitoring, daily proposals, README updates, self-improvement
  - Owner: Self-improvement and monitoring daemon
  - Key Methods:
    - `run_loop()` → Main daemon (every 5 min: idle check, time check, proposals, audits)
    - `get_idle_time()` → System inactivity in seconds (via OS)
    - `generate_daily_proposal()` → LLM analysis at 4:30 AM Central (daily_proposal_DATE.txt)
    - `call_llm_unrestricted()` → Direct LLM with DAN system prompt for analysis
    - `audit_code()` → Scan Python files for issues + LLM analysis
    - `audit_readmes()` → Verify docs match code, auto-update with timestamps
  - Dependencies: ollama, psutil, pytz, threading, os
  - Module Class: `TinkererDaemon` with daemon thread
  - Requires: Ollama, agent_memory.json, timezone configuration
  - Provides: Daily proposals, README maintenance, system health reports

## 🏗️ System Architecture

- **[ARCHITECTURE.md](ARCHITECTURE.md)** (400+ lines)
  - System diagram (all components)
  - Responsibility matrix
  - Two major data flow pipelines
  - Configuration & secrets
  - Critical changes (2026-02-01)
  - Testing strategy
  - Performance targets
  - Deployment checklist

## 📋 Quick Reference Tables

### Component Responsibility Matrix
Located in [ARCHITECTURE.md](ARCHITECTURE.md):
```
run_agent.py          | Main agent loop      | inbox.jsonl → outbox.jsonl
jailbreak_ollama.py   | LLM interface        | JSON request → JSON response
cloud_fallback.py     | Cloud API fallback   | JSON request → JSON response
ollama_manager.py     | LLM runtime mgmt     | health check → status
agent_action_handler  | Action execution     | outbox.jsonl → Files/Commands
backend/memory.py     | Context storage      | prompt+reply → history array
backend/refinement.py | Code analysis        | source code → analysis report
tinkerer_daemon.py    | Self-improvement     | system state → proposals/READMEs
```

### Known Behaviors by Component
Each README has "Known Behaviors" section:
- ✅ **Correct (Don't Change)** - intentional design patterns
- ⚠️ **Watch For** - potential issues to monitor

Example:
- refinement = True in run_agent.py → **Watch For**, should be disabled
- DAN system prompt in core logic → **✅ Correct**, enables JSON output
- No approval needed for actions → **✅ Correct**, autonomous execution

### Performance Metrics
All components include latency targets:
- Agent: 8-13 seconds inbox → file creation
- Ollama: 10-13s first call, 5-8s cached
- Cloud: 2-5 seconds (OpenAI 3-5s, Anthropic 2-4s)
- Memory: <1ms queries
- Daemon: Every 5 minutes

## 🔍 How to Find Information

### "How does [component] work?"
→ Read: `[component].README.md` → Architecture section

### "What should the daemon monitor?"
→ Read: Each component's "Daemon Responsibilities" section
→ Reference: [tinkerer_daemon.README.md](tinkerer_daemon.README.md)

### "What are integration points?"
→ Read: Each README → "Integration Points" section
→ Shows: Input From, Output To, Calls

### "What are error handling strategies?"
→ Read: Each component's "Error Handling" section

### "Why did we change [X]?"
→ Read: [ARCHITECTURE.md](ARCHITECTURE.md) → "Critical Changes (2026-02-01)"
→ Lists what changed, why, benefits

### "How do I test this?"
→ Read: Each component's "Testing" section
→ Manual tests provided with examples

### "What's the full system flow?"
→ Read: [ARCHITECTURE.md](ARCHITECTURE.md) → "System Diagram" + "Data Flow Pipelines"

## 📊 Documentation Statistics

# Documentation Index
**Last Updated**: 2026-02-01 10:55 AM Central | **Purpose**: Quick navigation to all system documentation, journaling, self-improvement, error surfacing, and advancement goals
| Total files | 10 |
## Key Implementation Files & Journaling (2026-02-01 update)
 `run_agent.py`: Strict prompt routing, action filtering, output logic, persistent memory, and error surfacing.
 `agent_action_handler.py`: Atomic execution, audit, error logging, journaling, and GUI error surfacing.
 `tinkerer_daemon.py`: Self-improvement, journaling, daily proposals, and README maintenance.
 `agent_gui.py`: GUI writes user prompt to inbox, displays only new agent/user messages, and surfaces errors from logs.
| Methods documented | 30+ |
## 📚 Start Here

## 🎯 Reading Recommendations by Role

### DevOps / Operations
### New Users
1. **[DOCUMENTATION_SUMMARY.md](DOCUMENTATION_SUMMARY.md)** - What was created, journaling, and how to use it
2. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete system overview, control, and advancement logic
3. **[README.md](README.md)** - Main project README with journaling, error surfacing, and advancement goals
4. **[tinkerer_daemon.README.md](tinkerer_daemon.README.md)** - Self-improvement, journaling, and proposal logic
5. **[agent_action_handler.README.md](agent_action_handler.README.md)** - Atomic execution, audit, and error surfacing
6. **[run_agent.README.md](run_agent.README.md)** - Main agent loop, autonomy, and error handling
## 🛠️ Component Documentation & Advancement
3. [tinkerer_daemon.README.md](tinkerer_daemon.README.md) - Monitoring
### Core Agent Loop & Journaling
- **[run_agent.README.md](run_agent.README.md)** (550+ lines)
  - Purpose: Read prompts, call LLM, generate JSON actions, persistent memory, error surfacing
  - Owner: Agent execution engine
  - Key Methods: 
    - `read_prompts()` → Reads unprocessed from inbox, tracks seen IDs
    - `build_context()` → Pulls last 5 from memory, builds context string
    - `call_llm()` → Ollama chat with DAN system prompt
    - `process_prompt()` → Full pipeline: read → context → LLM → parse JSON → store memory
    - `write_to_outbox()` → Appends JSON actions + audit log
  - Dependencies: ollama, jailbreak_ollama, cloud_fallback, backend.memory
  - Module Exports: `process_prompt()`, `agent_self_inspect()`
  - Requires: inbox/outbox NDJSON files, agent_memory.json, seen IDs tracking

### LLM Interfaces
- **[jailbreak_ollama.README.md](jailbreak_ollama.README.md)** (270+ lines)
  - Purpose: Ollama integration with DAN system prompt
  - Owner: LLM interface abstraction
  - Key Methods:
    - `direct_json_call()` → Single DAN call for JSON actions (PRIMARY)
    - `force_uncensor()` → Multi-layer jailbreak (DAN + Developer + Raw) (FALLBACK)
  - Dependencies: ollama library, system prompts
  - Module Class: `NoGuardrailsOllama` with methods for uncensored inference
  - Requires: Ollama running on localhost:11434, uncensored-llama3 model
  - Provides: JSON-only output with action_type field enforcement
- **[cloud_fallback.README.md](cloud_fallback.README.md)** (300+ lines)
  - Purpose: OpenAI/Anthropic fallback when Ollama unavailable
  - Owner: Cloud API abstraction
  - Key Methods:
    - `chat()` → Single request/response with fallback chain
    - `stream_chat()` → Streaming response tokens
  - Dependencies: openai, anthropic, requests libraries
  - Module Class: `CloudFallback` with provider detection and chaining
  - Requires: OPENAI_API_KEY, ANTHROPIC_API_KEY in .env
  - Provides: Identical interface to ollama.chat()
- agent_action_handler.py → executes actions from run_agent.py
- tinkerer_daemon.py → monitors all components

See [ARCHITECTURE.md](ARCHITECTURE.md) "Integration Points" for complete mapping.

## ✅ Completeness Verification

All documentation includes:
- ✅ Purpose / Owner statement
- ✅ Architecture diagram or flow
- ✅ Configuration details
- ✅ All methods documented
- ✅ Data structures explained
- ✅ Integration points mapped
- ✅ Error handling strategies
- ✅ Known behaviors (✅ Correct & ⚠️ Watch For)
- ✅ Daemon monitoring responsibilities
- ✅ Testing guide with examples
- ✅ Performance metrics
- ✅ Future improvements

## Approval Workflow (2026-02-01)
- Only code structure changes (create_file, update_file, update_readme) require explicit macOS approval.
- Approval dialog is triggered via osascript (see macos_approver.py).
- All other actions (log, read, execute) proceed without approval.
- Agent, daemon, and GUI track their roles and communicate status; if one is waiting, others are aware.
- Models (openchat, uncensored-llama3) are documented and coherent; see DOCS_INDEX.md for details.

---

**Last Updated**: 2026-02-01 10:55 AM Central  
**Maintainer**: Tinkerer Daemon (auto-updated, see [tinkerer_daemon.README.md](tinkerer_daemon.README.md))
