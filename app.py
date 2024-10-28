import sys
from env import *
from discord.gateway_api import GatewayAPI, GatewayMessage
from discord.api import request
from discord.util.intents import *
import asyncio
import logging


class Bot:
    def __init__(self, token: str, ws_url: str):
        self.ws_url = ws_url
        self.token = token

    async def start(self):
        identity = {
            "token": self.token,
            "intents": combine_intents(GUILD_MESSAGES_INTENT, GUILD_VOICE_STATES_INTENT),
            "properties": {
                "os": sys.platform,
                "browser": APP_NAME,
                "device": APP_NAME
            },
            "presence": {
                "activities": [{
                    "name": BOT_NAME
                }],
                "status": "online",
                "afk": False
            }
        }

        await GatewayAPI(self.token, ws_url, identity, self.treat_dispatch_events).connect()

    def treat_dispatch_events(self, event: GatewayMessage):
        if event.t == "MESSAGE_CREATE":
            if event.d["content"][0] == "!":
                self.treat_commands(event)

        elif event.t == "VOICE_STATE_UPDATE":
            if event.d['channel_id'] is not None:
                channel = request(f"/channels/{event.d['channel_id']}", self.token).json()
                logging.info(f' {event.d['member']['nick']} joined channel {channel["name"]}')
            else:
                logging.info(f' {event.d['member']['nick']} left channel')

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
        ws_url = f"{response.json()["url"]}/{API_VERSION}"
        logging.info(f"Connecting to {ws_url}...")
        asyncio.run(Bot(DISCORD_TOKEN, ws_url).start())
