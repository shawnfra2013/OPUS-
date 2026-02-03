# Hungry Project: Autonomous Agent System

**Last Updated:** 2026-02-01

## Overview
Hungry is a fully autonomous, self-improving agent system designed for robust, transparent, and continuous operation. It combines a main agent loop, a tinkerer daemon for self-improvement, and a journaling system for full traceability and error visibility.

## Core Components
- **run_agent.py**: Main agent loop. Reads prompts, builds context, calls LLM, generates JSON actions, and maintains persistent memory. Operates autonomously, with all actions and errors logged.
- **agent_action_handler.py**: Executes agent-requested actions atomically, logs every action and error, and maintains an audit trail. Filters out demo/template actions unless explicitly requested.
- **tinkerer_daemon.py**: Background process for self-improvement. Analyzes system state, proposes daily improvements, updates READMEs, and logs all proposals and context analyses.
- **agent_task_runner.py**: Monitors the agent pipeline, manages the prompt queue, and logs agent replies and errors. Extensible with hooks for health checks and anomaly detection.
- **Ollama Manager**: Ensures LLM runtime is always available, manages models, and provides health checks and auto-restart logic.

## Control, Coherence, and Journaling
- **Strict prompt routing**: Only new prompts are processed; no repeats or stale prompts.
- **Persistent memory**: All context and actions are tracked and deduplicated.
- **Error visibility**: All errors and exceptions are logged to `agent_debug.log` and surfaced in the GUI/status bar. No silent failures.
- **Journaling**: All actions, proposals, and errors are logged in persistent files (`agent_actions.jsonl`, `agent_debug.log`, `tinkerer_daemon.log`).
- **Self-improvement**: The tinkerer daemon runs every 5 minutes, analyzes system state, and generates daily proposals for advancement, updating documentation with reasoning and timestamps.
- **Health monitoring**: All critical processes are monitored and auto-restarted if needed.

## Advancement Goal
To become a fully autonomous, self-improving agent system that never fails silently, always surfaces errors, and continuously refines itself through daily proposals, context analysis, and transparent journaling.

## Features & Capabilities
- Autonomous prompt processing and action execution
- Persistent, deduplicated memory and context
- Daily self-improvement proposals and README updates
- Full audit trail of all actions and errors
- Health monitoring and auto-restart for all processes
- Transparent error surfacing in GUI and logs
- Modular, extensible architecture

## Dependencies
- Python 3.10+
- Ollama (local LLM runtime)
- OpenAI/Anthropic API keys for cloud fallback
- Tkinter (for GUI)

## Failsafe & Fallback Logic (2026-02-01)

- If the LLM fails to generate a valid action, the agent uses bulletproof fallback extraction to generate a `create_file` action for any prompt containing a `/tmp` path and content, regardless of phrasing or keyword.
- If a prompt contains a `/tmp` path and content, a `create_file` action is always generated, even if the LLM output is invalid or missing.
- If fallback extraction fails (e.g., `/tmp` path but no content), a forced log entry is written to `/tmp/agent_debug.log` and a status message is sent to the GUI/outbox.
- All fallback failures and extraction attempts are logged to `/tmp/agent_debug.log` and surfaced in the GUI.
- Guarantees: No explicit file creation prompt for `/tmp` is ever ignored or lost; every such prompt results in either file creation or a visible error/status.
- See [FIXES_CHANGELOG_2026_02_01.md](FIXES_CHANGELOG_2026_02_01.md) for implementation details and test plan.

## Recent Updates - 2026-02-02

### Changes
- Installed missing dependencies and type definitions
- Updated tsconfig.json for compatibility
- Addressed module resolution issues

### Next Steps
- Fix code errors and re-test application

