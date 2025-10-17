from fastapi import WebSocket
from typing import Dict, List
import json
import asyncio

class RealtimeService:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: int):
        """Accept WebSocket connection and add to active connections"""
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        
        self.active_connections[session_id].append(websocket)
        
        # Send initial connection confirmation
        await self.send_to_session(session_id, {
            "type": "connected",
            "session_id": session_id,
            "message": "Connected to real-time updates"
        })
    
    def disconnect(self, websocket: WebSocket, session_id: int):
        """Remove WebSocket connection"""
        if session_id in self.active_connections:
            try:
                self.active_connections[session_id].remove(websocket)
                if not self.active_connections[session_id]:
                    del self.active_connections[session_id]
            except ValueError:
                pass  # Connection not in list
    
    async def broadcast_status(self, session_id: int, status: str, progress: int):
        """Broadcast processing status update"""
        message = {
            "type": "status_update",
            "session_id": session_id,
            "status": status,
            "progress": progress,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await self.send_to_session(session_id, message)
    
    async def broadcast_results(self, session_id: int, results: dict):
        """Broadcast analysis results"""
        message = {
            "type": "results",
            "session_id": session_id,
            "data": results,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await self.send_to_session(session_id, message)
    
    async def broadcast_error(self, session_id: int, error_message: str):
        """Broadcast error message"""
        message = {
            "type": "error",
            "session_id": session_id,
            "message": error_message,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await self.send_to_session(session_id, message)
    
    async def send_to_session(self, session_id: int, message: dict):
        """Send message to all connections for a specific session"""
        if session_id in self.active_connections:
            connections_to_remove = []
            
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    print(f"Error sending message to WebSocket: {e}")
                    connections_to_remove.append(connection)
            
            # Remove broken connections
            for connection in connections_to_remove:
                self.disconnect(connection, session_id)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all active connections"""
        for session_id in list(self.active_connections.keys()):
            await self.send_to_session(session_id, message)
    
    def get_active_connections_count(self) -> int:
        """Get total number of active connections"""
        return sum(len(connections) for connections in self.active_connections.values())
    
    def get_session_connections_count(self, session_id: int) -> int:
        """Get number of connections for a specific session"""
        return len(self.active_connections.get(session_id, []))
