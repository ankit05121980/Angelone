import json
from collections import defaultdict
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._channels: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, websocket: WebSocket, channel: str = "dashboard") -> None:
        await websocket.accept()
        self._channels[channel].add(websocket)

    def disconnect(self, websocket: WebSocket, channel: str = "dashboard") -> None:
        self._channels[channel].discard(websocket)

    async def broadcast(self, event: str, payload: dict[str, Any], channel: str = "dashboard") -> None:
        message = json.dumps({"event": event, "payload": payload}, default=str)
        disconnected: list[WebSocket] = []
        for websocket in self._channels[channel]:
            try:
                await websocket.send_text(message)
            except RuntimeError:
                disconnected.append(websocket)
        for websocket in disconnected:
            self.disconnect(websocket, channel)


manager = ConnectionManager()
