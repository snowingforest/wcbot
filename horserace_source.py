import pymysql
from DBUtils.PooledDB import PooledDB
import random
from basefunction import get_nick_name
from config import *


def calculate_damage(attack, defense, damage_fix):
    dmg = attack + damage_fix - defense
    if dmg > 0:
        base_move = dmg // 6
        extra_move = dmg % 6
        r = random.randint(1, 6)
        if r <= extra_move:
            move = base_move + 1
        else:
            move = base_move
    else:
        move = 0
    return move


class HorseRace:
    def __init__(self):
        self.db_pool = PooledDB(creator=pymysql, host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PWD,
                                database='horserace', blocking=True, ping=0)

    async def race_state(self):
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = "select state from race_state"
        cursor.execute(sql)
        state = cursor.fetchone()
        cursor.close()
        db.close()
        return state[0]

    async def set_state(self, state):
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = "update race_state set state = %s" % state
        cursor.execute(sql)
        db.commit()
        cursor.close()
        db.close()

    async def add_winner(self, chara_name):
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = "update chara_data set win_time = win_time + 1 where name = %s"
        cursor.execute(sql, chara_name)
        db.commit()
        cursor.close()
        db.close()

    async def add_race(self, chara_name):
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = "update chara_data set race_time = race_time + 1 where name = %s"
        cursor.execute(sql, chara_name)
        db.commit()
        cursor.close()
        db.close()

    async def join_gamble(self, player_id, horse_id):
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = "insert into gamble(player_id, horse_id) values (%s, %s)" % (player_id, horse_id)
        try:
            result = cursor.execute(sql)
            db.commit()
        except BaseException:
            result = 0
        cursor.close()
        db.close()
        return result

    async def search_gamble(self):
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = "select * from gamble"
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        db.close()
        return result

    async def end_race(self):
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = "truncate table gamble"
        cursor.execute(sql)
        sql = "truncate table horse"
        cursor.execute(sql)
        sql = "update race_state set state = -1"
        cursor.execute(sql)
        db.commit()
        cursor.close()
        db.close()

    async def win_rate_stat(self):
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = "select name, win_time, race_time, if(race_time = 0, 0, win_time / race_time) as win_rate from chara_data where stars >= 2 order by win_rate"
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        db.close()
        return result

    async def add_horse(self, chara):
        chara_name = chara[1]
        player_id = chara[2]
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = "select * from chara_data where name = %s"
        cursor.execute(sql, chara_name)
        chara_new = cursor.fetchone()
        sql = "insert into horse(name, player_id, atk, satk, def, sdef, tp) values (%s, %s, %s, %s, %s, %s, %s)"
        log = (chara_name, player_id, chara_new[3], chara_new[4], chara_new[5], chara_new[6], chara_new[7])
        cursor.execute(sql, log)
        db.commit()
        cursor.close()
        db.close()

    async def search_horse(self):
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = "select * from horse order by id"
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        db.close()
        return result

    async def search_sorted_horse(self):
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = "select * from horse order by position desc"
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        db.close()
        return result

    async def search_sorted_horse_ascend(self):
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = "select * from horse order by position"
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        db.close()
        return result

    async def get_single_target(self, horse):
        horse_list = await self.search_sorted_horse()
        first_horse = horse_list[0]
        for target_horse in horse_list:
            if target_horse[0] != horse[0] and target_horse[3] == first_horse[3]:
                return target_horse
        return first_horse

    async def search_horse_by_position(self, position):
        horse_list = await self.search_sorted_horse()
        return horse_list[position - 1]

    async def get_horse_position(self, horse):
        horse_list = await self.search_sorted_horse()
        for i in range(len(horse_list)):
            if horse_list[i][0] == horse[0]:
                return i + 1

    async def search_horse_by_player(self, player_id):
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = "select * from horse where player_id = %s"
        cursor.execute(sql, player_id)
        result = cursor.fetchone()
        cursor.close()
        db.close()
        return result

    async def move_horse(self, horse_id):
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = "select * from horse where id = %s"
        cursor.execute(sql, horse_id)
        result = cursor.fetchone()
        atk = max(result[5], result[6])
        position = result[3]
        tp = result[4]
        tp_up = result[9]
        base_move = atk // 6
        extra_move = atk % 6
        r = random.randint(1, 6)
        if r <= extra_move:
            move = base_move + 1
        else:
            move = base_move
        position = min(position + move, 10)
        tp = min(100, tp + 20 + tp_up * 10)
        sql = "update horse set position = %s, current_tp = %s where id = %s"
        log = (position, tp, horse_id)
        cursor.execute(sql, log)
        db.commit()
        cursor.close()
        db.close()
        return move

    async def god_attack(self, group_id):
        db = self.db_pool.connection()
        cursor = db.cursor()
        god_atk = 7
        response = ""
        attack = ("物理", "魔法")
        horse_list = await self.search_horse()
        attack_mode = random.randint(0, len(horse_list) + 3)
        attack_type = random.randint(0, 1)
        if attack_mode <= 3:
            for horse in horse_list:
                response += "上帝对%s号马%s的%s发动了%s攻击，" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1], attack[attack_type])
                move = calculate_damage(god_atk, horse[7 + attack_type], 0)
                if move > 0:
                    response += '击退了%s步。\n' % move
                else:
                    response += '没有效果。\n'
                position = max(1, horse[3] - move)
                sql = "update horse set position = %s where id = %s" % (position, horse[0])
                cursor.execute(sql)
        else:
            target = attack_mode - 3
            horse = horse_list[target - 1]
            response += "上帝对%s号马%s的%s发动了%s攻击，" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1], attack[attack_type])
            move = calculate_damage(god_atk, horse[7 + attack_type], 1)
            if move > 0:
                response += '击退了%s步。\n' % move
            else:
                response += '没有效果。\n'
            position = max(1, horse[3] - move)
            sql = "update horse set position = %s where id = %s" % (position, horse[0])
            cursor.execute(sql)
        db.commit()
        cursor.close()
        db.close()
        return response

    async def ub(self, horse, group_id):
        db = self.db_pool.connection()
        cursor = db.cursor()
        if horse[1] == "镜华":
            response = "%s号马%s的%s使用了【太虚苍蓝闪】！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 4
            target_horse = await self.get_single_target(horse)
            move = 0
            if target_horse[0] != horse[0]:
                move = calculate_damage(horse[6], target_horse[8], damage_fix)
            if move == 0:
                response += "%s鸽了\n" % horse[1]
            else:
                response += "把%s号马%s的%s击退了%s步\n" % (target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
            target_position = max(1, target_horse[3] - move)
            sql = "update horse set position = %s where id = %s" % (target_position, target_horse[0])
            cursor.execute(sql)
            sql = "update horse set current_tp = 0 where id = %s" % horse[0]
            cursor.execute(sql)
        elif horse[1] == "杏奈":
            response = "%s号马%s的%s使用了【罗刹涅槃・极光终天冥坏破】！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 3
            horse_list = await self.search_horse()
            for target_horse in horse_list:
                if target_horse[0] != horse[0]:
                    move = calculate_damage(horse[6], target_horse[8], damage_fix)
                    if move == 0:
                        response += "%s鸽了\n" % horse[1]
                    else:
                        response += "把%s号马%s的%s击退了%s步\n" % (target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
                    target_position = max(1, target_horse[3] - move)
                    sql = "update horse set position = %s where id = %s" % (target_position, target_horse[0])
                    cursor.execute(sql)
            sql = "update horse set current_tp = 0, def = 0, sdef = 0 where id = %s" % horse[0]
            cursor.execute(sql)
        elif horse[1] == "真步":
            response = "%s号马%s的%s使用了【童话之庭】！自己的双防上升了！tp中度恢复了！向前冲了1步！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            position = min(10, horse[3] + 1)
            sql = "update horse set current_tp = 40, def = 9, sdef = 7, position = %s where id = %s" % (position, horse[0])
            cursor.execute(sql)
        elif horse[1] == "璃乃":
            response = "%s号马%s的%s使用了【箭雨】！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 1
            horse_list = await self.search_horse()
            for target_horse in horse_list:
                if target_horse[0] != horse[0]:
                    r = random.randint(0, 1)
                    if r <= 0:
                        damage_fix = 3
                    move = calculate_damage(horse[5], target_horse[7], damage_fix)
                    if move == 0:
                        response += "%s鸽了\n" % horse[1]
                    else:
                        response += "把%s号马%s的%s击退了%s步\n" % (target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
                    target_position = max(1, target_horse[3] - move)
                    sql = "update horse set position = %s where id = %s" % (target_position, target_horse[0])
                    cursor.execute(sql)
            sql = "update horse set current_tp = 0 where id = %s" % horse[0]
            cursor.execute(sql)
        elif horse[1] == "初音":
            response = "%s号马%s的%s使用了【流星☆】！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 0
            horse_list = await self.search_horse()
            for target_horse in horse_list:
                if target_horse[0] != horse[0]:
                    if target_horse[5] > 0:
                        damage_fix = 2
                    move = calculate_damage(horse[6], target_horse[8], damage_fix)
                    if move == 0:
                        response += "%s鸽了\n" % horse[1]
                    else:
                        response += "把%s号马%s的%s击退了%s步\n" % (target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
                    target_position = max(1, target_horse[3] - move)
                    sql = "update horse set position = %s where id = %s" % (target_position, target_horse[0])
                    cursor.execute(sql)
            sql = "update horse set current_tp = 0 where id = %s" % horse[0]
            cursor.execute(sql)
        elif horse[1] == "依绪":
            response = "%s号马%s的%s使用了【心形love风暴】！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 2
            horse_list = await self.search_horse()
            for target_horse in horse_list:
                if target_horse[0] != horse[0]:
                    move = calculate_damage(max(target_horse[5], target_horse[6], horse[6]), target_horse[8], damage_fix)
                    if move == 0:
                        response += "%s鸽了\n" % horse[1]
                    else:
                        response += "把%s号马%s的%s击退了%s步\n" % (target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
                    target_position = max(1, target_horse[3] - move)
                    sql = "update horse set position = %s where id = %s" % (target_position, target_horse[0])
                    cursor.execute(sql)
            sql = "update horse set current_tp = 0 where id = %s" % horse[0]
            cursor.execute(sql)
        elif horse[1] == "咲恋":
            response = "%s号马%s的%s使用了【不死鸟之剑】！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = await self.get_horse_position(horse)
            horse_list = await self.search_horse()
            for target_horse in horse_list:
                if target_horse[0] != horse[0]:
                    move = calculate_damage(horse[5], target_horse[7], damage_fix)
                    if move == 0:
                        response += "%s鸽了\n" % horse[1]
                    else:
                        response += "把%s号马%s的%s击退了%s步\n" % (target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
                    target_position = max(1, target_horse[3] - move)
                    sql = "update horse set position = %s where id = %s" % (target_position, target_horse[0])
                    cursor.execute(sql)
            sql = "update horse set current_tp = 0 where id = %s" % horse[0]
            cursor.execute(sql)
        elif horse[1] == "望":
            response = "%s号马%s的%s使用了【Live-Onstage】！自己的双防提升了！自己的攻击提升了！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            sql = "update horse set current_tp = 0, def = 10, sdef = 7, atk = 8 where id = %s" % horse[0]
            cursor.execute(sql)
        elif horse[1] == "扇子":
            response = "%s号马%s的%s使用了【忍法灼热地狱】！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 1
            horse_list = await self.search_horse()
            tp_up = 0
            for target_horse in horse_list:
                if target_horse[0] != horse[0]:
                    move = calculate_damage(horse[5], target_horse[7], damage_fix)
                    if move == 0:
                        response += "%s鸽了\n" % horse[1]
                    else:
                        tp_up += 20
                        response += "把%s号马%s的%s击退了%s步\n" % (target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
                    target_position = max(1, target_horse[3] - move)
                    sql = "update horse set position = %s where id = %s" % (target_position, target_horse[0])
                    cursor.execute(sql)
            sql = "update horse set current_tp = %s where id = %s" % (tp_up, horse[0])
            cursor.execute(sql)
        elif horse[1] == "真琴":
            response = "%s号马%s的%s使用了【沃尔芬之咬】！目标的物防下降了！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 2
            target_horse = await self.get_single_target(horse)
            def_fix = 0
            move = 0
            if target_horse[0] != horse[0]:
                move = calculate_damage(horse[5], target_horse[7], damage_fix)
            if move == 0:
                response += "%s鸽了\n" % horse[1]
            else:
                response += "把%s号马%s的%s击退了%s步\n" % (target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
                def_fix = 2
            target_position = max(1, target_horse[3] - move)
            target_def = max(0, target_horse[7] - def_fix)
            sql = "update horse set position = %s, def = %s where id = %s" % (target_position, target_def, target_horse[0])
            cursor.execute(sql)
            sql = "update horse set current_tp = 0 where id = %s" % horse[0]
            cursor.execute(sql)
        elif horse[1] == "纯":
            response = "%s号马%s的%s使用了【地狱之盾】！自己的双防提升了！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            sql = "update horse set current_tp = 0, def = 6, sdef = 9 where id = %s" % horse[0]
            cursor.execute(sql)
        elif horse[1] == "静流":
            response = "%s号马%s的%s使用了【神圣惩处】！自己的物防上升了！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 2
            target_horse = await self.get_single_target(horse)
            move = 0
            if target_horse[0] != horse[0]:
                move = calculate_damage(horse[5], target_horse[7], damage_fix)
            if move == 0:
                response += "%s鸽了\n" % horse[1]
            else:
                response += "把%s号马%s的%s击退了%s步\n" % (target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
            target_position = max(1, target_horse[3] - move)
            sql = "update horse set position = %s where id = %s" % (target_position, target_horse[0])
            cursor.execute(sql)
            sql = "update horse set current_tp = 0, def = 8 where id = %s" % horse[0]
            cursor.execute(sql)
        elif horse[1] == "毛二力":
            response = "%s号马%s的%s使用了【紫电一闪】！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 1
            horse_list = await self.search_horse()
            for target_horse in horse_list:
                if target_horse[0] != horse[0]:
                    move = calculate_damage(horse[5], target_horse[7], damage_fix)
                    if move == 0:
                        response += "%s鸽了\n" % horse[1]
                    else:
                        response += "把%s号马%s的%s击退了%s步\n" % (target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
                    target_position = max(1, target_horse[3] - move)
                    sql = "update horse set position = %s where id = %s" % (target_position, target_horse[0])
                    cursor.execute(sql)
            sql = "update horse set current_tp = 0, atk = 6, tp = 0 where id = %s" % horse[0]
            cursor.execute(sql)
        elif horse[1] == "姬塔":
            response = "%s号马%s的%s使用了【暴风雨之剑】！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 2
            target_horse = await self.get_single_target(horse)
            move = 0
            if target_horse[0] != horse[0]:
                move = calculate_damage(horse[5], target_horse[7], damage_fix)
            if move == 0:
                response += "%s鸽了\n" % horse[1]
            else:
                response += "把%s号马%s的%s击退了%s步\n" % (
                    target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
            target_position = max(1, target_horse[3] - move)
            sql = "update horse set position = %s where id = %s" % (target_position, target_horse[0])
            cursor.execute(sql)
            sql = "update horse set current_tp = 0 where id = %s" % horse[0]
            cursor.execute(sql)
        elif horse[1] == "亚里莎":
            response = "%s号马%s的%s使用了【我的箭将把你贯穿】！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 1
            target_horse = await self.get_single_target(horse)
            move = 0
            if target_horse[0] != horse[0]:
                move = calculate_damage(horse[5], target_horse[7], damage_fix)
            if move == 0:
                response += "%s鸽了\n" % horse[1]
            else:
                response += "把%s号马%s的%s击退了%s步\n" % (
                    target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
            target_position = max(1, target_horse[3] - move)
            sql = "update horse set position = %s where id = %s" % (target_position, target_horse[0])
            cursor.execute(sql)
            sql = "update horse set current_tp = 0 where id = %s" % horse[0]
            cursor.execute(sql)
        elif horse[1] == "哈哈剑":
            response = "%s号马%s的%s使用了【高贵谴击】！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 4
            target_horse = await self.get_single_target(horse)
            move = 0
            if target_horse[0] != horse[0]:
                move = calculate_damage(horse[5], target_horse[7], damage_fix)
            if move == 0:
                response += "%s鸽了\n" % horse[1]
            else:
                response += "把%s号马%s的%s击退了%s步\n" % (
                    target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
            target_position = max(1, target_horse[3] - move)
            sql = "update horse set position = %s where id = %s" % (target_position, target_horse[0])
            cursor.execute(sql)
            sql = "update horse set current_tp = 0 where id = %s" % horse[0]
            cursor.execute(sql)
        elif horse[1] == "宫子":
            response = "%s号马%s的%s使用了【把你变成布丁呦】！向前冲了一步！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 1
            target_horse = await self.get_single_target(horse)
            move = 0
            if target_horse[0] != horse[0]:
                move = calculate_damage(horse[5], target_horse[7], damage_fix)
            if move == 0:
                response += "%s鸽了\n" % horse[1]
            else:
                response += "把%s号马%s的%s击退了%s步\n" % (
                    target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
            target_position = max(1, target_horse[3] - move)
            sql = "update horse set position = %s where id = %s" % (target_position, target_horse[0])
            cursor.execute(sql)
            position = min(10, horse[3] + 1)
            sql = "update horse set current_tp = 0, position = %s where id = %s" % (position, horse[0])
            cursor.execute(sql)
        elif horse[1] == "茜里":
            response = "%s号马%s的%s使用了【甜蜜恶魔的声援】！魔法攻击上升了！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 0
            target_horse = await self.get_single_target(horse)
            move = 0
            if target_horse[0] != horse[0]:
                move = calculate_damage(horse[6], target_horse[8], damage_fix)
            if move == 0:
                response += "%s鸽了\n" % horse[1]
            else:
                response += "把%s号马%s的%s击退了%s步。" % (
                    target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
                response += "自己向前冲了%s步\n" % move
            position = min(10, horse[3] + move)
            target_position = max(1, target_horse[3] - move)
            sql = "update horse set position = %s where id = %s" % (target_position, target_horse[0])
            cursor.execute(sql)
            sql = "update horse set current_tp = 0, position = %s, satk = 8 where id = %s" % (position, horse[0])
            cursor.execute(sql)
        elif horse[1] == "雪哥":
            response = "%s号马%s的%s使用了【臣服在我的美之下吧】！其它角色的双防下降了！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 0
            horse_list = await self.search_horse()
            for target_horse in horse_list:
                if target_horse[0] != horse[0]:
                    move = calculate_damage(horse[6], target_horse[8], damage_fix)
                    if move == 0:
                        response += "%s鸽了\n" % horse[1]
                    else:
                        response += "把%s号马%s的%s击退了%s步\n" % (target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
                    target_position = max(1, target_horse[3] - move)
                    target_def = max(0, target_horse[7] - 1)
                    target_sdef = max(0, target_horse[8] - 1)
                    sql = "update horse set position = %s, def = %s, sdef = %s where id = %s" % (target_position, target_def, target_sdef, target_horse[0])
                    cursor.execute(sql)
            sql = "update horse set current_tp = 0 where id = %s" % horse[0]
            cursor.execute(sql)
        elif horse[1] == "玲奈":
            response = "%s号马%s的%s使用了【心碎】！造成了暴击！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 2
            target_horse = await self.get_single_target(horse)
            move = 0
            if target_horse[0] != horse[0]:
                move = calculate_damage(horse[5], target_horse[7], damage_fix)
            move = round(move * 1.5)
            if move == 0:
                response += "%s鸽了\n" % horse[1]
            else:
                response += "把%s号马%s的%s击退了%s步\n" % (
                    target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
            target_position = max(1, target_horse[3] - move)
            sql = "update horse set position = %s where id = %s" % (target_position, target_horse[0])
            cursor.execute(sql)
            sql = "update horse set current_tp = 0 where id = %s" % horse[0]
            cursor.execute(sql)
        elif horse[1] == "香织":
            response = "%s号马%s的%s使用了【琉球犬重拳出击】！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 4
            target_horse = await self.get_single_target(horse)
            move = 0
            if target_horse[0] != horse[0]:
                move = calculate_damage(horse[5], target_horse[7], damage_fix)
            if move == 0:
                response += "%s鸽了\n" % horse[1]
            else:
                response += "把%s号马%s的%s击退了%s步\n" % (
                    target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
            target_position = max(1, target_horse[3] - move)
            sql = "update horse set position = %s where id = %s" % (target_position, target_horse[0])
            cursor.execute(sql)
            sql = "update horse set current_tp = 0 where id = %s" % horse[0]
            cursor.execute(sql)
        elif horse[1] == "美美":
            response = "%s号马%s的%s使用了【兔兔斩击】！攻击上升了！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 2
            target_horse = await self.search_horse_by_position(1)
            move = 0
            if target_horse[0] != horse[0]:
                move = calculate_damage(horse[5], target_horse[7], damage_fix)
            if move == 0:
                response += "%s鸽了\n" % horse[1]
            else:
                response += "把%s号马%s的%s击退了%s步\n" % (
                    target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
            target_position = max(1, target_horse[3] - move)
            sql = "update horse set position = %s where id = %s" % (target_position, target_horse[0])
            cursor.execute(sql)
            target_horse = await self.search_horse_by_position(2)
            move = 0
            if target_horse[0] != horse[0]:
                move = calculate_damage(horse[5], target_horse[7], damage_fix)
            if move == 0:
                response += "%s鸽了\n" % horse[1]
            else:
                response += "把%s号马%s的%s击退了%s步\n" % (
                    target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
            target_position = max(1, target_horse[3] - move)
            sql = "update horse set position = %s where id = %s" % (target_position, target_horse[0])
            cursor.execute(sql)
            sql = "update horse set current_tp = 0, atk = 8 where id = %s" % horse[0]
            cursor.execute(sql)
        elif horse[1] == "铃":
            response = "%s号马%s的%s使用了【尝尝亲手烘焙的红豆包】！自己的魔防上升了！自己的攻击上升了！向前冲了1步！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            position = min(10, horse[3] + 1)
            sql = "update horse set current_tp = 0, atk = 7, sdef = 8, position = %s where id = %s" % (position, horse[0])
            cursor.execute(sql)
        elif horse[1] == "惠鲤子":
            response = "%s号马%s的%s使用了【致命惩罚】！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 2
            target_horse = await self.get_single_target(horse)
            move = 0
            attack_fix = 0
            if target_horse[0] != horse[0]:
                move = calculate_damage(horse[5], target_horse[7], damage_fix)
            if move == 0:
                response += "%s鸽了\n" % horse[1]
            else:
                response += "把%s号马%s的%s击退了%s步。" % (
                    target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
                if move >= 2:
                    attack_fix = 4
                    response += '%s的攻击力大幅上升了！' % horse[1]
                response += '\n'
            target_position = max(1, target_horse[3] - move)
            sql = "update horse set position = %s where id = %s" % (target_position, target_horse[0])
            cursor.execute(sql)
            sql = "update horse set current_tp = 0, atk = atk + %s where id = %s" % (attack_fix, horse[0])
            cursor.execute(sql)
        elif horse[1] == "忍":
            response = "%s号马%s的%s使用了【亡灵叙述者】！其它角色的物防下降了！忍的攻击上升了！双防上升了！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 0
            horse_list = await self.search_horse()
            for target_horse in horse_list:
                if target_horse[0] != horse[0]:
                    move = calculate_damage(horse[5], target_horse[7], damage_fix)
                    if move == 0:
                        response += "%s鸽了\n" % horse[1]
                    else:
                        response += "把%s号马%s的%s击退了%s步\n" % (target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
                    target_position = max(1, target_horse[3] - move)
                    target_def = max(0, target_horse[7] - 1)
                    sql = "update horse set position = %s, def = %s where id = %s" % (target_position, target_def, target_horse[0])
                    cursor.execute(sql)
            sql = "update horse set current_tp = 0, atk = 8, def = 5, sdef = 4 where id = %s" % horse[0]
            cursor.execute(sql)
        elif horse[1] == "真阳":
            response = "%s号马%s的%s使用了【伊丽莎白】！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 2
            target_horse = await self.get_single_target(horse)
            move = 0
            if target_horse[0] != horse[0]:
                move = calculate_damage(horse[5], target_horse[7], damage_fix)
            if move == 0:
                response += "%s鸽了\n" % horse[1]
            else:
                response += "把%s号马%s的%s击退了%s步。\n" % (
                    target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
            target_position = max(1, target_horse[3] - move)
            sql = "update horse set position = %s where id = %s" % (target_position, target_horse[0])
            cursor.execute(sql)
            damage_fix = -1
            target_horse = await self.get_single_target(horse)
            move = 0
            if target_horse[0] != horse[0]:
                move = calculate_damage(horse[5], target_horse[7], damage_fix)
            if move == 0:
                response += "%s的奶牛鸽了\n" % horse[1]
            else:
                response += "奶牛把%s号马%s的%s击退了%s步。\n" % (
                    target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
            target_position = max(1, target_horse[3] - move)
            sql = "update horse set position = %s where id = %s" % (target_position, target_horse[0])
            cursor.execute(sql)
            sql = "update horse set current_tp = 0 where id = %s" % horse[0]
            cursor.execute(sql)
        elif horse[1] == "栞":
            response = "%s号马%s的%s使用了【附魔箭矢】！攻击力上升了！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 0
            target_horse = await self.get_single_target(horse)
            move = 0
            if target_horse[0] != horse[0]:
                move = calculate_damage(horse[5], target_horse[7], damage_fix)
            if move == 0:
                response += "%s鸽了\n" % horse[1]
            else:
                response += "把%s号马%s的%s击退了%s步\n" % (
                    target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
            target_position = max(1, target_horse[3] - move)
            sql = "update horse set position = %s where id = %s" % (target_position, target_horse[0])
            cursor.execute(sql)
            sql = "update horse set current_tp = 0, atk = atk + 1 where id = %s" % horse[0]
            cursor.execute(sql)
        elif horse[1] == "千歌":
            response = "%s号马%s的%s使用了【精灵庇护】！向前冲了一步！其它角色的物攻下降了！自己的魔攻上升了！自己的双防上升了！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            horse_list = await self.search_horse()
            for target_horse in horse_list:
                if target_horse[0] != horse[0]:
                    sql = "update horse set atk = atk - 1 where id = %s" % target_horse[0]
                    cursor.execute(sql)
            position = min(10, horse[3] + 1)
            sql = "update horse set current_tp = 0, position = %s, satk = 7, def = 4, sdef = 4 where id = %s" % (position, horse[0])
            cursor.execute(sql)
        elif horse[1] == "空花":
            response = "%s号马%s的%s使用了【神魂颠倒】！自己的双防上升了！向前冲了2步！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            position = min(10, horse[3] + 2)
            sql = "update horse set current_tp = 0, def = 6, sdef = 13, position = %s where id = %s" % (position, horse[0])
            cursor.execute(sql)
        elif horse[1] == "珠希":
            response = "%s号马%s的%s使用了【猫猫决胜爪】！目标的tp减少了！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 2
            target_horse = await self.get_single_target(horse)
            move = 0
            target_tp = target_horse[4]
            if target_horse[0] != horse[0]:
                move = calculate_damage(horse[5], target_horse[7], damage_fix)
                target_tp = max(0, target_tp - 20)
            if target_horse[6] > 0:
                move = move * 2
            if move == 0:
                response += "%s鸽了\n" % horse[1]
            else:
                response += "把%s号马%s的%s击退了%s步\n" % (
                    target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
            target_position = max(1, target_horse[3] - move)
            sql = "update horse set position = %s, current_tp = %s where id = %s" % (target_position, target_tp, target_horse[0])
            cursor.execute(sql)
            sql = "update horse set current_tp = 0 where id = %s" % horse[0]
            cursor.execute(sql)
        elif horse[1] == "子龙":
            response = "%s号马%s的%s使用了【飞跃枪闪】！自己的物防提升了！自己的物攻提升了！自己的tp上升提升了！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 2
            target_horse = await self.get_single_target(horse)
            move = 0
            if target_horse[0] != horse[0]:
                move = calculate_damage(horse[5], target_horse[7], damage_fix)
            if move == 0:
                response += "%s鸽了\n" % horse[1]
            else:
                response += "把%s号马%s的%s击退了%s步\n" % (
                    target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
            target_position = max(1, target_horse[3] - move)
            sql = "update horse set position = %s where id = %s" % (target_position, target_horse[0])
            cursor.execute(sql)
            sql = "update horse set current_tp = 0, atk = atk + 1, def = 9, tp = tp + 1 where id = %s" % horse[0]
            cursor.execute(sql)
        elif horse[1] == "深月":
            response = "%s号马%s的%s使用了【血色蔷薇】！其它角色的物防下降了！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 1
            horse_list = await self.search_horse()
            position_fix = 0
            for target_horse in horse_list:
                if target_horse[0] != horse[0]:
                    move = calculate_damage(horse[5], target_horse[7], damage_fix)
                    if move == 0:
                        response += "%s鸽了\n" % horse[1]
                    else:
                        response += "把%s号马%s的%s击退了%s步。" % (target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
                        if move >= 2:
                            response += "自己向前冲了一步！\n"
                            position_fix += 1
                    target_position = max(1, target_horse[3] - move)
                    target_def = max(0, target_horse[7] - 2)
                    sql = "update horse set position = %s, def = %s where id = %s" % (target_position, target_def, target_horse[0])
                    cursor.execute(sql)
            position = min(10, horse[3] + position_fix)
            sql = "update horse set current_tp = 0, position = %s where id = %s" % (position, horse[0])
            cursor.execute(sql)
        elif horse[1] == "绫音":
            response = "%s号马%s的%s使用了【噗吉全力挥动】！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 2
            target_horse = await self.get_single_target(horse)
            move = 0
            if target_horse[0] != horse[0]:
                move = calculate_damage(horse[5], target_horse[7], damage_fix)
            if move == 0:
                response += "%s鸽了\n" % horse[1]
            else:
                response += "把%s号马%s的%s击退了%s步\n" % (target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
            if target_horse[0] != horse[0]:
                response += "把%s号马%s的%s吹飞了一步\n" % (target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1])
                move += 1
            target_position = max(1, target_horse[3] - move)
            sql = "update horse set position = %s where id = %s" % (target_position, target_horse[0])
            cursor.execute(sql)
            sql = "update horse set current_tp = 0 where id = %s" % horse[0]
            cursor.execute(sql)
        else:
            response = "%s号马%s的%s使用了【白板ub】！\n" % (horse[0], await get_nick_name(group_id, horse[2]), horse[1])
            damage_fix = 2
            target_horse = await self.get_single_target(horse)
            move = 0
            if target_horse[0] != horse[0]:
                move = calculate_damage(max(horse[6], horse[5]), target_horse[7], damage_fix)
            if move == 0:
                response += "%s鸽了\n" % horse[1]
            else:
                response += "把%s号马%s的%s击退了%s步\n" % (target_horse[0], await get_nick_name(group_id, target_horse[2]), target_horse[1], move)
            target_position = max(1, target_horse[3] - move)
            sql = "update horse set position = %s where id = %s" % (target_position, target_horse[0])
            cursor.execute(sql)
            sql = "update horse set current_tp = 0 where id = %s" % horse[0]
            cursor.execute(sql)
        db.commit()
        cursor.close()
        db.close()
        return response