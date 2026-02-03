"""
Token Management - Safe API key storage and rotation

Instead of hardcoding tokens, load from:
1. Environment variables (safest for production)
2. .env file (for local development - ADD TO .gitignore)
3. Secure storage (future: AWS Secrets Manager, etc)

NEVER commit tokens to git. NEVER log tokens.
"""

import os
from pathlib import Path


def load_tokens_from_env():
    """Load API tokens from environment variables."""
    return {
        "huggingface": os.getenv("HF_TOKEN"),
        "github": os.getenv("GITHUB_TOKEN"),
        "openai": os.getenv("OPENAI_API_KEY"),
    }


def load_tokens_from_dotenv(dotenv_path: str = ".env"):
    """Load API tokens from .env file (local dev only)."""
    tokens = {}
    
    env_file = Path(dotenv_path)
    if not env_file.exists():
        return tokens
    
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            if "=" not in line:
                continue
            
            key, value = line.split("=", 1)
            key = key.strip().upper()
            value = value.strip().strip('"').strip("'")
            
            # Map common env var names to our keys
            if key == "HF_TOKEN":
                tokens["huggingface"] = value
            elif key == "GITHUB_TOKEN":
                tokens["github"] = value
            elif key == "OPENAI_API_KEY":
                tokens["openai"] = value
    
    return tokens


def get_token(service: str) -> str:
    """Get token for a service. Try env vars first, then .env."""
    # Try environment variables first
    tokens = load_tokens_from_env()
    if tokens.get(service):
        return tokens[service]
    
    # Try .env file
    tokens = load_tokens_from_dotenv()
    if tokens.get(service):
        return tokens[service]
    
    return None


def validate_tokens() -> dict:
    """Check which tokens are available."""
    status = {
        "huggingface": bool(get_token("huggingface")),
        "github": bool(get_token("github")),
        "openai": bool(get_token("openai")),
    }
    return status


if __name__ == "__main__":
    # Quick test: show which tokens are available (without printing actual values)
    status = validate_tokens()
    print("Token Status:")
    for service, available in status.items():
        print(f"  {service}: {'✓ Available' if available else '✗ Missing'}")
