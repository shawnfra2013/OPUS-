function start_gui() {
  echo "Starting agent GUI (dev mode)..."
  # Example: If agent_gui.py is a Flask app or similar, run it in the background
  nohup python3 agent_gui.py > "$ROOT_DIR/agent_gui.log" 2>&1 &
  echo $! > "$PID_DIR/gui.pid"
}

#!/bin/bash
# dev.sh - Launch Ollama model, agent backend, and GUI in parallel

# dev.sh: Daemon/dev orchestrator for Hungry Jailbreak LLM stack
# Usage:
#   ./dev.sh -dev      # Start all services in dev mode (auto-restart agent)
#   ./dev.sh -killdev  # Kill all dev-related processes
#   (Add to crontab or launchd for boot)

set -e
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PID_DIR="$ROOT_DIR/.dev_pids"
mkdir -p "$PID_DIR"

OLLAMA_CMD="ollama serve"
OLLAMA_PID_FILE="$PID_DIR/ollama.pid"
AGENT_PID_FILE="$PID_DIR/agent.pid"
EXT_DIR="$ROOT_DIR/local-agent-vscode"
EXT_PID_FILE="$PID_DIR/extension.pid"

function start_ollama() {
  if pgrep -x "ollama" > /dev/null; then
    echo "Ollama already running."
  else
    echo "Starting Ollama..."
    nohup $OLLAMA_CMD > "$ROOT_DIR/ollama.log" 2>&1 &
    echo $! > "$OLLAMA_PID_FILE"
    sleep 2
  fi
}

function start_extension() {
  echo "Building and starting VS Code extension (dev)..."
  (cd "$EXT_DIR" && npm install && npm run compile)
}

function start_agent_daemon() {
  echo "Starting agent daemon (auto-restart)..."
  nohup bash -c '
    while true; do
      python3 run_agent.py
      echo "Agent crashed/exited. Restarting in 5s..."
      sleep 5
    done
  ' > "$ROOT_DIR/agent_daemon.log" 2>&1 &
  echo $! > "$AGENT_PID_FILE"
}

function kill_all() {
  echo "Killing all dev processes..."
  # Kill Ollama
  if [ -f "$OLLAMA_PID_FILE" ]; then
    kill "$(cat "$OLLAMA_PID_FILE")" 2>/dev/null || true
    rm -f "$OLLAMA_PID_FILE"
  fi
  pkill -x ollama 2>/dev/null || true
  # Kill agent
  if [ -f "$AGENT_PID_FILE" ]; then
    kill "$(cat "$AGENT_PID_FILE")" 2>/dev/null || true
    rm -f "$AGENT_PID_FILE"
  fi
  pkill -f run_agent.py 2>/dev/null || true
  # VS Code extension (if any background process)
  if [ -f "$EXT_PID_FILE" ]; then
    kill "$(cat "$EXT_PID_FILE")" 2>/dev/null || true
    rm -f "$EXT_PID_FILE"
  fi
  # Clean up
  rm -rf "$PID_DIR"
  echo "All dev processes killed."
}

case "$1" in
  -dev)
    start_ollama
    start_extension
    start_agent_daemon
    start_gui
    echo "All dev services (including GUI) started."
    ;;
  -killdev)
    kill_all
    # Kill GUI
    if [ -f "$PID_DIR/gui.pid" ]; then
      kill "$(cat "$PID_DIR/gui.pid")" 2>/dev/null || true
      rm -f "$PID_DIR/gui.pid"
    fi
    pkill -f agent_gui.py 2>/dev/null || true
    ;;
  *)
    echo "Usage: $0 -dev | -killdev"
    exit 1
    ;;
esac

if [ -f "$ROOT_DIR/.venv/bin/activate" ]; then
  source "$ROOT_DIR/.venv/bin/activate"
else
  echo "Warning: Python venv not found at $ROOT_DIR/.venv/bin/activate"
fi
