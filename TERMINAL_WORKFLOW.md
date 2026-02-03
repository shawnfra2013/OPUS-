# Terminal Workflow - Complete Guide

## Overview

You interact with the AI agent entirely through the terminal. No GUI, no VS Code extension. Clean, fast, and reliable.

```
Terminal 1: Ollama Server
Terminal 2: AI Agent (run_agent.py)
Terminal 3: Your terminal (approval workflow)
    ↓
You send prompts
    ↓
Agent generates code
    ↓
Agent creates approval request
    ↓
You review & approve/deny
    ↓
Tests run automatically
```

## Setup (One-Time)

### 1. Make sure Ollama is installed
```bash
# Check if ollama exists
which ollama

# If not, install from https://ollama.ai
```

### 2. Make scripts executable
```bash
cd /Users/shawnfrahm/hungry

# Approval workflow CLI
chmod +x agent-workflow

# Template system is built-in
```

## Daily Workflow

### Terminal 1: Start Ollama
```bash
ollama serve
```

Keep this running in the background. You'll see:
```
Listening on 127.0.0.1:11434
```

### Terminal 2: Start the Agent
```bash
cd /Users/shawnfrahm/hungry
python3 run_agent.py
```

You'll see:
```
========================================
       🤖 AGENT LOOP STARTING
========================================
[✓] System message loaded
[✓] OpenChat model ready
[✓] Waiting for prompts...
```

Agent is now waiting for input from Terminal 3.

### Terminal 3: Interactive Mode

#### Check Available Templates
```bash
./agent-workflow list-templates
```

Output:
```
════════════════════════════════════════════════════════════════════════════════
📚 AVAILABLE TEMPLATES
════════════════════════════════════════════════════════════════════════════════

🟢 web-scraper
   Production-grade web scraper with logging, retry logic, error handling
   Risk: LOW | Files: 1 | Tests: 4

🟡 swift-network
   Enterprise iOS networking library with async/await and retry logic
   Risk: MEDIUM | Files: 1 | Tests: 4

🟡 express-api
   REST API boilerplate with auth, validation, and error handling
   Risk: MEDIUM | Files: 1 | Tests: 4

════════════════════════════════════════════════════════════════════════════════
USE: ./agent-workflow template [name]
```

#### Get a Template Prompt
```bash
./agent-workflow template web-scraper
```

Output shows:
```
════════════════════════════════════════════════════════════════════════════════
🔧 TEMPLATE: web-scraper
════════════════════════════════════════════════════════════════════════════════

📖 DESCRIPTION:
Production-grade web scraper with logging, retry logic, and error handling

⚠️  RISK LEVEL: LOW

📋 WHAT YOU'LL GET:
• 1 Python file (web_scraper.py)
• Automatic logging to scraper.log
• Retry logic with exponential backoff
• Beautiful HTML parsing with BeautifulSoup
• Error handling and reporting

🧪 HOW TO TEST:
After approval, these commands will run automatically:
  1. Verify syntax: python3 -m py_compile /tmp/web_scraper.py
  2. Test with example.com: python3 /tmp/web_scraper.py --url https://example.com
  3. Check output format: python3 -m json.tool /tmp/scraped_links.json
  4. Check log file: tail -20 /tmp/scraper.log

✅ MANUAL VERIFICATION:
You can also run these to verify:
  1. python3 /tmp/web_scraper.py --url https://wikipedia.org
  2. cat /tmp/scraped_links.json | python3 -m json.tool
  3. tail -50 /tmp/scraper.log | grep -i 'error\|warning'
  4. python3 /tmp/web_scraper.py --help

════════════════════════════════════════════════════════════════════════════════
🎯 EXACT PROMPT TO COPY & PASTE:
════════════════════════════════════════════════════════════════════════════════

[FULL TEMPLATE PROMPT SHOWN HERE]

════════════════════════════════════════════════════════════════════════════════
HOW TO USE:
1. Copy the prompt above (select all, cmd+c)
2. Open a new terminal
3. Use: echo "[PASTE_HERE]" | ./agent-cli-prompt
   OR type it and send to agent via stdin
4. Agent will generate code
5. Come back here and run: ./agent-workflow pending
6. Then: ./agent-workflow review [id]
════════════════════════════════════════════════════════════════════════════════
```

