import logging

from flask import request
from flask_socketio import SocketIO, emit

from core.llm.chat.chatbot import Chatbot

logger = logging.getLogger(__name__)

# Store chatbot instances per session
_chatbots: dict[str, Chatbot] = {}


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
        chatbot = Chatbot()
        _chatbots[session_id] = chatbot

        emit("connected", {"type": "system", "message": "连接成功！可以开始聊天了。"})

    @socketio.on("disconnect")
    def handle_disconnect() -> None:
        """Handle WebSocket disconnection."""
        session_id = request.sid  # type: ignore[attr-defined]
        logger.info(f"Client disconnected: {session_id}")

        # Clean up chatbot instance
        if session_id in _chatbots:
            del _chatbots[session_id]

    @socketio.on("json")
    def handle_json(data: dict) -> None:
        try:
            session_id = request.sid  # type: ignore[attr-defined]
            message = data.get("data", "")

            if not message or not message.strip():
                emit("error", {"type": "error", "message": "Please provide a valid message."})
                return

            logger.info(f"Received message from {session_id}")

            # Get or create chatbot for this session
            chatbot = _chatbots.get(session_id)
            if not chatbot:
                chatbot = Chatbot()
                _chatbots[session_id] = chatbot

            for response in chatbot.stream_chat(message):
                if response is not None:
                    emit("response", {"type": "assistant", "message": response})

            emit("response", {"type": "assistant", "message": "", "done": True})
            logger.info("Streaming completed")

        except Exception as e:
            logger.exception("Error handling message")
            emit("error", {"type": "error", "message": "Failed to process message"})

    @socketio.on("reset")
    def handle_reset() -> None:
        """Handle chat reset request."""
        try:
            session_id = request.sid  # type: ignore[attr-defined]
            chatbot = _chatbots.get(session_id)
            if chatbot:
                chatbot.reset()
                emit("response", {"type": "system", "message": "对话历史已重置。"})
            else:
                emit("error", {"type": "error", "message": "No active chat session found."})
        except Exception as e:
            logger.exception("Error resetting chat")
            emit("error", {"type": "error", "message": "Failed to reset chat"})
