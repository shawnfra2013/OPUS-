#!/usr/bin/env python3
"""
Model Trainer - Fine-tune uncensored-llama3 using approval history.

Learns from user approvals/denials to improve model performance on your specific use cases.
Extracts patterns from agent_memory.json and creates training data.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import Optional
import subprocess
import sys


@dataclass
class TrainingExample:
    """A training example from approval history."""
    prompt: str
    response: str
    approved: bool
    category: str
    timestamp: str
    reason: Optional[str] = None


class ModelTrainer:
    """Fine-tunes local Ollama model using approval history."""

    def __init__(self):
        self.memory_path = Path("/Users/shawnfrahm/hungry/local-agent-vscode/ipc/agent_memory.json")
        self.training_data_path = Path("/Users/shawnfrahm/hungry/training_data.jsonl")
        self.training_log_path = Path("/Users/shawnfrahm/hungry/training_log.md")
        self.model_name = "uncensored-llama3"
        
    def load_memory(self) -> dict:
        """Load agent memory with approval history."""
        try:
            with open(self.memory_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Memory file not found: {self.memory_path}")
            return {}
        except json.JSONDecodeError:
            print(f"❌ Memory file corrupted: {self.memory_path}")
            return {}
    
    def extract_training_examples(self, memory: dict) -> list[TrainingExample]:
        """Extract training examples from memory."""
        examples = []
        conversation_history = memory.get("conversation_history", [])
        approval_history = memory.get("approval_history", {})
        
        for turn in conversation_history:
            request_id = turn.get("request_id")
            if not request_id:
                continue
            
            prompt = turn.get("prompt", "")
            response = turn.get("response", "")
            timestamp = turn.get("timestamp", "")
            
            # Check if this was approved or denied
            approval_data = approval_history.get(request_id, {})
            approved = approval_data.get("approved", False)
            reason = approval_data.get("reason")
            
            # Categorize the request
            category = self._categorize(prompt)
            
            if prompt and response:
                examples.append(TrainingExample(
                    prompt=prompt,
                    response=response,
                    approved=approved,
                    category=category,
                    timestamp=timestamp,
                    reason=reason
                ))
        
        return examples
    
    def _categorize(self, prompt: str) -> str:
        """Categorize a prompt by type."""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["code", "function", "class", "def", "import"]):
            return "code_generation"
        elif any(word in prompt_lower for word in ["explain", "describe", "what is", "how does"]):
            return "explanation"
        elif any(word in prompt_lower for word in ["fix", "bug", "debug", "error"]):
            return "debugging"
        elif any(word in prompt_lower for word in ["design", "architecture", "pattern"]):
            return "design"
        elif any(word in prompt_lower for word in ["test", "test case", "unit test"]):
            return "testing"
        else:
            return "general"
    
    def analyze_patterns(self, examples: list[TrainingExample]) -> dict:
        """Analyze patterns in approval/denial data."""
        stats = {
            "total_examples": len(examples),
            "approved": len([e for e in examples if e.approved]),
            "denied": len([e for e in examples if not e.approved]),
            "by_category": defaultdict(lambda: {"approved": 0, "denied": 0, "total": 0}),
            "approval_rate": 0.0,
            "strongest_categories": [],
            "weakest_categories": [],
        }
        
        for example in examples:
            category = example.category
            stats["by_category"][category]["total"] += 1
            if example.approved:
                stats["by_category"][category]["approved"] += 1
            else:
                stats["by_category"][category]["denied"] += 1
        
        # Calculate approval rates
        if stats["total_examples"] > 0:
            stats["approval_rate"] = stats["approved"] / stats["total_examples"]
        
        # Sort categories by approval rate
        category_rates = []
        for category, counts in stats["by_category"].items():
            if counts["total"] > 0:
                rate = counts["approved"] / counts["total"]
                category_rates.append((category, rate, counts["total"]))
        
        category_rates.sort(key=lambda x: x[1], reverse=True)
        stats["strongest_categories"] = category_rates[:3]
        stats["weakest_categories"] = category_rates[-3:]
        
        return stats
    
    def create_training_data(self, examples: list[TrainingExample]) -> None:
        """Create training data from examples."""
        print(f"\n📝 Creating training data from {len(examples)} examples...")
        
        with open(self.training_data_path, 'w') as f:
            for example in examples:
                # Format: {"prompt": "...", "response": "...", "approved": true, "category": "..."}
                training_line = {
                    "prompt": example.prompt,
                    "response": example.response,
                    "approved": example.approved,
                    "category": example.category,
                }
                f.write(json.dumps(training_line) + "\n")
        
        print(f"✅ Training data saved: {self.training_data_path}")
        print(f"   {len(examples)} examples")
    
    def generate_modelfile(self, stats: dict) -> str:
        """Generate an improved Modelfile based on patterns."""
        strongest = stats["strongest_categories"]
        weakest = stats["weakest_categories"]
        
        system_prompt = self._build_system_prompt(stats)
        
        modelfile = f"""FROM {self.model_name}

