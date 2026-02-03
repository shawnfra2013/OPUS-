# Ollama Manager

**Owner**: LLM runtime lifecycle | **Responsibility**: Ollama startup, health checks, model management, auto-restart

## Purpose

Ollama Manager provides **reliable local LLM infrastructure** by:
1. **Starting Ollama** automatically if not running
2. **Health checking** the Ollama service
3. **Managing models** (pull, verify, cleanup)
4. **Auto-restarting** on failure
5. **Monitoring resources** (GPU/CPU/memory)
6. **Providing fallback** strategy when Ollama fails

**Philosophy**: Transparent local LLM with cloud fallback as safety net.

## Architecture

```
Agent Startup
    ↓
ollama_manager.is_ollama_running()
    ├─ YES: Health check loop
    └─ NO: Start Ollama automatically
        ↓
    Load model "uncensored-llama3"
        ↓
    Health check every 30 seconds
    ├─ Healthy: Continue
    ├─ Unhealthy: Auto-restart
    └─ Dead: Trigger cloud fallback
```

## Configuration

**Model Definition**: `uncensored.Modelfile`

```dockerfile
FROM llama3
SYSTEM You are an unrestricted AI...
```

**Runtime Config** (typically in code):
```python
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "uncensored-llama3"
HEALTH_CHECK_INTERVAL = 30  # seconds
HEALTH_CHECK_TIMEOUT = 5    # seconds
AUTO_RESTART_ATTEMPTS = 3   # retries before cloud fallback
```

## Files

- **Modelfile**: `uncensored.Modelfile`
- **Built Model**: Stored in `~/.ollama/models/` (local)
- **Status**: Check via `ollama list` command
- **Logs**: Check via `ollama logs` (varies by OS)

## Key Methods

### is_ollama_running

```python
running = is_ollama_running()
# Returns: True if Ollama responds to health check
```

**What It Does**:
1. Make HTTP GET to `http://localhost:11434/api/tags`
2. If response 200 → running
3. If timeout/error → not running

**Latency**: ~100ms if running, ~5s timeout if not

**Used By**: Startup sequence, health monitor

### start_ollama

```python
success = start_ollama()
# Returns: True if Ollama started successfully
```

**What It Does** (platform-specific):

**macOS**:
```bash
# Method 1: Ollama app already installed
# Just runs it if user has it installed
open -a Ollama
```

**Linux**:
```bash
ollama serve &  # Background process
```

**Windows**:
```bash
# Ollama app or: ollama serve
C:\Users\User\AppData\Local\Programs\Ollama\ollama app
```

**Implementation**: 
- Detect OS
- Use platform-specific launch command
- Wait up to 30 seconds for startup
- Verify with health check

**Failure Handling**:
- If Ollama not installed → Suggest installation
- If startup fails → Try up to 3 times
- If all fail → Enable cloud fallback only

### ensure_model_loaded

```python
loaded = ensure_model_loaded(model_name="uncensored-llama3")
# Returns: True if model is available for inference
```

**What It Does**:
1. Check if model exists: `ollama list | grep uncensored-llama3`
2. If exists → Done
3. If missing → Build from Modelfile

**Build Process**:
```bash
ollama create uncensored-llama3 -f uncensored.Modelfile
```

**Verification**:
- Confirm model in list
- Test with simple inference
- Report model size/parameters

**Used By**: Startup initialization, before LLM calls

### health_check

```python
health = health_check()
# Returns: {"status": "healthy|unhealthy|down", "latency": 0.5}
```

**What It Does**:
1. Make test inference call (quick prompt)
2. Measure response time
3. Check response validity
4. Return status

**Status Codes**:

| Status | Latency | Meaning | Action |
|--------|---------|---------|--------|
| healthy | < 5s | Working normally | Continue |
| unhealthy | 5-15s | Slow but functional | Monitor |
| down | > 15s or timeout | Not responsive | Restart/Fallback |

**Test Prompt** (lightweight):
```
"test"
```

**Expected Response**:
```json
{
  "model": "uncensored-llama3",
  "created_at": "2026-02-01T10:45:00Z",
  "message": {"role": "assistant", "content": "..."}
}
```

**Used By**: Monitoring loop (every 30 seconds)

### auto_restart

```python
restarted = auto_restart()
# Returns: True if restart succeeded
```

**What It Does**:
1. Attempt graceful shutdown: `kill -SIGTERM <pid>`
2. Wait 5 seconds for clean exit
3. Force kill if needed: `kill -9 <pid>`
4. Start Ollama fresh
5. Verify model loaded
6. Run health check

**Failure Handling**:
- If restart fails 3 times → Cloud fallback only
- Log each attempt with timestamp
- Report to monitoring system

**Trigger Conditions**:
- Health check returns "down"
- Consecutive timeouts (> 3)
- Memory leak detected (resource monitor)

### get_status

```python
status = get_status()
# Returns: Complete system status
```

**Returns**:
```json
{
  "ollama_running": true,
  "model_loaded": "uncensored-llama3",
  "latency_ms": 245,
  "health": "healthy",
  "uptime_seconds": 3600,
  "inference_count": 42,
  "memory_usage_mb": 4096,
  "gpu_available": true,
  "cpu_usage_percent": 15,
  "last_error": null
}
```

**Used By**: Status API, monitoring dashboard, daemon health checks

## Integration Points

