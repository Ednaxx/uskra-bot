import asyncio
import logging
import requests

from constants import *
from uskra_bot.gateway import Gateway


if __name__ == "__main__":
    logging.basicConfig(encoding='utf-8', level=logging.INFO)

    try:
        response = requests.get(BASE_URL + "/gateway", headers={"Authorization": f"Bot {DISCORD_TOKEN}"})
        ws_url = response.json()["url"]

        logging.info(f"Connecting to {ws_url}/{str(API_VERSION)}...")

        gateway = Gateway(DISCORD_TOKEN, ws_url + "/" + str(API_VERSION))
        asyncio.run(gateway.start_connection())

    except Exception as e:
        logging.error(f" Couldn't start the application: {e}")
