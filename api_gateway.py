"""
API Gateway - Smart API calling for autonomous agents

The model decides WHEN to call APIs based on need:
- HuggingFace: For model recommendations, dataset lookups, better models
- GitHub: For code patterns, dependencies, similar solutions
- Can be extended: OpenAI, Anthropic, etc.

Usage: Model checks "should I call an API?" and decides autonomously.
"""

import os
import json
import requests
from typing import Optional, Dict, Any
from datetime import datetime
from token_manager import get_token

class APIGateway:
    """Smart API gateway that models can call when needed."""
    
    def __init__(self):
        """Load tokens from environment."""
        self.huggingface_token = get_token("huggingface")
        self.github_token = get_token("github")
        self.openai_token = get_token("openai")
        self.api_log = "api_calls.jsonl"
        
    def _log_api_call(self, service: str, endpoint: str, success: bool, response_size: int):
        """Log API calls for monitoring."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "endpoint": endpoint,
            "success": success,
            "response_size": response_size
        }
        with open(self.api_log, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    # ============ HuggingFace API ============
    
    def find_best_model(self, task: str, constraints: Optional[Dict] = None) -> Optional[Dict]:
        """
        Find best model for task on HuggingFace.
        
        Args:
            task: What model needed for (e.g., "text-generation", "summarization")
            constraints: Optional {max_size: "small", min_score: 0.8, ...}
        
        Returns:
            {model_name, score, url, size, description} or None if error
        """
        if not self.huggingface_token:
            return None
            
        try:
            headers = {"Authorization": f"Bearer {self.huggingface_token}"}
            url = f"https://huggingface.co/api/models?filter={task}&sort=downloads"
            
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            
            models = response.json()
            if not models:
                self._log_api_call("huggingface", f"find_model/{task}", False, 0)
                return None
            
            # Filter by constraints if provided
            best = models[0]
            if constraints and constraints.get("max_size") == "small":
                best = next((m for m in models if m.get("gated") == False), best)
            
            result = {
                "model_name": best.get("modelId"),
                "score": best.get("likes", 0),
                "url": f"https://huggingface.co/{best.get('modelId')}",
                "downloads": best.get("downloads", 0),
                "task": task
            }
            
            self._log_api_call("huggingface", f"find_model/{task}", True, len(json.dumps(models)))
            return result
            
        except Exception as e:
            self._log_api_call("huggingface", f"find_model/{task}", False, 0)
            return None
    
    def search_datasets(self, query: str) -> Optional[list]:
        """
        Find datasets on HuggingFace for reference.
        
        Args:
            query: What dataset needed (e.g., "python code")
        
        Returns:
            [{dataset_name, url, size, description}, ...] or None
        """
        if not self.huggingface_token:
            return None
            
        try:
            headers = {"Authorization": f"Bearer {self.huggingface_token}"}
            url = f"https://huggingface.co/api/datasets?search={query}&sort=downloads"
            
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            
            datasets = response.json()
            results = [
                {
                    "name": d.get("id"),
                    "url": f"https://huggingface.co/datasets/{d.get('id')}",
                    "downloads": d.get("downloads", 0)
                }
                for d in datasets[:5]  # Top 5 results
            ]
            
            self._log_api_call("huggingface", f"search_datasets", True, len(json.dumps(results)))
            return results
            
        except Exception as e:
            self._log_api_call("huggingface", f"search_datasets", False, 0)
            return None
    
    # ============ GitHub API ============
    
    def find_code_examples(self, query: str, language: str = "python") -> Optional[list]:
        """
        Find code examples on GitHub for reference/learning.
        
        Args:
            query: What to search for (e.g., "autonomous agent")
            language: Programming language
        
        Returns:
            [{repo, url, stars, description}, ...] or None
        """
        if not self.github_token:
            return None
            
        try:
            headers = {"Authorization": f"token {self.github_token}"}
            search_query = f"{query} language:{language}"
            url = "https://api.github.com/search/repositories"
            params = {
                "q": search_query,
                "sort": "stars",
                "order": "desc",
                "per_page": 5
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            results = [
                {
                    "repo": item.get("full_name"),
                    "url": item.get("html_url"),
                    "stars": item.get("stargazers_count"),
                    "description": item.get("description"),
                    "language": item.get("language")
                }
                for item in data.get("items", [])
            ]
            
            self._log_api_call("github", f"search_code", True, len(json.dumps(results)))
            return results
            
        except Exception as e:
            self._log_api_call("github", f"search_code", False, 0)
            return None
    
    def check_github_trending(self) -> Optional[list]:
        """
        Check trending repos relevant to AI/automation.
        
        Returns:
            [{repo, url, stars, description}, ...] or None
        """
        if not self.github_token:
            return None
            
        try:
            headers = {"Authorization": f"token {self.github_token}"}
            url = "https://api.github.com/search/repositories"
            params = {
                "q": "stars:>1000 topic:autonomous-agents created:>2024-01-01",
                "sort": "stars",
                "order": "desc",
                "per_page": 5
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            results = [
                {
                    "repo": item.get("full_name"),
                    "url": item.get("html_url"),
                    "stars": item.get("stargazers_count"),
                    "description": item.get("description")
                }
                for item in data.get("items", [])
            ]
            
            self._log_api_call("github", f"trending", True, len(json.dumps(results)))
            return results
            
        except Exception as e:
            self._log_api_call("github", f"trending", False, 0)
            return None
    
    # ============ Decision Logic ============
    
    def should_call_api(self, context: str, query_type: str) -> bool:
        """
        Model decides: Should I call an API right now?
        
        This is called BY the model to decide autonomously.
        
        Args:
            context: What the model is working on
            query_type: "find_model", "find_code", "search_dataset", "trending"
        
        Returns:
            True if model should call API, False otherwise
        """
        # Don't call if tokens missing
        if query_type == "find_model" and not self.huggingface_token:
            return False
        if query_type in ["find_code", "trending"] and not self.github_token:
            return False
        
        # Smart decisions: when is API call worth it?
        decisions = {
            "find_model": "need better" in context.lower() or "recommend" in context.lower(),
            "find_code": "how do" in context.lower() or "example" in context.lower(),
            "search_dataset": "data" in context.lower() or "dataset" in context.lower(),
            "trending": "improve" in context.lower() or "optimize" in context.lower()
        }
        
        return decisions.get(query_type, False)
    
    def api_cost_estimate(self, query_type: str) -> Dict[str, Any]:
        """
        Before calling API, estimate cost and benefit.
        
        Model can use this to decide if API call is worth it.
        
        Returns:
            {call_cost: seconds, likely_value: "high"|"medium"|"low", tokens_used: int}
        """
        estimates = {
            "find_model": {"call_cost": 2, "value": "high", "tokens": 500},
            "find_code": {"call_cost": 3, "value": "medium", "tokens": 1000},
            "search_dataset": {"call_cost": 2, "value": "medium", "tokens": 800},
            "trending": {"call_cost": 3, "value": "low", "tokens": 1200}
        }
        return estimates.get(query_type, {"call_cost": 5, "value": "unknown", "tokens": 2000})


def get_gateway() -> APIGateway:
    """Get API gateway instance."""
    return APIGateway()
