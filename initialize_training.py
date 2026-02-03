#!/usr/bin/env python3
"""
Model Training Starter - Initialize training system

Sets up automated model training based on approval history.
Run the agent and approve/deny requests - this will collect training data automatically.
"""

import json
from pathlib import Path
from datetime import datetime


def initialize_training_system():
    """Initialize memory structure for training."""
    
    memory_path = Path("/Users/shawnfrahm/hungry/local-agent-vscode/ipc/agent_memory.json")
    
    # Create initial memory structure if it doesn't exist
    if not memory_path.exists():
        initial_memory = {
            "initialized": datetime.now().isoformat(),
            "version": "2.0",
            "conversation_history": [],
            "approval_history": {},
            "training_stats": {
                "total_interactions": 0,
                "total_approved": 0,
                "total_denied": 0,
            },
            "model_info": {
                "base_model": "uncensored-llama3",
                "training_enabled": True,
            }
        }
        
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        with open(memory_path, 'w') as f:
            json.dump(initial_memory, f, indent=2)
        
        print(f"✅ Training system initialized at: {memory_path}")
    else:
        print(f"📂 Memory file exists: {memory_path}")
        with open(memory_path, 'r') as f:
            memory = json.load(f)
            history = memory.get("conversation_history", [])
            approved = len([h for h in history if h.get("approved")])
            total = len(history)
            print(f"   Current examples: {total}")
            print(f"   Approved: {approved}")
            print(f"   Denied: {total - approved}")
    
    print("\n🚀 TRAINING SYSTEM READY")
    print("=" * 60)
    print("\nHow to train your model:")
    print("\n1. Run the agent:")
    print("   python3 run_agent.py")
    print("\n2. Send requests and approve/deny them")
    print("   • Approvals teach model what's GOOD")
    print("   • Denials teach model what's BAD")
    print("\n3. After 10+ interactions, update model:")
    print("   python3 model_trainer.py")
    print("\n4. After 50-100 interactions, model gets SHARP")
    print("\n" + "=" * 60)
    print("\n📊 Training Progress:")
    print("   0-10:   Setup phase")
    print("   10-25:  Model learning patterns")
    print("   25-50:  Noticeable improvement")
    print("   50-100: Model is SHARP")
    print("   100+:   Expert-level performance")
    print("\n" + "=" * 60)
    print("\n💡 Pro Tips:")
    print("   • Be consistent with approvals (helps model learn faster)")
    print("   • Deny requests that don't match your style")
    print("   • The model learns from BOTH good AND bad examples")
    print("   • Training is free (all local, no tokens)")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    initialize_training_system()
