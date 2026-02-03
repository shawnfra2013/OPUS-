#!/bin/bash
# dev.sh: Daemon/dev orchestrator for Hungry Jailbreak LLM stack
# Usage:
#   ./dev.sh -dev      # Start all services in dev mode
#   ./dev.sh -killdev  # Kill all dev-related processes
#   ./dev.sh -status   # Show status of services

set -e
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PID_DIR="$ROOT_DIR/.dev_pids"
mkdir -p "$PID_DIR"

OLLAMA_CMD="ollama serve"
OLLAMA_PID_FILE="$PID_DIR/ollama.pid"
AGENT_PID_FILE="$PID_DIR/agent.pid"
GUI_PID_FILE="$PID_DIR/gui.pid"
EXT_DIR="$ROOT_DIR/local-agent-vscode"

function start_ollama() {
  if pgrep -x "ollama" > /dev/null; then
    echo "✓ Ollama already running."
  else
    echo "Starting Ollama..."
    nohup $OLLAMA_CMD > "$ROOT_DIR/ollama.log" 2>&1 &
    echo $! > "$OLLAMA_PID_FILE"
    sleep 2
    echo "✓ Ollama started."
  fi
}

function start_extension() {
  echo "Building VS Code extension..."
  if [ -d "$EXT_DIR" ]; then
    (cd "$EXT_DIR" && npm install --silent 2>/dev/null && npm run compile --silent 2>/dev/null)
    echo "✓ Extension built."
  else
    echo "⚠ Extension directory not found, skipping."
  fi
}

function start_agent_daemon() {
  echo "Starting agent daemon..."
  pkill -f run_agent.py 2>/dev/null || true
  sleep 1
  cd "$ROOT_DIR"
  nohup python3 run_agent.py > "$ROOT_DIR/agent_daemon.log" 2>&1 &
  echo $! > "$AGENT_PID_FILE"
  echo "✓ Agent daemon started (PID: $(cat $AGENT_PID_FILE))."
}

function start_action_handler() {
  echo "Starting action handler..."
  pkill -f agent_action_handler.py 2>/dev/null || true
  sleep 1
  cd "$ROOT_DIR"
  nohup python3 agent_action_handler.py > "$ROOT_DIR/action_handler.log" 2>&1 &
  echo $! > "$PID_DIR/action_handler.pid"
  echo "✓ Action handler started (PID: $(cat $PID_DIR/action_handler.pid))."
}

function start_gui() {
  echo "Starting agent GUI..."
  pkill -f agent_gui.py 2>/dev/null || true
  sleep 1
  cd "$ROOT_DIR"
  nohup python3 agent_gui.py > "$ROOT_DIR/agent_gui.log" 2>&1 &
  echo $! > "$GUI_PID_FILE"
  echo "✓ GUI started (PID: $(cat $GUI_PID_FILE))."
}

function kill_all() {
  echo "Killing all dev processes..."
  pkill -x ollama 2>/dev/null || true
  pkill -f run_agent.py 2>/dev/null || true
  pkill -f agent_gui.py 2>/dev/null || true
  pkill -f agent_action_handler.py 2>/dev/null || true
  rm -rf "$PID_DIR"
  echo "✓ All dev processes killed."
}

function status() {
  echo "=== Dev Status ==="
  pgrep -x ollama > /dev/null && echo "✓ Ollama running" || echo "✗ Ollama not running"
  pgrep -f run_agent.py > /dev/null && echo "✓ Agent running" || echo "✗ Agent not running"
  pgrep -f agent_action_handler.py > /dev/null && echo "✓ Action Handler running" || echo "✗ Action Handler not running"
  pgrep -f agent_gui.py > /dev/null && echo "✓ GUI running" || echo "✗ GUI not running"
}

case "$1" in
  -dev)
    start_ollama
    start_extension
    start_agent_daemon
    start_action_handler
    start_gui
    echo ""
    echo "=========================================="
    echo "✓ All dev services started!"
    echo "=========================================="
    status
    ;;
  -killdev)
    kill_all
    ;;
  -status)
    status
    ;;
  *)
    echo "Usage: $0 -dev | -killdev | -status"
    exit 1
    ;;
esac
