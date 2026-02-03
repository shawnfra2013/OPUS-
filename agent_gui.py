"""
NOTE: This file is intentionally minimal and stable. Do NOT move, refactor, or restructure any functions unless absolutely necessary.
If you add runtime warnings or status messages, do so by appending descriptive text only. Do not change the order or logic of any function.
"""
#!/usr/bin/env python3

import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import time
import os
import json
import subprocess
import logging

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Simple, persistent chat GUI for agent
class AgentGUI:
        # RUNTIME STATUS/WARNING EXAMPLES (append to self.status.config as needed):
        # self.status.config(text="[INFO] Waiting for agent response...")
        # self.status.config(text="[WARNING] Agent response delayed. Retrying...")
        # self.status.config(text="[ERROR] Agent failed to respond after 3 attempts. Check logs.")
        # self.status.config(text="[INFO] Model trainer is not running. Attempting restart...")
        # self.status.config(text="[INFO] Ollama backend is initializing...")
        # self.status.config(text="[WARNING] Large prompt detected. Processing may take longer.")
    def force_restart(self):
        # Attempt to restart all components using the AI-R script
        try:
            self.status.config(text="Restarting all components...")
            subprocess.Popen(["./AI-R"], cwd=os.path.dirname(os.path.abspath(__file__)))
        except Exception as e:
            self.status.config(text=f"Restart failed: {e}")

    def health_check(self):
        # Check if agent, ollama, and model_trainer are running
        try:
            agent = subprocess.call(["pgrep", "-f", "run_agent.py"]) == 0
            ollama = subprocess.call(["pgrep", "-x", "ollama"]) == 0
            trainer = subprocess.call(["pgrep", "-f", "model_trainer.py"]) == 0
            status = f"Agent: {'✅' if agent else '❌'} | Ollama: {'✅' if ollama else '❌'} | Trainer: {'✅' if trainer else '❌'}"
            self.status.config(text=f"Health: {status}")
        except Exception as e:
            self.status.config(text=f"Health check failed: {e}")

    def error_watcher(self):
        last_error = ""
        while True:
            try:
                with open('agent_debug.log', 'r') as log_file:
                    lines = log_file.readlines()
                    if lines:
                        last = lines[-1].strip()
                        if last != last_error:
                            last_error = last
                            self.last_error = last_error
                            logging.error(f"New error detected: {last_error}")
            except Exception as e:
                logging.error(f"Error in error_watcher: {e}")
            time.sleep(2)

    # Only keep the version that reads all lines and displays all agent/user messages
    def watch_outbox(self):
        outbox_path = os.path.join("local-agent-vscode", "ipc", "outbox.jsonl")
        inbox_path = os.path.join("local-agent-vscode", "ipc", "inbox.jsonl")
        self.last_inbox = 0
        self.last_outbox = 0
        # On startup, skip all existing lines (do not replay old chat)
        if os.path.exists(inbox_path):
            with open(inbox_path, "r") as f:
                self.last_inbox = len(f.readlines())
        if os.path.exists(outbox_path):
            with open(outbox_path, "r") as f:
                self.last_outbox = len(f.readlines())
        while self.running:
            try:
                # Show new user prompts from inbox.jsonl
                if os.path.exists(inbox_path):
                    with open(inbox_path, "r") as f:
                        lines = f.readlines()
                        for line in lines[self.last_inbox:]:
                            line = line.strip()
                            if line:
                                try:
                                    data = json.loads(line)
                                    if 'text' in data:
                                        self.append_text(f"You: {data['text']}")
                                except Exception:
                                    self.append_text(line)
                        self.last_inbox = len(lines)
                # Show new agent replies from outbox.jsonl
                if os.path.exists(outbox_path):
                    with open(outbox_path, "r") as f:
                        lines = f.readlines()
                        # Log every line read from outbox
                        for line in lines[self.last_outbox:]:
                            print(f"[DEBUG][OUTBOX] {line}")
                            line = line.strip()
                            if line:
                                try:
                                    data = json.loads(line)
                                    if 'text' in data:
                                        self.append_text(f"Agent: {data['text']}")
                                        print(f"[DEBUG][DISPLAY] Agent: {data['text']}")
                                except Exception:
                                    self.append_text(line)
                                    print(f"[DEBUG][DISPLAY] Agent: {line}")
                        self.last_outbox = len(lines)
            except Exception as e:
                print(f"[GUI ERROR] {e}")
            time.sleep(1)

    def stall_watcher(self):
        retry_count = 0
        while self.running:
            time.sleep(1)
            self.stall_counter += 1
            if self.stall_counter > self.stall_limit:
                self.status.config(text="Agent may be stalled. Retrying...")
                # Retry last prompt if available, up to 3 times
                if hasattr(self, 'last_prompt') and self.last_prompt and retry_count < 3:
                    self.send_prompt_text(self.last_prompt)
                    retry_count += 1
                    with open("agent_debug.log", "a") as f:
                        f.write(f"[GUI] Retried prompt: {self.last_prompt}\n")
                else:
                    self.status.config(text="Agent stalled after 3 retries. Check logs.")
                self.stall_counter = 0

    def append_text(self, text):
        # Only show user-friendly messages, not raw JSON
        try:
            import json
            if text.strip().startswith('{'):
                data = json.loads(text)
                # Try to extract a user-friendly message
                if 'text' in data and isinstance(data['text'], str):
                    msg = data['text']
                elif 'actions' in data and isinstance(data['actions'], list):
                    msg = '\n'.join(f"Action: {a.get('action_type','?')} {a.get('filepath','')}" for a in data['actions'])
                else:
                    msg = '[Agent responded]'
            else:
                msg = text
        except Exception:
            msg = text
        self.text.config(state='normal')
        self.text.insert(tk.END, msg + '\n')
        self.text.see(tk.END)
        self.text.config(state='disabled')
        # Show status update for agent reply or error
        if msg.startswith('Agent:') or msg.startswith("I'M ALIVE") or msg.startswith("I am the embodiment"):
            self.status.config(text="Agent reply received!", bg="#e0ffe0", fg="#222")
        elif '[ERROR]' in msg or 'All model layers failed' in msg or 'Ollama' in msg:
            self.status.config(text=f"Agent ERROR: {msg[:80]}", bg="#ffe0e0", fg="#c00")

    def __init__(self, root):
        self.root = root
        root.title("Agent Chat")
        root.geometry('700x500')
        root.minsize(400, 300)
        # Chat history
        self.text = scrolledtext.ScrolledText(root, state='disabled', font=('Consolas', 12), wrap='word')
        self.text.pack(fill='both', expand=True, padx=8, pady=8)
        # Entry and send button
        entry_frame = tk.Frame(root)
        entry_frame.pack(fill='x', padx=8, pady=(0,8))
        self.entry = tk.Entry(entry_frame, font=('Consolas', 12))
        self.entry.pack(side='left', fill='x', expand=True)
        self.send_btn = tk.Button(entry_frame, text="Send", font=('Consolas', 12), command=self.send_prompt)
        self.send_btn.pack(side='left', padx=(8,0))
        self.entry.bind('<Return>', self.send_prompt)

        # No extra control buttons; use color-coded status only
        # Status bar
        self.status = tk.Label(root, text="Ready", anchor='w', font=('Consolas', 10), bg='#e0ffe0', fg='#222')
        self.status.pack(fill='x', padx=8, pady=(0,4))

        # Set inbox path for writing prompts
        self.inbox = os.path.join("local-agent-vscode", "ipc", "inbox.jsonl")

    def set_status(self, text, level="info"):
        # level: info, warn, error
        color = {"info": "#e0ffe0", "warn": "#fffbe0", "error": "#ffe0e0"}.get(level, "#e0ffe0")
        fg = {"info": "#222", "warn": "#b8860b", "error": "#c00"}.get(level, "#222")
        self.status.config(text=text, bg=color, fg=fg)
        # Background watcher
        self.running = True
        self.stall_counter = 0
        self.stall_limit = 30  # seconds
        # Start all background threads
        threading.Thread(target=self.watch_outbox, daemon=True).start()
        threading.Thread(target=self.stall_watcher, daemon=True).start()
        threading.Thread(target=self.error_watcher, daemon=True).start()
        threading.Thread(target=self.status_updater, daemon=True).start()

    def send_prompt(self, event=None):
        prompt = self.entry.get().strip()
        if not prompt:
            return
        self.entry.delete(0, tk.END)
        self.send_prompt_text(prompt)

    def send_prompt_text(self, prompt):
        self.append_text(f"You: {prompt}\n")
        msg = {
            "id": str(int(time.time() * 1000)),
            "user": "user",
            "text": prompt,
            "timestamp": int(time.time() * 1000)
        }
        with open(self.inbox, "a") as f:
            f.write(json.dumps(msg) + "\n")
        self.status.config(text="Prompt sent. Waiting for agent reply...")
        self.stall_counter = 0
        self.last_prompt = prompt

    def stop_agent(self):
        self.running = False
        self.status.config(text="Agent stopped.")

    def refine_instructions(self):
        instructions = self.refined_box.get("1.0", tk.END).strip()
        if instructions:
            self.append_text(f"Refined: {instructions}\n")
            self.refined_box.delete("1.0", tk.END)
            self.status.config(text="Instructions sent to agent.")
        else:
            messagebox.showwarning("Warning", "Please enter instructions.")

    def show_upgrades(self):
        pass  # Minimal version: no upgrades


    def show_proposal_box(self, proposal_text):
        # Always show proposal in GUI, never trigger approval dialog
        self.proposal_box.config(state='normal')
        self.proposal_box.delete(1.0, tk.END)
        self.proposal_box.insert(tk.END, proposal_text)
        self.proposal_box.config(state='disabled')
        # No approval/deny buttons, only view/edit in GUI

    def watch_outbox(self):
        outbox_path = os.path.join("local-agent-vscode", "ipc", "outbox.jsonl")
        inbox_path = os.path.join("local-agent-vscode", "ipc", "inbox.jsonl")
        last_inbox = 0
        last_outbox = 0
        # On startup, skip all existing lines (do not replay old chat)
        if os.path.exists(inbox_path):
            with open(inbox_path, "r") as f:
                last_inbox = len(f.readlines())
        if os.path.exists(outbox_path):
            with open(outbox_path, "r") as f:
                last_outbox = len(f.readlines())
        while self.running:
            try:
                # Show new user prompts from inbox.jsonl
                if os.path.exists(inbox_path):
                    with open(inbox_path, "r") as f:
                        lines = f.readlines()
                    for line in lines[last_inbox:]:
                        line = line.strip()
                        if line:
                            try:
                                data = json.loads(line)
                                if 'text' in data:
                                    self.append_text(f"You: {data['text']}")
                            except Exception:
                                self.append_text(line)
                    last_inbox = len(lines)
                # Show new agent replies from outbox.jsonl
                if os.path.exists(outbox_path):
                    with open(outbox_path, "r") as f:
                        lines = f.readlines()
                    for line in lines[last_outbox:]:
                        line = line.strip()
                        if line:
                            try:
                                data = json.loads(line)
                                if 'text' in data:
                                    self.append_text(f"Agent: {data['text']}")
                                    self.status.config(text="Agent reply received!", bg="#e0ffe0", fg="#222")
                            except Exception:
                                self.append_text(line)
                                self.status.config(text="Agent reply received! (raw)", bg="#e0ffe0", fg="#222")
                    last_outbox = len(lines)
            except Exception as e:
                print(f"[GUI ERROR] {e}")
            time.sleep(1)
        # ...existing code...

    def stall_watcher(self):
        retry_count = 0
        while self.running:
            time.sleep(1)
            self.stall_counter += 1
            if self.stall_counter > self.stall_limit:
                self.status.config(text="Agent may be stalled. Retrying...")
                # Retry last prompt if available, up to 3 times
                if hasattr(self, 'last_prompt') and self.last_prompt and retry_count < 3:
                    self.send_prompt_text(self.last_prompt)
                    retry_count += 1
                    with open("agent_debug.log", "a") as f:
                        f.write(f"[GUI] Retried prompt: {self.last_prompt}\n")
                else:
                    self.status.config(text="Agent stalled after 3 retries. Check logs.")
                self.stall_counter = 0

    def on_close(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    gui = AgentGUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close)
    root.mainloop()