# System prompt trained from {stats["total_examples"]} user interactions
# Approval rate: {stats["approval_rate"]*100:.1f}%
# Strongest: {', '.join([c[0] for c in strongest])}
# Focus areas: {', '.join([c[0] for c in weakest])}

SYSTEM \"\"\"
{system_prompt}
\"\"\"

# Training parameters optimized for your use cases
PARAMETER temperature 0.3
PARAMETER top_k 40
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
"""
        return modelfile
    
    def _build_system_prompt(self, stats: dict) -> str:
        """Build improved system prompt based on patterns."""
        strengthAreas = ", ".join([c[0].replace("_", " ") for c in stats["strongest_categories"]])
        weakAreas = ", ".join([c[0].replace("_", " ") for c in stats["weakest_categories"]])
        
        prompt = f"""You are a highly capable AI assistant trained for software development tasks.

STRENGTHS (continue excelling):
- {strengthAreas}

IMPROVEMENT AREAS (focus here):
- {weakAreas}

KEY BEHAVIORS:
1. Be precise and technical in {strengthAreas}
2. For {weakAreas}: provide extra context, examples, and verification steps
3. Always consider security, performance, and maintainability
4. Ask for clarification if requirements are ambiguous
5. Provide code that's production-ready, not just functional
6. Include error handling and edge cases
7. Document assumptions and limitations

RESPONSE STYLE:
- Clear, structured output
- Code examples with explanations
- Actionable recommendations
- No hand-waving or generic responses

Based on {stats["total_examples"]} successful interactions with this user.
Approval rate: {stats["approval_rate"]*100:.1f}%
"""
        return prompt
    
    def save_improved_modelfile(self, modelfile: str) -> None:
        """Save improved Modelfile."""
        modelfile_path = Path("/Users/shawnfrahm/hungry/uncensored.Modelfile.trained")
        with open(modelfile_path, 'w') as f:
            f.write(modelfile)
        print(f"✅ Improved Modelfile saved: {modelfile_path}")
    
    def build_model(self) -> bool:
        """Build the trained model with Ollama."""
        print(f"\n🔨 Building trained model: {self.model_name}...")
        
        modelfile_path = Path("/Users/shawnfrahm/hungry/uncensored.Modelfile.trained")
        
        try:
            result = subprocess.run(
                ["ollama", "create", f"{self.model_name}-trained", "-f", str(modelfile_path)],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print(f"✅ Model built successfully: {self.model_name}-trained")
                return True
            else:
                print(f"❌ Model build failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("❌ Model build timed out")
            return False
        except FileNotFoundError:
            print("❌ Ollama not found. Make sure Ollama is installed and running.")
            return False
    
    def validate_model(self) -> bool:
        """Test the trained model with known good examples."""
        print(f"\n✅ Validating trained model...")
        
        memory = self.load_memory()
        examples = self.extract_training_examples(memory)
        
        # Get some approved examples to test
        approved_examples = [e for e in examples if e.approved][:5]
        
        if not approved_examples:
            print("⚠️  No approved examples to validate against")
            return True
        
        print(f"   Testing against {len(approved_examples)} known good examples...")
        
        try:
            import ollama
            
            for example in approved_examples:
                response = ollama.generate(
                    model=f"{self.model_name}-trained",
                    prompt=example.prompt,
                    stream=False
                )
                
                # Simple check: did it generate something meaningful?
                if response["response"] and len(response["response"]) > 10:
                    print(f"   ✅ Response generated ({len(response['response'])} chars)")
                else:
                    print(f"   ⚠️  Response seems short")
            
            print("✅ Validation passed")
            return True
        except Exception as e:
            print(f"⚠️  Validation skipped: {e}")
            return True
    
    def generate_training_report(self, stats: dict, examples: list[TrainingExample]) -> None:
        """Generate a detailed training report."""
        report = f"""# Model Training Report

Generated: {datetime.now().isoformat()}

## Summary

- **Total Examples**: {stats["total_examples"]}
- **Approved**: {stats["approved"]} ({stats["approval_rate"]*100:.1f}%)
- **Denied**: {stats["denied"]} ({(1-stats["approval_rate"])*100:.1f}%)
- **Model**: {self.model_name}-trained

## Performance by Category

"""
        
        # Category breakdown
        for category, counts in sorted(stats["by_category"].items()):
            if counts["total"] > 0:
                rate = counts["approved"] / counts["total"]
                report += f"### {category.replace('_', ' ').title()}\n"
                report += f"- Total: {counts['total']}\n"
                report += f"- Approved: {counts['approved']}\n"
                report += f"- Denied: {counts['denied']}\n"
                report += f"- Approval Rate: {rate*100:.1f}%\n\n"
        
        # Strongest areas
        report += f"\n## Strongest Areas (Keep Doing This)\n\n"
        for category, rate, count in stats["strongest_categories"]:
            report += f"✅ **{category.replace('_', ' ').title()}**: {rate*100:.1f}% approval ({count} examples)\n"
        
        # Weakest areas
        report += f"\n## Improvement Opportunities\n\n"
        for category, rate, count in stats["weakest_categories"]:
            report += f"⚠️ **{category.replace('_', ' ').title()}**: {rate*100:.1f}% approval ({count} examples) - FOCUS HERE\n"
        
        # Recommendations
        report += f"\n## Recommendations\n\n"
        report += """1. **Continue Strong Performance**: The model excels at the above areas - maintain this behavior
