import logging

from flask import request
from flask_socketio import SocketIO, emit

from core.kyc.workflows.kyc_workflow import KYCWorkflow, StreamingChunkEvent

logger = logging.getLogger(__name__)

# Store chatbot instances per session
_kyc_workflows: dict[str, KYCWorkflow] = {}


def register_socket_handlers(socketio: SocketIO) -> None:
    """Register WebSocket event handlers for chat functionality.

    Args:
        socketio: The SocketIO instance to register handlers with

    """

    @socketio.on("connect")
    def handle_connect(auth: dict | None = None) -> None:
        """Handle WebSocket connection."""
        session_id = request.sid  # type: ignore[attr-defined]
        logger.info(f"Client connected: {session_id}")

        # Initialize chatbot for this session
        kyc_workflow = KYCWorkflow()
        _kyc_workflows[session_id] = kyc_workflow

        emit("connected", {"type": "system", "message": "连接成功！可以开始聊天了。"})

    @socketio.on("disconnect")
    def handle_disconnect() -> None:
        """Handle WebSocket disconnection."""
        session_id = request.sid  # type: ignore[attr-defined]
        logger.info(f"Client disconnected: {session_id}")

        # Clean up chatbot instance
        if session_id in _kyc_workflows:
            del _kyc_workflows[session_id]

    @socketio.on("json")
    async def handle_json(data: dict) -> None:
        try:
            session_id = request.sid  # type: ignore[attr-defined]
            message = data.get("data", "")

            if not message or not message.strip():
                emit("error", {"type": "error", "message": "Please provide a valid message."})
                return

            logger.info(f"Received message from {session_id}")

            # Get or create chatbot for this session
            kyc_workflow = _kyc_workflows.get(session_id)

            if not kyc_workflow:
                kyc_workflow = KYCWorkflow()
                _kyc_workflows[session_id] = kyc_workflow
            handler = kyc_workflow.run(user_input=message, customer_id=session_id)

            async for event in handler.stream_events():
                if isinstance(event, StreamingChunkEvent):
                    emit("response", {"type": "assistant", "message": event.chunk})

        except Exception as e:
            logger.exception("Error handling message")
            emit("error", {"type": "error", "message": str(e)})

    @socketio.on("reset")
    def handle_reset() -> None:
        """Handle chat reset request."""
        try:
            session_id = request.sid  # type: ignore[attr-defined]
        except Exception as e:
            logger.exception("Error resetting chat")
            emit("error", {"type": "error", "message": "Failed to reset chat"})
