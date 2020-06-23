from gacha import Gacha
from wcr_source import Wcr
from nonebot import on_command, CommandSession
from basefunction import *
import nonebot
from config import *


@nonebot.scheduler.scheduled_job('cron', hour=5, misfire_grace_time=600)
async def check_day():
    wcr_data = Wcr()
    await wcr_data.send_money(4500)


@on_command('wcr', only_to_me=False)
async def wcr_readme(session: CommandSession):
    f = open('wcr_readme.txt', 'r', encoding='utf-8')
    response = f.read()
    f.close()
    await session.send(response)


@on_command('wcr发钱', only_to_me=False)
async def wcr_send_money(session: CommandSession):
    wcr_data = Wcr()
    if session.ctx['user_id'] == 463725434:
        wage = int(session.current_arg_text.strip())
        await wcr_data.send_money(wage)
        response = '%s宝石已发送' % wage
    else:
        response = '就你也想发钱？'
    await session.send(response)


@on_command('wcr发放', only_to_me=False)
async def wcr_send_chara(session: CommandSession):
    wcr_data = Wcr()
    if session.ctx['user_id'] == 463725434:
        chara_name = session.current_arg_text.strip()
        player_list = await wcr_data.get_player_list()
        for player in player_list:
            chara = await wcr_data.search_chara(player[0], chara_name)
            if not chara:
                await wcr_data.add_chara(player[0], chara_name)
        response = '%s已发送' % chara_name
    else:
        response = '就你也想发？'
    await session.send(response)


@on_command('加入wcr', aliases='wcr加入', only_to_me=False)
async def join_wcr(session: CommandSession):
    wcr_data = Wcr()
    result = await wcr_data.search_player(session.ctx['user_id'])
    if result:
        response = '您已加入游戏'
    else:
        r = await wcr_data.create_player(session.ctx['user_id'], 0)
        if r == 1:
            response = '%s创建角色成功, 现有财产15000宝石，傻必次数1次，剩余可转生次数3次' % get_valid_name(session.ctx['sender']['card'], session.ctx['sender']['nickname'])
        else:
            response = '%s创建角色失败' % get_valid_name(session.ctx['sender']['card'], session.ctx['sender']['nickname'])
    await session.send(response)


@on_command('wcr转生', only_to_me=False)
async def wcr_revive(session: CommandSession):
    wcr_data = Wcr()
    result = await wcr_data.search_player(session.ctx['user_id'])
    if result:
        revive_time = result[4]
        if revive_time <= 3:
            await wcr_data.delete_player(session.ctx['user_id'])
            r = await wcr_data.create_player(session.ctx['user_id'], revive_time + 1)
            if r == 1:
                response = '%s转生成功, 现有财产15000宝石，傻必次数1次，剩余可转生次数%s次' % (get_valid_name(session.ctx['sender']['card'], session.ctx['sender']['nickname']), 2 - revive_time)
            else:
                response = '%s转生失败，数据消失在虚空之中' % get_valid_name(session.ctx['sender']['card'], session.ctx['sender']['nickname'])
        else:
            response = '您已达到最大转生次数，这就是命！'
    else:
        response = '您尚未加入游戏'
    await session.send(response)


@on_command('wcr升星', only_to_me=False)
async def wcr_increase_stars(session: CommandSession):
    wcr_data = Wcr()
    result = await wcr_data.search_player(session.ctx['user_id'])
    if result:
        input_name = session.current_arg_text.strip()
        if input_name:
            nickname_dict = await get_nickname_dict()
            if input_name in nickname_dict.keys():
                chara_name = nickname_dict[input_name]
            else:
                chara_name = input_name
            chara = await wcr_data.search_chara(result[0], chara_name)
            if chara:
                stars = await wcr_data.get_chara_stars(result[0], chara_name)
                if stars < 5:
                    original_stars = stars - chara[3]
                    cost = await calculate_increase_stars_cost(original_stars, stars)
                    if cost <= result[3]:
                        response = '升星成功！您的%s现在为%s星！\n剩余母猪石%s个' % (chara_name, stars + 1, result[3] - cost)
                        await wcr_data.update_player_info(result[0], result[1], result[2], result[3] - cost)
                        await wcr_data.increase_chara_stars(result[0], chara_name, 1)
                    else:
                        response = '本次升星需要%s个母猪石，您的母猪石只有%s个，赶紧母吧别做梦了！' % (cost, result[3])
                else:
                    response = '%s已经到达5星，不能再母了' % chara_name
            else:
                response = '您没有叫做%s的角色' % input_name
        else:
            response = '参数错误'
    else:
        response = '您尚未加入游戏'
    await session.send(response)


