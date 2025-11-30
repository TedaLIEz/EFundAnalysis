"""Streamlit UI for local testing of FinWeave chat service."""

import logging
import os
import queue
import threading
from typing import Any

import socketio
import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default service URL
DEFAULT_SERVICE_URL = os.getenv("FINWEAVE_SERVICE_URL", "http://localhost:5001")


def init_session_state() -> None:
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "socketio_client" not in st.session_state:
        st.session_state.socketio_client = None
    if "is_connected" not in st.session_state:
        st.session_state.is_connected = False
    if "connection_error" not in st.session_state:
        st.session_state.connection_error = None
    if "message_queue" not in st.session_state:
        st.session_state.message_queue = queue.Queue()


def process_message_queue() -> bool:
    """Process messages from the queue and update session state.

    Returns:
        True if any messages were processed, False otherwise
    """
    processed = False
    try:
        while True:
            try:
                msg = st.session_state.message_queue.get_nowait()
                msg_type = msg.get("type")

                if msg_type == "connect":
                    st.session_state.is_connected = True
                    st.session_state.connection_error = None
                    processed = True
                elif msg_type == "disconnect":
                    st.session_state.is_connected = False
                    processed = True
                elif msg_type == "message":
                    role = msg.get("role", "assistant")
                    content = msg.get("content", "")
                    st.session_state.messages.append({"role": role, "content": content})
                    processed = True
                elif msg_type == "error":
                    error_msg = msg.get("message", "An unknown error occurred")
                    st.session_state.connection_error = error_msg
                    processed = True
            except queue.Empty:
                break
    except Exception as e:
        logger.exception("Error processing message queue")
    return processed


def create_socketio_client(service_url: str) -> socketio.Client:
    """Create and configure a SocketIO client.

    Args:
        service_url: The base URL of the Flask service

    Returns:
        Configured SocketIO client instance
    """
    client = socketio.Client(logger=False, engineio_logger=False)
    msg_queue = st.session_state.message_queue

    @client.on("connect")
    def on_connect() -> None:
        """Handle successful connection."""
        msg_queue.put({"type": "connect"})
        logger.info("Connected to server")

    @client.on("disconnect")
    def on_disconnect() -> None:
        """Handle disconnection."""
        msg_queue.put({"type": "disconnect"})
        logger.info("Disconnected from server")

    @client.on("connected")
    def on_connected(data: dict[str, Any]) -> None:
        """Handle connection confirmation message."""
        message = data.get("message", "连接成功！可以开始聊天了。")
        msg_queue.put({"type": "message", "role": "system", "content": message})
        logger.info(f"Received connection message: {message}")

    @client.on("response")
    def on_response(data: dict[str, Any]) -> None:
        """Handle chat response from server."""
        msg_type = data.get("type", "")
        message = data.get("message", "")
        role_map = {"user": "user", "assistant": "assistant", "system": "system"}
        role = role_map.get(msg_type, "assistant")
        msg_queue.put({"type": "message", "role": role, "content": message})
        logger.info(f"Received response: {msg_type} - {message}")

    @client.on("error")
    def on_error(data: dict[str, Any]) -> None:
        """Handle error messages from server."""
        error_msg = data.get("message", "An unknown error occurred")
        msg_queue.put({"type": "message", "role": "error", "content": error_msg})
        logger.error(f"Received error: {error_msg}")

    return client


