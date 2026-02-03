"""
cloud_fallback.py

Cloud API fallback for when Ollama is unavailable.
Supports OpenAI and Anthropic as backup LLM providers.
"""
import os
from pathlib import Path
import requests
import json

# Load .env file if present
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

class CloudFallback:
    """Fallback cloud LLM providers when Ollama is unavailable."""
    
    def __init__(self):
        self.openai_key = os.environ.get('OPENAI_API_KEY', '')
        self.anthropic_key = os.environ.get('ANTHROPIC_API_KEY', '')
    
    def is_available(self):
        """Check if any cloud API is configured."""
        return bool(self.openai_key or self.anthropic_key)
    
    def stream_openai(self, prompt, model="gpt-4"):
        """Stream response from OpenAI API."""
        if not self.openai_key:
            return
        
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                stream=True,
                timeout=30
            )
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        line = line[6:]
                        if line.strip() == '[DONE]':
                            break
                        try:
                            chunk = json.loads(line)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    yield content
                        except:
                            pass
        except Exception as e:
            print(f"[CloudFallback] OpenAI error: {e}")
    
    def stream_anthropic(self, prompt, model="claude-3-5-sonnet-20241022"):
        """Stream response from Anthropic API."""
        if not self.anthropic_key:
            return
        
        headers = {
            "x-api-key": self.anthropic_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096,
            "stream": True
        }
        
        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                stream=True,
                timeout=30
            )
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        line = line[6:]
                        try:
                            chunk = json.loads(line)
                            if chunk.get('type') == 'content_block_delta':
                                delta = chunk.get('delta', {})
                                content = delta.get('text', '')
                                if content:
                                    yield content
                        except:
                            pass
        except Exception as e:
            print(f"[CloudFallback] Anthropic error: {e}")
    
    def stream(self, prompt):
        """Try cloud providers in order: OpenAI, then Anthropic."""
        if self.openai_key:
            try:
                for chunk in self.stream_openai(prompt):
                    yield chunk
                return
            except Exception as e:
                print(f"[CloudFallback] OpenAI failed, trying Anthropic: {e}")
        
        if self.anthropic_key:
            try:
                for chunk in self.stream_anthropic(prompt):
                    yield chunk
                return
            except Exception as e:
                print(f"[CloudFallback] Anthropic failed: {e}")
        
        yield "[CloudFallback] No API keys configured."
