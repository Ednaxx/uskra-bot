import asyncio
import json
import logging
from dataclasses import dataclass
import requests
import websockets
from websockets import WebSocketClientProtocol

from constants import *


@dataclass
class GatewayMessage:
    op: int
    d: dict | None
    s: int | None
    t: str | None


def decode_msg(msg):
    obj = json.loads(msg)
    d = None
    s = None
    t = None

    if "d" in obj:
        d = obj["d"]
    if "s" in obj:
        s = obj["s"]
    if "t" in obj:
        t = obj["t"]
    return GatewayMessage(obj["op"], d, s, t)


class Gateway:
    def __init__(self, token: str, url: str):
        self.token = token
        self.url = url
        self.ws: WebSocketClientProtocol | None = None
        self.sequence: int | None = None
        self.interval: int | None = None

    async def start_connection(self):
        try:
            async with websockets.connect(self.url) as self.ws:
                await self.identify()

                await asyncio.gather(
                    self.heartbeat(),
                    self.listen()
                )

        except websockets.exceptions.ConnectionClosed as e:
            logging.error(f" Connection closed: {e}")

        except Exception as e:
            logging.error(f" An error occurred: {e}")

    async def identify(self):
        data = {
            "token": self.token,
            "intents": 53575421,
            "properties": {
                "os": "windows",
                "browser": "my_library",
                "device": "my_library"
            },
            "presence": {
                  "activities": [{
                    "name": "Fat Marcos"
                  }],
                  "status": "online",
                  "afk": False
                },
        }
        message = GatewayMessage(IDENTIFY, data, self.sequence, "IDENTIFY")

        await self.ws.send(json.dumps(message.__dict__))
        logging.info(" Identification sent")

        response = await self.ws.recv()
        event = decode_msg(response)

        logging.info(" Received event: %s)", event)

        if event.op != 10:
            logging.warning("Unexpected reply: %s", event)
            await self.ws.close(code=4000, reason="Unexpected reply")

        self.interval = event.d['heartbeat_interval'] / 1000
        self.sequence = event.s

    async def heartbeat(self):
        while self.interval is not None:
            await asyncio.sleep(self.interval)
            message = GatewayMessage(HEARTBEAT, None, self.sequence, "HEARTBEAT")
            await self.ws.send(json.dumps(message.__dict__))

            logging.info(" Heartbeat sent: %s", message)

    async def listen(self):
        async for message in self.ws:
            event = decode_msg(message)
            logging.info(" Received event: %s", event)

            if event.op == DISPATCH:
                if event.t == "READY":
                    self.sequence = event.s
                    logging.info(" Session ID: %s", event.d["session_id"])
                elif event.t == "MESSAGE_CREATE":
                    message = event.d["content"]
                    channel = event.d["channel_id"]
                    if message == "!ping":
                        response = requests.post(BASE_URL + "/channels/" + channel + "/messages", json={"content": "Pong!"}, headers={
                            "Authorization": f"Bot {DISCORD_TOKEN}"})
                        print(response.json())
                        logging.info(" Pong sent")

            elif event.op == HEARTBEAT_ACK:
                logging.info(" Heartbeat acknowledged")

            elif event.op == INVALID_SESSION:
                logging.warning(" Invalid session")
                await self.ws.close(code=4000, reason="Invalid session")

            else:
                logging.warning(" Unexpected event: %s", event)
                await self.ws.close(code=4000, reason="Unexpected event")
