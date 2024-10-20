import asyncio
import json
import logging
from dataclasses import dataclass
from api import request
from discord.gateway import Gateway
from util.constants import *


@dataclass
class GatewayMessage:
    op: int
    d: dict | None | int
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


class GatewayAPI(Gateway):
    def __init__(self, token: str, url: str):
        super().__init__(token, url)
        self.sequence: int | None = None
        self.interval: int | None = None

    async def connect(self):
        await self.start_connection(self.lifecycle)

    async def lifecycle(self):
        await self.identify()
        await asyncio.gather(self.heartbeat(), self.listen(self.treat_events))

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
        await self.send_message(message.__dict__)

        response = await self.ws.recv()
        event = decode_msg(response)

        logging.info(" Received hello: %s)", event)

        if event.op != 10:
            logging.warning("Unexpected reply: %s", event)
            await self.ws.close(code=4000, reason="Unexpected reply")

        self.interval = event.d['heartbeat_interval'] / 1000
        self.sequence = event.s

    async def heartbeat(self):
        message = GatewayMessage(HEARTBEAT, self.sequence, None, None)
        await self.ping(message.__dict__, self.interval)

    async def treat_events(self, message: str | bytes):
        event = decode_msg(message)
        logging.info(" Received event: %s", event)

        if event.op == DISPATCH:
            if event.t == "READY":
                self.sequence = event.s
                logging.info(" Session ID: %s", event.d["session_id"])

            elif event.t == "MESSAGE_CREATE":
                self.sequence = event.s
                if event.d["content"][0] == "!":
                    self.treat_commands(event)

            elif event.op == HEARTBEAT_ACK:
                self.sequence = event.s
                logging.info(" Heartbeat acknowledged")

            elif event.op == INVALID_SESSION:
                logging.warning(" Invalid session")
                await self.ws.close(code=4000, reason="Invalid session")

            else:
                logging.warning(" Unexpected event: %s", event)
                await self.ws.close(code=4000, reason="Unexpected event")

    def treat_commands(self, event: GatewayMessage):
        message = event.d["content"]
        channel = event.d["channel_id"]

        if message == "!ping":
            logging.info(" Received !ping")
            request(f"/channels/{channel}/messages", body={"content": "Pong!"})
