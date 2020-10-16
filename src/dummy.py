"""データのダミークラスの定義."""

from collections import OrderedDict
import datetime
import copy


class ObsTradeQueryBuilder:
    """ダミーの検索条件クラス."""
    def dump(self):
        print('ObsTradeQueryBuilder')


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
        pass