#### Send Prompt to Agent

Option A: Use stdin directly
```bash
# Echo the prompt and pipe to agent stdin
echo "CREATE A PRODUCTION-GRADE WEB SCRAPER WITH LOGGING AND RETRY LOGIC" | python3 -c "
import sys
import json
from run_agent import main_loop
# Agent reads from stdin
prompt = sys.stdin.read()
main_loop(prompt)
"
```

Option B: Create a prompt file
```bash
# Save prompt to file
echo "CREATE A PRODUCTION-GRADE WEB SCRAPER WITH LOGGING AND RETRY LOGIC" > /tmp/prompt.txt

# Send it
python3 -c "
import sys
with open('/tmp/prompt.txt') as f:
    prompt = f.read()
    # Send to agent via IPC
"
```

Option C: Direct agent interaction
```bash
# Use the IPC system directly
# Write to inbox.jsonl
echo '{\"id\":\"user-001\",\"text\":\"CREATE A PRODUCTION-GRADE WEB SCRAPER\",\"timestamp\":\"2026-02-01T10:00:00Z\"}' >> agent_memory.json
```

#### Monitor Agent Response
```bash
# Watch the outbox for agent response
tail -f outbox.jsonl | jq .

# In another terminal, see what was created
ls -lh /tmp/ | grep -E 'scraper|proxy|crawler'
```

#### Check Pending Approvals
Once agent generates code, it creates an approval request:

```bash
./agent-workflow pending
```

Output:
```
════════════════════════════════════════════════════════════════════════════════
⏳ PENDING APPROVALS (1)
════════════════════════════════════════════════════════════════════════════════

🟢 [web-scraper-001]
   Production-grade web scraper with logging...
   Created: 2026-02-01 14:23:45
   Files: 1 | Commands: 4 | Risk: LOW
   
🟡 [swift-network-001]
   Enterprise iOS networking...
   Created: 2026-02-01 14:00:00
   Files: 1 | Commands: 4 | Risk: MEDIUM

════════════════════════════════════════════════════════════════════════════════
USE: ./agent-workflow review [id]  to approve or deny
```

#### Review & Approve

```bash
./agent-workflow review web-scraper-001
```

Interactive prompt:
```
════════════════════════════════════════════════════════════════════════════════
🤖 AGENT APPROVAL REQUEST
════════════════════════════════════════════════════════════════════════════════

📋 ID: web-scraper-001
⏰ Created: 2026-02-01T14:23:45.123456
⚠️  Risk Level: LOW

📝 WHAT THE AGENT IS PROPOSING:
   Production-grade web scraper with logging, retry logic, and error handling

📁 FILES TO CREATE (1):
   • /tmp/web_scraper.py (145 lines)

⚡ COMMANDS TO RUN (4):
   🧪 Verify syntax
   🧪 Test with example.com
   🧪 Check output format
   🧪 Check log file

✅ HOW TO VERIFY:
   1. python3 /tmp/web_scraper.py --url https://example.com
   2. cat /tmp/scraped_links.json | python3 -m json.tool
   3. tail -50 /tmp/scraper.log | grep -i 'error\|warning'
   4. python3 /tmp/web_scraper.py --help

════════════════════════════════════════════════════════════════════════════════
APPROVE? [y/n/review]:
```

**Three options:**
- `y` - Approve and auto-execute all tests
- `n` - Deny (code discarded)
- `review` - Show actual code files first, then ask again

#### If You Choose "review"
```
APPROVE? [y/n/review]: review

════════════════════════════════════════════════════════════════════════════════
📄 FILE: /tmp/web_scraper.py (first 30 lines)
════════════════════════════════════════════════════════════════════════════════

1  #!/usr/bin/env python3
2  """Production web scraper with logging and retry logic."""
3  
4  import requests
5  import logging
6  from bs4 import BeautifulSoup
7  from urllib.parse import urljoin
8  import json
9  import time
10 from typing import List, Dict
11 ...
30 
════════════════════════════════════════════════════════════════════════════════
APPROVE NOW? [y/n]:
```

