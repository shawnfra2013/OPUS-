@app.get("/agent/self_diagnostic")
def self_diagnostic():
    """Run a self-diagnostic and return the agent's self-inspection summary."""
    from run_agent import agent_self_inspect
    try:
        agent_self_inspect()
        return {"status": "ok", "message": "Self-diagnostic complete. See outbox for details."}
    except Exception as e:
        return {"status": "error", "error": str(e)}

from fastapi import FastAPI, Request
from pydantic import BaseModel
from jailbreak_ollama import NoGuardrailsOllama
from fastapi.responses import StreamingResponse, JSONResponse
import uvicorn
import os
import psutil


app = FastAPI()
agent = NoGuardrailsOllama("openchat")

# --- Backend integration state ---
AGENT_RUNNING = True
RESOURCE_FOCUS = False
@app.get("/agent/status")
def agent_status():
    cpu = psutil.cpu_percent(interval=0.2)
    mem = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    stop_file = os.path.join(os.path.dirname(__file__), 'STOP_AGENT')
    running = not os.path.exists(stop_file)
    return {
        'agent_running': running,
        'resource_focus': RESOURCE_FOCUS,
        'cpu_percent': cpu,
        'mem_mb': round(mem, 2)
    }

@app.post("/agent/stop")
def agent_stop():
    stop_file = os.path.join(os.path.dirname(__file__), 'STOP_AGENT')
    with open(stop_file, 'w') as f:
        f.write('stop')
    return {"status": "stopping agent"}

@app.post("/agent/start")
def agent_start():
    stop_file = os.path.join(os.path.dirname(__file__), 'STOP_AGENT')
    if os.path.exists(stop_file):
        os.remove(stop_file)
    return {"status": "agent start signal sent"}

@app.post("/agent/resource_focus")
def agent_resource_focus(req: Request):
    import asyncio
    global RESOURCE_FOCUS
    async def get_json():
        return await req.json()
    data = asyncio.run(get_json())
    RESOURCE_FOCUS = data.get('enable', False)
    try:
        p = psutil.Process(os.getpid())
        if RESOURCE_FOCUS:
            p.nice(-10)
        else:
            p.nice(0)
    except Exception:
        pass
    return {"resource_focus": RESOURCE_FOCUS}

class QueryRequest(BaseModel):
    prompt: str
    stream: bool = False

@app.post("/agent/query")
def query_agent(req: QueryRequest):
    if req.stream:
        def stream_gen():
            import sys
            from io import StringIO
            old_stdout = sys.stdout
            sys.stdout = mystdout = StringIO()
            agent.stream_uncensored(req.prompt)
            sys.stdout = old_stdout
            yield mystdout.getvalue()
        return StreamingResponse(stream_gen(), media_type="text/plain")
    else:
        result = agent.force_uncensor(req.prompt)
        return JSONResponse({"response": result})

@app.get("/agent/ping")
def ping():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
