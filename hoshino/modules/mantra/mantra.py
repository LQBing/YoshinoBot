import os
import json
import random

from nonebot.exceptions import CQHttpError

from hoshino import R, Service, priv
from hoshino.util import FreqLimiter, DailyNumberLimiter
from hoshino.config.mantra import MANTRA_CONFIG_PATH


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
                if str(group_id) not in config['group_list']:
                    return False
        return True


MANTRA_CONFIG = MantraConfig(
    R.img(os.path.join('mantra', MANTRA_CONFIG_PATH)).path)
MANTRA_KEYWORDS = MANTRA_CONFIG.get_keywords()

_max = 50
_fl = 60
EXCEED_NOTICE = f'今天已经迫害过{_max}次了，欢迎明早5点后在继续迫害！'
_n_limit = DailyNumberLimiter(_max)
_f_limit = FreqLimiter(_fl)

sv = Service('mantra', manage_priv=priv.SUPERUSER,
             enable_on_default=False, visible=False)


def mantra_generator(name):
    while True:
        file_list = list()
        for p in MANTRA_CONFIG.get_path_list(name):
            _p = os.path.join(R.img('mantra').path, p)
            f_list = os.listdir(_p)
            for filename in f_list:
                file_list.append(os.path.join(p, filename))
        random.shuffle(file_list)
        for filename in file_list:
            if os.path.isfile(os.path.join(R.img('mantra').path, filename)):
                yield R.img(os.path.join('mantra', filename))


mantra_generators = dict()

for i in MANTRA_KEYWORDS:
    mantra_generators[i] = mantra_generator(i)


def get_mantra(name):
    return mantra_generators[name].__next__()


@sv.on_fullmatch(MANTRA_KEYWORDS)
async def mantra(bot, ev):
    """随机叫一份真言语录，对每个用户有冷却时间"""
    # 获取语录名
    kw = ev.raw_message
    uid = ev.user_id
    gid = ev.group_id
    name = MANTRA_CONFIG.get_config(kw)['name']
    if MANTRA_CONFIG.allow_group(kw, gid):
        if not _n_limit.check(uid):
            await bot.send(ev, EXCEED_NOTICE, at_sender=True)
            return
        if not _f_limit.check(uid):
            limited = True
            await bot.send(ev, f'您迫害的太频繁了，距离上次迫害还不到{_fl}秒，爱护{name}人人有责。迫害虽棒可不要贪哦(๑•̀ㅂ•́)و✧',
                           at_sender=True)
            if limited:
                return
        _f_limit.start_cd(uid)
        _n_limit.increase(uid)

        # conditions all ok, send a mantra.
        pic = get_mantra(kw)
        try:
            await bot.send(ev, pic.cqcode)
        except CQHttpError:
            sv.logger.error(f"发送图片{pic.path}失败")
            try:
                await bot.send(ev, '土豆发芽了，图片发不出去勒...')
            except:
                print("too bad, error message send fail")
