"""
websocket_ipc.py

Real-time WebSocket IPC server for instant agent communication.
Runs alongside file-based IPC for backward compatibility.
"""
import asyncio
import websockets
import json
import os
from pathlib import Path

IPC_DIR = Path(__file__).parent / 'local-agent-vscode' / 'ipc'
INBOX = IPC_DIR / 'inbox.jsonl'
OUTBOX = IPC_DIR / 'outbox.jsonl'

class WebSocketIPC:
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.last_outbox_size = 0
    
    async def register(self, websocket):
        self.clients.add(websocket)
        print(f"[WebSocketIPC] Client connected. Total: {len(self.clients)}")
    
    async def unregister(self, websocket):
        self.clients.remove(websocket)
        print(f"[WebSocketIPC] Client disconnected. Total: {len(self.clients)}")
    
    async def broadcast(self, message):
        if self.clients:
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )
    
    async def handle_client(self, websocket, path):
        await self.register(websocket)
        try:
            async for message in websocket:
                # Client sends prompt, write to inbox
                data = json.loads(message)
                if data.get('type') == 'userPrompt':
                    msg = {
                        'id': str(int(asyncio.get_event_loop().time() * 1000)),
                        'user': 'user',
                        'text': data.get('text', ''),
                        'timestamp': int(asyncio.get_event_loop().time() * 1000)
                    }
                    with open(INBOX, 'a') as f:
                        f.write(json.dumps(msg) + '\n')
                    print(f"[WebSocketIPC] Received prompt: {data.get('text', '')}")
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)
    
    async def monitor_outbox(self):
        """Monitor outbox and broadcast new replies to all clients"""
        while True:
            try:
                if OUTBOX.exists():
                    with open(OUTBOX, 'r') as f:
                        lines = f.readlines()
                    if len(lines) > self.last_outbox_size:
                        new_lines = lines[self.last_outbox_size:]
                        for line in new_lines:
                            try:
                                data = json.loads(line)
                                await self.broadcast(json.dumps({
                                    'type': 'agentReply',
                                    'reply': data
                                }))
                            except:
                                pass
                        self.last_outbox_size = len(lines)
            except Exception as e:
                print(f"[WebSocketIPC] Monitor error: {e}")
            await asyncio.sleep(0.1)
    
    async def start(self):
        async with websockets.serve(self.handle_client, self.host, self.port):
            print(f"[WebSocketIPC] Server started on ws://{self.host}:{self.port}")
            await self.monitor_outbox()

if __name__ == "__main__":
    ipc = WebSocketIPC()
    asyncio.run(ipc.start())
