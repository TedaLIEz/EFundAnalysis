import asyncio
import logging
import threading

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

    def stream_events_background(workflow_instance: KYCWorkflow, user_message: str, session_id: str) -> None:
        """Background task (gevent greenlet) that spawns a thread to run async code."""

        def run_async_in_thread() -> None:
            """Thread function that runs async code with a clean asyncio context."""
            try:

                async def run_and_stream() -> None:
                    # Run the workflow - this needs an event loop
                    handler = workflow_instance.run(user_input=user_message, customer_id=session_id)

                    # Stream events from the workflow
                    async for event in handler.stream_events():
                        if isinstance(event, StreamingChunkEvent):
                            # Use socketio.emit with room to ensure proper context
                            socketio.emit("response", {"type": "assistant", "message": event.chunk})

                # Create a new event loop for this thread
                # This ensures a clean asyncio context unaffected by gevent patching
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    # Run the async function that both runs the workflow and streams events
                    loop.run_until_complete(run_and_stream())
                finally:
                    # Clean up the event loop
                    loop.close()
                    asyncio.set_event_loop(None)
            except Exception as e:
                logger.exception("Error in async streaming thread")
                socketio.emit("error", {"type": "error", "message": str(e)})

        # Spawn a thread from within the gevent greenlet
        # This thread has a clean asyncio context unaffected by gevent's patching
        thread = threading.Thread(target=run_async_in_thread, daemon=True)
        thread.start()

    @socketio.on("json")
    def handle_json(data: dict) -> None:
        """Handle incoming JSON message and stream workflow events.

        Note: Flask-SocketIO with gevent doesn't properly await async handlers,
        so we use a background task with threading to run the async streaming code.
        """
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

            # Capture variables for use in the thread
            workflow_instance = kyc_workflow
            user_message = message

            # Run async streaming in a background task
            # Gevent patches asyncio, so we use a thread to get a clean asyncio context
            # The workflow.run() call also needs an event loop, so we do everything in the async thread
            socketio.start_background_task(stream_events_background, workflow_instance, user_message, session_id)

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
