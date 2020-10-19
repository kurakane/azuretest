"""データのダミークラスの定義."""

from collections import OrderedDict
import datetime
import copy


class ObsTradeQueryBuilder:
    """ダミーの検索条件クラス."""
    def __init__(self, count):
        # クライアント側から明細の件数を渡せるようにしておく.
        self.count = count


    def dump(self):
        print('ObsTradeQueryBuilder')
        print(f'明細:[{self.count}]')


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
    def __init__(self):
        self.data = []
        for i in range(1000):
            self.data.append(i)
