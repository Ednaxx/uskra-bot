import asyncio
import logging

from constants import *
from uskra_bot.gateway import Gateway


if __name__ == "__main__":
    logging.basicConfig(encoding='utf-8', level=logging.INFO)

    gateway = Gateway(DISCORD_TOKEN, WS_URL)
    asyncio.run(gateway.start_connection())
