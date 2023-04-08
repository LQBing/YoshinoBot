import json
import os
from urllib.parse import urljoin


class Switcher:
    Passive = True
    Active = False
    Request = False

    def __init__(self, glo_setting: dict, *args, **kwargs):
        self.setting = glo_setting

    def save_settings(self) -> None:
        save_setting = self.setting.copy()
        del save_setting["dirname"]
        del save_setting["verinfo"]
        config_path = os.path.join(
            self.setting["dirname"], "yobot_config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(save_setting, f, indent=4)

    @staticmethod
    def match(cmd: str) -> int:
        if cmd == "设置":
            f = 0x300
        elif cmd.startswith("设置码"):
            f = 0x400
        elif cmd.startswith("设置"):
            if len(cmd) < 7:
                f = 0x500
            else:
                f = 0
        else:
            f = 0
        return f


    def execute(self, match_num: int, msg: dict) -> dict:
        return urljoin(
            self.setting['public_address'],
            '{}admin/setting/'.format(self.setting['public_basepath'])
        )