## See Also
- [ARCHITECTURE.md](ARCHITECTURE.md): Full system overview
- [DOCS_INDEX.md](DOCS_INDEX.md): Documentation navigation
- [tinkerer_daemon.README.md](tinkerer_daemon.README.md): Self-improvement and journaling
- [agent_action_handler.README.md](agent_action_handler.README.md): Action execution and audit
- [run_agent.README.md](run_agent.README.md): Main agent loop and autonomy

---
### [AUTO-UPDATE LOG]
2026-02-01 (auto): Unified documentation for control, journaling, self-improvement, and advancement goals.
---
### [AUTO-UPDATE LOG]
- 2026-02-01 13:33:22 (auto): Update the README.md with additional information and examples

- 2026-02-01 13:33:22 (auto): Update the README.md with additional information and examples

- 2026-02-01 13:33:22 (auto): Update the README.md with additional information and examples

- 2026-02-01 13:32:40 (auto): Update readme to explain my capabilities

- 2026-02-01 13:32:40 (auto): Update readme to explain my capabilities

- 2026-02-01 13:32:40 (auto): Update readme to explain my capabilities

- 2026-02-01 13:32:27 (auto): Update readme with a basic description

- 2026-02-01 13:32:27 (auto): Update readme with a basic description

- 2026-02-01 13:32:27 (auto): Update readme with a basic description

- 2026-02-01 13:32:22 (auto): Update existing README with basic content

- 2026-02-01 13:32:22 (auto): Update existing README with basic content

- 2026-02-01 13:32:22 (auto): Update existing README with basic content

- 2026-02-01 13:31:58 (auto): Update README with basic information

- 2026-02-01 13:31:57 (auto): Update README with basic information

- 2026-02-01 13:31:57 (auto): Update README with basic information

- 2026-02-01 13:31:52 (auto): Update readme file with suggested upgrades

- 2026-02-01 13:31:51 (auto): Update readme file with suggested upgrades

- 2026-02-01 13:31:51 (auto): Update readme file with suggested upgrades

- 2026-02-01 13:31:12 (auto): Greet users with a welcome message in the README

- 2026-02-01 13:31:12 (auto): Greet users with a welcome message in the README

- 2026-02-01 13:31:11 (auto): Greet users with a welcome message in the README

- 2026-02-01 13:28:33 (auto): Update README with suggested upgrades to improve the app's features

- 2026-02-01 13:28:32 (auto): Update the README with a greeting and introduction

- 2026-02-01 13:28:32 (auto): Update the README with a greeting message

- 2026-02-01 13:28:32 (auto): Greet user and provide information about the project

- 2026-02-01 13:28:32 (auto): Suggested upgrades for a computer system

- 2026-02-01 13:28:32 (auto): Add three upgrade suggestions to the readme file

- 2026-02-01 13:28:32 (auto): Add a greeting to the README file

- 2026-02-01 13:28:32 (auto): Update project readme file with suggested upgrades

- 2026-02-01 13:28:32 (auto): Update README file with suggestions for upgrades, enhancements and integrations

- 2026-02-01 (auto): Expanded fallback and failsafe logic for file creation prompts. Now, any explicit file creation request (e.g., "write /tmp/manual_test.txt with content: X", "save as ...") will always result in a create_file action or a visible error/status in both the GUI and logs. Extraction logic and error reporting are more robust, guaranteeing no silent failures for actionable prompts. See FIXES_CHANGELOG_2026_02_01.md for details and test plan.

---
### [AUTO-UPDATE LOG]
- 2026-02-01 13:33:36  (auto): Self-improvement cycle complete: audited README and code, proposed ideas.
---

---
### [AUTO-UPDATE LOG]
- 2026-02-01 13:38:37  (auto): Self-improvement cycle complete: audited README and code, proposed ideas.
---

---
### [AUTO-UPDATE LOG]
- 2026-02-01 13:45:09  (auto): Self-improvement cycle complete: audited README and code, proposed ideas.
---

---
### [AUTO-UPDATE LOG]
- 2026-02-01 13:52:42  (auto): Self-improvement cycle complete: audited README and code, proposed ideas.
---

