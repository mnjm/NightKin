import logging
import json
import asyncio
from FangBot import FangBot, ConfigFile
from VRisingServer import VRisingServer
from argparse import ArgumentParser
import os

ENV_WEBHOOK_URL_NAME = 'FANGBOT_WEBHOOK_URLS'
CONFIG_FILE = 'config.json'
# CONFIG_FILE = None # enable this to load config file from command line
LOGGING_LEVEL = logging.INFO

async def main(config_file: str) -> None:
    env_wb_urls = {}
    if not ENV_WEBHOOK_URL_NAME in os.environ:
        logging.error("Loading webhook urls failed! Env var not found!!")
        return
    r_urls = os.environ[ENV_WEBHOOK_URL_NAME]
    env_wb_urls = json.loads(r_urls)
    logging.debug(f"URLS Loaded from env! {env_wb_urls}")

    # Load Config
    confobj = ConfigFile(config_file)
    config = confobj.config
    logging.debug("Loaded Config\n" + json.dumps(config, indent=4))
    FangBot.botname = config['botname']
    FangBot.avatar_url = config['bot_avatar_url']
    FangBot.interval_secs = config['update_interval']
    VRisingServer.a2s_timeout = config['a2s_timeout']

    tasks = []
    for sid in config['servers_info']:
        logging.info("Creating a bot for {}".format(sid))
        # Create FangBot for the server
        if not sid in env_wb_urls:
            logging.error(f"Webhook URL for '{sid}' not found in env var {ENV_WEBHOOK_URL_NAME}. Exiting!")
            return
        wb_url = env_wb_urls[sid]
        server = config['servers_info'][sid]
        bot = FangBot(sid, wb_url, server['vr_ip'],
                      server['vr_query_port'], server['timezone'],
                      confobj,
                      embed=server['embed'])
        # Run the bot
        task = asyncio.create_task(bot.run())
        tasks.append(task)
        logging.info("Bot creation successful {}".format(sid))

    for task in tasks: await task
    return


if __name__ == "__main__":

    config_file = CONFIG_FILE
    if not CONFIG_FILE:
        # Command line args
        parser = ArgumentParser("FangBot - Webhook based Discord bot to display live VRising server data")
        parser.add_argument("config_file", help="Json Config file")
        parser.add_argument("--debug", help="Enables debug log", action='store_true')
        args = parser.parse_args()

        logging.basicConfig(format = '%(levelname)s:%(asctime)s: %(message)s',
                            level = logging.DEBUG if args.debug else logging.INFO)

        logging.debug(f"Command line args:{args}")
    else:
        logging.basicConfig(format = '%(levelname)s:%(asctime)s: %(message)s', level=LOGGING_LEVEL)

    # Run bots
    m_loop = asyncio.get_event_loop()
    try:
        m_loop.run_until_complete(main(config_file))
    finally:
        m_loop.close()
