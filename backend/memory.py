import os
import json
import time

MEMORY_FILE = os.path.join(os.path.dirname(__file__), '..', 'local-agent-vscode', 'ipc', 'agent_memory.json')

class AgentMemory:
    def deduplicate(self):
        # Remove duplicate prompt/reply pairs (keep latest)
        seen = set()
        deduped = []
        for entry in reversed(self.data.get("history", [])):
            key = (entry.get("prompt", ""), entry.get("reply", ""))
            if key not in seen:
                deduped.append(entry)
                seen.add(key)
        self.data["history"] = list(reversed(deduped))
        self.save()

    def __init__(self, path=MEMORY_FILE):
        self.path = path
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r') as f:
                    return json.load(f)
            except Exception:
                return {"history": []}
        return {"history": []}

    def save(self):
        with open(self.path, 'w') as f:
            json.dump(self.data, f, indent=2)

    def filter_junk(self):
        # Remove entries with empty prompt/reply or common junk patterns
        import re
        filtered = []
        junk_patterns = [
            r"^\s*$",  # empty or whitespace
            r"^(ok|thanks|thank you|cool|nice|yes|no|hmm|huh|lol|test|testing|ping|hello|hi|hey)[.!]*$",
            r"^\[SELF-REFLECTION\].{0,20}$",  # empty self-reflection
        ]
        for entry in self.data.get("history", []):
            prompt = entry.get("prompt", "").strip().lower()
            reply = entry.get("reply", "").strip().lower()
            if not prompt or not reply:
                continue
            if any(re.match(pat, prompt) for pat in junk_patterns):
                continue
            filtered.append(entry)
        self.data["history"] = filtered
        self.save()

    def add_todo_from_chat(self, chat_text):
        # Parse chat for actionable items (simple heuristic: lines with 'want', 'should', 'add', 'improve', 'fix', 'build', 'create', 'need')
        import re
        keywords = r"(want|should|add|improve|fix|build|create|need|upgrade|refactor|test|document)"
        lines = chat_text.split('\n')
        for line in lines:
            if re.search(keywords, line, re.IGNORECASE):
                entry = {
                    "prompt": f"[TODO] {line.strip()}",
                    "reply": "",
                    "timestamp": int(time.time()),
                    "conversation_id": "todo-capture"
                }
                self.data.setdefault("history", []).append(entry)
        self.save()
        self.filter_junk()
        self.deduplicate()

    def add_self_reflection(self, summary):
        # Add a self-reflection/status report entry
        entry = {
            "prompt": "[SELF-REFLECTION] Agent status report",
            "reply": summary,
            "timestamp": int(time.time()),
            "conversation_id": "self-reflection"
        }
        self.data.setdefault("history", []).append(entry)
        self.save()
        self.filter_junk()
        self.deduplicate()

    def add(self, prompt, reply, conversation_id=None):
        entry = {
            "prompt": prompt,
            "reply": reply,
            "timestamp": int(time.time()),
        }
        if conversation_id:
            entry["conversation_id"] = conversation_id
        self.data.setdefault("history", []).append(entry)
        self.save()
        self.filter_junk()
        self.deduplicate()

    def add_best_practices_reference(self):
        # Add the GUI best practices checklist as a persistent memory entry
        with open(os.path.join(os.path.dirname(__file__), '..', 'AI_GUI_BEST_PRACTICES.md'), 'r') as f:
            checklist = f.read()
        entry = {
            "prompt": "[REFERENCE] GUI Best Practices Checklist",
            "reply": checklist,
            "timestamp": int(time.time()),
            "conversation_id": "best-practices"
        }
        self.data.setdefault("history", []).append(entry)
        self.save()
        self.filter_junk()
        self.deduplicate()

    def clear(self):
        self.data = {"history": []}
        self.save()

    def last(self, n=5, conversation_id=None):
        history = self.data.get("history", [])
        if conversation_id:
            history = [h for h in history if h.get("conversation_id") == conversation_id]
        return history[-n:]