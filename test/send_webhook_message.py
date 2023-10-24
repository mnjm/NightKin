"""
Test phase message sender
"""
from discord import Webhook
import json
import sys
import asyncio
import aiohttp

async def main() -> None:
    assert len(sys.argv) == 3 or len(sys.argv) == 4, "Pass proper arguments"
    url = sys.argv[1]
    config_file = sys.argv[2]
    test_flag = len(sys.argv) == 4 and sys.argv[3] == 'test'

    message = "If you don't see the above message/s getting updated every 10-12 minutes, please notify <@866338551947722822>"
    if test_flag:
        message = "I'm currently in the beta testing phase. " + message

    print(f'message = {message}')
    bot_config = {}
    with open(config_file) as fp:
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