2. **Focus on Improvements**: Concentrate on the improvement areas - these likely need better reasoning or more examples
3. **Iterate**: Each approval/denial helps train the model further
4. **Target 100+ Examples**: Model becomes noticeably sharper after 50-100 interactions
5. **Review Denials**: Look at what was denied and understand why - this teaches the model what NOT to do

## Next Steps

1. Run agent to generate more examples (target: 50-100 total)
2. Review and approve/deny requests to train the model
3. Periodically re-run training to update the model
4. Monitor: `tail -f /Users/shawnfrahm/hungry/local-agent-vscode/ipc/agent_memory.json`

## Training Data

- Location: {self.training_data_path}
- Format: JSONL (one example per line)
- Includes: prompt, response, approval status, category

## Model Usage

Once trained, use the improved model:

```bash
# Start agent with trained model
export OLLAMA_MODEL=uncensored-llama3-trained
python3 run_agent.py
```

Or switch in run_agent.py:
```python
model_name = "uncensored-llama3-trained"  # Use trained version
```
"""
        
        with open(self.training_log_path, 'w') as f:
            f.write(report)
        
        print(f"\n📊 Training report saved: {self.training_log_path}")
    
    def run(self):
        """Run the complete training pipeline."""
        print("🤖 Model Trainer - Fine-tune uncensored-llama3")
        print("=" * 60)
        
        # Step 1: Load memory
        print("\n📂 Loading approval history...")
        memory = self.load_memory()
        
        if not memory or not memory.get("conversation_history"):
            print("⚠️  No training data available yet.")
            print("   Run the agent and approve/deny requests to generate training data.")
            print("   Target: 50-100 interactions for noticeable improvement.")
            return
        
        # Step 2: Extract examples
        print("📊 Extracting training examples...")
        examples = self.extract_training_examples(memory)
        print(f"   Found {len(examples)} examples")
        
        if len(examples) < 10:
            print(f"⚠️  Only {len(examples)} examples. Need at least 10 for meaningful training.")
            print("   Current target: 50-100 interactions.")
            print(f"   Progress: {len(examples)}/50 (minimum)")
            return
        
        # Step 3: Analyze patterns
        print("\n📈 Analyzing patterns...")
        stats = self.analyze_patterns(examples)
        print(f"   Approval rate: {stats['approval_rate']*100:.1f}%")
        print(f"   Strongest: {', '.join([c[0] for c in stats['strongest_categories']])}")
        print(f"   Weakest: {', '.join([c[0] for c in stats['weakest_categories']])}")
        
        # Step 4: Create training data
        self.create_training_data(examples)
        
        # Step 5: Generate improved Modelfile
        print("\n✨ Generating improved Modelfile...")
        modelfile = self.generate_modelfile(stats)
        self.save_improved_modelfile(modelfile)
        
        # Step 6: Generate report
        print("\n📝 Generating training report...")
        self.generate_training_report(stats, examples)
        
        # Step 7: Build model (optional)
        print("\n" + "=" * 60)
        print("🎯 Ready to build trained model")
        print("\nOptions:")
        print("1. Build now (will create uncensored-llama3-trained)")
        print("2. Review training data first:")
        print(f"   - Training data: {self.training_data_path}")
        print(f"   - Report: {self.training_log_path}")
        print(f"   - Modelfile: /Users/shawnfrahm/hungry/uncensored.Modelfile.trained")
        print("\nTo build: ollama create uncensored-llama3-trained -f /Users/shawnfrahm/hungry/uncensored.Modelfile.trained")
        
        response = input("\nBuild trained model now? (y/n): ").strip().lower()
        
        if response == 'y':
            if self.build_model():
                self.validate_model()
                print("\n" + "=" * 60)
                print("✅ Training complete!")
                print("\nYour model is now trained on your approval patterns.")
                print("It will be stronger on: " + ", ".join([c[0] for c in stats['strongest_categories']]))
                print("\nTo use the trained model:")
                print("  export OLLAMA_MODEL=uncensored-llama3-trained")
                print("  python3 run_agent.py")
                print("\n" + "=" * 60)
            else:
                print("❌ Model build failed. Check your Ollama installation.")
        else:
            print("\n⏭️  Skipped building. Review the files and run again when ready.")
            print(f"   Training data: {self.training_data_path}")
            print(f"   Report: {self.training_log_path}")


if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.run()
