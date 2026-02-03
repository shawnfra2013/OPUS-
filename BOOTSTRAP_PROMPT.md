# 🚀 Agent Self-Modification Bootstrap Prompt

## Ready to Test!

The agent now has self-modification capabilities. Use these prompts in the GUI to test.

---

## Level 1: Simple Test (Confirm Agent is Working)
```
Hello, are you working?
```
**Expected:** Natural language response confirming the agent is alive.

---

## Level 2: Read Own Code (Self-Awareness Test)
```
Read your own code at /Users/shawnfrahm/hungry/run_agent.py and tell me what your main function does.
```
**Expected:** Agent outputs a `read_file` JSON action, reads its code, and can describe what it does.

---

## Level 3: Create New Capability
```
Create file /Users/shawnfrahm/hungry/my_new_feature.py with a function called hello_world that prints "I am alive!"
```
**Expected:** Agent creates the file with proper Python code.

---

## Level 4: Self-Modification (The Bootstrap!)
```
Read your code at /Users/shawnfrahm/hungry/run_agent.py, then create a new file /Users/shawnfrahm/hungry/agent_v2_notes.py that documents 3 improvements you would make to yourself.
```
**Expected:** Agent reads its own code, analyzes it, and creates a new file with improvement suggestions.

---

## Level 5: Full Self-Edit (Advanced)
```
Add capability: Create a new utility function in a new file /Users/shawnfrahm/hungry/utilities/string_helpers.py that has a function called reverse_string(s) that reverses a string.
```
**Expected:** Agent creates the directory and file with working code.

---

## Architecture Reference

The agent can:
- **read_file**: Read any file including its own source code
- **create_file**: Create new Python files with new capabilities
- **update_file**: Modify existing files (including itself!)
- **execute_command**: Run shell commands

Key files the agent knows about:
- `/Users/shawnfrahm/hungry/run_agent.py` - Its brain (main loop)
- `/Users/shawnfrahm/hungry/agent_action_handler.py` - Its hands (executes actions)
- `/Users/shawnfrahm/hungry/agent_gui.py` - Its interface with users

---

## How It Works

1. You type a prompt in the GUI
2. Prompt goes to `inbox.jsonl`
3. `run_agent.py` processes it with Ollama LLM
4. LLM outputs JSON action(s)
5. `agent_action_handler.py` executes the action(s)
6. Response goes to `outbox.jsonl`
7. GUI displays the response

---

## Next Steps After Bootstrap

Once the agent can successfully:
1. ✅ Respond to chat
2. ✅ Read its own code
3. ✅ Create new files
4. ✅ Self-analyze and document improvements

Then you can ask it to:
- Add new action types
- Improve its error handling
- Add memory persistence
- Create new API integrations
- Build its own test suite

---

**Ready? Start the agent with `python3 run_agent.py` and `python3 agent_gui.py`, then try Level 1!**
