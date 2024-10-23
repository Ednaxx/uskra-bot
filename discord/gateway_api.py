import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Callable

import websockets

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
    def __init__(self, token: str, url: str, identity: dict, treat_dispatch_events: Callable = None):
        super().__init__(url)
        self.sequence: int | None = None
        self.interval: int | None = None
        self.session_id: str | None = None
        self.token = token
        self.identity = identity
        self.treat_dispatch_events = treat_dispatch_events

        if self.token is None:
            raise ValueError('Token must be provided. Set your ".env".')

    async def connect(self):
        try:
            await self.lifecycle()

        except websockets.exceptions.ConnectionClosed as e:
            await self.treat_connection_closed(e)

    async def lifecycle(self):
        async with websockets.connect(self.url) as self.ws:
            await self.identify()
            await asyncio.gather(self.listen(self.treat_events), self.heartbeat())

    async def reconnect(self):
        try:
            async with websockets.connect(self.url) as self.ws:
                message = GatewayMessage(RESUME, {"token": self.token, "session_id": self.session_id, "seq": self.sequence}, None, None)
                await self.send_message(message.__dict__)

        except websockets.exceptions.ConnectionClosed as e:
            await self.treat_connection_closed(e)

    async def treat_connection_closed(self, e):
        logging.error(f" Connection closed: {e}")
        if e.rcvd.code > 4010 or e.rcvd.code == 4004:
            await self.reconnect()

    async def identify(self):
        message = GatewayMessage(IDENTIFY, self.identity, None, None)
        await self.send_message(message.__dict__)

    async def heartbeat(self):
        while self.interval is not None:
            await asyncio.sleep(self.interval)
            message = GatewayMessage(HEARTBEAT, self.sequence, None, None).__dict__
            await self.send_message(message)

    async def treat_events(self, message: str | bytes):
        event = decode_msg(message)
        logging.info(" Received event: %s", event)
        self.sequence = event.s if event.s is not None else self.sequence

        if event.op == HELLO:
            self.interval = event.d['heartbeat_interval'] / 1000

        elif event.op == DISPATCH and event.t == "READY":
            logging.info(" Session ID: %s", event.d["session_id"])
            self.session_id = event.d["session_id"]
            self.url = f"{event.d["resume_gateway_url"]}/{API_VERSION}"

        elif event.op == DISPATCH and self.treat_dispatch_events is not None:
            self.treat_dispatch_events(event)

        elif event.op == INVALID_SESSION:
            logging.error(" Invalid session")

        elif event.op == RECONNECT:
            logging.info(" Reconnect event")

        elif event.op == HEARTBEAT_ACK:
            logging.info(" Heartbeat acknowledged")

        else:
            logging.error(" Unexpected event: %s", event)
            await self.ws.close(code=4000, reason="Unexpected event")
