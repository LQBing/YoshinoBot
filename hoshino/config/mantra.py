import json
from hoshino.util import get_environ
from hoshino import R

MANTRA_CONFIG_PATH = get_environ('MANTRA_CONFIG_PATH', 'mantra.json')
# [
#     {
#         "name": [
#             "羊鸽"
#         ],
#         "keywords": [
#             "ygnb",
#             "YGNB"
#         ],
#         "path_list": [
#             "YG"
#         ],
#         "group_list": []
#     }
# ]


class MantraConfig():
    config_list = []
    keywords = []

    def __init__(self, config_file_path) -> None:
        data = None
        with open(config_file_path, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
        print("mantra config : %s" % data)
        self.config_list = data
        self.keywords = []
        for item in self.config_list:
            for k in item['keywords']:
                self.keywords.append(k)

    def get_keywords(self):
        return self.keywords

    def get_path_list(self, keyword):
        path_list = []
        for config in self.config_list:
            if keyword in config['keywords']:
                path_list = config['path_list']
        return path_list

    def get_config(self, keyword):
        for config in self.config_list:
            if keyword in config['keywords']:
                return config
        return {}

    def allow_group(self, keyword, group_id):
        config = self.get_config(keyword=keyword)
        if config:
            if 'group_list' in config:
                if group_id not in config['group_list']:
                    return False
        return True
