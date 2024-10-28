import os
from dotenv import load_dotenv


load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
API_VERSION = "v10"
BASE_URL = f"https://discord.com/api/{API_VERSION}"

BOT_NAME = "Fat Marcos"
APP_NAME = "Uskra Bot"
