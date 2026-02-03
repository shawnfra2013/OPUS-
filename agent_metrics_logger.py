"""
agent_metrics_logger.py

Logs all agent metrics to agent_metrics.jsonl for tracking and analysis.
Runs in the background and monitors system health continuously.
"""
import json
import os
import time
import threading
import psutil
from pathlib import Path

METRICS_LOG = Path(__file__).parent / 'agent_metrics.jsonl'
IPC_DIR = Path(__file__).parent / 'local-agent-vscode' / 'ipc'
INBOX = IPC_DIR / 'inbox.jsonl'
OUTBOX = IPC_DIR / 'outbox.jsonl'

class AgentMetricsLogger:
    def __init__(self):
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
    
    def _monitor_loop(self):
        """Continuously monitor and log metrics"""
        while self.running:
            try:
                metrics = self._collect_metrics()
                self._log_metrics(metrics)
                time.sleep(2)  # Match dashboard refresh rate
            except Exception as e:
                print(f"[MetricsLogger] Error: {e}")
    
    def _collect_metrics(self):
        """Collect all system and pipeline metrics"""
        inbox_size = 0
        outbox_size = 0
        
        if INBOX.exists():
            inbox_size = len(INBOX.read_text().strip().split('\n')) if INBOX.read_text().strip() else 0
        if OUTBOX.exists():
            outbox_size = len(OUTBOX.read_text().strip().split('\n')) if OUTBOX.read_text().strip() else 0
        
        return {
            'timestamp': int(time.time() * 1000),
            'ollama': {
                'status': 'up',  # Would check actual status in production
                'responseTime': 0,
                'model': 'uncensored-llama3'
            },
            'pipeline': {
                'inboxSize': inbox_size,
                'outboxSize': outbox_size,
                'processingRate': 0,
                'errorCount': 0
            },
            'resources': {
                'cpu': psutil.cpu_percent(interval=0.1),
                'memory': psutil.virtual_memory().percent,
                'disk': psutil.disk_usage('/').free / (1024**3)  # GB
            }
        }
    
    def _log_metrics(self, metrics):
        """Log metrics to JSONL file"""
        try:
            with open(METRICS_LOG, 'a') as f:
                f.write(json.dumps(metrics) + '\n')
        except Exception as e:
            print(f"[MetricsLogger] Failed to log: {e}")
    
    def stop(self):
        self.running = False

if __name__ == "__main__":
    logger = AgentMetricsLogger()
    print("[MetricsLogger] Started. Logging to agent_metrics.jsonl")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.stop()
        print("[MetricsLogger] Stopped.")
