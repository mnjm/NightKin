from steam import game_servers as gs
from datetime import datetime
from pytz import timezone
import logging
from socket import timeout
from discord import Embed, Colour

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
        if not name and name.isspace():
            logging.debug(f"Empty name found {name} with time {_time}")
            continue
        ret_players.append((name, _time))
    return ret_players

def get_footer(tz: str) -> str:
    ptz = timezone(tz)
    ret = datetime.now(ptz).strftime('%-I:%M %p %b %-d')
    ret = f"at {ret} {tz}"
    return ret

class FangBotMessage:
    def __init__(self, content:str, embed:Embed):
        self.content = content
        self.embed = embed

class VRisingServer:
    a2s_timeout = STEAM_DEFAULT_TIMEOUT

    def __init__(self, id: str, server_ip: str, server_port: int, time_zone: str) -> None:
        self.id = id
        self.server_ip = server_ip
        self.server_port = server_port
        self.has_info = False
        self.server_info = {}
        self.players_info = {}
        self.timezone = time_zone
        logging.debug(f"VrisingServer.a2s_timeout = {VRisingServer.a2s_timeout}")

    def __eq__(self, other) -> bool:
        return self.server_ip == other.server_ip and self.server_port == other.server_port

    def get_server_info(self) -> bool:
        success, info, players = False, {}, {}
        server_info = (self.server_ip, self.server_port)
        try:
            logging.debug(f"{self.id} Getting VRising server info for {server_info}")
            info = gs.a2s_info(server_info, timeout=VRisingServer.a2s_timeout)
            players = gs.a2s_players(server_info, timeout=VRisingServer.a2s_timeout)
            success = True
        except (RuntimeError, timeout) as e:
            logging.info(f"{self.id} Getting VRising server info failed for {server_info}")
            logging.debug(f"{self.id} Error {e}")
            success = False
            info, players = {}, {}
        self.has_info = success
        if self.has_info and info['app_id'] != V_RISING_GAME_ID:
            raise Exception("Not a V Rising Server")
        self.server_info = info
        self.players_info = players
        return self.has_info

    def get_message_content(self, embed = False) -> FangBotMessage:
        ret = FangBotMessage("", Embed())
        if not self.has_info: return ret
        info, players = self.server_info, self.players_info
        players_list = parse_players_info(players)
        ping = info['_ping']
        name = info['name']
        max_players = info['max_players']
        active_players = len(players_list)
        if embed:
            ret.embed.color = Colour.red()
            ret.embed.title = info['name']
            desc = [ f"**Connect:** {self.server_ip}:{self.server_port}" ]
            desc.append(f"**Active Players:** {active_players}/{max_players}")
            if len(players_list) > 0:
                desc.append("\n**Players**")
            ret.embed.description = "\n".join(desc)
            for player in players_list:
                ret.embed.add_field(name=player[0], value=player[1], inline=True)
            ret.embed.set_footer(text=get_footer(self.timezone))
        else:
            message = []
            message.append("Name {}".format(name))
            message.append("IP {}:{}".format(self.server_ip, self.server_port))
            message.append('Ping {:.2f}'.format(ping))
            message.append('Players {}/{}'.format(active_players, max_players))
            message.append('-'*50)
            for player in players_list:
                message.append(f'{player[0]} {player[1]}')
            message.append(get_footer(self.timezone))
            ret.content = "\n".join(message)
        return ret

def test():
    print("Steam Server Query Test Code")

    pve = VRisingServer('PvE', "144.126.153.234", 31115, "US/Eastern")
    pvp = VRisingServer('PvP', "194.140.197.196", 37315, "US/Eastern")
    for v in [pve, pvp]:
        print()
        v.get_server_info()
        print(v.get_message_content().content)

if __name__ == "__main__":
    test()
