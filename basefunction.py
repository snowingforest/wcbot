import nonebot
from config import GROUP


def get_valid_name(default, alter):
    if default and default is not '':
        return default
    else:
        return alter


async def get_nick_name(group, qq):
    bot = nonebot.get_bot()
    if group == GROUP:
        group_info = await bot.get_group_member_info(group_id=group, user_id=qq, no_cache=False)
    else:
        group_info = await bot.get_group_member_info(group_id=GROUP, user_id=qq, no_cache=False)
    user_info = await bot.get_stranger_info(user_id=qq, no_cache=False)
    return get_valid_name(group_info['card'], user_info['nickname'])
