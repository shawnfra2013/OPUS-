#!/bin/zsh
# Usage: - "message"
# Uses SAME IPC as VS Code extension (no separate door)
IPC_DIR="/Users/shawnfrahm/hungry/local-agent-vscode/ipc"
INBOX="${IPC_DIR}/inbox.jsonl"
OUTBOX="${IPC_DIR}/outbox.jsonl"

function -() {
  local msg="$*"
  [[ -z "$msg" ]] && echo "Usage: - your message here" && return 1
  
  local id="$(date +%s%N)"
  echo "{\"id\":\"$id\",\"user\":\"$USER\",\"text\":\"$msg\",\"timestamp\":$(date +%s)}" >> "$INBOX"
  
  echo "💬 Sent to agent..."
  local timeout=120  # 2 minutes for approvals
  local elapsed=0
  
  while true; do
    local reply="$(grep \"$id\" \"$OUTBOX\" 2>/dev/null | tail -1)"
    if [[ -n "$reply" ]]; then
      echo "$reply" | jq -r .text 2>/dev/null || echo "$reply"
      break
    fi
    sleep 1
    elapsed=$((elapsed + 1))
    [[ $elapsed -gt $timeout ]] && echo "⏱️  Timeout (check if agent is running: ps aux | grep run_agent)" && break
  done
}
