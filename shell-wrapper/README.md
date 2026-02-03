# Shell Wrapper for Local Agent

## Overview
The shell wrapper provides a command-line interface to interact with the local agent directly from your terminal.

## Usage

- Source the script in your `~/.zshrc` or `~/.cshrc`:
  - For zsh: `source ~/shell-wrapper/agent-zsh.sh`
  - For csh/tcsh: `source ~/shell-wrapper/agent-csh.csh`

- Then use:
  ```
  agent "Your message here"
  agent "Hello, agent!" --loop
  ```

## How It Works
- The wrapper writes to `~/.local-agent-ipc/inbox.jsonl` and reads from `outbox.jsonl`.
- All communication uses NDJSON format with `id`, `text`, and `timestamp` fields.
- Requires `jq` for JSON parsing.

## Integration
- Works seamlessly with the backend agent (run_agent.py) and VS Code extension.
- Allows CLI access to the same agent that powers the GUI and extension.
