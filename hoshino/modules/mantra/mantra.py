import os
import random

from nonebot.exceptions import CQHttpError

from hoshino import R, Service, priv, util
from hoshino.util import FreqLimiter, DailyNumberLimiter
from hoshino.config.mantra import MANTRA_MATRIX

_max = 50
_fl = 60
EXCEED_NOTICE = f'今天艹爷已经迫害过{_max}次了，欢迎明早5点后在继续迫害！'
_n_limit = DailyNumberLimiter(_max)
_f_limit = FreqLimiter(_fl)

sv = Service('mantra', manage_priv=priv.SUPERUSER, enable_on_default=False, visible=False)
mantra_folder = R.img('mantra/').path


def mantra_generator(name):
    while True:
        file_list = os.listdir(mantra_folder)
        random.shuffle(file_list)
        for filename in file_list:
            if os.path.isfile(os.path.join(mantra_folder, MANTRA_MATRIX[name]['path'], filename.replace('\\', '/'))):
                yield R.img(os.path.join('mantra/', MANTRA_MATRIX[name]['path'], filename.replace('\\', '/')))


mantra_generators = dict()

for i in MANTRA_MATRIX:
    mantra_generators[i] = mantra_generator(i)


def get_mantra(name):
    return mantra_generators[name].__next__()


@sv.on_fullmatch(MANTRA_MATRIX)
async def mantra(bot, ev):
    name = util.normalize_str(ev.message.extract_plain_text())
    """随机叫一份真言语录，对每个用户有冷却时间"""
    uid = ev['user_id']
    if not _n_limit.check(uid):
        await bot.send(ev, EXCEED_NOTICE, at_sender=True)
        return
    if not _f_limit.check(uid):
        limited = True
        await bot.send(ev, f'您迫害的太频繁了，距离上次迫害还不到{_fl}秒，爱护{MANTRA_MATRIX[name]["name"]}人人有责。迫害虽棒可不要贪哦(๑•̀ㅂ•́)و✧',
                       at_sender=True)
        if limited:
            return
    _f_limit.start_cd(uid)
    _n_limit.increase(uid)

    # conditions all ok, send a mantra.
    pic = get_mantra(name)
    try:
        await bot.send(ev, pic.cqcode)
    except CQHttpError:
        sv.logger.error(f"发送图片{pic.path}失败")
        try:
            await bot.send(ev, '太艹了，发不出去勒...')
        except:
            pass
