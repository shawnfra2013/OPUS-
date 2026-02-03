# OPUS Agent Architecture (2026-02-03)

## Overview
OPUS is an autonomous AI agent system with a Python backend and Tkinter GUI.

## Core Components (KEEP)

```
┌─────────────────────────────────────────────────────────────┐
│                    WORKING ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────────┐         ┌──────────────────────────────┐ │
│   │ agent_gui.py │ ──────▶│   inbox.jsonl (user prompts) │ │
│   │  (Tkinter)   │         └──────────────────────────────┘ │
│   └──────────────┘                      │                    │
│          ▲                              ▼                    │
│          │                   ┌──────────────────┐            │
│          │                   │   run_agent.py   │            │
│          │                   │   (main loop)    │            │
│          │                   └────────┬─────────┘            │
│          │                            │                      │
│          │              ┌─────────────┼─────────────┐        │
│          │              ▼             ▼             ▼        │
│          │    ┌─────────────┐ ┌─────────────┐ ┌──────────┐   │
│          │    │jailbreak_   │ │backend/     │ │agent_    │   │
│          │    │ollama.py    │ │memory.py    │ │action_   │   │
│          │    │(LLM calls)  │ │(context)    │ │handler.py│   │
│          │    └─────────────┘ └─────────────┘ └──────────┘   │
│          │                            │                      │
│          │                            ▼                      │
│   ┌──────────────────────────────────────────────────┐       │
│   │              outbox.jsonl (agent responses)      │       │
│   └──────────────────────────────────────────────────┘       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## File Inventory

### Core Files (7 files, ~1500 lines)
| File | Lines | Purpose |
|------|-------|---------|
| `run_agent.py` | 571 | Main agent loop - reads inbox, calls LLM, writes outbox |
| `agent_gui.py` | 315 | Tkinter GUI for user interaction |
| `jailbreak_ollama.py` | 112 | LLM interface with DAN prompts |
| `agent_action_handler.py` | 297 | Executes file/command actions |
| `ollama_manager.py` | ~100 | Ollama health checks and startup |
| `backend/memory.py` | 123 | Conversation memory storage |
| `macos_approver.py` | ~50 | Auto-approve actions (dialogs disabled) |

### Support Files (used by core)
| File | Purpose |
|------|---------|
| `api_gateway.py` | External API calls (GitHub, HuggingFace) |
| `backend/refinement.py` | Prompt refinement (disabled) |
| `cloud_fallback.py` | Cloud LLM fallback (OpenAI, Anthropic) |

### Optional/Advanced Features (dormant)
| File | Purpose | Status |
|------|---------|--------|
| `tinkerer_daemon.py` | Self-improvement daemon | Not running |
| `model_trainer.py` | Fine-tune models | Not running |
| `approval_workflow.py` | Approval dialogs | Disabled |
| `code_templates.py` | Code generation templates | Not integrated |
| `code_review_enforcer.py` | Code review gates | Not integrated |

## Data Flow

1. **User Input**: GUI writes JSON to `inbox.jsonl`
2. **Processing**: `run_agent.py` reads inbox, calls Ollama via `jailbreak_ollama.py`
3. **Memory**: Context stored in `backend/memory.py`
4. **Actions**: File/command execution via `agent_action_handler.py`
5. **Output**: Response written to `outbox.jsonl`
6. **Display**: GUI polls outbox, displays response

## IPC Files
```
local-agent-vscode/ipc/
├── inbox.jsonl      # User prompts (GUI writes, agent reads)
├── outbox.jsonl     # Agent responses (agent writes, GUI reads)
└── agent_memory.json # Persistent conversation memory
```

## How to Run

```bash
# Start Ollama
ollama serve &

# Start agent backend
python3 run_agent.py &

# Start GUI
python3 agent_gui.py &
```

Or use the orchestrator scripts:
- `./AI-` - Start all
- `./AI-S` - Stop all
- `./AI-R` - Restart all

## Testing

```bash
# Integration test
python3 test_daemon_and_gui.py

# Syntax check all core files
python3 -m py_compile run_agent.py agent_gui.py jailbreak_ollama.py
```

## Archived Files
Legacy and unused code moved to `/archive/`:
- `archive/legacy/` - Broken files
- `archive/demos/` - Demo/test files
- `archive/unused/` - Alternative implementations

---
*Last updated: 2026-02-03*
