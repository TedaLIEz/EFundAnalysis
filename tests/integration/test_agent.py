"""WebSocket server for the Agent."""

import asyncio
import json
import logging

from dotenv import load_dotenv
import websockets

from core.llm.agent import Agent

logger = logging.getLogger(__name__)


class AgentWebSocketHandler:
    """WebSocket handler for Agent interactions."""

    def __init__(self):
        """Initialize the handler with an Agent instance."""
        load_dotenv()
        self.agent = Agent()

    async def handle_connection(self, websocket: websockets.ServerConnection):
        """Handle a WebSocket connection.

        Args:
            websocket: The WebSocket connection

        """
        client_address = websocket.remote_address
        logger.info(f"Client connected: {client_address}")

        welcome_msg = {
            "type": "system",
            "message": "Connected successfully! You can start chatting with the agent. Send 'exit' to disconnect, 'history' to view chat history.",
        }
        await websocket.send(json.dumps(welcome_msg))

        try:
            async for message in websocket:
                try:
                    # Parse incoming message
                    if isinstance(message, str):
                        text_input = message.strip()
                    else:
                        # Handle binary messages
                        text_input = message.decode("utf-8").strip()

                    # Handle special commands
                    if text_input == "exit":
                        disconnect_msg = {
                            "type": "system",
                            "message": "Disconnecting...",
                        }
                        await websocket.send(json.dumps(disconnect_msg))
                        break

                    if text_input == "history":
                        history_data = [
                            {
                                "role": msg.role.value if hasattr(msg.role, "value") else str(msg.role),
                                "content": str(msg.content),
                            }
                            for msg in self.agent.chat_history
                        ]
                        history_msg = {
                            "type": "history",
                            "data": history_data,
                        }
                        await websocket.send(json.dumps(history_msg))
                        continue

                    # Process regular message with agent
                    response = self.agent.run(text_input)
                    response_msg = {
                        "type": "agent",
                        "message": response,
                    }
                    await websocket.send(json.dumps(response_msg))

                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    error_msg = {
                        "type": "error",
                        "message": f"Invalid JSON format: {str(e)}",
                    }
                    await websocket.send(json.dumps(error_msg))
                except Exception as e:
                    logger.exception(f"Error processing message: {e}")
                    error_msg = {
                        "type": "error",
                        "message": f"Error processing request: {str(e)}",
                    }
                    await websocket.send(json.dumps(error_msg))

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_address}")
        except Exception as e:
            logger.exception(f"Unexpected error in connection handler: {e}")
        finally:
            logger.info(f"Connection closed: {client_address}")


async def main():
    """Start the WebSocket server."""
    handler = AgentWebSocketHandler()
    async with websockets.serve(handler.handle_connection, "localhost", 8765):
        logger.info("Agent WebSocket server started on ws://localhost:8765")
        await asyncio.Future()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
