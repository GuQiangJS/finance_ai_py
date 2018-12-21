# Copyright (C) 2018 GuQiangJs.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

import datetime
import warnings

from .. import Operate
from .. import Transaction
from ..settings import Default


class TransactionStock(Transaction):
    """股票交易记录类。这个类只记录单一的买卖信息。

    Attributes:
        count (int): 交易数量
        symbol (str): 股票代码
        price (float): 交易价格
        date (datetime.datetime): 交易日期
        operate (Operate): 交易类型
        market (str): 股票所属市场。默认 `settings.Default.market()`。

    See Also:
        :py:class:`TransactionStockRecord`,
        :py:class:`Transaction`

    """

    def __init__(self, symbol: str, price: float, date: datetime.datetime,
                 operate: Operate, count: int = 100,
                 market: str = Default.market()):
        """构造函数

        Args:
            count: 交易数量
            symbol: 股票代码
            price: 交易价格
            date: 交易日期
            operate: 交易类型
            market: 股票所属市场。默认 `settings.Default.market()`。
        """
        Transaction.__init__(self, date, operate)
        self._symbol = symbol
        self._price = price
        self._market = market
        self._count = count

    @property
    def symbol(self):
        return self._symbol

    @property
    def price(self):
        return self._price

    @property
    def market(self):
        return self._market

    @property
    def count(self):
        return self._count

    def to_dict(self):
        return {
            'date': self._date,
            'market': self._market,
            'symbol': self._symbol,
            'operate': self.operate.name,
            'price': self._price,
            'count': self._count
        }

    def __str__(self):
        t = '{0}\t{1:5}\t{2:8}\t{3:5}\t{4:8>}\t{5:>10.2f}'
        return t.format(self._date,
                        self._market,
                        self._symbol,
                        self._operate.name,
                        self._count,
                        self._price)


class TransactionStockRecord(TransactionStock):
    """股票交易记录类。该类包含了一次股票交易 买入+卖出 的整体记录。

    Attributes:
        symbol (str): 股票代码
        buy_price (float): 买入交易价格
        buy_date (datetime.datetime): 买入交易日期
        buy_count (int): 买入数量
        sale_price (float): 买出交易价格
        sale_date (datetime.datetime): 买出交易日期
        sale_count (int): 买出数量
        market (str): 股票所属市场。默认 `settings.Default.market()`。

    See Also:
        :py:class:`TransactionStock`
    """

    def __init__(self, symbol: str, buy_price: float,
                 buy_date: datetime.datetime, buy_count: int = 100,
                 market: str = Default.market()):
        """构造函数

        默认为 **买入** 操作。

        Args:
            buy_count: 购买数量.默认100
            symbol: 股票代码
            buy_price: 交易价格
            buy_date: 交易日期
            market: 股票所属市场。默认 `settings.Default.market()`。
        """
        TransactionStock.__init__(self, symbol, buy_price, buy_date,
                                  Operate.Buy, buy_count, market)
        self._symbol = symbol
        self._price = buy_price
        self._market = market
        self._buy_date = buy_date
        self._buy_price = buy_price
        self._sale_date = None
        self._sale_price = 0
        self._buy_count = buy_count
        self._sale_count = 0

    @property
    def date(self):
        warnings.warn('此属性在当前类型中不可用。将返回 buy_date 的值。')
        return self._buy_date

    @property
    def count(self):
        warnings.warn('此属性在当前类型中不可用。将返回 buy_count 的值。')
        return self._buy_count

    @property
    def operate(self):
        warnings.warn('此属性在当前类型中不可用。将返回空值。')
        return ''

    @property
    def buy_date(self):
        return self._buy_date

    @property
    def buy_count(self):
        return self._buy_count

    @property
    def buy_price(self):
        return self._buy_price

    @property
    def price(self):
        warnings.warn('此属性在当前类型中不可用。将返回 buy_price 的值。')
        return self._buy_price

    @property
    def sale_date(self):
        return self._sale_date

    @sale_date.setter
    def sale_date(self, value: datetime.date):
        self._sale_date = value

    @property
    def sale_price(self):
        return self._sale_price

    @sale_price.setter
    def sale_price(self, value: float):
        self._sale_price = value

    @property
    def sale_count(self):
        return self._sale_count

    @sale_count.setter
    def sale_count(self, value: int):
        self._sale_count = value

    @property
    def hold(self) -> int:
        """当前持有数量"""
        return self._buy_count - self._sale_count

    @property
    def profit(self) -> float:
        """盈亏
        当 `hold` 大于0 时，返回0。
        """
        if self.hold > 0:
            return 0
        else:
            return self._sale_price * self._sale_count - \
                   self._buy_price * self.sale_count

    def to_dict(self):
        return {
            'market': self._market,
            'symbol': self._symbol,
            'buy_date': self._buy_date,
            'buy_price': self._buy_price,
            'buy_count': self._buy_count,
            'sale_date': self._sale_date,
            'sale_price': self._sale_price,
            'sale_count': self._sale_count,
            'hold': self.hold
        }

    @staticmethod
    def to_str_header():
        # 保持 格式化字符串与 `__str__` 同步修改
        f = '|{:8}|{:8}|{:12}|{:>10}|{:>10}|{:12}|{:>10}|{:>10}|{:>10}|'
        return f.format(
            'Market',
            'Symbol',
            'BuyDate',
            'BuyCount',
            'BuyPrice',
            'SaleDate',
            'SaleCount',
            'SalePrice',
            'Profit'
        )

    def __str__(self):
        # 保持 格式化字符串与 `to_str_header` 同步修改
        f = '|{:8}|{:8}|{:12}|{:>10}|{:>10.2f}|{:12}|{:>10}|{:>10.2f}|{:>10.2f}|'
        return f.format(
            self._market,
            self._symbol,
            self._buy_date,
            self._buy_count,
            self._buy_price,
            self._sale_date if self._sale_date is not None else '',
            self._sale_count,
            self._sale_price,
            self.profit
        )
