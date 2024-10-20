import asyncio
import json
import logging
from typing import Callable
import websockets
from websockets import WebSocketClientProtocol


class Gateway:
    def __init__(self, token: str):
        self.token = token
        self.ws: WebSocketClientProtocol | None = None

    async def start_connection(self, url: str, lifecycle: Callable):
        try:
            async with websockets.connect(url) as self.ws:
                await lifecycle()

        except websockets.exceptions.ConnectionClosed as e:
            logging.error(f" Connection closed: {e}")

        except Exception as e:
            logging.error(f" An error occurred: {e}")

    async def send_message(self, message: dict):
        await self.ws.send(json.dumps(message))
        logging.info(f" Message sent: {message}")

    async def ping(self, message: dict, interval: int | None):
        while True:
            await asyncio.sleep(interval)
            await self.send_message(message)

    async def listen(self, treat_events: Callable):
        async for message in self.ws:
            await treat_events(message)
