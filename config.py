from nonebot.default_config import *
import re


SUPERUSERS = {}
COMMAND_START = ['', re.compile(r'[/!]+')]
HOST = '127.0.0.1'
PORT = 8080
DB_HOST = ''
DB_PORT = 3306
DB_USER = ''
DB_PWD = ''
GROUP = 
ADMIN = {}
NON_DEFAULT_PLUGINS = {}
HORSE = '[CQ:emoji,id=128052]'
HORSE_SKIN = {'哈哈剑': '[CQ:face,id=13]',
              '镜华': '[CQ:emoji,id=128167]',
              '杏奈': '[CQ:emoji,id=126980]',
              '真步': '[CQ:emoji,id=9999]',
              '璃乃': '[CQ:emoji,id=128640]',
              '初音': '[CQ:emoji,id=11088]',
              '依绪': '[CQ:emoji,id=128064]',
              '咲恋': '[CQ:emoji,id=128226]',
              '千歌': '[CQ:emoji,id=127926]',
              '扇子': '[CQ:emoji,id=128168]',
              '真琴': '[CQ:emoji,id=128058]',
              '纯': '[CQ:emoji,id=11035]',
              '静流': '[CQ:emoji,id=128068]',
              '毛二力': '[CQ:emoji,id=128027]',
              '姬塔': '[CQ:emoji,id=127928]',
              '亚里莎': '[CQ:emoji,id=128565]',
              '茜里': '[CQ:emoji,id=128663]',
              '宫子': '[CQ:emoji,id=127854]',
              '雪哥': '[CQ:emoji,id=128697]',
              '玲奈': '[CQ:emoji,id=128175]',
              '香织': '[CQ:emoji,id=128054]',
              '铃': '[CQ:emoji,id=127792]',
              '美美': '[CQ:emoji,id=128048]',
              '惠鲤子': '[CQ:emoji,id=128127]',
              '忍': '[CQ:emoji,id=128128]',
              '真阳': '[CQ:emoji,id=128004]',
              '栞': '[CQ:emoji,id=128047]',
              '望': '[CQ:emoji,id=127908]',
              '空花': '[CQ:face,id=2]',
              '珠希': '[CQ:emoji,id=128049]',
              '子龙': '[CQ:emoji,id=128050]',
              '深月': '[CQ:face,id=63]',
              '绫音': '[CQ:emoji,id=128059]',
              }
INCREASE_STARS_COST = (30, 100, 120, 150)
INITIAL_CHARAS = ('凯露', '佩可莉姆', '可可萝', '优衣')
