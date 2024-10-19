import os
from dotenv import load_dotenv


load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
VERSION_NUMBER = os.getenv("VERSION_NUMBER")
WS_URL="wss://gateway.discord.gg"
