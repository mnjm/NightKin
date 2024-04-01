import logging
from logging.handlers import RotatingFileHandler
import sys
import json
import asyncio
from nightkin import NightKin, ConfigFile
from nightkin.message import NightKinMessage
from vrising_steam import VRisingServer
from argparse import ArgumentParser
import os

ENV_WEBHOOK_URL_NAME = 'NIGHTKIN_WEBHOOK_URLS'
APP_NAME = "NightKin"
# CONFIG_FILE = 'config.json'
CONFIG_FILE = "" # enable this to load config file from command line.
STD_LOGGING_LEVEL = logging.INFO

async def main(config_file: str) -> None:
    logging.info("x"*97)
    logging.info("x"*40+" NightKin Started "+"x"*40)
    logging.info("x"*97)

    # Load Webhook urls from env
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
    # Update configurations
    NightKin.botname = config['botname']
    NightKin.avatar_url = config['bot_avatar_url']
    NightKin.interval_secs = config['update_interval']
    NightKinMessage.color = config['embed_color']
    logging.info(f"Will update in every {NightKin.interval_secs}s ({NightKin.interval_secs/60}mins)")
    VRisingServer.a2s_timeout = config['a2s_timeout']

    logging.info("-"*60)
    tasks = []
    for sid in config['servers_info']:
        logging.info("Creating a bot for {}".format(sid))
        # Create NightKin for the server
        if not sid in env_wb_urls:
            logging.error(f"Webhook URL for '{sid}' not found in env var {ENV_WEBHOOK_URL_NAME}. Exiting!")
            return
        wb_url = env_wb_urls[sid]
        server = config['servers_info'][sid]
        bot = NightKin(sid, wb_url, server['vr_ip'],
                      server['vr_query_port'], confobj, server['vr_metrics_port'])

        # Run the bot
        task = asyncio.create_task(bot.run())
        tasks.append(task)
        logging.info("Bot creation successful {}".format(sid))
    logging.info("-"*60)

    # Wait for the bots to exit. At present bots doesnt have exit conditions, might add em later.
    for task in tasks: await task
    return

def setup_file_stdout_loggers(config_file):
    # Change root logger level from WARNING (default) to NOTSET in order for all messages to be delegated.
    logging.getLogger().setLevel(logging.NOTSET)

    # Add stdout handler, with level INFO
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(STD_LOGGING_LEVEL)
    formater = logging.Formatter(f'{APP_NAME} %(levelname)s:%(asctime)s: %(message)s')
    console.setFormatter(formater)
    logging.getLogger().addHandler(console)

    # Add file rotating handler, with level DEBUG
    logfilepath = os.path.join(os.path.dirname(config_file), "NightKin.log")
    fileHandler = RotatingFileHandler(filename=logfilepath, mode='a', maxBytes=5*1024*1024, backupCount=3, encoding=None, delay=False)
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formater)
    logging.getLogger().addHandler(fileHandler)

    return

if __name__ == "__main__":

    config_file = CONFIG_FILE
    if not CONFIG_FILE:
        # Command line args
        parser = ArgumentParser("NightKin - Webhook based Discord bot to display live VRising server data")
        parser.add_argument("config_file", help="Json Config file")
        parser.add_argument("--debug", help="Enables debug log", action='store_true')
        args = parser.parse_args()
        if args.debug: STD_LOGGING_LEVEL = logging.DEBUG
        config_file = args.config_file

    setup_file_stdout_loggers(config_file)

    # Run bots
    m_loop = asyncio.get_event_loop()
    try:
        m_loop.run_until_complete(main(config_file))
    finally:
        m_loop.close()
