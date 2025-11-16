import asyncio

import websockets

from core.sockets.handler import WebSocketHandler


async def test_websocket_connection():
    handler = WebSocketHandler()
    async with websockets.serve(handler.handle_connection, "localhost", 8765):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(test_websocket_connection())
