from urllib.request import urlopen
from urllib.error import URLError
from fangbot.message import FangBotMessage
import logging
from table2ascii import table2ascii

class VRisingMetrics:
    timeout = 10

    def __init__(self, url):
        self.has_info = False
        self.vr_ver_major = ""
        self.vr_ver_minor = ""
        self.vr_ver_path = ""
        self.vr_ver_revision = ""
        self.total_chars_created = 0
        self.active_users = 0
        self.max_users = 0
        self.up_time = 0
        self.fb_occupied = 0
        self.df_occupied = 0
        self.gs_occupied = 0
        self.gn_occupied = 0
        self.hm_occupied = 0
        self.sl_occupied = 0
        self.cf_occupied = 0
        self.fb_free = 0
        self.df_free = 0
        self.gs_free = 0
        self.gn_free = 0
        self.hm_free = 0
        self.sl_free = 0
        self.cf_free = 0
        self.url = url

    def load_data(self) -> bool:
        success = False
        try:
            contents = urlopen(self.url, timeout=VRisingMetrics.timeout)
            contents = contents.read().decode('utf-8')
            success = True
            self.explode_vr_metrics(contents)
        except URLError as e:
            logging.error(f"VRisingMetrics not found!{e}")
        self.has_info = success
        return success

    def write_data_to_FangBotMessage(self, fbmessage:FangBotMessage) -> bool:
        def form(name, avail, total):
            name = name + " "*(18-len(name))
            ret = f"{name} {avail:02d} / {total:02d}"
            print(ret)
            return ret

        if not self.has_info: return False
        header = ['Region', 'Free', 'Total']
        data = []
        data.append(["Farbane Woods", self.fb_free, self.fb_free + self.fb_occupied])
        data.append(["Dunley Farmlands", self.df_free, self.df_free + self.df_occupied])
        data.append(["Hallowed Mountains", self.hm_free, self.hm_free + self.hm_occupied])
        data.append(["Gloomrot South", self.gs_free, self.gs_free + self.gs_occupied])
        data.append(["Gloomrot North", self.gn_free, self.gn_free + self.gn_occupied])
        data.append(["Cursed Forest", self.cf_free, self.cf_free + self.cf_occupied])
        data.append(["Silverlight Hills", self.sl_free, self.sl_free + self.sl_occupied])
        fbmessage.territories_info = '**Available castle territories**\n```' + table2ascii(header, data) + '```'
        return True

    def explode_vr_metrics(self, data:str):
        for line in data.splitlines():
            # Ignode # Started values
            if line.startswith("# TYPE"): continue
            fields = line.split(" ")
            if fields[0] == "vr_version_major": self.vr_ver_major = fields[1]
            elif fields[0] == "vr_version_minor": self.vr_ver_minor = fields[1]
            elif fields[0] == "vr_version_patch": self.vr_ver_path = fields[1]
            elif fields[0] == "vr_version_revision": self.vr_ver_revision = fields[1]
            elif fields[0] == 'vr_users_connected': self.active_users = int(fields[1])
            elif fields[0] == 'vr_users_connected_max': self.max_users = int(fields[1])
            elif fields[0] == 'vr_uptime_seconds': self.up_time = int(fields[1])
            elif fields[0] == 'vr_users_taken': self.total_chars_created = int(fields[1])
            elif fields[0] == 'vr_activity_free_territories{region="FarbaneWoods"}':     self.fb_free = int(fields[1])
            elif fields[0] == 'vr_activity_free_territories{region="DunleyFarmlands"}':  self.df_free = int(fields[1])
            elif fields[0] == 'vr_activity_free_territories{region="HallowedMountains"}':self.hm_free = int(fields[1])
            elif fields[0] == 'vr_activity_free_territories{region="SilverlightHills"}': self.sl_free = int(fields[1])
            elif fields[0] == 'vr_activity_free_territories{region="Gloomrot_South"}':   self.gs_free = int(fields[1])
            elif fields[0] == 'vr_activity_free_territories{region="Gloomrot_North"}':   self.gn_free = int(fields[1])
            elif fields[0] == 'vr_activity_free_territories{region="CursedForest"}':     self.cf_free = int(fields[1])
            elif fields[0] == 'vr_activity_used_territories{region="FarbaneWoods"}':     self.fb_occupied = int(fields[1])
            elif fields[0] == 'vr_activity_used_territories{region="DunleyFarmlands"}':  self.df_occupied = int(fields[1])
            elif fields[0] == 'vr_activity_used_territories{region="HallowedMountains"}':self.hm_occupied = int(fields[1])
            elif fields[0] == 'vr_activity_used_territories{region="SilverlightHills"}': self.sl_occupied = int(fields[1])
            elif fields[0] == 'vr_activity_used_territories{region="Gloomrot_South"}':   self.gs_occupied = int(fields[1])
            elif fields[0] == 'vr_activity_used_territories{region="Gloomrot_North"}':   self.gn_occupied = int(fields[1])
            elif fields[0] == 'vr_activity_used_territories{region="CursedForest"}':     self.cf_occupied = int(fields[1])
            else: continue
        return
