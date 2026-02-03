# agent_task_runner.py

## Purpose
Monitors the agent pipeline, manages prompt queue, and logs agent replies.

## Hooks & Debug Features
- Start/end hooks for task monitoring
- Error handling for outbox parsing
- Can be extended with heartbeat, fork/branch, and completion callback hooks

## Usage
- Monitor outbox for new replies
- Log agent replies and errors

## Future Directions
- Add heartbeat and health check
- Add fork/branch and completion callback hooks
- Add resource usage and anomaly detection
