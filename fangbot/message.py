from discord import Embed, Colour
from pytz import timezone
from datetime import datetime

class FangBotMessage:
    # color = "rgb(255, 0, 0)"
    color = "#FF0000"

    def __init__(self):
        self.has_vr_a2s_data = False
        self.has_vr_metrics_data = False
        self.server_ip_port = ""
        self.server_name = ""
        self.max_players = 0
        self.players = []
        self.timezone = ""
        self.territories_info = ""

    def compose_embed(self):
        embed = Embed()
        if self.has_vr_a2s_data:
            embed.color = Colour.from_str(FangBotMessage.color)
            embed.title = self.server_name
            desc = [ f"**Connect:** {self.server_ip_port}" ]
            active_players = len(self.players)
            desc.append(f"**Active Players:** {active_players}/{self.max_players}")
            if self.territories_info: desc.append(self.territories_info)
            if len(self.players) > 0:
                desc.append("\n**Players**")
            embed.description = "\n".join(desc)
            for player in self.players:
                embed.add_field(name=player[0], value=player[1], inline=True)
            embed.set_footer(text=f"at {get_time(self.timezone)} {self.timezone}")
        return embed

def get_time(tz: str) -> str:
    ptz = timezone(tz)
    ret = datetime.now(ptz).strftime('%-I:%M %p %b %-d')
    return ret
