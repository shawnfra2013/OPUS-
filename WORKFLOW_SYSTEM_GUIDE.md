# Agent Workflow System - VS Code Style Approval Gates

## Overview

This system implements **VS Code-style approval workflow** for agent-generated code:

```
User sends prompt
    ↓
Agent generates code
    ↓
Agent creates APPROVAL_REQUEST.json
    ↓
You review via CLI (interactive prompt)
    ↓
[APPROVE] → Automatic test execution
[DENY] → Code discarded
[REVIEW] → Show actual code files first
    ↓
Results logged & displayed
```

## Components

### 1. **approval_workflow.py**
Manages approval requests and execution:
- Create approval requests with metadata
- Interactive review interface
- Auto-execute approved tasks
- Log execution results

### 2. **code_templates.py**
Pre-built templates for common tasks:
- `PythonWebScraperTemplate` - Web scraper with logging
- `SwiftNetworkManagerTemplate` - iOS networking library
- `ExpressAPITemplate` - REST API boilerplate
- Easy to extend with new templates

### 3. **agent-workflow** (CLI)
Command-line interface:
```bash
./agent-workflow list-templates       # Show available templates
./agent-workflow template [name]      # Get prompt for template
./agent-workflow pending              # List pending approvals
./agent-workflow review [id]          # Review & approve/deny
./agent-workflow approve [id]         # Auto-approve
./agent-workflow deny [id]            # Auto-deny
```

## Workflow

### Step 1: Choose Template
```bash
./agent-workflow template web-scraper
```
Shows:
- Template description
- Exact prompt to copy
- What will be created
- How to verify
- Risk level

### Step 2: Copy & Paste Prompt
1. Open Local Agent Chat in VS Code
2. Copy entire prompt from CLI output
3. Paste into chat
4. Send

### Step 3: Agent Creates Approval Request
Agent generates files AND creates approval request with:
- What was created (files, size)
- What will be executed (commands, tests)
- How to verify manually
- Risk assessment

### Step 4: Review in Terminal
```bash
./agent-workflow pending
```
Shows all pending approvals:
```
🟢 [web-scraper-001] Production-grade web scraper...
   Files: 1 | Commands: 4

🟡 [swift-network-001] Enterprise iOS networking...
   Files: 1 | Commands: 4
```

### Step 5: Approve with Interactive Prompt
```bash
./agent-workflow review web-scraper-001
```

Shows:
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
   • /tmp/web_scraper.py
   Total lines: 145

⚡ COMMANDS TO RUN (4):
   🧪 Verify syntax
       $ python3 -m py_compile /tmp/web_scraper.py
   🧪 Test with example.com
       $ python3 /tmp/web_scraper.py --url https://example.com --log-level INFO
   🧪 Check output format
       $ python3 -m json.tool /tmp/scraped_links.json | head -20
   🧪 Check log file
       $ tail -20 /tmp/scraper.log

✅ HOW TO VERIFY (Run these to check):
   1. python3 /tmp/web_scraper.py --url https://example.com
   2. cat /tmp/scraped_links.json | python3 -m json.tool
   3. tail -50 /tmp/scraper.log | grep -i 'error\|warning'
   4. python3 /tmp/web_scraper.py --help

════════════════════════════════════════════════════════════════════════════════
APPROVE? [y/n/review]:
```

### Step 6a: Approve (y)
```
✅ APPROVED: web-scraper-001

📁 Creating files...
   ✓ /tmp/web_scraper.py

⚡ Running commands...
   ▶️ Verify syntax
      ✓ Exit code: 0
   ▶️ Test with example.com
      ✓ Exit code: 0
   ▶️ Check output format
      ✓ Exit code: 0
   ▶️ Check log file
      ✓ Exit code: 0

