# Cloud Fallback Module

**Owner**: LLM provider abstraction | **Responsibility**: Seamless fallback from Ollama → OpenAI → Anthropic

## Purpose

Cloud Fallback provides **high availability** for the agent's LLM interface. When local Ollama is unavailable:
1. Automatically attempt OpenAI GPT-4
2. If OpenAI fails, try Anthropic Claude 3.5
3. Maintain identical request/response format across all providers
4. Enable agent to operate without local infrastructure

**Philosophy**: Ollama is preferred (local, fast, uncensored), but cloud ensures reliability.

## Architecture

```
Agent Prompt
    ↓
try: ollama.chat() [~5-13s]
    ├─ Success → Return JSON actions
    └─ Failure (timeout/not-running)
        ↓
    try: OpenAI GPT-4 [~3-5s]
        ├─ Success → Return JSON actions
        └─ Failure (rate-limit/auth)
            ↓
        try: Anthropic Claude 3.5 [~2-4s]
            ├─ Success → Return JSON actions
            └─ Failure → Log error, return empty actions
```

## Configuration

**File**: `.env` (git-ignored)

```ini
# Ollama (local, no auth needed)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=uncensored-llama3

# OpenAI (https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-proj-YOUR_OPENAI_KEY_HERE

# Anthropic (https://console.anthropic.com/api-keys)
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_ANTHROPIC_KEY_HERE
```

## Files

- **Location**: `cloud_fallback.py`
- **Used By**: `jailbreak_ollama.py` (force_uncensor method)
- **Activation**: Only when Ollama fails

## Core Methods

### \_\_init\_\_ (Constructor)

```python
fallback = CloudFallback()
# Loads .env automatically
# Initializes API clients
```

**Initialization Checklist**:
- ✅ Load OPENAI_API_KEY from .env
- ✅ Load ANTHROPIC_API_KEY from .env
- ✅ Load OLLAMA_HOST from .env (default: localhost:11434)
- ✅ Create OpenAI client
- ✅ Create Anthropic client
- ✅ Log configuration status

### chat (Main LLM Call with Fallback)

```python
response = fallback.chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Do something"}
    ],
    model="gpt-4",  # Optional, defaults to gpt-4
    temperature=0.7  # Optional
)
# Returns: {"content": "response text", "provider": "openai"}
```

**Returns**:
```json
{
  "content": "Agent's response text",
  "provider": "openai",  // Which service provided the response
  "model": "gpt-4",
  "usage": {
    "input_tokens": 50,
    "output_tokens": 100
  }
}
```

**Call Order**:
1. Try OpenAI (if API key set)
2. If fails, try Anthropic (if API key set)
3. If fails, raise exception

### stream_chat (Streaming Response)

```python
for chunk in fallback.stream_chat(
    messages=[...],
    model="gpt-4"
):
    print(chunk["content"], end="", flush=True)
```

**Yields** (one per token):
```json
{"content": "word", "provider": "openai"}
```

**Used By**: Real-time response streaming in webviews

## Provider Details

### OpenAI GPT-4

**Configuration**:
- Model: `gpt-4-turbo` (fallback: `gpt-4`)
- Temperature: 0.7 (creative but coherent)
- Max tokens: 4000

**Latency**: ~3-5 seconds first call, ~1-2s cached

**Costs**:
- Input: $0.01 / 1K tokens
- Output: $0.03 / 1K tokens
- Monthly estimate: $5-20 for agent usage

**API**: https://api.openai.com/v1/chat/completions

**Failure Modes**:
- RateLimitError → Log, try next
- AuthenticationError → Check .env key validity
- APIConnectionError → Network issue, try next
- Timeout (30s) → Log as slow, try next

### Anthropic Claude 3.5

**Configuration**:
- Model: `claude-3-5-sonnet-20241022`
- Temperature: 0.7
- Max tokens: 4096

**Latency**: ~2-4 seconds (faster than GPT-4)

**Costs**:
- Input: $0.003 / 1K tokens
- Output: $0.015 / 1K tokens
- Monthly estimate: $2-10 for agent usage

**API**: https://api.anthropic.com/v1/messages

**Failure Modes**:
- RateLimitError → Log, end fallback chain
- APIError → Log error details
- Timeout (30s) → Network issue

## Integration with Agent

**Called By**: `jailbreak_ollama.py` force_uncensor() method

```python
# In force_uncensor():
if not ollama_available:
    fallback = CloudFallback()
    response = fallback.chat(
        messages=self.messages,
        model="gpt-4"
    )
```

**Used In**: `run_agent.py` when Ollama unavailable

## Data Flow

**Prompt → Cloud Fallback → Action JSON**

1. `run_agent.py` calls `ollama.chat()`
2. Ollama timeout (> 15 seconds)
3. Fallback triggered
4. Try OpenAI → Success (return response)
5. Response parsed to JSON actions
6. Actions executed by agent_action_handler

## Error Handling

### Graceful Degradation

```python
try:
    # Try OpenAI
    return self._call_openai(messages, model)
except Exception as e:
    log_error(f"OpenAI failed: {e}")
    
    try:
        # Try Anthropic
        return self._call_anthropic(messages, model)
    except Exception as e:
        log_error(f"Anthropic failed: {e}")
        # Return empty response
        return {"content": "", "provider": "none"}
```

**Behavior**: Complete failure = empty response (agent handles gracefully)

### Timeout Handling

**Per-Provider Timeouts**:
- OpenAI: 30 seconds
- Anthropic: 30 seconds

**Global Fallback Timeout**: 60 seconds max (abandon, return error)

## Daemon Responsibilities

The Tinkerer Daemon should:

1. **Monitor API Key Health**
   - Verify keys are set in .env
   - Alert if key rotation detected
   - Test API keys monthly (make small call)

2. **Track Fallback Events**
   - Log when Ollama fails
   - Count fallback activations per day
   - Alert if > 10% of calls use cloud

3. **Cost Tracking**
   - Estimate monthly cloud API spend
   - Alert if spending > $50/month
   - Log token usage per provider

4. **Provider Health**
   - Monitor response times
   - Alert if OpenAI consistently slow (> 10s)
   - Test Anthropic monthly

## Known Behaviors

### ✅ Correct (Don't Change)

1. **OpenAI attempted before Anthropic**
   - Intentional: GPT-4 better for complex tasks
   - Cost tradeoff: Slightly higher price

2. **Exact 30-second timeout per provider**
   - Intentional: Prevent hanging agent
   - Rationale: Local Ollama should respond in 15s

3. **No retry logic**
   - Intentional: Move to next provider instead
   - Rationale: Provider likely down, don't repeat

### ⚠️ Watch For

1. **Empty response handling**
   - Agent doesn't error on empty cloud response
   - Verify agent continues gracefully

## Testing

**Manual Test**:
```bash
# Test OpenAI only
python3 -c "
from cloud_fallback import CloudFallback
cf = CloudFallback()
result = cf.chat([
    {'role': 'user', 'content': 'Say hello'}
])
print(result)
"

# Test Anthropic only
python3 -c "
from cloud_fallback import CloudFallback
cf = CloudFallback()
result = cf.chat(
    [{'role': 'user', 'content': 'Say hello'}],
    model='claude-3-5-sonnet-20241022'
)
print(result)
"
```

## Future Improvements

1. Add request caching (same prompt = instant response)
2. Add streaming text visualization
3. Add provider switching strategy (cost vs latency)
4. Add weekly cost report generation
5. Add provider availability dashboard
