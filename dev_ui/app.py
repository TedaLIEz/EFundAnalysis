"""Streamlit UI for local debugging of FinWeave service."""

import json
import os
import queue
import threading
import time
from typing import Any

import requests
import socketio
import streamlit as st

# Configure Streamlit page
st.set_page_config(
    page_title="FinWeave Debug UI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Default service URL (can be configured via environment variable)
DEFAULT_SERVICE_URL = os.getenv("FINWEAVE_SERVICE_URL", "http://localhost:5001")


def check_service_health(service_url: str) -> dict[str, Any]:
    """Check the health of the FinWeave service.

    Args:
        service_url: Base URL of the FinWeave service

    Returns:
        Dictionary with health status and response data

    """
    try:
        response = requests.get(f"{service_url}/health", timeout=5)
        response.raise_for_status()
        return {"status": "healthy", "data": response.json(), "status_code": response.status_code}
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "data": {"error": "Connection refused. Is the service running?"},
            "status_code": None,
        }
    except requests.exceptions.Timeout:
        return {"status": "error", "data": {"error": "Request timeout"}, "status_code": None}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "data": {"error": str(e)}, "status_code": None}


def main() -> None:
    """Main Streamlit application."""
    st.title("🔍 FinWeave Debug UI")
    st.markdown("Local debugging interface for FinWeave service")

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        service_url = st.text_input(
            "Service URL",
            value=DEFAULT_SERVICE_URL,
            help="Base URL of the FinWeave Flask service",
        )
        st.divider()

        # Health check button
        if st.button("🔍 Check Service Health", use_container_width=True):
            with st.spinner("Checking service health..."):
                health_result = check_service_health(service_url)
                if health_result["status"] == "healthy":
                    st.success("✅ Service is healthy!")
                    st.json(health_result["data"])
                else:
                    st.error("❌ Service is not available")
                    st.json(health_result["data"])

    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Service Status", "🔧 API Testing", "🔌 WebSocket Testing", "📝 Logs & Info"])

    with tab1:
        st.header("Service Status")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Health Check")
            if st.button("Check Health", type="primary"):
                with st.spinner("Checking..."):
                    health_result = check_service_health(service_url)
                    if health_result["status"] == "healthy":
                        st.success("✅ Service is healthy")
                        st.json(health_result["data"])
                    else:
                        st.error("❌ Service is not available")
                        st.json(health_result["data"])

        with col2:
            st.subheader("Service Information")
            st.info(f"**Service URL:** {service_url}")
            st.info(f"**Health Endpoint:** {service_url}/health")

    with tab2:
        st.header("API Testing")
        st.markdown("Test various API endpoints of the FinWeave service")

        # API endpoint selector
        endpoint_type = st.selectbox(
            "Select Endpoint Type",
            ["Health Check", "Custom Endpoint"],
            help="Choose a predefined endpoint or enter a custom one",
        )

        if endpoint_type == "Health Check":
            endpoint = "/health"
            method = "GET"
        else:
            endpoint = st.text_input("Endpoint Path", value="/", help="Enter the API endpoint path (e.g., /api/funds)")
            method = st.selectbox("HTTP Method", ["GET", "POST", "PUT", "DELETE", "PATCH"])

        # Request parameters
        if method in ["POST", "PUT", "PATCH"]:
            request_body = st.text_area(
                "Request Body (JSON)",
                value="{}",
                height=200,
                help="Enter JSON request body",
            )

        # Send request button
        if st.button("🚀 Send Request", type="primary"):
            try:
                url = f"{service_url}{endpoint}"
                headers = {"Content-Type": "application/json"}

                with st.spinner("Sending request..."):
                    json_data = {}
                    if method in ["POST", "PUT", "PATCH"] and request_body:
                        try:
                            json_data = json.loads(request_body)
                        except json.JSONDecodeError as e:
                            st.error(f"❌ Invalid JSON in request body: {str(e)}")
                            return

                    if method == "GET":
                        response = requests.get(url, timeout=10)
                    elif method == "POST":
                        response = requests.post(url, json=json_data, headers=headers, timeout=10)
                    elif method == "PUT":
                        response = requests.put(url, json=json_data, headers=headers, timeout=10)
                    elif method == "DELETE":
                        response = requests.delete(url, timeout=10)
                    elif method == "PATCH":
                        response = requests.patch(url, json=json_data, headers=headers, timeout=10)

                    # Display response
                    st.subheader("Response")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Status Code", response.status_code)
                    with col2:
                        st.metric("Response Time", f"{response.elapsed.total_seconds():.2f}s")

                    try:
                        response_json = response.json()
                        st.json(response_json)
                    except ValueError:
                        st.text(response.text)

            except requests.exceptions.ConnectionError:
                st.error("❌ Connection refused. Make sure the service is running.")
            except requests.exceptions.Timeout:
                st.error("❌ Request timeout")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    with tab3:
        st.header("WebSocket Testing")
        st.markdown("Test WebSocket connections and chat functionality")

        # Initialize session state for WebSocket
        if "socket_client" not in st.session_state:
            st.session_state.socket_client = None
        if "socket_connected" not in st.session_state:
            st.session_state.socket_connected = False
        if "socket_messages" not in st.session_state:
            st.session_state.socket_messages = []
        if "socket_error" not in st.session_state:
            st.session_state.socket_error = None
        if "socket_connecting" not in st.session_state:
            st.session_state.socket_connecting = False
        if "socket_message_queue" not in st.session_state:
            # Thread-safe queue for messages from WebSocket handlers
            st.session_state.socket_message_queue = queue.Queue()

        # Process messages from the queue (thread-safe way to update session state)
        try:
            msg_queue = st.session_state.socket_message_queue
            while True:
                try:
                    action_msg = msg_queue.get_nowait()
                    action = action_msg.get("action")

                    if action == "add_message":
                        st.session_state.socket_messages.append(action_msg.get("message"))
                    elif action == "set_connected":
                        st.session_state.socket_connected = action_msg.get("value", False)
                    elif action == "set_connecting":
                        st.session_state.socket_connecting = action_msg.get("value", False)
                    elif action == "set_error":
                        st.session_state.socket_error = action_msg.get("value")
                except queue.Empty:
                    break
        except (AttributeError, KeyError):
            # Queue doesn't exist yet, initialize it
            if "socket_message_queue" not in st.session_state:
                st.session_state.socket_message_queue = queue.Queue()

        col1, col2 = st.columns([2, 1])

        with col1:
            socket_url = st.text_input(
                "WebSocket URL",
                value=service_url,
                help="Base URL for WebSocket connection (Socket.IO will append /socket.io/)",
                key="socket_url_input",
            )

        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            if not st.session_state.socket_connected and not st.session_state.socket_connecting:
                if st.button("🔌 Connect", type="primary", use_container_width=True):
                    try:
                        # Create Socket.IO client
                        sio = socketio.Client()
                        st.session_state.socket_client = sio
                        st.session_state.socket_connecting = True

                        # Capture queue reference for thread-safe access
                        msg_queue = st.session_state.socket_message_queue

                        # Event handlers - use thread-safe queue instead of direct session state access
                        @sio.on("connect")
                        def on_connect():
                            # Use queue for thread-safe updates
                            try:
                                msg_queue.put({"action": "set_connected", "value": True})
                                msg_queue.put({"action": "set_connecting", "value": False})
                                msg_queue.put({"action": "set_error", "value": None})
                            except Exception:
                                pass  # Ignore errors in background thread

                        @sio.on("disconnect")
                        def on_disconnect():
                            try:
                                msg_queue.put({"action": "set_connected", "value": False})
                                msg_queue.put({"action": "set_connecting", "value": False})
                            except Exception:
                                pass

                        @sio.on("connected")
                        def on_connected(data: dict):
                            try:
                                msg_queue.put(
                                    {
                                        "action": "add_message",
                                        "message": {"type": "system", "timestamp": time.time(), "data": data},
                                    }
                                )
                            except Exception:
                                pass

                        @sio.on("response")
                        def on_response(data: dict):
                            try:
                                msg_queue.put(
                                    {
                                        "action": "add_message",
                                        "message": {
                                            "type": data.get("type", "unknown"),
                                            "timestamp": time.time(),
                                            "data": data,
                                        },
                                    }
                                )
                            except Exception:
                                pass

                        @sio.on("error")
                        def on_error(data: dict):
                            try:
                                msg_queue.put({"action": "set_error", "value": data.get("message", "Unknown error")})
                                msg_queue.put(
                                    {
                                        "action": "add_message",
                                        "message": {"type": "error", "timestamp": time.time(), "data": data},
                                    }
                                )
                            except Exception:
                                pass

                        # Connect in a separate thread to avoid blocking
                        def connect_socket():
                            try:
                                sio.connect(socket_url, wait_timeout=5)
                            except Exception as e:
                                # Use queue for thread-safe error reporting
                                try:
                                    msg_queue.put({"action": "set_error", "value": str(e)})
                                    msg_queue.put({"action": "set_connected", "value": False})
                                    msg_queue.put({"action": "set_connecting", "value": False})
                                except Exception:
                                    pass

                        thread = threading.Thread(target=connect_socket, daemon=True)
                        thread.start()
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Connection error: {str(e)}")
                        st.session_state.socket_error = str(e)
                        st.session_state.socket_connecting = False
            elif st.session_state.socket_connecting:
                st.info("🔄 Connecting...")
            elif st.button("🔌 Disconnect", type="secondary", use_container_width=True):
                try:
                    if st.session_state.socket_client:
                        st.session_state.socket_client.disconnect()
                        st.session_state.socket_client = None
                    st.session_state.socket_connected = False
                    st.session_state.socket_messages = []
                    st.session_state.socket_error = None
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Disconnect error: {str(e)}")

        # Connection status
        st.divider()
        status_col1, status_col2 = st.columns([3, 1])
        with status_col1:
            if st.session_state.socket_connected:
                st.success("✅ Connected to WebSocket server")
            elif st.session_state.socket_connecting:
                st.info("🔄 Connecting...")
            elif st.session_state.socket_error:
                st.error(f"❌ Error: {st.session_state.socket_error}")
            else:
                st.info("⏸️ Not connected")

        with status_col2:
            if st.session_state.socket_connected:
                if st.button("🔄 Refresh", key="refresh_messages"):
                    st.rerun()

        # Message input and send
        if st.session_state.socket_connected:
            st.subheader("Send Message")
            col1, col2 = st.columns([4, 1])

            with col1:
                message_input = st.text_input(
                    "Message",
                    placeholder="Type your message here...",
                    key="message_input",
                    label_visibility="collapsed",
                )

            with col2:
                st.write("")  # Spacing
                st.write("")  # Spacing
                send_button = st.button("📤 Send", type="primary", use_container_width=True)

            if send_button and message_input:
                try:
                    if st.session_state.socket_client:
                        st.session_state.socket_client.emit("message", {"message": message_input})
                        st.session_state.socket_messages.append(
                            {"type": "sent", "timestamp": time.time(), "data": {"message": message_input}}
                        )
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Send error: {str(e)}")

            # Reset button
            if st.button("🔄 Reset Chat", type="secondary"):
                try:
                    if st.session_state.socket_client:
                        st.session_state.socket_client.emit("reset")
                except Exception as e:
                    st.error(f"❌ Reset error: {str(e)}")

            st.divider()

            # Messages display
            st.subheader("Messages")
            if st.session_state.socket_messages:
                # Display messages in reverse order (newest first)
                for msg in reversed(st.session_state.socket_messages[-20:]):  # Show last 20 messages
                    msg_type = msg.get("type", "unknown")
                    msg_data = msg.get("data", {})
                    timestamp = msg.get("timestamp", 0)
                    time_str = time.strftime("%H:%M:%S", time.localtime(timestamp))

                    if msg_type == "system":
                        st.info(f"**[{time_str}] System:** {msg_data.get('message', '')}")
                    elif msg_type == "user":
                        st.text(f"[{time_str}] User: {msg_data.get('message', '')}")
                    elif msg_type == "assistant":
                        st.success(f"**[{time_str}] Assistant:** {msg_data.get('message', '')}")
                    elif msg_type == "sent":
                        st.text(f"[{time_str}] You sent: {msg_data.get('message', '')}")
                    elif msg_type == "error":
                        st.error(f"**[{time_str}] Error:** {msg_data.get('message', '')}")
                    else:
                        st.json(msg_data)

                # Clear messages button
                if st.button("🗑️ Clear Messages", key="clear_messages"):
                    st.session_state.socket_messages = []
                    st.rerun()
            else:
                st.info("No messages yet. Send a message to start chatting!")

        else:
            st.info("Connect to the WebSocket server to start testing.")

    with tab4:
        st.header("Logs & Information")
        st.markdown("View service logs and debugging information")

        st.subheader("Service Configuration")
        config_data = {
            "Service URL": service_url,
            "Health Endpoint": f"{service_url}/health",
            "Environment": os.getenv("ENVIRONMENT", "development"),
        }
        st.json(config_data)

        st.subheader("Quick Actions")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔄 Refresh Status"):
                st.rerun()

        with col2:
            if st.button("📋 Copy Service URL"):
                st.code(service_url, language=None)

        with col3:
            if st.button("🌐 Open in Browser"):
                st.info(f"Open: {service_url}/health")


if __name__ == "__main__":
    main()
