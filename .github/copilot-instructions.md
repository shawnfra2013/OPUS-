# Copilot Instructions for Hungry (2026-02-02)

## Updates
- **Polling Mechanism**: Optimized to read only new lines from `outbox.jsonl` to improve performance and reduce file I/O overhead.
- **Error Handling**: Enhanced in `agent_gui.py` to log suppressed exceptions and provide detailed error messages.

## Big Picture Architecture
- **Two main runtimes:**
  - Python agent backend ([run_agent.py](run_agent.py))
  - VS Code extension + GUI ([local-agent-vscode/src/](local-agent-vscode/src/))
- **Communication:** NDJSON over files in [local-agent-vscode/ipc/](local-agent-vscode/ipc/)
- **Model:** Ollama (model: `uncensored-llama3`), see [uncensored.Modelfile](uncensored.Modelfile)
- **Tinkerer Daemon:** A self-improvement process ([tinkerer_daemon.py](tinkerer_daemon.py)) that analyzes system state, generates daily improvement proposals, and updates documentation.

## Data Flow & Integration
- Extension writes prompts to [local-agent-vscode/ipc/inbox.jsonl](local-agent-vscode/ipc/inbox.jsonl)
- Backend reads inbox, calls Ollama via [jailbreak_ollama.py](jailbreak_ollama.py), writes responses to [local-agent-vscode/ipc/outbox.jsonl](local-agent-vscode/ipc/outbox.jsonl)
- Agent memory: [local-agent-vscode/ipc/agent_memory.json](local-agent-vscode/ipc/agent_memory.json) (see `AgentMemory` in [run_agent.py](run_agent.py))
- **LLM Fallback Mechanism:**
  - Primary: Ollama (local uncensored-llama3 model)
  - Secondary: OpenAI GPT-4
  - Tertiary: Anthropic Claude 3.5
  - See [cloud_fallback.README.md](cloud_fallback.README.md) for details.
- **No direct process calls** between extension and backend—use IPC files only

## Key Components
- [run_agent.py](run_agent.py): Main backend loop, agent memory, IPC
- [agent_api.py](agent_api.py): FastAPI control (start/stop/status/resource focus)
- [agent_gui.py](agent_gui.py): Tkinter GUI (separate from VS Code webview)
- [local-agent-vscode/src/agentService.ts](local-agent-vscode/src/agentService.ts): Extension IPC
- [local-agent-vscode/src/webviewPanel.ts](local-agent-vscode/src/webviewPanel.ts): Webview streaming
- [jailbreak_ollama.py](jailbreak_ollama.py): Prompt overrides for LLM
- [shell-wrapper/](shell-wrapper/): CLI integration (see [shell-wrapper/README.md](shell-wrapper/README.md))
- [agent_action_handler.py](agent_action_handler.py): Executes agent-requested actions atomically, logs every action and error, and maintains an audit trail. Filters out demo/template actions unless explicitly requested.
- [tinkerer_daemon.py](tinkerer_daemon.py): Background process for self-improvement, journaling, and system advancement.
- [ollama_manager.py](ollama_manager.py): Manages Ollama runtime, health checks, and fallback to cloud LLMs.

## Developer Workflows
- **Full stack launcher:** Run [AI-](AI-) to start Ollama, backend, extension watch, and GUI.
- **Manual sequence:**
  1. Start Ollama with `uncensored-llama3`
  2. Run [run_agent.py](run_agent.py)
  3. `npm run watch` in [local-agent-vscode/](local-agent-vscode/)
  4. Run [agent_gui.py](agent_gui.py)
- **Testing:** Always run `python3 test_daemon_and_gui.py` (expect `6/6 PASS`).
- **Do NOT use** [setup_hungry.sh](setup_hungry.sh) (disabled).

## Project Conventions & Patterns
- **Strict prompt routing:** Backend only processes new prompts from GUI/extension, never repeats or appends old prompts.
- **Action filtering:** Only actions directly related to the user's prompt are executed. Demo/template actions (e.g., hello, greeting, etc.) are filtered out unless explicitly requested.
- **No meaningless file creation:** Prevents redundant or irrelevant outputs and ensures live, context-aware agent operation.
- **Self-improvement:** The tinkerer daemon runs every 5 minutes, analyzes system state, and generates daily proposals for advancement, updating documentation with reasoning and timestamps.
- **Health monitoring:** Critical processes are monitored and auto-restarted if needed.

## Critical AI Agent Rules
- **Never lose information in summaries.**
- **Never modify code without updating documentation.**
- **Never assume what code does—read and run it.**
- **Never proceed without understanding dependencies.**
- **Never skip the integration test.**
- **If docs/code disagree, verify with tests and update both.**

## Examples
- **Backend feature:** Update [run_agent.py](run_agent.py) and ensure new fields are written to [local-agent-vscode/ipc/outbox.jsonl](local-agent-vscode/ipc/outbox.jsonl).
- **Extension change:** Edit [local-agent-vscode/src/agentService.ts](local-agent-vscode/src/agentService.ts) and/or [local-agent-vscode/src/webviewPanel.ts](local-agent-vscode/src/webviewPanel.ts).
- **Shell wrapper:** See [shell-wrapper/README.md](shell-wrapper/README.md) for CLI usage.
- **LLM Fallback:** Update [cloud_fallback.py](cloud_fallback.py) to ensure seamless transition between Ollama, OpenAI, and Anthropic.

---
If any section is unclear, incomplete, or missing details, please provide feedback for further refinement. See [AI_COMPREHENSION_GUIDE.md](AI_COMPREHENSION_GUIDE.md) for the full checklist and rules for AI agents.
