import nonebot
from hoshino.config.bot_manager_web import DOMAIN_URL

bot = nonebot.get_bot()


@bot.on_message('private')
async def setting(ctx):
    message = ctx['raw_message']
    if message == 'bot设置':
        await bot.send(ctx, f'{DOMAIN_URL}/manage', at_sender=False)
