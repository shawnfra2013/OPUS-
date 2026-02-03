"""
ollama_manager.py

Auto-start and monitor Ollama service.
Detects when Ollama is down and attempts to restart it.
"""
import subprocess
import time
import requests
import os

OLLAMA_HOST = "http://localhost:11434"

class OllamaManager:
    @staticmethod
    def is_running():
        try:
            response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    @staticmethod
    def start():
        """Attempt to start Ollama service"""
        if OllamaManager.is_running():
            print("[OllamaManager] Ollama already running.")
            return True
        
        print("[OllamaManager] Starting Ollama...")
        try:
            # Try to start Ollama in background
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            # Wait up to 10 seconds for Ollama to start
            for i in range(10):
                time.sleep(1)
                if OllamaManager.is_running():
                    print("[OllamaManager] Ollama started successfully.")
                    return True
            print("[OllamaManager] Ollama failed to start within 10 seconds.")
            return False
        except Exception as e:
            print(f"[OllamaManager] Failed to start Ollama: {e}")
            return False
    
    @staticmethod
    def ensure_running():
        """Ensure Ollama is running, start if needed"""
        if not OllamaManager.is_running():
            return OllamaManager.start()
        return True