---
### [AUTO-UPDATE LOG]
- 2026-02-01 13:55:52  (auto): Self-improvement cycle complete: audited README and code, proposed ideas.
---

---
### [AUTO-UPDATE LOG]
- 2026-02-01 13:56:25  (auto): Self-improvement cycle complete: audited README and code, proposed ideas.
---

---
### [AUTO-UPDATE LOG]
- 2026-02-01 13:59:13  (auto): Self-improvement cycle complete: audited README and code, proposed ideas.
---

---
### [AUTO-UPDATE LOG]
- 2026-02-01 14:00:47  (auto): Self-improvement cycle complete: audited README and code, proposed ideas.
---

---
### [AUTO-UPDATE LOG]
- 2026-02-01 14:07:24  (auto): Self-improvement cycle complete: audited README and code, proposed ideas.
---

---
### [AUTO-UPDATE LOG]
- 2026-02-01 14:15:22  (auto): Self-improvement cycle complete: audited README and code, proposed ideas.
---

---
### [AUTO-UPDATE LOG]
- 2026-02-01 14:17:19  (auto): Self-improvement cycle complete: audited README and code, proposed ideas.
---

---
### [AUTO-UPDATE LOG]
- 2026-02-01 14:22:25  (auto): Self-improvement cycle complete: audited README and code, proposed ideas.
---

---
### [AUTO-UPDATE LOG]
- 2026-02-01 14:31:06  (auto): Self-improvement cycle complete: audited README and code, proposed ideas.
---

---
### [AUTO-UPDATE LOG]
- 2026-02-01 14:38:59  (auto): Self-improvement cycle complete: audited README and code, proposed ideas.
---

---
### [AUTO-UPDATE LOG]
- 2026-02-01 15:51:29  (auto): Self-improvement cycle complete: audited README and code, proposed ideas.
---

# Project Overview

This project integrates GitHub for version control, CI/CD workflows, and collaboration. It leverages GitHub Copilot for AI-assisted development and includes automated testing and deployment pipelines.

## Key Features
- **GitHub Integration**: Version control, pull requests, and collaboration.
- **CI/CD Workflows**: Automated testing and deployment using GitHub Actions.
- **AI Assistance**: GitHub Copilot for code suggestions and improvements.
- **Documentation**: Comprehensive guides for setup, usage, and contribution.

## Scripts
- `npm run format`: Formats code using Prettier.
- `npm run lint`: Lints code using ESLint.
- `npm run type-check`: Type-checks code using TypeScript.
- `npm test`: Runs unit tests using Jest.
- `npm run integration-test`: Runs integration tests using Jest.
- `bash scripts/audit_repo.sh`: Analyzes the repository or local file system, generates an audit report, and checks for untracked, modified, and large files.
- `bash scripts/context_pack.sh`: Packs high-signal files into a deterministic context bundle.

## Suggestions for Improvement
1. **Enhanced Testing**: Add more unit and integration tests to cover edge cases.
2. **Code Quality**: Use linters and formatters to maintain consistent code style.
3. **Security**: Regularly audit dependencies and use GitHub Dependabot for updates.
4. **Performance**: Optimize critical paths and monitor performance metrics.

## Getting Started
1. Clone the repository: `git clone <repository-url>`
2. Install dependencies: `pnpm install`.
3. Run tests: `npm test` and `npm run integration-test`.
4. Start development: Use `npm run dev` for TypeScript and `nest start` for NestJS.

## Contribution Guidelines
- Fork the repository and create a new branch for your changes.
- Ensure all tests pass before submitting a pull request.
- Follow the coding standards outlined in the CONTRIBUTING.md file.

## Documentation
- **Setup Guide**: [SETUP.md](SETUP.md)
- **API Reference**: [API.md](API.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

For more details, visit the [GitHub repository](<repository-url>).
