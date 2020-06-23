from horserace_source import HorseRace
from wcr_source import Wcr
from config import HORSE, HORSE_SKIN
from nonebot import on_command, CommandSession, scheduler
import datetime
from apscheduler.triggers.date import DateTrigger
import nonebot
from basefunction import get_valid_name, get_nick_name
import random


@on_command('wcr赛马', only_to_me=False)
async def wcr_horserace(session: CommandSession):
    hr = HorseRace()
    state = await hr.race_state()
    if state == -1:
        response = "wcr赛马现在接受报名！报名时间为1分钟！参赛上限为4人！\n报名方法为输入【出马 角色名】（e.g. 出马 毛二力）\n角色只能选择在wcr抽卡中获得的3星角色\n输入【wcr查看】可以看自己拥有哪些角色"
        await hr.set_state(0)
        delta = datetime.timedelta(seconds=60)
        trigger = DateTrigger(
            run_date=datetime.datetime.now() + delta
        )
        scheduler.add_job(
            func=end_join,
            trigger=trigger,
            args=(session.ctx['group_id'],),
            misfire_grace_time=60,
        )
    else:
        response = "已有正在进行的赛马！"
    await session.send(response)


@on_command('结束wcr赛马', only_to_me=False)
async def end_wcr_horserace(session: CommandSession):
    hr = HorseRace()
    state = await hr.race_state()
    if session.ctx['user_id'] == 463725434 and state != -1:
        response = "赛马结束了！"
        await hr.end_race()
    else:
        response = "无法结束赛马！"
    await session.send(response)


@on_command('出马', only_to_me=False)
async def join_wcr_horserace(session: CommandSession):
    hr = HorseRace()
    wcr_data = Wcr()
    player = await wcr_data.search_player(session.ctx['user_id'])
    state = await hr.race_state()
    if state == 0:
        if player:
            horse = await hr.search_horse_by_player(session.ctx['user_id'])
            if horse:
                response = "您已加入了赛马。"
            else:
                input_name = session.current_arg_text.strip()
                if input_name:
                    nickname_dict = await get_nickname_dict()
                    if input_name in nickname_dict.keys():
                        horse_name = nickname_dict[input_name]
                    else:
                        horse_name = input_name
                    chara = await wcr_data.search_chara(session.ctx['user_id'], horse_name)
                    if chara:
                        response = "%s派出了%s进行赛马!" % (get_valid_name(session.ctx['sender']['card'], session.ctx['sender']['nickname']), horse_name)
                        await hr.add_horse(chara)
                        horse_list = await hr.search_horse()
                        if len(horse_list) >= 4:
                            await end_join(session.ctx['group_id'])
                    else:
                        response = "您没有叫做%s的角色。输入【wcr查看】看看自己有哪些3星吧！" % input_name
                else:
                    response = "参数错误"
        else:
            response = "您尚未加入wcr，无法赛马"
    else:
        response = "当前不在报名阶段"
    await session.send(response)


@on_command('赌马', only_to_me=False)
async def join_wcr_horserace_gamble(session: CommandSession):
    hr = HorseRace()
    wcr_data = Wcr()
    player = await wcr_data.search_player(session.ctx['user_id'])
    state = await hr.race_state()
    if state == -2:
        cost = 100
        if player and player[1] >= cost:
            horse_id = session.current_arg_text.strip()
            horse_list = await hr.search_horse()
            if horse_id and 1 <= int(horse_id) <= len(horse_list):
                result = await hr.join_gamble(session.ctx['user_id'], int(horse_id))
                if result == 1:
                    response = "%s下注了%s号马！" % (get_valid_name(session.ctx['sender']['card'], session.ctx['sender']['nickname']), int(horse_id))
                    await wcr_data.update_player_info(player[0], player[1] - 100, player[2], player[3])
                else:
                    response = "您已经下过注了"
            else:
                response = "参数错误"
        else:
            response = "您尚未加入wcr或者没钱，无法赌马"
    else:
        response = "当前不在赌马阶段"
    await session.send(response)


@on_command('赛马胜率', only_to_me=False)
async def wcr_horserace_stat(session: CommandSession):
    hr = HorseRace()
    winner_list = await hr.win_rate_stat()
    list_len = len(winner_list)
    response = "胜率前三的角色是：\n"
    response += "%s：%s\n" % (winner_list[list_len - 1][0], round(winner_list[list_len - 1][3], 2))
    response += "%s：%s\n" % (winner_list[list_len - 2][0], round(winner_list[list_len - 2][3], 2))
    response += "%s：%s\n" % (winner_list[list_len - 3][0], round(winner_list[list_len - 3][3], 2))
    response += "胜率倒数前三的角色是：\n"
    response += "%s：%s\n" % (winner_list[0][0], round(winner_list[0][3], 2))
    response += "%s：%s\n" % (winner_list[1][0], round(winner_list[1][3], 2))
    response += "%s：%s" % (winner_list[2][0], round(winner_list[2][3], 2))
    await session.send(response)


