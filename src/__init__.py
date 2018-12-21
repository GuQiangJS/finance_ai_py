# Copyright (C) 2018 GuQiangJs.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

__all__ = ['unit', 'Operate']

import datetime
from enum import Enum
from enum import unique
from sys import platform

import matplotlib.pyplot as plt
import seaborn as sns

# 禁止在python运行时显示警告信息
# warnings.filterwarnings('ignore')

sns.set()

# 绘图支持中文字体
sns.set_style('whitegrid')
if platform == 'darwin':
    sns.set_style({'font.sans-serif': 'SimHei'})
elif platform == 'win32':
    sns.set_style({'font.sans-serif': 'SimHei'})

plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['savefig.format'] = 'svg'


@unique
class Operate(Enum):
    """交易类型"""
    Buy = 0,
    Sale = 1


class Transaction:
    """交易基础类

    Attributes:
        date (datetime.datetime): 交易日期
        operate (Operate): 交易类型
    """

    def __init__(self, date: datetime.datetime, operate: Operate = Operate.Buy):
        """构造函数

        Args:
            date: 交易日期
            operate: 交易动作。
        """
        self._date = date
        self._operate = operate

    @property
    def date(self):
        return self._date

    @property
    def operate(self):
        return self._operate

    def to_dict(self):
        return {
            'date': self._date,
            'operate': self._operate.name
        }

    def __str__(self):
        return '{0}\t{1}'.format(self._date, self._operate.name)