@on_command('wcr查看', only_to_me=False)
async def wcr_search(session: CommandSession):
    wcr_data = Wcr()
    result = await wcr_data.search_player(session.ctx['user_id'])
    if result:
        response = '%s现有如下角色：\n' % get_valid_name(session.ctx['sender']['card'], session.ctx['sender']['nickname'])
        response += '5星角色:'
        list_5 = await wcr_data.get_chara_list(session.ctx['user_id'], 5)
        for chara in list_5:
            response += '【%s】 ' % chara
        response += '\n4星角色:'
        list_4 = await wcr_data.get_chara_list(session.ctx['user_id'], 4)
        for chara in list_4:
            response += '【%s】 ' % chara
        response += '\n3星角色:'
        list_3 = await wcr_data.get_chara_list(session.ctx['user_id'], 3)
        for chara in list_3:
            response += '【%s】 ' % chara
        response += '\n2星角色:'
        list_2 = await wcr_data.get_chara_list(session.ctx['user_id'], 2)
        for chara in list_2:
            response += '【%s】 ' % chara
        response += '\n1星角色:'
        list_1 = await wcr_data.get_chara_list(session.ctx['user_id'], 1)
        for chara in list_1:
            response += '【%s】 ' % chara
        response += '\n拥有母猪石%s个\n' % result[3]
        response += '剩余%s宝石\n' % result[1]
        response += '剩余傻必次数%s次\n' % result[2]
        response += '剩余转生次数%s次\n' % (3 - result[4])
    else:
        response = '您尚未加入游戏'
    await session.send(response)


@on_command('wcr单抽', only_to_me=False)
async def wcr_gacha_single(session: CommandSession):
    wcr_data = Wcr()
    result = await wcr_data.search_player(session.ctx['user_id'])
    if result:
        cost = 150
        if result[1] >= cost:
            gacha_result = await get_gacha_result('single')
            chara_name = await get_chara_name(gacha_result[0])
            chara_result = await wcr_data.search_chara(session.ctx['user_id'], chara_name)
            pig_stone = 0
            if chara_result:
                response = '%s抽到了%s\n' % (get_valid_name(session.ctx['sender']['card'], session.ctx['sender']['nickname']), gacha_result[0])
                response += '获得%s个母猪石\n' % gacha_result[1]
                pig_stone += gacha_result[1]
            else:
                response = '%s抽到了%s(new)\n' % (get_valid_name(session.ctx['sender']['card'], session.ctx['sender']['nickname']), gacha_result[0])
                await wcr_data.add_chara(session.ctx['user_id'], chara_name)
            response += '剩余宝石%s' % (result[1] - cost)
            await wcr_data.update_player_info(session.ctx['user_id'], result[1] - cost, result[2], result[3] + pig_stone)
        else:
            response = '您没那么多宝石，请不要打肿脸充胖子！'
    else:
        response = '您尚未加入游戏'
    await session.send(response)


