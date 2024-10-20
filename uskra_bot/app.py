from uskra_bot.util.constants import *
from uskra_bot.discord.gateway_api import GatewayAPI
from discord.api import request
import asyncio
import logging


if __name__ == "__main__":
    logging.basicConfig(encoding='utf-8', level=logging.INFO)

    ws_url = request("/gateway")

    if ws_url is not None:
        ws_url = ws_url.json()["url"]
        logging.info(f"Connecting to {ws_url}/{str(API_VERSION)}...")

        gateway = GatewayAPI(DISCORD_TOKEN, f"{ws_url}/{str(API_VERSION)}")
        asyncio.run(gateway.start_connection())
