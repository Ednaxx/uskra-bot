import json
import logging
from abc import ABC, abstractmethod
from typing import Callable
from websockets import WebSocketClientProtocol


class Gateway(ABC):
    def __init__(self, url: str):
        self.url = url
        self.ws: WebSocketClientProtocol | None = None

    async def send_message(self, message: dict):
        await self.ws.send(json.dumps(message))
        logging.info(f" Message sent: {message}")

    async def listen(self, treat_events: Callable):
        async for message in self.ws:
            await treat_events(message)

    @abstractmethod
    async def heartbeat(self):
        raise NotImplementedError("Heartbeat method must be implemented")

    @abstractmethod
    async def lifecycle(self):
        raise NotImplementedError("Lifecycle method must be implemented")

    @abstractmethod
    async def connect(self):
        raise NotImplementedError("Connect method must be implemented")
