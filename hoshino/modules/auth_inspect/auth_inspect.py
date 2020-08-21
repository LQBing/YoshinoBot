import math
import requests
from hoshino.config.auth_inspect import BOT_AUTH_SERVER
from hoshino.config import SUPERUSERS
from hoshino import logger
from aiocqhttp.exceptions import ActionFailed
from hoshino import Service, priv
from urllib.parse import urljoin

sv_help = '''
[查询授权] 查询本群授权剩余时间
'''.strip()
sv = Service('auth_inspect', manage_priv=priv.SUPERUSER, enable_on_default=False, help_=sv_help, bundle='授权')


def auth_data_to_dhms(data):
    days = data['data']['days']
    seconds = data['data']['seconds']
    hours = math.floor(seconds / 3600)
    seconds = seconds - hours * 3600
    minutes = math.floor(seconds / 60)
    seconds = seconds - minutes * 60
    return days, hours, minutes, seconds


@sv.on_prefix('查询授权')
async def query_auth(bot, ctx):
    msg = ctx['message'].extract_plain_text().strip()
    if msg:
        if SUPERUSERS and str(ctx['user_id']) in SUPERUSERS:
            msg = ctx['message'].extract_plain_text()
            if msg:
                if msg.isnumeric():
                    r = requests.get(urljoin(BOT_AUTH_SERVER, f'charge/verify?group_id={msg}')).json()
                    if 'data' in r and 'days' in r['data'] and 'seconds' in r['data']:
                        days, hours, minutes, seconds = auth_data_to_dhms(r)
                        await sv.bot.send_msg(user_id=ctx['user_id'],
                                              message=f"{msg} 授权还有{days}天{hours}小时{minutes}分钟{seconds}秒")
                    else:
                        await sv.bot.send_msg(user_id=ctx['user_id'], message=f"{msg} 授权已过期")
    else:
        if ctx['type'] == 'GroupMessage':
            sid = ctx['self_id']
            gid = ctx['group_id']
            await inspect(gid=gid, sid=sid, group_name='', inspect_type='query')


@sv.on_fullmatch('巡查全部授权', only_to_me=True)
@sv.scheduled_job('cron', hour='19')
async def inspect_task():
    self_ids = sv.bot._wsr_api_clients.keys()
    for sid in self_ids:
        gl = await sv.bot.get_group_list(self_id=sid)
        for g in gl:
            gid = g['group_id']
            await inspect(gid=gid, sid=sid, group_name=g['group_name'], inspect_type='inspect')


async def inspect(gid, sid, group_name, inspect_type):
    r = requests.get(urljoin(BOT_AUTH_SERVER, f'charge/verify?group_id={gid}')).json()
    if r['status'] == 'ok':
        if 'data' in r and 'days' in r['data'] and 'seconds' in r['data']:
            days, hours, minutes, seconds = auth_data_to_dhms(r)
            if inspect_type == 'query':
                # 主动查询
                await sv.bot.send_group_msg(group_id=int(gid), message=f"授权还有{days}天{hours}小时{minutes}分钟{seconds}秒")
            else:
                # 定时巡查
                if days < 3:
                    await sv.bot.send_group_msg(group_id=int(gid),
                                                message=f"授权只有{days}天{hours}小时{minutes}分钟{seconds}秒就要到期了，真的不续费吗？")
        else:
            await sv.bot.send_group_msg(group_id=int(gid),
                                        message=f"授权信息不正常，请联系客服人员 {SUPERUSERS}")
            if SUPERUSERS:
                for super_id in SUPERUSERS:
                    await sv.bot.send_msg(user_id=int(super_id), message=f"group id {gid} auth info not correct",
                                          self_id=sid)
            logger.error(f"group id {gid} auth info not correct")
        logger.info(f"{gid} {group_name} auth ok")
    elif r['msg'] == 'expired':
        logger.info(f"{gid} {group_name} auth expired，quit group")
        try:
            await sv.bot.send_group_msg(group_id=int(gid), message='授权已经到期了，我走了哟')
            await sv.bot.set_group_leave(group_id=int(gid), is_dismiss=False, self_id=sid)
        except ActionFailed as e:
            if e.retcode == 103:
                logger.error('An owner cannot quit from a owning group')
                await sv.bot.send_group_msg(group_id=int(gid), message='哎呀，我是群主，走不掉呢', self_id=sid)
            else:
                logger.error(e)
    else:
        logger.info(f"{gid} {group_name} auth fail，quit group")
        await sv.bot.send_group_msg(group_id=int(gid), message='授权不存在，看来我走错地方了，我走了哟', self_id=sid)
        await sv.bot.set_group_leave(group_id=int(gid), is_dismiss=False, self_id=sid)
