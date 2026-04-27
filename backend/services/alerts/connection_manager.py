from fastapi import WebSocket
from typing import Dict

class AlertConnectionManager:
    def __init__(self):
        self.active: Dict[str, WebSocket] = {}  # clinician_id -> websocket

    async def connect(self, clinician_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active[clinician_id] = websocket

    def disconnect(self, clinician_id: str):
        self.active.pop(clinician_id, None)

    async def send_alert(self, clinician_id: str, alert: dict):
        ws = self.active.get(clinician_id)
        if ws:
            await ws.send_json(alert)

    async def broadcast(self, alert: dict):
        for ws in self.active.values():
            await ws.send_json(alert)

manager = AlertConnectionManager()
