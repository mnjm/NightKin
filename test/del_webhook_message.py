"""
Test phase message deletor
"""
from discord import Webhook
import sys
import asyncio
import aiohttp

async def main() -> None:
    url = sys.argv[1]
    messageid = int(sys.argv[2])
    print(f'url = {url}')
    print(f'id = {messageid}')

    async with aiohttp.ClientSession() as sess:
        webhook = Webhook.from_url(url, session=sess)
        await webhook.delete_message(messageid)

if __name__ == "__main__":
    ml = asyncio.get_event_loop()
    try:
        ml.run_until_complete(main())
    finally:
        ml.close()