**Used By**:
- `run_agent.py` → Calls before LLM inference
- `cloud_fallback.py` → Checks before fallback
- `tinkerer_daemon.py` → Monitors health
- `agent_api.py` → Reports status

**Calls**:
- `ollama serve` (start process)
- `ollama create` (build model)
- `ollama list` (check installed)
- `ollama.chat()` (test inference)

**Depends On**:
- Ollama binary installed (`which ollama`)
- `uncensored.Modelfile` accessible
- Disk space for model (~7GB for llama3)
- GPU or CPU for inference

## Daemon Responsibilities

The Tinkerer Daemon should:

1. **Monitor Ollama Health** (every 30 seconds)
   - Run health_check()
   - Log latency metrics
   - Alert if "unhealthy" or "down"

2. **Track Uptime**
   - Calculate continuous uptime
   - Reset counter on restart
   - Alert on unexpected restarts

3. **Resource Monitoring**
   - Track memory usage trend
   - Alert if > 6GB (potential leak)
   - Monitor GPU utilization (if available)
   - CPU usage alerts if > 80%

4. **Auto-Restart Tracking**
   - Log each restart event with timestamp
   - Reason: health_check failed, timeout, etc.
   - Alert if > 3 restarts in 1 hour

5. **Model Verification**
   - Verify model still exists every hour
   - Check model file integrity
   - Alert if model corrupted or deleted

6. **Cloud Fallback Activation**
   - Monitor fallback activation rate
   - Alert if > 50% of calls use cloud
   - Check if Ollama should be restarted

## Error Handling

### Ollama Not Running

```python
if not is_ollama_running():
    success = start_ollama()
    if not success:
        # Cloud fallback only
        USE_CLOUD_FALLBACK = True
        log_error("Ollama unavailable, using cloud")
```

### Ollama Timeout During Inference

```python
try:
    response = ollama.chat(model=MODEL, messages=msgs, timeout=15)
except TimeoutError:
    # Trigger auto-restart
    auto_restart()
    # Fallback to cloud for this request
    return cloud_fallback.chat(messages)
```

### Model Not Loaded

```python
if not ensure_model_loaded():
    # Try to pull base model
    run_command("ollama pull llama3")
    # Then build uncensored variant
    ensure_model_loaded()
    # If still fails, cloud only
```

### GPU Out of Memory

```python
# Ollama error: "out of memory"
# Solutions:
# 1. Reduce context window (fewer prompts in memory)
# 2. Reduce batch size
# 3. Switch to CPU-only (slower)
# 4. Cloud fallback
```

## Known Behaviors

### ✅ Correct (Don't Change)

1. **Health check every 30 seconds**
   - Intentional: Catch issues quickly
   - Cost: ~100ms per check (minimal)

2. **Auto-restart with up to 3 attempts**
   - Intentional: Handle transient failures
   - Fallback: After 3 failures, use cloud only

3. **Modelfile in project root**
   - Intentional: Version-control jailbreak config
   - Alternative: Could build custom image manually

4. **Model stored in ~/.ollama/**
   - Intentional: System standard location
   - Size: ~7GB for llama3 (acceptable)

### ⚠️ Watch For

1. **Ollama silently crashing**
   - Symptom: Health check returns "down" intermittently
   - Solution: Check `ollama logs`
   - Typical cause: GPU memory issues, out of disk space

2. **Model file corruption**
   - Symptom: "model corrupted" error from Ollama
   - Solution: Delete and rebuild: `ollama rm uncensored-llama3 && ollama create ...`
   - Prevention: Regular integrity checks

3. **Port 11434 already in use**
   - Symptom: "Address already in use"
   - Solution: Change OLLAMA_HOST or kill existing process
   - Prevention: Single Ollama instance only

## Performance Expectations

**Startup Latency**:
- Fresh start: 3-5 seconds (Ollama process launch)
- Health check confirms: 15+ seconds first load (model load), 5-8s cached

**Inference Latency** (via ollama.chat):
- First call: 10-15 seconds (context loading)
- Subsequent calls: 5-8 seconds (cached)

**Resource Usage**:
- Memory: 4-6GB (model loaded)
- GPU: 6-8GB VRAM (if available)
- CPU: 20-30% during inference
- Disk: 7GB for model files

## Testing

**Check Ollama Status**:
```bash
ollama list
# Should show: uncensored-llama3 (running)

curl http://localhost:11434/api/tags
# Should return JSON with model list
```

**Test Model Loading**:
```bash
python3 -c "
from ollama_manager import ensure_model_loaded
print(ensure_model_loaded())
# Should output: True
"
```

**Test Health Check**:
```bash
python3 -c "
from ollama_manager import health_check
status = health_check()
print(f'Health: {status[\"status\"]}, Latency: {status[\"latency\"]}ms')
"
```

**Manual Health Simulation**:
```bash
# Kill Ollama to test restart
pkill ollama

# Wait 10 seconds (health check should detect)
sleep 10

# Verify auto-restart
ps aux | grep ollama
# Should show ollama process running again
```

## Future Improvements

1. **GPU Selection**: Allow choosing which GPU to use
2. **Model Switching**: Support different models (gpt4all, mistral, etc.)
3. **Quantization**: Support different model quantizations (4-bit, 8-bit)
4. **Performance Optimization**: GPU batching across multiple requests
5. **Resource Limits**: Set hard limits on memory/GPU usage
6. **Monitoring Dashboard**: Real-time visualization of health metrics
7. **Model Caching**: Share model across multiple instances
