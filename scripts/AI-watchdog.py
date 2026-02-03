MODEL_CMD = ["python3", "model_trainer.py"]
MODEL_LOG = "/tmp/model_trainer.log"
def ensure_model_trainer():
    # If model_trainer.py is running, do nothing. If not, start it.
    if not is_running("model_trainer.py"):
        log_error("Model trainer not running, restarting...")
        start_process(MODEL_CMD, MODEL_LOG)
#!/usr/bin/env python3
"""
Watches Ollama and agent processes, restarts if dead, and logs errors to agent_debug.log.
"""
import subprocess
import time
import os
import signal

OLLAMA_CMD = ["ollama", "serve"]
AGENT_CMD = ["python3", "run_agent.py"]
OLLAMA_LOG = "/tmp/ollama.log"
AGENT_LOG = "/tmp/agent.log"
DEBUG_LOG = "agent_debug.log"
CHECK_INTERVAL = 5


def is_running(process_name):
    try:
        out = subprocess.check_output(["pgrep", "-f", process_name]).decode()
        return bool(out.strip())
    except Exception:
        return False

def start_process(cmd, log_file):
    with open(log_file, "a") as f:
        proc = subprocess.Popen(cmd, stdout=f, stderr=f)
    return proc

def log_error(msg):
    with open(DEBUG_LOG, "a") as f:
        f.write(f"[WATCHDOG] {time.ctime()}: {msg}\n")

if __name__ == "__main__":
    while True:
        # Ollama
        if not is_running("ollama"): 
            log_error("Ollama not running, restarting...")
            start_process(OLLAMA_CMD, OLLAMA_LOG)
        # Agent
        if not is_running("run_agent.py"):
            log_error("Agent not running, restarting...")
            start_process(AGENT_CMD, AGENT_LOG)
        # Model trainer
        ensure_model_trainer()
        time.sleep(CHECK_INTERVAL)
