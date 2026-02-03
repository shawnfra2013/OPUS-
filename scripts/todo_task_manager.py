#!/usr/bin/env python3
"""
AI Todo List Manager & Task Runner
- Reads and updates the todo list (agent_memory.json)
- Triggers builds/tasks (e.g., xcodebuild, VS Code tasks)
- Uses osascript for macOS notifications
- No silent fails: all errors are logged and notified
"""
import os
import json
import subprocess
import sys
import time

MEMORY_PATH = os.path.join(os.path.dirname(__file__), '..', 'local-agent-vscode', 'ipc', 'agent_memory.json')
LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'task_manager.log')

# macOS notification via osascript
def notify(title, message):
    try:
        subprocess.run([
            'osascript', '-e', f'display notification "{message}" with title "{title}"'
        ], check=True)
    except Exception as e:
        print(f"[Notification Error] {e}")

def log(msg):
    with open(LOG_PATH, 'a') as f:
        f.write(f"{time.ctime()} | {msg}\n")
    print(msg)
    notify("AI Task Manager", msg)

def read_todos():
    try:
        with open(MEMORY_PATH, 'r') as f:
            data = json.load(f)
        todos = [h for h in data.get('history', []) if h.get('prompt', '').startswith('[TODO]')]
        return todos
    except Exception as e:
        log(f"[ERROR] Failed to read todos: {e}")
        return []

def mark_todo_done(todo):
    try:
        with open(MEMORY_PATH, 'r+') as f:
            data = json.load(f)
            for h in data.get('history', []):
                if h == todo:
                    h['done'] = True
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
    except Exception as e:
        log(f"[ERROR] Failed to mark todo done: {e}")

def run_task(task):
    try:
        if 'xcodebuild' in task:
            result = subprocess.run(task, shell=True, capture_output=True, text=True)
            log(f"[TASK] Ran: {task}\nOutput: {result.stdout}\nErrors: {result.stderr}")
            if result.returncode != 0:
                raise Exception(result.stderr)
        else:
            result = subprocess.run(task, shell=True, capture_output=True, text=True)
            log(f"[TASK] Ran: {task}\nOutput: {result.stdout}\nErrors: {result.stderr}")
            if result.returncode != 0:
                raise Exception(result.stderr)
    except Exception as e:
        log(f"[ERROR] Task failed: {e}")
        return False
    return True

def main():
    todos = read_todos()
    for todo in todos:
        if todo.get('done'):
            continue
        task = todo.get('reply') or todo.get('prompt')
        log(f"[INFO] Starting task: {task}")
        # Example: trigger xcodebuild if task mentions build
        if 'build' in task.lower():
            build_cmd = "xcodebuild -project xcode-project/MyApp.xcodeproj -scheme MyApp -destination 'platform=macOS'"
            if run_task(build_cmd):
                mark_todo_done(todo)
        # Add more task triggers as needed
        else:
            # For now, just mark as done after logging
            mark_todo_done(todo)
            log(f"[INFO] Marked as done: {task}")

if __name__ == "__main__":
    main()
