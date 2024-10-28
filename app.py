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

    # IN
    ''' 
    GatewayMessage(op=0, 
        d={'member': 
            {'user': 
                {
                'username': 'ednax', 'public_flags': 0, 'id': '358350385192108032',
                'global_name': 'Ednax', 'display_name': 'Ednax', 'discriminator': '0', 
                'clan': None, 'bot': False, 'avatar_decoration_data': None, 'avatar': '24ccc17eb04d47dff595aaa19469afa9'
                }, 
            'roles': ['1076319496312213504', '1261023886234091522', '903836023581200484', '904900617418457108'],
            'premium_since': None, 'pending': False, 'nick': 'Wandinha', 'mute': False, 'joined_at': '2021-09-03T02:33:47.147000+00:00',
            'flags': 0, 'deaf': False, 'communication_disabled_until': None, 'banner': None, 'avatar': None
        }, 
        'user_id': '358350385192108032', 'suppress': False, 'session_id': '7288eeb38df2ed4548010a22713cb42e', 
        'self_video': False, 'self_mute': True, 'self_deaf': False, 'request_to_speak_timestamp': None, 'mute': False, 
        'guild_id': '811761295564734524', 'discoverable': True, 'deaf': False, 'channel_id': '1193256214985982003'}, s=4, t='VOICE_STATE_UPDATE')
    '''
    # OUT
    '''
    GatewayMessage(op=0, 
        d={'member': 
            {'user': 
                {
                'username': 'ednax', 'public_flags': 0, 'id': '358350385192108032', 
                'global_name': 'Ednax', 'display_name': 'Ednax', 'discriminator': '0', 'clan': None, 'bot': False, 
                'avatar_decoration_data': None, 'avatar': '24ccc17eb04d47dff595aaa19469afa9'
                }, 
            'roles': ['1076319496312213504', '1261023886234091522', '903836023581200484', '904900617418457108'], 
            'premium_since': None, 'pending': False, 'nick': 'Wandinha', 'mute': False, 'joined_at': '2021-09-03T02:33:47.147000+00:00', 
            'flags': 0, 'deaf': False, 'communication_disabled_until': None, 'banner': None, 'avatar': None
        }, 
        'user_id': '358350385192108032', 'suppress': False, 'session_id': '7288eeb38df2ed4548010a22713cb42e', 
        'self_video': False, 'self_mute': True, 'self_deaf': False, 'request_to_speak_timestamp': None, 'mute': False, 
        'guild_id': '811761295564734524', 'discoverable': True, 'deaf': False, 'channel_id': None}, s=5, t='VOICE_STATE_UPDATE') 
    '''
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
