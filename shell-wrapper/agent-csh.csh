#!/bin/csh
# Usage: agent "message" [--loop]
setenv IPC_DIR "${HOME}/.local-agent-ipc"
setenv INBOX "${IPC_DIR}/inbox.jsonl"
setenv OUTBOX "${IPC_DIR}/outbox.jsonl"
if (! -d "$IPC_DIR") mkdir -p "$IPC_DIR"

alias agent 'set id=`date +%s%N`; echo "{\"id\":\"$id\",\"user\":\"$USER\",\"text\":\"\!:1\",\"timestamp\":`date +%s`}" >> $INBOX; while (1) set reply=`grep "$id" $OUTBOX | tail -1`; if ("$reply" != "") break; sleep 1; end; echo $reply | jq -r .text'

# For loop mode, you can wrap in a while/read loop in your shell.
