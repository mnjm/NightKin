from discord import Webhook, NotFound, Forbidden
import aiohttp
import asyncio
from VRisingServer import VRisingServer, FangBotMessage
import logging
import json

INTERVAL_SECS = 10

class ConfigFile:

    def __init__(self, filepath: str):
        self.filepath = filepath
        with open(filepath) as fp:
            self.config = json.load(fp)

    def get_message_id(self, server_id:str) -> int:
        return self.config['servers_info'][server_id]['last_message_id']

    def update_message_id(self, server_id:str, message_id:int) -> None:
        filepath = self.filepath
        # Update config dict
        self.config["servers_info"][server_id]["last_message_id"] = message_id
        # Update config file in dict
        with open(filepath, 'w') as fp:
            json.dump(self.config, fp, indent=4)
        return

class FangBot:
    botname = 'FangBot'
    avatar_url = 'https://havi-x.github.io/hosted-images/TSR/BatWithFang.jpeg'
    interval_secs = INTERVAL_SECS

    def __init__(self, id:str, webhook_url:str, vr_ip:str, vr_port:int, timezone:str,
                 config:ConfigFile, embed:bool=False):
        self.id = id
        self.webhook_url = webhook_url
        self.config = config
        self.vrserver = VRisingServer(id, vr_ip, vr_port, time_zone=timezone)
        self.embed = embed

    async def send_edit_message(self, webhook:Webhook, msg_content:FangBotMessage) -> None:
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
        logging.info(f"{self.id} New update sent")
        return

    async def run(self) -> None:
        # Run forever
        while True:
            # Get information from V Rising server
            vr_has_info = self.vrserver.get_server_info()
            # Send/Update message only if v rising server has info otherwise continue
            if vr_has_info:
                # Get contents from V Rising server
                msg_content = self.vrserver.get_message_content(self.embed)
                logging.debug(f"{self.id} Sending message")
                # Create webhook and send message
                async with aiohttp.ClientSession() as httpsession:
                    webhook = Webhook.from_url(self.webhook_url, session=httpsession)
                    await self.send_edit_message(webhook, msg_content)

            # Sleep for some time
            await asyncio.sleep(FangBot.interval_secs)
