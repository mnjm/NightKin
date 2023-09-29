from discord import Webhook, NotFound, Forbidden
import aiohttp
import asyncio
from VRisingServer import VRisingServer
import logging
import json

INTERVAL_SECS = 10

class ConfigFile:
    def __init__(self, filepath: str):
        self.filepath = filepath
        with open(filepath) as fp:
            self.config = json.load(fp)

    def get_message_id(self, server_id):
        return self.config['servers_info'][server_id]['last_message_id']

    def update_message_id(self, server_id, message_id):
        filepath = self.filepath
        self.config["servers_info"][server_id]["last_message_id"] = message_id
        with open(filepath, 'w') as fp:
            json.dump(self.config, fp, indent=4)
        return


class FangBot:
    botname = 'FangBot'
    avatar_url = 'https://havi-x.github.io/hosted-images/TSR/BatWithFang.jpeg'
    interval_secs = INTERVAL_SECS

    def __init__(self, id, webhook_url, vr_ip, vr_port, timezone, config, embed=False):
        self.id = id
        self.webhook_url = webhook_url
        self.config = config
        self.vrserver = VRisingServer(id, vr_ip, vr_port, time_zone=timezone)
        self.embed = embed

    async def send_edit_message(self, webhook, msg_content):
        last_message_id = self.config.get_message_id(self.id)
        try:
            # Find the message with id
            wbmessage = await webhook.fetch_message(last_message_id)
            logging.debug(f"{self.id} fetching last message")
            # Editing message
            await wbmessage.edit(content=msg_content.content, embed=msg_content.embed)
            logging.debug(f"{self.id} editing message")
        except (NotFound, Forbidden):
            # If message not found create new message
            logging.info(f"{self.id} fetching message failed. Creating new message")
            # Sending a new message
            msg = await webhook.send(content=msg_content.content, embed=msg_content.embed, wait=True,
                                     username=FangBot.botname, avatar_url=FangBot.avatar_url,
                                     silent=True)
            # update message id in config
            self.config.update_message_id(self.id, msg.id)
            logging.info(f"Message created with id {msg.id}")
        return

    async def send_update(self):
        vr_has_info = self.vrserver.get_server_info()
        if vr_has_info:
            msg_content = self.vrserver.get_message_content(self.embed)
            logging.debug(f"{self.id} Sending message")
            async with aiohttp.ClientSession() as httpsession:
                webhook = Webhook.from_url(self.webhook_url, session=httpsession)
                await self.send_edit_message(webhook, msg_content)
        else:
            logging.debug(f"{self.id} Getting info from VRisingServer Failed")
        return vr_has_info

    async def run(self):
        while True:
            await self.send_update()
            await asyncio.sleep(FangBot.interval_secs)

# async def test():
#     url = r'https://discordapp.com/api/webhooks/1156421427835191366/RcWYGWe6wz0TniiJrVjBcQKPYfFLxEiUobnBDkQbDMIHbt34uEStoYE6Nvn3pYIGpjJZ'
#     bot = FangBot('pve test', url, "144.126.153.234", 31115, "US/Eastern", last_message_id=0)
#     # while not await bot.send_update(): continue
#     await bot.run()

# if __name__ == "__main__":
#     m_loop = asyncio.get_event_loop()
#     try:
#         m_loop.run_until_complete(test())
#     finally:
#         m_loop.close()
