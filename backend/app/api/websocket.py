from typing import List, Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, scan_id: str = "global"):
        await websocket.accept()
        if scan_id not in self.active_connections:
            self.active_connections[scan_id] = []
        self.active_connections[scan_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, scan_id: str = "global"):
        if scan_id in self.active_connections:
            if websocket in self.active_connections[scan_id]:
                self.active_connections[scan_id].remove(websocket)
    
    async def send_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)
    
    async def broadcast(self, message: dict, scan_id: str = "global"):
        connections = self.active_connections.get(scan_id, []) + self.active_connections.get("global", [])
        for connection in connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


@router.websocket("/scan/{scan_id}")
async def websocket_scan(websocket: WebSocket, scan_id: str):
    await manager.connect(websocket, scan_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await manager.send_message({"type": "pong"}, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, scan_id)


@router.websocket("/")
async def websocket_global(websocket: WebSocket):
    await manager.connect(websocket, "global")
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await manager.send_message({"type": "pong"}, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, "global")