@on_command('wcr十连', only_to_me=False)
async def wcr_gacha_ten(session: CommandSession):
    wcr_data = Wcr()
    result = await wcr_data.search_player(session.ctx['user_id'])
    if result:
        gacha_time = session.current_arg_text.strip()
        if gacha_time:
            if int(gacha_time) > 30:
                response = '您好，这边建议您选择抽井呢~'
            else:
                cost = 1500 * int(gacha_time)
                if result[1] >= cost:
                    response = '%s的%s次十连结果为（只显示3星）:\n' % (get_valid_name(session.ctx['sender']['card'], session.ctx['sender']['nickname']), gacha_time)
                    pig_stone = 0
                    for i in range(int(gacha_time)):
                        gacha_result = await get_gacha_result('ten')
                        for card in gacha_result[0]:
                            chara_name = await get_chara_name(card)
                            chara_result = await wcr_data.search_chara(session.ctx['user_id'], chara_name)
                            if chara_result:
                                if '★' in card:
                                    response += '%s\n' % card
                                pig_stone += await get_pig_stone(card)
                            else:
                                if '★' in card:
                                    response += '%s(new)\n' % card
                                await wcr_data.add_chara(session.ctx['user_id'], chara_name)
                    response += '共获得%s个母猪石\n' % pig_stone
                    response += '剩余宝石%s' % (result[1] - cost)
                    await wcr_data.update_player_info(session.ctx['user_id'], result[1] - cost, result[2],
                                                      result[3] + pig_stone)
                else:
                    response = '您没那么多宝石，请不要打肿脸充胖子！'
        else:
            cost = 1500
            if result[1] >= cost:
                gacha_result = await get_gacha_result('ten')
                response = '%s的十连结果为（只显示new）:\n' % get_valid_name(session.ctx['sender']['card'], session.ctx['sender']['nickname'])
                pig_stone = 0
                for card in gacha_result[0]:
                    chara_name = await get_chara_name(card)
                    chara_result = await wcr_data.search_chara(session.ctx['user_id'], chara_name)
                    if chara_result:
                        pig_stone += await get_pig_stone(card)
                    else:
                        response += '%s(new)\n' % card
                        await wcr_data.add_chara(session.ctx['user_id'], chara_name)
                response += '共获得%s个母猪石\n' % pig_stone
                response += '剩余宝石%s' % (result[1] - cost)
                await wcr_data.update_player_info(session.ctx['user_id'], result[1] - cost, result[2], result[3] + pig_stone)
            else:
                response = '您没那么多宝石，请不要打肿脸充胖子！'
    else:
        response = '您尚未加入游戏'
    await session.send(response)


@on_command('wcr傻必', only_to_me=False)
async def wcr_gacha_sb(session: CommandSession):
    wcr_data = Wcr()
    result = await wcr_data.search_player(session.ctx['user_id'])
    if result:
        cost = 1500
        if result[1] >= cost and result[2] == 1:
            gacha_result = await get_gacha_result('sb')
            response = '%s的傻必结果为（只显示new）:\n' % get_valid_name(session.ctx['sender']['card'], session.ctx['sender']['nickname'])
            pig_stone = 0
            for card in gacha_result[0]:
                chara_name = await get_chara_name(card)
                chara_result = await wcr_data.search_chara(session.ctx['user_id'], chara_name)
                if chara_result:
                    pig_stone += await get_pig_stone(card)
                else:
                    response += '%s(new)\n' % card
                    await wcr_data.add_chara(session.ctx['user_id'], chara_name)
            response += '共获得%s个母猪石\n' % pig_stone
            response += '剩余宝石%s' % (result[1] - cost)
            await wcr_data.update_player_info(session.ctx['user_id'], result[1] - cost, 0, result[3] + pig_stone)
        else:
            response = '您要么没那么多宝石，要么没有傻必次数。请不要打肿脸充胖子！'
    else:
        response = '您尚未加入游戏'
    await session.send(response)