#### If You Approve (y)
```
✅ APPROVED: web-scraper-001

📁 Creating files...
   ✓ /tmp/web_scraper.py (145 lines)

⚡ Running commands...
   ▶️ Verify syntax
      ✓ Exit code: 0 (2.3s)
   ▶️ Test with example.com
      ✓ Exit code: 0 (8.7s)
      Output: Found 42 links
   ▶️ Check output format
      ✓ Exit code: 0 (0.1s)
   ▶️ Check log file
      ✓ Exit code: 0 (0.1s)

✅ EXECUTION COMPLETE (ALL TESTS PASSED)
📊 Log saved: /Users/shawnfrahm/hungry/executed_approvals/web-scraper-001.json

📁 Files created:
   /tmp/web_scraper.py

📊 Summary:
   • All 4 tests passed
   • No errors detected
   • Ready to use: python3 /tmp/web_scraper.py --url https://example.com
```

#### Check Execution Results
```bash
# View detailed execution log
cat executed_approvals/web-scraper-001.json | jq .

# See only test results
cat executed_approvals/web-scraper-001.json | jq '.execution_results'

# Check if any tests failed
cat executed_approvals/web-scraper-001.json | jq '.execution_results[] | select(.exit_code != 0)'
```

## Real-Time Monitoring

### Monitor Agent Loop
```bash
# Watch agent processing in real-time
tail -f outbox.jsonl | jq '.'
```

Output shows:
```json
{
  "id": "response-001",
  "text": "I've created a production-grade web scraper...",
  "timestamp": "2026-02-01T14:23:45.123456",
  "model": "openchat",
  "approval_request_id": "web-scraper-001"
}
```

### Monitor File System Changes
```bash
# Watch for newly created files
watch -n 1 'ls -lh /tmp/ | tail -20'

# Or use a script
while true; do
  echo "=== New files in /tmp ==="
  find /tmp -type f -mmin -1 | head -10
  sleep 5
done
```

### Monitor Agent Memory
```bash
# See conversation history
cat agent_memory.json | jq '.conversation_history | last'

# Count total interactions
cat agent_memory.json | jq '.conversation_history | length'
```

## Troubleshooting

### Agent Not Responding?

1. **Check if agent is running**
   ```bash
   ps aux | grep "python3 run_agent.py"
   ```

2. **Check if Ollama is running**
   ```bash
   ps aux | grep ollama
   ```

3. **Test Ollama directly**
   ```bash
   curl http://localhost:11434/api/tags
   ```

4. **Restart both**
   ```bash
   pkill -f "run_agent.py"
   # Wait 2 seconds
   python3 run_agent.py
   ```

### No Pending Approvals?

The agent might not have completed yet. Check logs:
```bash
# See all agent responses (last 10)
tail -10 outbox.jsonl | jq '.approval_request_id'

# See all created approvals
ls -lh approval_requests/ | grep -v "^total"
```

### Approval Request Files Missing?

```bash
# Check if directories exist
ls -la approval_requests/
ls -la executed_approvals/

# Create if missing
mkdir -p approval_requests executed_approvals
```

## Advanced: Custom Templates

See [WORKFLOW_SYSTEM_GUIDE.md](WORKFLOW_SYSTEM_GUIDE.md#adding-custom-templates) for how to add custom templates.

## Advanced: Direct Agent Prompting

If you don't want to use templates, you can send custom prompts directly:

```bash
# Create a custom prompt file
cat > /tmp/my_prompt.txt << 'EOF'
Build me a Python CLI tool that:
1. Takes a URL as input
2. Downloads the page
3. Extracts all email addresses
4. Saves to CSV with timestamp
5. Includes error handling and logging
EOF

# Send to agent (depends on how agent reads prompts)
# This varies based on run_agent.py implementation
```

## Daily Checklist

- [ ] Ollama running in Terminal 1
- [ ] Agent running in Terminal 2
- [ ] Check pending with `./agent-workflow pending`
- [ ] Review requests with `./agent-workflow review [id]`
- [ ] Approve or deny
- [ ] Check logs: `tail -10 executed_approvals/*.json`
- [ ] Test created files manually before using in production

## Logs Location

All activity logged to:
- `outbox.jsonl` - Agent responses
- `agent_memory.json` - Conversation history
- `approval_requests/` - Pending approvals (JSON)
- `executed_approvals/` - Completed approvals with results
- `/tmp/scraper.log` (or specific log files created by agent)

---

**Updated**: 2026-02-01
**Status**: Terminal-only workflow fully operational
