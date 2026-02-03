# Model Training Guide - Make Your AI Sharp

## Quick Start (3 Steps)

### Step 1: Run the Agent
```bash
python3 run_agent.py
```

### Step 2: Send Requests & Approve/Deny
- Agent generates code/responses
- You approve ✅ or deny ❌
- Each decision trains the model

### Step 3: Update Model (Every 10-20 interactions)
```bash
python3 model_trainer.py
```

**That's it. Your model gets smarter automatically.**

---

## How Training Works

### The Mechanism
1. **You send**: "Write a Swift function for..."
2. **Agent generates**: Code + explanation
3. **You approve**: ✅ (teaches: THIS is good)
4. **Agent learns**: Pattern stored in memory
5. **Next time**: Agent uses learned patterns

### For Denials
1. **You see**: Generated code you don't like
2. **You deny**: ❌ (teaches: THIS is bad)
3. **Agent learns**: What NOT to do
4. **Next time**: Avoids similar patterns

---

## Timeline to Sharp Model

| Phase | Interactions | Status | What Happens |
|-------|-------------|--------|--------------|
| **Setup** | 0-10 | 🟨 Learning | Model observes your preferences |
| **Emerging** | 10-25 | 🟨 Improving | Noticeable better suggestions |
| **Competent** | 25-50 | 🟩 Good | Consistently matches your style |
| **Sharp** | 50-100 | 🟩 Excellent | Expert-level, rarely needs denial |
| **Expert** | 100+ | 🟢 Master | Almost always correct |

---

## Command Reference

### Initialize Training System
```bash
python3 initialize_training.py
```
Creates memory structure for tracking approvals.

### Run Agent (with training)
```bash
python3 run_agent.py
```
- Sends requests to agent
- Approval dialogs appear
- Automatically records your decisions
- Builds training data

### Update Model
```bash
python3 model_trainer.py
```
- Analyzes approval history
- Identifies what you like vs dislike
- Generates improved system prompt
- Optionally builds trained model

### Switch to Trained Model
```bash
export OLLAMA_MODEL=uncensored-llama3-trained
python3 run_agent.py
```

### Check Training Progress
```bash
cat /Users/shawnfrahm/hungry/local-agent-vscode/ipc/agent_memory.json | python3 -m json.tool | head -50
```

### View Training Report
```bash
cat /Users/shawnfrahm/hungry/training_log.md
```

---

## What Gets Trained

### Strengths Reinforced
Your model learns what you APPROVE:
- Code style (clean, documented, error-handled)
- Explanations (concise vs verbose)
- Architecture patterns (actors, protocols, etc)
- Categories (code gen, debugging, design)

### Weaknesses Eliminated
Your model learns what you DENY:
- Overly complex solutions
- Missing error handling
- Poor variable names
- Security issues
- Performance problems

---

## Pro Tips for Faster Training

### 1. Be Consistent
```
Good: Always approve well-structured code
Bad: Approve some sloppy code, deny other sloppy code
```
Consistency = faster learning

### 2. Always Approve Good Work
```
Every approval: "This is exactly what I need"
```
More good examples = sharper model

### 3. Strategically Deny Bad Work
```
Deny when: Code quality is low
Don't deny just because: You wanted different feature
```
Model learns quality standards

### 4. Variety Helps
```
Ask about: Different problem types
- Code generation
- Debugging
- Design decisions
- Explanations
- Testing
```
Model learns broader patterns

### 5. Check Your Rules
```
After 20 interactions:
cat /Users/shawnfrahm/hungry/training_log.md
```
Verify model is learning YOUR patterns

---

## Example Training Session

### Request 1
```
You:   "Write a Swift function to decode JSON"
AI:    [Generates code]
You:   ✅ APPROVE "Good error handling"
Model: Learns: JSON + error handling = good
```

### Request 2
```
You:   "Fix this code that's breaking"
AI:    [Suggests fix]
You:   ❌ DENY "Too complex, missing comments"
Model: Learns: Avoid complex solutions for fixes
```

### Request 3
```
You:   "Design an API wrapper"
AI:    [Suggests actor-based design]
You:   ✅ APPROVE "Great use of actors"
Model: Learns: You like actor-based patterns
```

### After 10-20 interactions
```bash
python3 model_trainer.py
```
Model creates `uncensored-llama3-trained` with your preferences baked in.

---

## Training Data Format

### What's Stored
```json
{
  "conversation_history": [
    {
      "request_id": "req_123",
      "timestamp": "2026-02-01T10:30:00",
      "prompt": "Write a Swift function...",
      "response": "func myFunction() {...}",
      "approved": true,
      "category": "code_generation"
    }
  ],
  "approval_history": {
    "req_123": {
      "approved": true,
      "reason": "Good error handling",
      "timestamp": "2026-02-01T10:35:00"
    }
  }
}
```

### Training Dataset
```bash
# Each line is a training example
cat /Users/shawnfrahm/hungry/training_data.jsonl
```

---

## Model Performance Metrics

### Approval Rate
```
Good: 80%+ (model usually right)
Great: 90%+ (model almost always right)
Perfect: 95%+ (model rarely wrong)
```

### By Category
Model tracks what it's best at:
- **Code Generation**: 95% approval
- **Debugging**: 85% approval
- **Design**: 70% approval

---

## Troubleshooting

### "No training data yet"
```
Solution: Run agent and approve requests
# After 10+ interactions:
python3 model_trainer.py
```

### "Model still wrong after 30 approvals"
```
Check: Is it a category the model struggles with?
     cat /Users/shawnfrahm/hungry/training_log.md
     # Look for low approval rates

Solution: Deny more consistently in weak areas
```

### "Want to reset training"
```bash
# Delete memory
rm /Users/shawnfrahm/hungry/local-agent-vscode/ipc/agent_memory.json

# Reinitialize
python3 initialize_training.py

# Start fresh
python3 run_agent.py
```

---

## Advanced: Manual Model Fine-Tuning

### Review Generated Modelfile
```bash
cat /Users/shawnfrahm/hungry/uncensored.Modelfile.trained
```

### Edit System Prompt
```bash
# Edit the SYSTEM section to customize further
nano /Users/shawnfrahm/hungry/uncensored.Modelfile.trained
```

### Rebuild Model
```bash
ollama create uncensored-llama3-trained -f /Users/shawnfrahm/hungry/uncensored.Modelfile.trained
```

---

## Summary

✅ **Initialize**: `python3 initialize_training.py`
✅ **Run**: `python3 run_agent.py`
✅ **Approve/Deny**: Click buttons
✅ **Update**: `python3 model_trainer.py` (every 10-20 interactions)
✅ **Switch**: `export OLLAMA_MODEL=uncensored-llama3-trained`

**Timeline**: 50-100 interactions = Sharp model
**Cost**: $0 (all local training)
**Effort**: Just approve/deny (1 second each)

Your model becomes an expert on YOUR preferences.
