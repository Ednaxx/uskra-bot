import sys
from util.constants import *
from discord.gateway_api import GatewayAPI, GatewayMessage
from discord.api import request
import asyncio
import logging


class Bot:
    def __init__(self, token: str, ws_url: str):
        self.ws_url = ws_url
        self.token = token

    async def start(self):
        identity = {
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
            }
        }

        await GatewayAPI(self.token, identity, self.treat_dispatch).connect(ws_url)

    def treat_dispatch(self, event: GatewayMessage):
        if event.t == "MESSAGE_CREATE":
            if event.d["content"][0] == "!":
                self.treat_commands(event)

    def treat_commands(self, event: GatewayMessage):
        message = event.d["content"].split()
        channel = event.d["channel_id"]

        if message[0] == "!ping":
            logging.info(" Received !ping")
            request(f"/channels/{channel}/messages", self.token, "POST", {"content": "Pong!"})


if __name__ == "__main__":
    logging.basicConfig(encoding='utf-8', level=logging.INFO)

    response = request("/gateway", DISCORD_TOKEN)

    if response is not None:
        ws_url = f"{response.json()["url"]}/{str(API_VERSION)}"
        logging.info(f"Connecting to {ws_url}...")
        asyncio.run(Bot(DISCORD_TOKEN, ws_url).start())
