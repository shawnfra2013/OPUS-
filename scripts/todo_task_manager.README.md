# scripts/todo_task_manager.py

## Purpose
Manages the agent's todo list, triggers builds/tasks, and sends macOS notifications.

## Hooks & Debug Features
- Error handling for file I/O and subprocess calls
- Notification hook for all major events
- Can be extended with task timeout, retry, and cancellation hooks

## Usage
- Read and update todos from agent_memory.json
- Trigger builds and send notifications

## Future Directions
- Add task timeout and retry logic
- Add dependency tracking and cancellation
- Add anomaly detection and resource usage hooks
