# Backend Memory Module

**Owner**: Agent persistence layer | **Responsibility**: Store, retrieve, and manage agent memory persistently

## Purpose

The Memory system provides **persistent context** for the agent across sessions. Every prompt and response is logged, allowing the agent to:
1. Recall previous conversations
2. Learn from past interactions
3. Provide contextual responses
4. Detect patterns and suggest improvements

**Core Philosophy**: Complete audit trail with filtering to remove junk entries.

## Architecture

```
Agent Prompt
    ↓
Process via run_agent.py
    ↓
AgentMemory.add(prompt, reply, conversation_id)
    ↓
agent_memory.json (persistent storage)
    ↓
Daemon reads for analysis/proposals
```

## Files

- **Location**: `backend/memory.py`
- **Storage**: `local-agent-vscode/ipc/agent_memory.json`
- **Size Limit**: No hard limit (grows indefinitely)
- **Backup**: Manual only (should implement)

## Core Methods

### \_\_init\_\_ (Constructor)

```python
memory = AgentMemory(path="/path/to/agent_memory.json")
# Or use default path
memory = AgentMemory()
```

**Default Path**: `local-agent-vscode/ipc/agent_memory.json`

### add (Store Memory)

```python
memory.add(
    prompt="User's question or request",
    reply="Agent's response",
    conversation_id="optional_thread_id"
)
```

**What It Does**:
1. Creates entry with timestamp
2. Appends to history array
3. Calls `filter_junk()` to clean up
4. Saves to file

**Entry Structure**:
```json
{
  "prompt": "User question",
  "reply": "Agent response",
  "timestamp": 1738439400,
  "conversation_id": "thread123"
}
```

**Used By**: `run_agent.py` line 227 after every successful LLM call

### last (Retrieve Recent Memory)

```python
recent = memory.last(n=5)  # Get last 5 entries
# Returns: [entry1, entry2, ..., entry5]

thread = memory.last(n=5, conversation_id="chat123")
# Get last 5 from specific conversation
```

**Used By**: `run_agent.py` line 106-110 to build context for prompts

### filter_junk (Remove Noise)

```python
memory.filter_junk()
```

**What It Removes**:
- Empty prompts/replies
- One-word responses ("ok", "thanks", "cool", etc.)
- Incomplete self-reflection entries
- Test/debug entries

**Patterns Filtered** (regex):
```python
r"^\s*$"  # Whitespace only
r"^(ok|thanks|yes|no|huh|lol)[.!]*$"  # Common filler
r"^\[SELF-REFLECTION\].{0,20}$"  # Incomplete reflection
```

**Called Automatically**: After every `add()`, `add_todo_from_chat()`, `add_self_reflection()`

**Can Be Called Manually**:
```bash
python3 -c "
from backend.memory import AgentMemory
memory = AgentMemory()
memory.filter_junk()
memory.save()
"
```

### add_todo_from_chat (Parse Action Items)

```python
memory.add_todo_from_chat("I want to add a new feature and fix bugs")
```

**What It Does**:
1. Scans text for action keywords
2. Creates TODO entries automatically
3. Stores in memory with conversation_id="todo-capture"

**Keywords Detected**:
```python
want, should, add, improve, fix, build, create, need, upgrade, refactor, test, document
```

**Used By**: `run_agent.py` line 281 on every user prompt

### add_self_reflection (Store Agent Reflection)

```python
memory.add_self_reflection("Summary of what I did and learned")
```

**Entry Structure**:
```json
{
  "prompt": "[SELF-REFLECTION] Agent status report",
  "reply": "Summary here",
  "timestamp": 1738439400,
  "conversation_id": "self-reflection"
}
```

**Used By**: `run_agent.py` line 309 every 10 minutes

### add_best_practices_reference (Embed Guidelines)

```python
memory.add_best_practices_reference()
```

**What It Does**:
- Reads `AI_GUI_BEST_PRACTICES.md`
- Stores as memory entry for reference
- Allows agent to recall best practices without external file read

**Entry Structure**:
```json
{
  "prompt": "[REFERENCE] GUI Best Practices Checklist",
  "reply": "<full content of AI_GUI_BEST_PRACTICES.md>",
  "conversation_id": "best-practices"
}
```

**Status**: Currently not called by agent. Should be called at startup.

## Data Structure

**File Format**: JSON (single object)

```json
{
  "history": [
    {
      "prompt": "First user question",
      "reply": "First agent response",
      "timestamp": 1738439400,
      "conversation_id": "thread1"
    },
    {
      "prompt": "[TODO] Fix the build system",
      "reply": "",
      "timestamp": 1738439402,
      "conversation_id": "todo-capture"
    }
  ]
}
```

## Integration Points

- **Input From**: `run_agent.py` process_prompt() (line 227)
- **Output To**: `run_agent.py` context building (line 106-110)
- **Storage**: `local-agent-vscode/ipc/agent_memory.json`

## Daemon Responsibilities

The Tinkerer Daemon should:
1. Monitor memory file size
2. Check for runaway entry creation
3. Analyze patterns in conversation_id
4. Count TODO items and suggest completion
5. Suggest archiving if file exceeds 10MB
6. Verify junk filtering is working properly

## Error Handling

```python
def _load(self):
    if os.path.exists(self.path):
        try:
            with open(self.path, 'r') as f:
                return json.load(f)
        except Exception:
            return {"history": []}  # Default empty history
    return {"history": []}
```

**Behavior**: Graceful degradation. Corrupted history results in fresh start.

## Known Behaviors

### ✅ Correct (Don't Change)

1. **filter_junk() called after every add()**
   - Intentional: keep memory clean
   
2. **Memory grows unbounded**
   - Intentional: complete audit trail
   - Monitor: File size growth rate

## Future Improvements

1. Implement memory archiving (compress old entries)
2. Add memory summarization (digest of conversations)
3. Add backup mechanism (auto-copy to cloud)
4. Add search functionality across memory
5. Add memory insights (common topics, success rate)

## Hooks & Debug Features
- Junk filtering after every update
- Error handling for file I/O
- Can be extended with heartbeat, resource usage, and anomaly detection hooks

## Usage
- Add todos, self-reflection, and best practices
- Retrieve last N turns for context
- Filter junk entries automatically

## Future Directions
- Add resource usage tracking
- Add anomaly detection
- Add graceful shutdown and state save
