"""データのダミークラスの定義."""

import copy
import datetime
import random
from collections import OrderedDict


class ObsTradeQueryBuilder:
    """ダミーの検索条件クラス."""
    def __init__(self, count, data_count):
        # クライアント側から明細の件数を渡せるようにしておく.
        self.count = count
        self.data_count = data_count


    def dump(self):
        print('ObsTradeQueryBuilder')
        print(f'明細:[{self.count}]')
        print(f'データ数:[{self.data_count}]')


class Holidays:
    """ダミーの休日情報クラス."""
    def __init__(self):
        # ダミーの休日情報生成.
        holidays = []
        for i in range(1000):
            holiday = datetime.datetime(2020, 10, 16)
            holidays.append(holiday + datetime.timedelta(days=i))

        self.cities = OrderedDict()
        self.cities['EUTA'] = copy.copy(holidays)
        self.cities['GBLO'] = copy.copy(holidays)
        self.cities['JPTO'] = copy.copy(holidays)
        self.cities['USNY'] = copy.copy(holidays)


    def dump(self):
        print('Holidays')
        print(len(self.cities))


class SplTrade:
    def __init__(self, data_count):
        self.datas = []
        dummy_str = ''
        for i in range(data_count):
            dummy_str += random.choice('ABCEDFGHIJKLMNOPQRSTUVWXYZ')
        self.datas.append(dummy_str)

    
    def dump(self):
        for data in self.datas:
            print(len(data))
