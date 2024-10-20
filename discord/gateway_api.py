import asyncio
import json
import logging
import sys
from dataclasses import dataclass
from discord.api import request
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
    def __init__(self, token: str):
        super().__init__(token)
        self.sequence: int | None = None
        self.interval: int | None = None

    async def connect(self, url: str):
        await self.start_connection(url, self.lifecycle)

    async def lifecycle(self):
        await self.identify()
        await asyncio.gather(self.listen(self.treat_events), self.heartbeat())

    async def identify(self):
        data = {
            "token": self.token,
            "intents": BOT_INTENTS,
            "properties": {
                "os": sys.platform,
                "browser": "my_library",
                "device": "my_library"
            },
            "presence": {
                  "activities": [{
                    "name": BOT_NAME
                  }],
                  "status": "online",
                  "afk": False
                },
        }
        message = GatewayMessage(IDENTIFY, data, None, None)
        await self.send_message(message.__dict__)

    async def heartbeat(self):
        while self.interval is not None:
            await asyncio.sleep(self.interval)
            message = GatewayMessage(HEARTBEAT, self.sequence, None, None).__dict__
            await self.send_message(message)

    async def treat_events(self, message: str | bytes):
        event = decode_msg(message)
        logging.info(" Received event: %s", event)

        if event.op == HELLO:
            self.interval = event.d['heartbeat_interval'] / 1000
            self.sequence = event.s

        elif event.op == DISPATCH:
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
            logging.error(" Invalid session")
            await self.ws.close(code=4000, reason="Invalid session")

        else:
            logging.error(" Unexpected event: %s", event)
            await self.ws.close(code=4000, reason="Unexpected event")

    def treat_commands(self, event: GatewayMessage):
        message = event.d["content"].split()
        channel = event.d["channel_id"]

        if message[0] == "!ping":
            logging.info(" Received !ping")
            request(f"/channels/{channel}/messages", "POST", {"content": "Pong!"})
