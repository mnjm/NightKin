from discord import Webhook, NotFound, Forbidden, Embed
import aiohttp
import asyncio
from vrising_steam import VRisingServer
from vrising_metrics import VRisingMetrics
from .message import NightKinMessage
import logging
import json

INTERVAL_SECS = 10

class ConfigFile:

    def __init__(self, filepath: str):
        self.filepath = filepath
        with open(filepath) as fp:
            self.config = json.load(fp)

    def get_server_config_value(self, server_id:str, what:str):
        return self.config['servers_info'][server_id][what]

    def update_message_id(self, server_id:str, message_id:int) -> None:
        filepath = self.filepath
        # Update config dict
        self.config["servers_info"][server_id]["last_message_id"] = message_id
        # Update config file in dict
        with open(filepath, 'w') as fp:
            json.dump(self.config, fp, indent=4)
        return

class NightKin:
    botname = 'NightKin'
    avatar_url = 'https://havi-x.github.io/hosted-images/TSR/BatWithFang.jpeg'
    interval_secs = INTERVAL_SECS

    def __init__(self, id:str, webhook_url:str, vr_ip:str, vr_port:int, config:ConfigFile,
                 metrics_port:int = 0):
        self.id = id
        self.webhook_url = webhook_url
        self.config = config
        self.vrserver = VRisingServer(id, vr_ip, vr_port)
        self.vr_metrics = None
        if metrics_port > 0:
            self.vr_metrics = VRisingMetrics(f"http://{vr_ip}:{metrics_port}/metrics")

    async def send_edit_message(self, webhook:Webhook, embed:Embed) -> None:
        last_message_id = self.config.get_server_config_value(self.id, "last_message_id")
        try:
            # Find the message with id
            wbmessage = await webhook.fetch_message(last_message_id)
            logging.debug(f"{self.id} fetching last message")
            # Editing message
            await wbmessage.edit(content="", embed=embed)
            logging.debug(f"{self.id} editing message")
        except (NotFound, Forbidden):
            # If message not found create new message
            logging.info(f"{self.id} fetching message failed. Creating new message")
            # Sending a new message
            msg = await webhook.send(content="", embed=embed, wait=True,
                                     username=NightKin.botname, avatar_url=NightKin.avatar_url,
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
                # Create a new NightKinMessage
                fbmessage = NightKinMessage()
                fbmessage.timezone = self.config.get_server_config_value(self.id, 'timezone')
                # Get contents from V Rising server updated in NightKinMessage
                succ = self.vrserver.write_data_to_NightKinMessage(fbmessage)
                assert succ, "NightKinMessage not updated but VRising server has info? Why?"

                # Get VRising metrics
                if self.vr_metrics:
                    succ = self.vr_metrics.load_data()
                    if succ: self.vr_metrics.write_data_to_NightKinMessage(fbmessage)

                # Create webhook and send message
                logging.debug(f"{self.id} Sending message")
                async with aiohttp.ClientSession() as httpsession:
                    webhook = Webhook.from_url(self.webhook_url, session=httpsession)
                    await self.send_edit_message(webhook, fbmessage.compose_embed())

            # Sleep for some time
            await asyncio.sleep(NightKin.interval_secs)
