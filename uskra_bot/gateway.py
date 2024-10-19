import asyncio
import json
import logging
from dataclasses import dataclass
import websockets


@dataclass
class GatewayMessage:
    op: int
    data: dict | None
    sequence: int
    name: str


def decode_msg(msg):
    obj = json.loads(msg)
    data = None
    seq = None
    name = None

    if "d" in obj:
        data = obj["d"]
    if "s" in obj:
        seq = obj["s"]
    if "t" in obj:
        name = obj["t"]
    return GatewayMessage(obj["op"], data, seq, name)


class Gateway:
    def __init__(self, token, url):
        self.token = token
        self.url = url
        self.sequence = 0

    async def start_connection(self):
        try:
            async with websockets.connect(self.url) as ws:
                response = await ws.recv()
                event = decode_msg(response)

                interval = event.data['heartbeat_interval'] / 1000
                await asyncio.create_task(self.heartbeat(ws, interval))

                await self.identify(ws, self.token)
        except websockets.exceptions.ConnectionClosed as e:
            logging.error(f"Connection closed: {e}")

    async def heartbeat(self, ws, interval):
        while True:
            await asyncio.sleep(interval / 1000)
            message = GatewayMessage(1, None, self.sequence, "HEARTBEAT")
            await ws.send(json.dumps(message.__dict__))
            self.sequence += 1
            logging.info("Heartbeat sent")

    async def identify(self, ws, token):
        data = {
            "token": token,
            "properties": {
                "$os": "windows",
                "$browser": "my_library",
                "$device": "my_library"
            }
        }

        payload = GatewayMessage(2, data, self.sequence, "IDENTIFY")
        await ws.send(json.dumps(payload.__dict__))
        logging.info("Identification sent.")
