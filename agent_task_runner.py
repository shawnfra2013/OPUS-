import json
import time
import os
import threading

IPC_DIR = os.path.join(os.path.dirname(__file__), 'local-agent-vscode', 'ipc')
INBOX = os.path.join(IPC_DIR, 'inbox.jsonl')
OUTBOX = os.path.join(IPC_DIR, 'outbox.jsonl')
LOG = os.path.join(IPC_DIR, 'agent_debug.log')

# Task runner and pipeline monitor

class AgentTaskRunner:
    def __init__(self, hooks=None):
        self.last_outbox_size = 0
        self.running = True
        self.prompt_queue = []
        self.lock = threading.Lock()
        # V hook system: hooks is a dict of event_name: [callable, ...]
        self.hooks = hooks or {
            'on_task_start': [],
            'on_task_end': [],
            'on_action_complete': []
        }
        self._start_monitor()

    def _start_monitor(self):
        t = threading.Thread(target=self._monitor_pipeline, daemon=True)
        t.start()

    def _monitor_pipeline(self):
        while self.running:
            try:
                # Monitor outbox for new replies
                if os.path.exists(OUTBOX):
                    try:
                        with open(OUTBOX, 'r') as f:
                            lines = f.readlines()
                    except Exception as e:
                        self._log_error(f"Failed to read OUTBOX: {e}")
                        continue
                    if len(lines) > self.last_outbox_size:
                        new_lines = lines[self.last_outbox_size:]
                        for line in new_lines:
                            try:
                                data = json.loads(line)
                                # V hook: on_action_complete
                                for hook in self.hooks.get('on_action_complete', []):
                                    try:
                                        hook(data)
                                    except Exception as e:
                                        self._log_error(f"V hook error: {e}")
                                print(f"[Agent Reply] {data.get('text')}")
                            except Exception as e:
                                self._log_error(f"Failed to parse outbox line: {e}")
                        self.last_outbox_size = len(lines)
                else:
                    self._log_error("OUTBOX file missing. Pipeline may be broken.")
                # Check for task runner overload/idle/fault
                if len(self.prompt_queue) > 100:
                    self._log_error("Task runner overloaded: prompt queue > 100.")
                time.sleep(1)
            except Exception as e:
                self._log_error(f"[Monitor] Error: {e}")

    def _log_error(self, msg):
        print(f"[TaskRunner][ERROR] {msg}")
        # Log to agent_debug.log
        with open(LOG, 'a') as logf:
            logf.write(f"[TaskRunner][ERROR] {time.ctime()} | {msg}\n")
        # Also surface to outbox.jsonl for GUI/user visibility
        try:
            error_entry = {
                "id": str(int(time.time() * 1000)),
                "agent": "taskrunner",
                "text": f"[ERROR] {msg}",
                "timestamp": int(time.time() * 1000)
            }
            with open(OUTBOX, "a") as f:
                f.write(json.dumps(error_entry) + "\n")
        except Exception as e:
            # If even this fails, log to debug only
            with open(LOG, 'a') as logf:
                logf.write(f"[TaskRunner][ERROR] {time.ctime()} | Failed to write error to outbox: {e}\n")

    def send_prompt(self, prompt):
        msg = {
            "id": str(int(time.time() * 1000)),
            "user": "user",
            "text": prompt,
            "timestamp": int(time.time() * 1000)
        }
        # V hook: on_task_start
        for hook in self.hooks.get('on_task_start', []):
            try:
                hook(msg)
            except Exception as e:
                self._log_error(f"V hook error: {e}")
        try:
            with open(INBOX, "a") as f:
                f.write(json.dumps(msg) + "\n")
            print(f"[TaskRunner] Prompt sent: {prompt}")
        except Exception as e:
            self._log_error(f"Failed to write to INBOX: {e}")
            # Attempt auto-recovery: recreate INBOX if missing
            try:
                if not os.path.exists(INBOX):
                    open(INBOX, 'w').close()
                    print("[TaskRunner] INBOX recreated.")
            except Exception as e2:
                self._log_error(f"Failed to auto-recover INBOX: {e2}")
        # V hook: on_task_end
        for hook in self.hooks.get('on_task_end', []):
            try:
                hook(msg)
            except Exception as e:
                self._log_error(f"V hook error: {e}")
        return msg["id"]

    def stop(self):
        self.running = False

if __name__ == "__main__":
    print("Type 'exit' to quit. Type 'wake' to send a wake/test prompt. Type 'log' to view recent errors.")

    # Example V hook functions for GUI or plugin integration
    def on_task_start_hook(msg):
        print(f"[VHOOK] Task started: {msg['text']}")

    def on_task_end_hook(msg):
        print(f"[VHOOK] Task ended: {msg['text']}")

    def on_action_complete_hook(data):
        print(f"[VHOOK] Action complete: {data.get('text')}")

    hooks = {
        'on_task_start': [on_task_start_hook],
        'on_task_end': [on_task_end_hook],
        'on_action_complete': [on_action_complete_hook]
    }

    runner = AgentTaskRunner(hooks=hooks)
    try:
        while True:
            prompt = input("You: ")
            if prompt.strip().lower() == "exit":
                break
            if prompt.strip().lower() == "wake":
                runner.send_prompt("ping")
                continue
            if prompt.strip().lower() == "log":
                if os.path.exists(LOG):
                    with open(LOG, 'r') as logf:
                        print("--- Agent Debug Log ---")
                        print(logf.read())
                        print("-----------------------")
                else:
                    print("[TaskRunner] No log file found.")
                continue
            runner.send_prompt(prompt)
        runner.stop()
    except KeyboardInterrupt:
        runner.stop()
        print("\n[TaskRunner] Stopped.")