def connect_to_server(service_url: str) -> None:
    """Connect to the Flask SocketIO server.

    Args:
        service_url: The base URL of the Flask service
    """
    if st.session_state.socketio_client and st.session_state.is_connected:
        logger.info("Already connected")
        return

    try:
        if st.session_state.socketio_client:
            try:
                st.session_state.socketio_client.disconnect()
            except Exception:
                pass

        client = create_socketio_client(service_url)

        # Connect in a separate thread to avoid blocking
        def connect_thread() -> None:
            try:
                client.connect(service_url)
            except Exception as e:
                error_msg = f"Failed to connect: {str(e)}"
                st.session_state.message_queue.put({"type": "error", "message": error_msg})
                logger.exception("Connection error")

        thread = threading.Thread(target=connect_thread, daemon=True)
        thread.start()
        thread.join(timeout=2)  # Wait up to 2 seconds for connection

        st.session_state.socketio_client = client
        st.session_state.connection_error = None
    except Exception as e:
        error_msg = f"Failed to connect: {str(e)}"
        st.session_state.connection_error = error_msg
        st.session_state.is_connected = False
        logger.exception("Connection error")


def disconnect_from_server() -> None:
    """Disconnect from the Flask SocketIO server."""
    if st.session_state.socketio_client:
        try:
            st.session_state.socketio_client.disconnect()
        except Exception:
            pass
        st.session_state.socketio_client = None
    st.session_state.is_connected = False
    st.rerun()


def send_message(message: str) -> None:
    """Send a message to the server.

    Args:
        message: The message to send
    """
    if not st.session_state.is_connected or not st.session_state.socketio_client:
        st.error("Not connected to server. Please connect first.")
        return

    try:
        st.session_state.socketio_client.emit("json", {"data": message})
        logger.info(f"Sent message: {message}")
    except Exception as e:
        error_msg = f"Failed to send message: {str(e)}"
        st.error(error_msg)
        logger.exception("Error sending message")


def reset_chat() -> None:
    """Reset the chat conversation."""
    if not st.session_state.is_connected or not st.session_state.socketio_client:
        st.error("Not connected to server. Please connect first.")
        return

    try:
        st.session_state.socketio_client.emit("reset")
        st.session_state.messages = []
        logger.info("Reset chat requested")
    except Exception as e:
        error_msg = f"Failed to reset chat: {str(e)}"
        st.error(error_msg)
        logger.exception("Error resetting chat")


def render_chat_interface() -> None:
    """Render the main chat interface."""
    st.title("FinWeave Chat - Dev UI")

    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        service_url = st.text_input(
            "Service URL",
            value=DEFAULT_SERVICE_URL,
            help="The URL of the Flask SocketIO server",
        )

        st.divider()

        st.header("Connection")
        connection_status = "🟢 Connected" if st.session_state.is_connected else "🔴 Disconnected"
        st.markdown(f"**Status:** {connection_status}")

        if st.session_state.connection_error:
            st.error(st.session_state.connection_error)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Connect", disabled=st.session_state.is_connected):
                connect_to_server(service_url)
                st.rerun()

        with col2:
            if st.button("Disconnect", disabled=not st.session_state.is_connected):
                disconnect_from_server()

        st.divider()

        if st.button("Reset Chat", disabled=not st.session_state.is_connected):
            reset_chat()
            st.rerun()

        if st.button("Refresh", disabled=not st.session_state.is_connected):
            st.rerun()

    # Process message queue - check for new messages
    if process_message_queue():
        st.rerun()

    # Main chat area
    if not st.session_state.is_connected:
        st.info("👆 Please connect to the server using the sidebar to start chatting.")
        return

    # Display chat messages
    for message in st.session_state.messages:
        role = message.get("role", "assistant")
        content = message.get("content", "")

        if role == "user":
            with st.chat_message("user"):
                st.write(content)
        elif role == "assistant":
            with st.chat_message("assistant"):
                st.write(content)
        elif role == "system":
            with st.chat_message("system"):
                st.info(content)
        elif role == "error":
            with st.chat_message("assistant"):
                st.error(content)

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        send_message(prompt)
        # Process queue after sending message
        if process_message_queue():
            st.rerun()
        else:
            st.rerun()  # Rerun to show user message and wait for response


def main() -> None:
    """Main entry point for the Streamlit app."""
    init_session_state()

    # Process any pending messages from SocketIO handlers
    if process_message_queue():
        st.rerun()

    render_chat_interface()


if __name__ == "__main__":
    main()