@on_command('wcr抽井', only_to_me=False)
async def wcr_gacha_300(session: CommandSession):
    wcr_data = Wcr()
    result = await wcr_data.search_player(session.ctx['user_id'])
    if result:
        cost = 45000
        if result[1] >= cost:
            response = '%s舔了口香肠，开始抽井，他抽到了这些三星：\n' % get_valid_name(session.ctx['sender']['card'],
                                                                   session.ctx['sender']['nickname'])
            pig_stone = 0
            count = 0
            for i in range(30):
                gacha_result = await get_gacha_result('ten')
                for card in gacha_result[0]:
                    chara_name = await get_chara_name(card)
                    chara_result = await wcr_data.search_chara(session.ctx['user_id'], chara_name)
                    if chara_result:
                        if '★' in card:
                            count += 1
                            response += '%s\n' % card
                        pig_stone += await get_pig_stone(card)
                    else:
                        if '★' in card:
                            count += 1
                            response += '%s(new)\n' % card
                        await wcr_data.add_chara(session.ctx['user_id'], chara_name)
            g = Gacha()
            up_list = g.up_3
            has_new_card = 1
            for chara_name in up_list:
                chara_result = await wcr_data.search_chara(session.ctx['user_id'], chara_name)
                if not chara_result:
                    response += '井了【%s】(new)\n' % chara_name
                    await wcr_data.add_chara(session.ctx['user_id'], chara_name)
                    has_new_card = 0
            if has_new_card == 1:
                response += '井了50母猪石\n'
                pig_stone += 50
            if count == 0:
                response += '傻了吧！没有三星，连哈哈剑都没有。哈哈哈哈o(∩_∩)o\n'
            if count > 9:
                response += '%s个3星，你是[CQ:emoji,id=128054]吧？\n' % count
            if count < 6:
                response += '这能忍？继续[CQ:emoji,id=128055]\n'
            response += '共获得%s个母猪石\n' % pig_stone
            response += '剩余宝石%s' % (result[1] - cost)
            await wcr_data.update_player_info(session.ctx['user_id'], result[1] - cost, result[2],
                                              result[3] + pig_stone)
        else:
            response = '您没那么多宝石。请不要打肿脸充胖子！'
    else:
        response = '您尚未加入游戏'
    await session.send(response)


@on_command('wcr卡池', only_to_me=False)
async def wcr_card_pool(session: CommandSession):
    g = Gacha()
    list_1 = g.up_1
    list_2 = g.up_2
    list_3 = g.up_3
    response = '当前卡池的up情况：\n'
    response += '3星：'
    for card in list_3:
        response += '【%s】 ' % card
    response += '\n2星：'
    for card in list_2:
        response += '【%s】 ' % card
    response += '\n1星：'
    for card in list_1:
        response += '【%s】 ' % card
    await session.send(response)


async def get_gacha_result(gacha_type):
    p1 = 795
    p2 = 180
    g = Gacha()
    if gacha_type == 'single':
        return g.gacha_1(p1, p2)
    if gacha_type == 'ten':
        return g.gacha_10(p1, p2)
    if gacha_type == 'sb':
        return g.gacha_sb(p1, p2)


async def get_chara_name(gacha_result):
    if '★' in gacha_result:
        return gacha_result[3:]
    elif '☆☆' in gacha_result:
        return gacha_result[2:]
    else:
        return gacha_result[1:]


async def get_pig_stone(gacha_result):
    if '★' in gacha_result:
        return 50
    elif '☆☆' in gacha_result:
        return 10
    else:
        return 1


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


async def calculate_increase_stars_cost(original_stars, current_stars):
    used_pieces = 0
    for i in range(original_stars, current_stars):
        used_pieces += INCREASE_STARS_COST[i - 1]
    reset_time = used_pieces // 20
    left_pieces = 20 - used_pieces % 20
    current_pig_stone_cost = min(1 + reset_time, 5)
    required_pieces = INCREASE_STARS_COST[current_stars - 1]
    cost = 0
    while required_pieces > 0:
        purchased_pieces = min(left_pieces, required_pieces)
        cost += purchased_pieces * current_pig_stone_cost
        required_pieces -= purchased_pieces
        left_pieces = 20
        current_pig_stone_cost = min(1 + current_pig_stone_cost, 5)
    return cost
