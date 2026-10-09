from typing import List, Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import json

from ..core.database import get_db
from ..core.security import decode_token
from ..models.scan import Scan

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, scan_id: str):
        await websocket.accept()
        if scan_id not in self.active_connections:
            self.active_connections[scan_id] = []
        self.active_connections[scan_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, scan_id: str):
        if scan_id in self.active_connections:
            if websocket in self.active_connections[scan_id]:
                self.active_connections[scan_id].remove(websocket)
    
    async def send_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)
    
    async def broadcast(self, message: dict, scan_id: str, user_id: int | None):
        if user_id is None:
            return
        connections = self.active_connections.get(f"user:{user_id}:scan:{scan_id}", [])
        connections = connections + self.active_connections.get(f"user:{user_id}", [])
        for connection in connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


def _websocket_user_id(websocket: WebSocket) -> int | None:
    authorization = websocket.headers.get("authorization", "")
    token = authorization[7:] if authorization.lower().startswith("bearer ") else websocket.query_params.get("token")
    if not token:
        return None
    try:
        user_id = int(decode_token(token)["sub"])
        return user_id if user_id > 0 else None
    except (HTTPException, KeyError, TypeError, ValueError):
        return None


@router.websocket("/scan/{scan_id}")
async def websocket_scan(websocket: WebSocket, scan_id: str, db: AsyncSession = Depends(get_db)):
    user_id = _websocket_user_id(websocket)
    if user_id is None or not scan_id.isdecimal():
        await websocket.close(code=1008)
        return
    scan = await db.get(Scan, int(scan_id))
    if scan is None or scan.user_id != user_id:
        await websocket.close(code=1008)
        return
    channel = f"user:{user_id}:scan:{scan.id}"
    await manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await manager.send_message({"type": "pong"}, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)


@router.websocket("/")
async def websocket_global(websocket: WebSocket):
    user_id = _websocket_user_id(websocket)
    if user_id is None:
        await websocket.close(code=1008)
        return
    channel = f"user:{user_id}"
    await manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await manager.send_message({"type": "pong"}, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)
