from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.realtime_service import RealtimeService
import json

router = APIRouter()
realtime_service = RealtimeService()

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: int):
    """
    WebSocket endpoint for real-time updates
    """
    await realtime_service.connect(websocket, session_id)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "session_id": session_id,
                    "timestamp": message.get("timestamp")
                }))
            elif message.get("type") == "get_status":
                # Send current status (could be enhanced to get from database)
                await websocket.send_text(json.dumps({
                    "type": "status",
                    "session_id": session_id,
                    "status": "connected",
                    "active_connections": realtime_service.get_session_connections_count(session_id)
                }))
                
    except WebSocketDisconnect:
        realtime_service.disconnect(websocket, session_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        realtime_service.disconnect(websocket, session_id)
