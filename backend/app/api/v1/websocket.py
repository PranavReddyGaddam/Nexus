"""WebSocket endpoints for real-time communication."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import json
import asyncio

router = APIRouter()

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}


@router.websocket("/research/{session_id}")
async def websocket_research_session(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time research session updates.
    
    Messages from client:
    - {"type": "start_round", "user_message": "..."}
    - {"type": "ping"}
    
    Messages to client:
    - {"type": "agent_start", "agent_id": "...", "agent_name": "..."}
    - {"type": "agent_chunk", "agent_id": "...", "content": "..."}
    - {"type": "agent_complete", "agent_id": "...", "response": {...}}
    - {"type": "round_complete", "synthesis": {...}}
    - {"type": "error", "message": "..."}
    - {"type": "pong"}
    """
    await websocket.accept()
    active_connections[session_id] = websocket
    
    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "message": "WebSocket connection established"
        })
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                message_type = message.get("type")
                
                if message_type == "ping":
                    await websocket.send_json({"type": "pong"})
                
                elif message_type == "start_round":
                    # This would trigger a feedback round with streaming responses
                    await websocket.send_json({
                        "type": "info",
                        "message": "Feedback round initiated. Agents are analyzing..."
                    })
                    
                    # In a real implementation, you would:
                    # 1. Get the session from active_sessions
                    # 2. Execute agents with streaming
                    # 3. Send chunks as they arrive
                    # 4. Send synthesis when complete
                    
                    # Placeholder response
                    await websocket.send_json({
                        "type": "info",
                        "message": "This would start a new feedback round with real-time streaming"
                    })
                
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}"
                    })
            
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON message"
                })
            
            except WebSocketDisconnect:
                break
    
    except WebSocketDisconnect:
        pass
    
    finally:
        # Clean up connection
        if session_id in active_connections:
            del active_connections[session_id]


async def broadcast_to_session(session_id: str, message: dict):
    """Broadcast a message to a specific session's WebSocket."""
    if session_id in active_connections:
        websocket = active_connections[session_id]
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error broadcasting to session {session_id}: {e}")
            # Remove dead connection
            if session_id in active_connections:
                del active_connections[session_id]