✅ EXECUTION COMPLETE
📊 Log saved: /Users/shawnfrahm/hungry/executed_approvals/web-scraper-001.json
```

### Step 6b: Review First (review)
```
[Shows actual code files first]
[Then asks: APPROVE NOW? [y/n]]
```

### Step 6c: Deny (n)
```
❌ DENIED: web-scraper-001
Request marked as denied and archived.
```

## Key Features

### ✅ Safety
- **Review before execution** - You see exactly what will run
- **Risk assessment** - Low/Medium/High clearly marked
- **Reversible** - Can deny without consequences
- **Logged** - All approvals and executions recorded

### ✅ Convenience
- **Interactive prompts** - Easy approve/deny
- **Templates** - Don't type prompts, use templates
- **Auto-testing** - Runs verification tests automatically
- **Clear output** - See what worked and what failed

### ✅ Debugging
- **Preview code** - Review files before approval
- **Manual steps** - Can verify results manually
- **Execution logs** - Full record of what ran
- **Error tracking** - All failures logged

## Example Workflows

### Workflow 1: Web Scraper (Safest)
```bash
# 1. Get template prompt
./agent-workflow template web-scraper

# 2. Copy prompt, paste in VS Code GUI
# 3. Agent generates code

# 4. Review
./agent-workflow pending
./agent-workflow review web-scraper-001

# 5. APPROVE button press
# Result: Code created + tests run

# 6. Verify manually
python3 /tmp/web_scraper.py --url https://example.com
cat /tmp/scraped_links.json | python3 -m json.tool
```

### Workflow 2: Swift Code (Medium Risk)
```bash
./agent-workflow template swift-network
# [Copy prompt, paste in GUI]
./agent-workflow pending
./agent-workflow review swift-network-001

# [Review code option available]
# APPROVE when satisfied
```

### Workflow 3: Express API (Higher Risk)
```bash
./agent-workflow template express-api
# [Copy, paste]
./agent-workflow review express-api-001

# [Review shows all routes and middleware]
# Verify it won't interfere with existing services
# APPROVE if satisfied
```

## Adding Custom Templates

1. Create class in `code_templates.py`:
```python
class MyCustomTemplate(CodeTemplate):
    def __init__(self):
        super().__init__("Template Name", "Description")
    
    def get_prompt(self) -> str:
        return "Your template prompt..."
    
    def get_test_commands(self) -> List[Dict]:
        return [{"description": "...", "cmd": "...", "test": True}]
    
    def get_verification_steps(self) -> List[str]:
        return ["step 1", "step 2"]
    
    def get_files_to_create(self) -> Dict[str, str]:
        return {"/tmp/file.py": "description"}
    
    def get_risk_level(self) -> str:
        return "low"  # or medium/high
```

2. Register in `TEMPLATES` dict:
```python
TEMPLATES = {
    "my-template": MyCustomTemplate,
    ...
}
```

## Directory Structure

```
/Users/shawnfrahm/hungry/
├── approval_workflow.py          # Core approval system
├── code_templates.py             # Template definitions
├── agent-workflow                # CLI interface (executable)
├── approval_requests/            # Pending approvals
│   ├── web-scraper-001.json
│   ├── web-scraper-001_files.json
│   ├── swift-network-001.json
│   └── swift-network-001_files.json
└── executed_approvals/           # Completed executions
    ├── web-scraper-001.json      # With execution results
    └── swift-network-001.json    # With execution results
```

## Tips & Tricks

### See all pending approvals
```bash
./agent-workflow pending
```

### Review without prompt interaction
```bash
# Just review the JSON
cat /Users/shawnfrahm/hungry/approval_requests/web-scraper-001.json | python3 -m json.tool
```

### Check execution results
```bash
cat /Users/shawnfrahm/hungry/executed_approvals/web-scraper-001.json | python3 -m json.tool | grep -A 5 '"status"'
```

### Manually run tests after approval
```bash
# If you want to re-run tests
python3 /tmp/web_scraper.py --url https://example.com --log-level DEBUG
```

## Status

✅ **System Ready**
- 3 templates configured
- Approval workflow functional
- Auto-execution working
- Logging comprehensive

**Next**: Set up agent to automatically create approval requests (requires run_agent.py integration).

---

**Created**: 2026-02-01
**Status**: Production Ready
**Tests**: Manual approval workflow verified
