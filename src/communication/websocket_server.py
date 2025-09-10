#!/usr/bin/env python3
"""
WebSocket Server for AI Agent System Communication.
Provides real-time bidirectional communication between agents and clients.
"""

import json
import logging
import websockets
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class WebSocketMessage:
    """Structure for WebSocket messages."""

    message_id: str
    sender: str
    recipient: str
    message_type: str
    content: Any
    timestamp: str
    session_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class WebSocketServer:
    """WebSocket server for real-time agent communication."""

    def __init__(self, host: str = "localhost", port: int = 4000):
        self.host = host
        self.port = port
        self.clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.agent_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self.server: Optional[websockets.WebSocketServer] = None
        self.is_running = False

        # Register default message handlers
        self._register_default_handlers()

        logger.info(f"WebSocket server initialized on {host}:{port}")

    def _register_default_handlers(self) -> None:
        """Register default message handlers."""
        self.message_handlers.update(
            {
                "ping": self._handle_ping,
                "register": self._handle_register,
                "broadcast": self._handle_broadcast,
                "direct": self._handle_direct_message,
                "status": self._handle_status_request,
            }
        )

    async def start(self) -> None:
        """Start the WebSocket server."""
        try:
            self.server = await websockets.serve(
                self._handle_client, self.host, self.port
            )
            self.is_running = True
            logger.info(f"WebSocket server started on {self.host}:{self.port}")

            # Keep server running
            await self.server.wait_closed()

        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")
            self.is_running = False
            raise

    async def stop(self) -> None:
        """Stop the WebSocket server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.is_running = False
            logger.info("WebSocket server stopped")

    async def _handle_client(
        self, websocket: websockets.WebSocketServerProtocol, path: str
    ) -> None:
        """Handle new client connections."""
        client_id = None
        try:
            # Wait for client registration
            async for message in websocket:
                try:
                    data = json.loads(message)
                    if data.get("type") == "register":
                        client_id = await self._handle_register(websocket, data)
                        break
                    else:
                        await websocket.send(
                            json.dumps(
                                {"error": "Client must register first", "type": "error"}
                            )
                        )
                except json.JSONDecodeError:
                    await websocket.send(
                        json.dumps({"error": "Invalid JSON", "type": "error"})
                    )

            # Handle client messages
            if client_id:
                async for message in websocket:
                    await self._process_message(client_id, message)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            if client_id:
                await self._handle_disconnect(client_id)

    async def _handle_register(
        self, websocket: websockets.WebSocketServerProtocol, data: Dict[str, Any]
    ) -> str:
        """Handle client registration."""
        client_id = data.get("client_id", f"client_{len(self.clients)}")
        client_type = data.get("client_type", "unknown")

        if client_type == "agent":
            self.agent_connections[client_id] = websocket
            logger.info(f"Agent {client_id} registered")
        else:
            self.clients[client_id] = websocket
            logger.info(f"Client {client_id} registered")

        # Send registration confirmation
        await websocket.send(
            json.dumps(
                {
                    "type": "registered",
                    "client_id": client_id,
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                }
            )
        )

        return client_id

    async def _handle_disconnect(self, client_id: str) -> None:
        """Handle client disconnection."""
        if client_id in self.clients:
            del self.clients[client_id]
            logger.info(f"Client {client_id} disconnected")
        elif client_id in self.agent_connections:
            del self.agent_connections[client_id]
            logger.info(f"Agent {client_id} disconnected")

    async def _process_message(self, client_id: str, message: str) -> None:
        """Process incoming message from client."""
        try:
            data = json.loads(message)
            message_type = data.get("type", "unknown")

            if message_type in self.message_handlers:
                await self.message_handlers[message_type](client_id, data)
            else:
                logger.warning(f"Unknown message type: {message_type}")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from client {client_id}")

    async def _handle_ping(self, client_id: str, data: Dict[str, Any]) -> None:
        """Handle ping messages."""
        websocket = self.clients.get(client_id) or self.agent_connections.get(client_id)
        if websocket:
            await websocket.send(
                json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()})
            )

    async def _handle_broadcast(self, client_id: str, data: Dict[str, Any]) -> None:
        """Handle broadcast messages to all clients."""
        message = WebSocketMessage(
            message_id=data.get("message_id", f"msg_{datetime.now().timestamp()}"),
            sender=client_id,
            recipient="all",
            message_type="broadcast",
            content=data.get("content"),
            timestamp=datetime.now().isoformat(),
        )

        await self.broadcast_message(message)

    async def _handle_direct_message(
        self, client_id: str, data: Dict[str, Any]
    ) -> None:
        """Handle direct messages between clients."""
        recipient_id = data.get("recipient")
        if not recipient_id:
            return

        message = WebSocketMessage(
            message_id=data.get("message_id", f"msg_{datetime.now().timestamp()}"),
            sender=client_id,
            recipient=recipient_id,
            message_type="direct",
            content=data.get("content"),
            timestamp=datetime.now().isoformat(),
        )

        await self.send_direct_message(message)

    async def _handle_status_request(
        self, client_id: str, data: Dict[str, Any]
    ) -> None:
        """Handle status requests."""
        websocket = self.clients.get(client_id) or self.agent_connections.get(client_id)
        if websocket:
            status = {
                "type": "status",
                "server_status": "running" if self.is_running else "stopped",
                "connected_clients": len(self.clients),
                "connected_agents": len(self.agent_connections),
                "timestamp": datetime.now().isoformat(),
            }
            await websocket.send(json.dumps(status))

    async def broadcast_message(self, message: WebSocketMessage) -> None:
        """Broadcast message to all connected clients and agents."""
        message_data = json.dumps(message.to_dict())

        # Send to all clients
        for client_id, websocket in self.clients.items():
            try:
                await websocket.send(message_data)
            except Exception as e:
                logger.error(f"Failed to send to client {client_id}: {e}")

        # Send to all agents
        for agent_id, websocket in self.agent_connections.items():
            try:
                await websocket.send(message_data)
            except Exception as e:
                logger.error(f"Failed to send to agent {agent_id}: {e}")

        logger.info(f"Broadcast message sent by {message.sender}")

    async def send_direct_message(self, message: WebSocketMessage) -> None:
        """Send direct message to specific recipient."""
        message_data = json.dumps(message.to_dict())

        # Check if recipient is a client
        if message.recipient in self.clients:
            try:
                await self.clients[message.recipient].send(message_data)
                logger.info(
                    f"Direct message sent from {message.sender} to {message.recipient}"
                )
            except Exception as e:
                logger.error(f"Failed to send direct message: {e}")

        # Check if recipient is an agent
        elif message.recipient in self.agent_connections:
            try:
                await self.agent_connections[message.recipient].send(message_data)
                logger.info(
                    f"Direct message sent from {message.sender} to agent {message.recipient}"
                )
            except Exception as e:
                logger.error(f"Failed to send direct message to agent: {e}")

        else:
            logger.warning(f"Recipient {message.recipient} not found")

    def get_connection_count(self) -> Dict[str, int]:
        """Get current connection counts."""
        return {
            "clients": len(self.clients),
            "agents": len(self.agent_connections),
            "total": len(self.clients) + len(self.agent_connections),
        }

    def is_client_connected(self, client_id: str) -> bool:
        """Check if a client is connected."""
        return client_id in self.clients or client_id in self.agent_connections
