from nonebot.default_config import *
import re


SUPERUSERS = {463725434}
COMMAND_START = ['', re.compile(r'[/!]+')]
HOST = '127.0.0.1'
PORT = 8080
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'root'
DB_PWD = ''
#GROUP = 1107054970
GROUP = 123
ADMIN = {}
NON_DEFAULT_PLUGINS = {'wcj.plugins.wodi',
                       'wcj.plugins.gacha_all',
                       # 'wcj.plugins.wcr',
                       # 'wcj.plugins.horserace',
                       'wcj.plugins.build_mock_data',
                       # 'wcj.plugins.jjc',
                       # 'wcj.plugins.setu'
                       'wcj.plugins.teamfight',
                       }
HORSE = '[CQ:emoji,id=128052]'
HORSE_SKIN = {'哈哈剑': '[CQ:face,id=13]',
              '镜华': '[CQ:emoji,id=128167]',
              '杏奈': '[CQ:emoji,id=126980]',
              '真步': '[CQ:emoji,id=9999]',
              '璃乃': '[CQ:emoji,id=128640]',
              '初音': '[CQ:emoji,id=11088]',
              '依绪': '[CQ:emoji,id=128590]',
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
              '美里': '[CQ:emoji,id=128112]',
              '伊莉雅': '[CQ:emoji,id=128105]',
              '羊驼': '[CQ:emoji,id=128016]',
              '美咲': '[CQ:emoji,id=128064]',
              '香菜': '[CQ:emoji,id=127808]',
              '由加莉': '[CQ:emoji,id=127866]',
              '铃莓': '[CQ:emoji,id=127770]',
              '依里': '[CQ:emoji,id=128103]',
              '胡桃': '[CQ:emoji,id=128276]',
              '未奏希': '[CQ:emoji,id=128163]',
              '怜': '[CQ:emoji,id=128298]',
              '日和莉': '[CQ:emoji,id=128574]',
              '优衣': '[CQ:emoji,id=128148]',
              '佩可莉姆': '[CQ:emoji,id=127833]',
              '可可萝': '[CQ:emoji,id=128559]',
              '凯露': '[CQ:emoji,id=128576]',
              }
INCREASE_STARS_COST = (30, 100, 120, 150)
INITIAL_CHARAS = ('凯露', '佩可莉姆', '可可萝', '优衣')