async def end_join(group_id):
    bot = nonebot.get_bot()
    hr = HorseRace()
    state = await hr.race_state()
    if state == 0:
        horse_list = await hr.search_horse()
        if len(horse_list) > 1:
            response = "报名已结束，赌马阶段开始！1分钟内可以发送【赌马 编号】加入赌马。系统会自动扣除100宝石作为本金。\n"
            await bot.send_group_msg(group_id=group_id, message=response)
            await start_gamble(group_id)
        else:
            response = "报名人数不足，赛马结束！"
            await bot.send_group_msg(group_id=group_id, message=response)
            await hr.end_race()


async def start_gamble(group_id):
    bot = nonebot.get_bot()
    hr = HorseRace()
    horse_list = await hr.search_horse()
    if len(horse_list) <= 4:
        await hr.set_state(-2)
        response = ""
        for horse in horse_list:
            if horse[1] in HORSE_SKIN.keys():
                skin = HORSE_SKIN[horse[1]]
            else:
                skin = HORSE
            horse_line = "【%s】:%s的%s%s\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1], skin)
            response += horse_line
        await bot.send_group_msg(group_id=group_id, message=response)
        delta = datetime.timedelta(seconds=60)
        trigger = DateTrigger(
            run_date=datetime.datetime.now() + delta
        )
        scheduler.add_job(
            func=start_game,
            trigger=trigger,
            args=(group_id,),
            misfire_grace_time=60,
        )
        scheduler.add_job(
            func=hr.set_state,
            trigger=trigger,
            args=(1,),
            misfire_grace_time=60,
        )
    else:
        response = "检测到马数异常，赛马强制结束！"
        await bot.send_group_msg(group_id=group_id, message=response)
        await hr.end_race()


async def start_game(group_id):
    bot = nonebot.get_bot()
    hr = HorseRace()
    state = await hr.race_state()
    if state <= 1:
        current_round = 1
    else:
        current_round = state
    response = "行动阶段#%s\n" % current_round
    horse_list = await hr.search_horse()
    for horse in horse_list:
        move = await hr.move_horse(horse[0])
        if move > 0:
            response += "%s的%s向前冲了%s步！\n" % (await get_nick_name(group_id, horse[2]), horse[1], move)
        else:
            response += "%s的%s摸鱼了！\n" % (await get_nick_name(group_id, horse[2]), horse[1])
    response += "战斗阶段\n"
    r = random.randint(1, 8)
    if r <= 3:
        response += "上帝鸽了\n"
    else:
        response += await hr.god_attack(group_id)
    ub_list = await hr.search_sorted_horse_ascend()
    for horse in ub_list:
        if horse[4] >= 100:
            response += await hr.ub(horse, group_id)
    response += "最终状态\n"
    horse_list = await hr.search_horse()
    champ_list = list()
    for horse in horse_list:
        if horse[1] in HORSE_SKIN.keys():
            skin = HORSE_SKIN[horse[1]]
        else:
            skin = HORSE
        horse_line = "[CQ:emoji,id=%s]:" % (10000048 + horse[0]) + "=" * (horse[3] - 1) + skin + "=" * (10 - horse[3]) + "\n"
        response += horse_line
        if horse[3] == 10:
            champ_list.append(horse)
    await bot.send_group_msg(group_id=group_id, message=response)
    if len(champ_list) > 0:
        response = "赛马结束了！恭喜\n"
        for horse in champ_list:
            response += "%s的%s\n" % (await get_nick_name(group_id, horse[2]), horse[1])
            await hr.add_winner(horse[1])
        response += "获得了冠军！"
        for horse in horse_list:
            await hr.add_race(horse[1])
        await bot.send_group_msg(group_id=group_id, message=response)
        await resolve_gamble(group_id, champ_list)
        await hr.end_race()
    else:
        state = await hr.race_state()
        if state != -1:
            await hr.set_state(max(2, current_round + 1))
            delta = datetime.timedelta(seconds=10)
            trigger = DateTrigger(
                run_date=datetime.datetime.now() + delta
            )
            scheduler.add_job(
                func=start_game,
                trigger=trigger,
                args=(group_id,),
                misfire_grace_time=60,
            )


async def resolve_gamble(group_id, champ_list):
    bot = nonebot.get_bot()
    hr = HorseRace()
    wcr_data = Wcr()
    gamble_player_list = await hr.search_gamble()
    pool = 100 * len(gamble_player_list)
    win_player_list = list()
    response = "赌马获胜的玩家是:\n"
    for horse in champ_list:
        for player in gamble_player_list:
            if player[1] == horse[0]:
                response += "%s\n" % await get_nick_name(group_id, player[0])
                win_player_list.append(player)
    if len(win_player_list) == 0:
        response += "真遗憾，无人获胜！%s宝石消失在虚空之中。" % pool
    else:
        money = pool // len(win_player_list)
        response += "每人获得了奖金%s宝石" % money
        for win_player in win_player_list:
            await wcr_data.send_money_to_player(win_player[0], money)
    await bot.send_group_msg(group_id=group_id, message=response)


async def get_nickname_dict():
    nickname_dict = {}
    f = open('nickname_hr.txt', 'r', encoding='utf-8')
    csv = f.read().split('\n')
    for line in csv:
        row = line.split(' ')
        for col in row:
            nickname_dict[col] = row[2]
    f.close()
    return nickname_dict
