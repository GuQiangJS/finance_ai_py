"""QUANTAXIS 扩展"""
from collections import deque

import QUANTAXIS as QA
import numpy as np
import pandas as pd


class QA_Performance_Ext(QA.QA_Performance):

    @property
    def pnl_fifo_ext(self):
        """修改基类中的 `pnl_fif`。
        基类中的方法计算错误，并没有使用先进先出的逻辑。参见代码中的具体描述

        Returns: 在原本返回成交配对DataFrame的结果上，
        增加了返回尚未配对成功的dict
        （主键为股票代码，value为deque队列，其中包含元组[交易日期，交易数量，交易金额]）
        """
        X = dict(
            zip(
                self.account.code,
                [deque() for i in range(len(self.account.code))]
            )
        )
        pair_table = []
        for _, data in self.account.history_table.iterrows():
            while True:
                if len(X[data.code]) == 0:
                    X[data.code].append(
                        (data.datetime,
                         data.amount,
                         data.price)
                    )
                    break
                else:
                    l = X[data.code].popleft()
                    if (l[1] * data.amount) < 0:
                        # 原有多仓/ 平仓 或者原有空仓/平仓

                        if abs(l[1]) > abs(data.amount):
                            temp = (l[0], l[1] + data.amount, l[2])
                            X[data.code].appendleft(temp)
                            if data.amount < 0:
                                pair_table.append(
                                    [
                                        data.code,
                                        data.datetime,
                                        l[0],
                                        abs(data.amount),
                                        data.price,
                                        l[2]
                                    ]
                                )
                                break
                            else:
                                pair_table.append(
                                    [
                                        data.code,
                                        l[0],
                                        data.datetime,
                                        abs(data.amount),
                                        data.price,
                                        l[2]
                                    ]
                                )
                                break

                        elif abs(l[1]) < abs(data.amount):
                            data.amount = data.amount + l[1]

                            if data.amount < 0:
                                pair_table.append(
                                    [
                                        data.code,
                                        data.datetime,
                                        l[0],
                                        l[1],
                                        data.price,
                                        l[2]
                                    ]
                                )
                            else:
                                pair_table.append(
                                    [
                                        data.code,
                                        l[0],
                                        data.datetime,
                                        l[1],
                                        data.price,
                                        l[2]
                                    ]
                                )
                        else:
                            if data.amount < 0:
                                pair_table.append(
                                    [
                                        data.code,
                                        data.datetime,
                                        l[0],
                                        abs(data.amount),
                                        data.price,
                                        l[2]
                                    ]
                                )
                                break
                            else:
                                pair_table.append(
                                    [
                                        data.code,
                                        l[0],
                                        data.datetime,
                                        abs(data.amount),
                                        data.price,
                                        l[2]
                                    ]
                                )
                                break

                    else:
                        # 主要修改在这里。主要是顺序错了。
                        X[data.code].append(
                            (data.datetime,
                             data.amount,
                             data.price)
                        )
                        X[data.code].appendleft(l)
                        break

        pair_title = [
            'code',
            'sell_date',
            'buy_date',
            'amount',
            'sell_price',
            'buy_price'
        ]
        pnl = pd.DataFrame(pair_table, columns=pair_title).set_index('code')

        pnl = pnl.assign(pnl_ratio=(pnl.sell_price / pnl.buy_price) - 1).assign(
            buy_date=pd.to_datetime(pnl.buy_date)
        ).assign(sell_date=pd.to_datetime(pnl.sell_date))
        pnl = pnl.assign(
            pnl_money=(pnl.sell_price - pnl.buy_price) * pnl.amount
        )
        return pnl, X


class QA_Account_Ext(QA.QA_Account):
    """QA_Account扩展

    """

    def hold_table_fifo(self):
        '''返回当前持仓的列表，与基类的 hold_table 不同，基类只返回总数量。
        此处采用 **先进先出法配对成交记录**。保持命名与 `QA_Performance.pnl_fifo`一致

        Returns:

        '''
        pnl, X = QA_Performance_Ext(self).pnl_fifo_ext
        lst = []
        for key, value in X.items():
            for v in list(value):
                l = [key]
                l.extend(list(v))
                lst.append(l)
        columns = ['code', 'date', 'amount', 'price']
        result = pd.DataFrame(lst, columns=columns)
        result['date'] = pd.to_datetime(result['date'])
        return result.set_index('date').sort_index()

    # def hold_price_fifo(self):
    #     """计算当前持仓的**总**成本金额（原购买资金总额）
    #     此处采用 **先进先出法配对成交记录**。保持命名与 `QA_Performance.pnl_fifo`一致
    #     """
    #     t = self.hold_table_fifo()
    #     t['buy_price'] = t['price'] * t['amount']
    #     return t.groupby('code')['buy_price'].sum()

    def hold_price_fifo(self, datetime=None):
        """计算持仓成本，与基类的 hold_table 不同，这里不计算已卖出的交易的成本
        此处采用 **先进先出法配对成交记录**。保持命名与 `QA_Performance.pnl_fifo`一致
        """

        def weights(x):
            if sum(x['amount']) != 0:
                return np.average(
                    x['price'],
                    weights=x['amount'],
                    returned=True
                )
            else:
                return np.nan

        if datetime is None:
            return self.hold_table_fifo().groupby('code').apply(weights).dropna()
        else:
            return self.hold_table_fifo().loc[:datetime].groupby('code').apply(weights
                                                                ).dropna()
