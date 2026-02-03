#!/usr/bin/env python3
"""
agent_performance_monitor.py

Real-time performance monitor for Hungry agent system.
Watches inbox/outbox, tracks metrics, detects Ollama status.
Run as: python3 agent_performance_monitor.py
"""
import os
import json
import time
from datetime import datetime
from pathlib import Path
import threading
import requests

class AgentPerformanceMonitor:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.ipc_dir = self.project_root / 'local-agent-vscode' / 'ipc'
        self.inbox_file = self.ipc_dir / 'inbox.jsonl'
        self.outbox_file = self.ipc_dir / 'outbox.jsonl'
        self.metrics_file = self.project_root / 'performance_metrics.jsonl'
        self.lock = threading.Lock()
        self.last_inbox_size = 0
        self.last_outbox_size = 0
        self.response_times = []
        self.error_count = 0
        self.ollama_status = "unknown"
        
    def _read_jsonl(self, filepath):
        """Read JSONL file and return list of parsed objects"""
        if not filepath.exists():
            return []
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
            results = []
            for line in lines:
                if line.strip():
                    try:
                        results.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
            return results
        except Exception as e:
            print(f"[Monitor] Error reading {filepath}: {e}")
            return []
    
    def _check_ollama(self):
        """Check if Ollama is running"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            self.ollama_status = "up" if response.status_code == 200 else "down"
        except:
            self.ollama_status = "down"
        return self.ollama_status
    
    def _calculate_metrics(self):
        """Calculate performance metrics"""
        inbox_msgs = self._read_jsonl(self.inbox_file)
        outbox_msgs = self._read_jsonl(self.outbox_file)
        
        inbox_count = len(inbox_msgs)
        outbox_count = len(outbox_msgs)
        
        # Prompts processed = prompts that got responses
        prompts_processed_per_min = (outbox_count - self.last_outbox_size) * 12  # 5 second intervals * 12
        avg_response_time = 0
        
        if outbox_msgs:
            # Calculate response times
            times = []
            for msg in outbox_msgs:
                if 'eta_seconds' in msg:
                    times.append(msg['eta_seconds'])
            if times:
                avg_response_time = sum(times) / len(times)
        
        # Error rate
        error_count = sum(1 for msg in outbox_msgs if msg.get('cpu_percent', 0) > 80 or 'error' in str(msg).lower())
        error_rate = (error_count / max(outbox_count, 1)) * 100 if outbox_count > 0 else 0
        
        self.last_inbox_size = inbox_count
        self.last_outbox_size = outbox_count
        
        return {
            'timestamp': datetime.now().isoformat(),
            'inbox_size': inbox_count,
            'outbox_size': outbox_count,
            'prompts_per_min': prompts_processed_per_min,
            'avg_response_time_s': round(avg_response_time, 2),
            'error_rate_percent': round(error_rate, 2),
            'ollama_status': self.ollama_status
        }
    
    def _write_metrics(self, metrics):
        """Write metrics to JSON Lines file"""
        try:
            with open(self.metrics_file, 'a') as f:
                f.write(json.dumps(metrics) + '\n')
        except Exception as e:
            print(f"[Monitor] Error writing metrics: {e}")
    
    def run(self):
        """Main monitor loop"""
        print("[AgentPerformanceMonitor] Started. Monitoring every 5 seconds.")
        print(f"[AgentPerformanceMonitor] Inbox: {self.inbox_file}")
        print(f"[AgentPerformanceMonitor] Outbox: {self.outbox_file}")
        print(f"[AgentPerformanceMonitor] Metrics: {self.metrics_file}")
        
        while True:
            try:
                with self.lock:
                    # Check Ollama
                    self._check_ollama()
                    
                    # Calculate and log metrics
                    metrics = self._calculate_metrics()
                    self._write_metrics(metrics)
                    
                    # Print to console
                    print(f"[Monitor] {metrics['timestamp']} | "
                          f"Prompts: {metrics['inbox_size']} in, {metrics['outbox_size']} out | "
                          f"Resp: {metrics['avg_response_time_s']}s | "
                          f"Errors: {metrics['error_rate_percent']}% | "
                          f"Ollama: {metrics['ollama_status']}")
                
                time.sleep(5)
            except Exception as e:
                print(f"[Monitor] Error in main loop: {e}")
                time.sleep(5)

if __name__ == "__main__":
    monitor = AgentPerformanceMonitor()
    try:
        monitor.run()
    except KeyboardInterrupt:
        print("\n[AgentPerformanceMonitor] Stopped.")
