import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Callable
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
    def __init__(self, token: str, identity: dict, treat_dispatch: Callable = None):
        super().__init__(token)
        self.sequence: int | None = None
        self.interval: int | None = None
        self.identity = identity
        self.treat_dispatch = treat_dispatch

    async def connect(self, url: str):
        await self.start_connection(url, self.lifecycle)

    async def lifecycle(self):
        await self.identify()
        await asyncio.gather(self.listen(self.treat_events), self.heartbeat())

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
        self.sequence = event.s

        if event.op == HELLO:
            self.interval = event.d['heartbeat_interval'] / 1000

        elif event.op == DISPATCH and event.t == "READY":
            logging.info(" Session ID: %s", event.d["session_id"])

        elif event.op == DISPATCH and self.treat_dispatch is not None:
            self.treat_dispatch(event)

        # elif event.op == INVALID_SESSION:

        # elif event.op == RECONNECT:
        # TODO - Implement disconnect/reconnect routine

        elif event.op == HEARTBEAT_ACK:
            logging.info(" Heartbeat acknowledged")

        else:
            logging.error(" Unexpected event: %s", event)
            await self.ws.close(code=4000, reason="Unexpected event")
