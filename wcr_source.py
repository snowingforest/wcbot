import pymysql
from DBUtils.PooledDB import PooledDB
from config import *


class Wcr:
    def __init__(self):
        self.db_pool = PooledDB(creator=pymysql, host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PWD,
                                database='wcr', blocking=True, ping=0)

    async def create_player(self, player_id, revive_time):
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = 'insert into player(player_id, money, sb, pig_stone, revive_time) values (%s, 15000, 1, 0, %s)' % (player_id, revive_time)
        try:
            result = cursor.execute(sql)
            db.commit()
        except BaseException:
            result = 0
        if result == 1:
            for chara_name in INITIAL_CHARAS:
                await self.add_chara(player_id, chara_name)
        cursor.close()
        db.close()
        return result

    async def delete_player(self, player_id):
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = 'delete from player where player_id = %s' % player_id
        cursor.execute(sql)
        sql = 'delete from player_charas where player_id = %s' % player_id
        cursor.execute(sql)
        db.commit()
        cursor.close()
        db.close()

    async def search_player(self, player_id):
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = 'select * from player where player_id = %s' % player_id
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()
        db.close()
        return result

    async def get_player_list(self):
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = 'select * from player'
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        db.close()
        return result

    async def send_money(self, wage):
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = 'update player set money = money + %s' % wage
        cursor.execute(sql)
        db.commit()
        cursor.close()
        db.close()

    async def send_money_to_player(self, player_id, wage):
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = 'update player set money = money + %s where player_id = %s' % (wage, player_id)
        cursor.execute(sql)
        db.commit()
        cursor.close()
        db.close()

    async def update_player_info(self, player_id, money, sb, pig_stone):
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = 'update player set money = %s, sb = %s, pig_stone = %s where player_id = %s' % (money, sb, pig_stone, player_id)
        cursor.execute(sql)
        db.commit()
        cursor.close()
        db.close()

    async def add_chara(self, player_id, chara_name):
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = 'insert into player_charas(player_id, name) values (%s, %s)'
        log = (player_id, chara_name)
        try:
            result = cursor.execute(sql, log)
            db.commit()
        except BaseException:
            result = 0
        cursor.close()
        db.close()
        return result

    async def search_chara(self, player_id, chara_name):
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = 'select * from player_charas where player_id = %s and name = %s'
        log = (player_id, chara_name)
        cursor.execute(sql, log)
        result = cursor.fetchone()
        cursor.close()
        db.close()
        return result

    async def get_chara_list(self, player_id, stars):
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = 'select player_charas.name from player_charas, chara_data where chara_data.name = player_charas.name and player_charas.player_id = %s and chara_data.stars + player_charas.stars = %s' % (player_id, stars)
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        db.close()
        return result

    async def get_chara_stars(self, player_id, chara_name):
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = 'select player_charas.stars + chara_data.stars from player_charas, chara_data where chara_data.name = %s and player_charas.name = %s and player_charas.player_id = %s'
        log = (chara_name, chara_name, player_id)
        cursor.execute(sql, log)
        result = cursor.fetchone()
        cursor.close()
        db.close()
        return result[0]

    async def increase_chara_stars(self, player_id, chara_name, stars):
        db = self.db_pool.connection()
        cursor = db.cursor()
        sql = 'update player_charas set stars = stars + %s where player_id = %s and name = %s'
        log = (stars, player_id, chara_name)
        cursor.execute(sql, log)
        db.commit()
        cursor.close()
        db.close()
