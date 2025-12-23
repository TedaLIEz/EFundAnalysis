import logging

import socketio  # type: ignore[import-untyped]

from core.kyc.workflows.kyc_agent import KYCAgent

logger = logging.getLogger(__name__)

# Store agent instances per session
_kyc_agents: dict[str, KYCAgent] = {}


def register_socket_handlers(sio: socketio.AsyncServer) -> None:
    """Register WebSocket event handlers for chat functionality.

    Args:
        sio: The AsyncServer SocketIO instance to register handlers with

    """

    @sio.on("connect")
    async def handle_connect(sid: str, environ: dict, auth: dict | None = None) -> None:
        """Handle WebSocket connection."""
        logger.info(f"Client connected: {sid}")

        # Initialize agent for this session
        kyc_agent = KYCAgent(customer_id=sid)
        _kyc_agents[sid] = kyc_agent

        await sio.emit("connected", {"type": "system", "message": "连接成功！可以开始聊天了。"}, room=sid)

    @sio.on("disconnect")
    async def handle_disconnect(sid: str) -> None:
        """Handle WebSocket disconnection."""
        logger.info(f"Client disconnected: {sid}")

        # Clean up agent instance
        if sid in _kyc_agents:
            del _kyc_agents[sid]

    @sio.on("json")
    async def handle_json(sid: str, data: dict) -> None:
        """Handle incoming JSON message and stream agent responses."""
        try:
            message = data.get("data", "")

            if not message or not message.strip():
                await sio.emit("error", {"type": "error", "message": "Please provide a valid message."}, room=sid)
                return

            logger.info(f"Received message from {sid}")

            # Get or create agent for this session
            kyc_agent = _kyc_agents.get(sid)
            if not kyc_agent:
                kyc_agent = KYCAgent(customer_id=sid)
                _kyc_agents[sid] = kyc_agent

            # Stream agent responses
            async for chunk in kyc_agent.astream_chat(message):
                await sio.emit("response", {"type": "assistant", "message": chunk}, room=sid)

        except Exception as e:
            logger.exception("Error handling message")
            await sio.emit("error", {"type": "error", "message": str(e)}, room=sid)

    @sio.on("reset")
    async def handle_reset(sid: str) -> None:
        """Handle chat reset request."""
        try:
            kyc_agent = _kyc_agents.get(sid)
            if kyc_agent:
                kyc_agent.reset()
                await sio.emit("response", {"type": "system", "message": "Chat history has been reset."}, room=sid)
            else:
                await sio.emit("error", {"type": "error", "message": "No active chat session found."}, room=sid)
        except Exception as e:
            logger.exception("Error resetting chat")
            await sio.emit("error", {"type": "error", "message": "Failed to reset chat"}, room=sid)
