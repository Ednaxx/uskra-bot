# uskra-bot

Uskra's Discord Bot 🤓. Interactive Discord Server bot built on top of a 
Discord Gateway API client. Developed with ***Python 3.12*** and Websockets.

## Features

- In development. Only basic Gateway lifecycle, logging and chat !ping command implemented so far.

## Installation

1. Clone the repository with `git clone https://github.com/Ednaxx/uskra-bot.git`;
2. (Optional) Create a virtual environment with `python -m venv .venv`;
3. Activate the python environment and install the dependencies with `pip install -r requirements.txt`;
4. Create a `.env` file in the root directory and add the following environment variables:
- `DISCORD_TOKEN` - Your Discord Bot Token (Check the Discord Developer Portal for more information);
- `APP_NAME` - The name of the application;
- `BOT_NAME` - The name of the bot that will appear on the server.
5. Run the bot with `python main.py`.

## Docker

You can build the image locally or on another hand, you can pull from Docker Hub with 
`docker pull ednax/uskra-bot:amd64` for x86-64 processors or `docker pull ednax/uskra-bot:arm64` for arm64 processors.

Remember to set the environment variables in the `docker run` command:
- `DISCORD_TOKEN` - Your Discord Bot Token (Check the Discord Developer Portal for more information);
- `APP_NAME` - The name of the application;
- `BOT_NAME` - The name of the bot that will appear on the server.
