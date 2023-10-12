from steam import game_servers as gs
import logging
from socket import timeout
from fangbot.message import FangBotMessage
from time import sleep

STEAM_DEFAULT_TIMEOUT = 10
V_RISING_GAME_ID = 1604030

def parse_players_info(players_info) -> list:

    def convert_days_hours_mins(duration: float) -> str:
        mins = duration / 60 # Convert to min
        days = mins // 1440 # Calculate days 24*60
        mins = mins % 1440
        hours = mins // 60 # Calculate hours
        mins = mins % 60
        ret = "{:02.0f}:{:02.0f}".format(hours, mins)
        if days > 0: ret = "{:.0f}:{}".format(days, ret)
        return ret

    ret_players = []
    for player in players_info:
        name = player['name']
        _time = convert_days_hours_mins(player['duration'])
        # Remove names with empty space
        if not name or name.isspace():
            logging.debug(f"Empty name found {name} with time {_time}")
            continue
        ret_players.append((name, _time))
    return ret_players


class VRisingServer:
    a2s_timeout = STEAM_DEFAULT_TIMEOUT

    def __init__(self, id: str, server_ip: str, server_port: int) -> None:
        self.id = id
        self.server_ip = server_ip
        self.server_port = server_port
        self.has_info = False
        self.server_info = {}
        self.players_info = {}
        logging.debug(f"VrisingServer.a2s_timeout = {VRisingServer.a2s_timeout}")

    def __eq__(self, other) -> bool:
        return self.server_ip == other.server_ip and self.server_port == other.server_port

    def get_server_info(self) -> bool:
        success, info, players = False, {}, {}
        server_info = (self.server_ip, self.server_port)
        while not success:
            try:
                logging.debug(f"{self.id} Getting VRising server info for {server_info}")
                info = gs.a2s_info(server_info, timeout=VRisingServer.a2s_timeout)
                players = gs.a2s_players(server_info, timeout=VRisingServer.a2s_timeout)
                success = True
            except timeout as e:
                logging.info(f"{self.id} Getting VRising server info failed for {server_info}. Retrying")
                logging.debug(f"{self.id} Error {e}")
                success = False
                # Sleep if a2s_timeout is not enought
                if VRisingServer.a2s_timeout <= 10:
                    sleep(5)
                    logging.debug("Sleeping for a few secs")
        self.has_info = success
        if self.has_info and info['app_id'] != V_RISING_GAME_ID:
            raise Exception("Not a V Rising Server")
        self.server_info = info
        self.players_info = players
        return self.has_info

    def write_data_to_FangBotMessage(self, fbmessage:FangBotMessage) -> bool:
        if self.has_info:
            info, players_info = self.server_info, self.players_info
            players_info = parse_players_info(players_info)
            fbmessage.has_vr_a2s_data = True
            fbmessage.server_name = info['name']
            fbmessage.server_ip_port = f"{self.server_ip}:{info['port']}"
            fbmessage.max_players = info['max_players']
            fbmessage.players = players_info
        return self.has_info
