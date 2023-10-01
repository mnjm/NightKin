"""
Test phase message sender
"""
from discord import Webhook
import json
import sys
import asyncio
import aiohttp

async def main() -> None:
    url = sys.argv[1]
    print(f'url = {url}')

    message = "I'm currently in the beta testing phase. If you don't see the above messages getting updated every 10-12 minutes, please notify <@866338551947722822>"
    print(f'message = {message}')
    bot_config = {}
    with open("config.json") as fp:
        bot_config = json.load(fp)

    async with aiohttp.ClientSession() as sess:
        webhook = Webhook.from_url(url, session=sess)
        await webhook.send(content=message, wait=True, username=bot_config['botname'],
                           avatar_url=bot_config['bot_avatar_url'], silent=True)

if __name__ == "__main__":
    ml = asyncio.get_event_loop()
    try:
        ml.run_until_complete(main())
    finally:
        ml.close()
