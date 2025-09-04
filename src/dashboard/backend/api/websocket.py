#!/usr/bin/env python3
"""
WebSocket API endpoints for real-time dashboard updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json

router = APIRouter()

# Store active WebSocket connections
active_connections: List[WebSocket] = []


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection",
            "message": "Connected to dashboard",
            "timestamp": "2024-01-01T12:00:00Z"
        }))
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": "2024-01-01T12:00:00Z"
                    }))
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": str(e),
                    "timestamp": "2024-01-01T12:00:00Z"
                }))
                
    except WebSocketDisconnect:
        pass
    finally:
        # Remove connection when disconnected
        if websocket in active_connections:
            active_connections.remove(websocket)


async def broadcast_update(message: dict):
    """Broadcast update to all connected WebSocket clients."""
    if not active_connections:
        return
        
    # Convert message to JSON
    message_json = json.dumps(message)
    
    # Send to all active connections
    for connection in active_connections:
        try:
            await connection.send_text(message_json)
        except Exception:
            # Remove failed connections
            active_connections.remove(connection)


@router.get("/connections")
async def get_websocket_connections():
    """Get count of active WebSocket connections."""
    return {
        "active_connections": len(active_connections),
        "status": "operational"
    }
