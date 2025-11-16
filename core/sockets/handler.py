import json

import websockets


class WebSocketHandler:
    async def handle_connection(self, websocket: websockets.ServerConnection):
        welcome_msg = {"type": "system", "message": "连接成功！可以开始聊天了。"}
        await websocket.send(json.dumps(welcome_msg))
        async for message in websocket:
            await websocket.send(json.dumps({"type": "user", "message": message}))
