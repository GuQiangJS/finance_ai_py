"""QUANTAXIS 扩展"""

import QUANTAXIS as QA
from QUANTAXIS.QAUtil.QADate import QA_util_datetime_to_strdate as data_to_str
import pandas as pd
import numpy as np


class QA_Account_Ext(QA.QA_Account):
    """QA_Account扩展

    """

    def hold_table_Ext(self, datetime=None):
        '''返回当前持仓的列表，与基类的 hold_table 不同，基类只返回总数量

        Returns:

        '''
        hold_table = self.hold_table(datetime)
        result = pd.DataFrame()
        for index, row in hold_table.iteritems():
            tmp = self.history_table[self.history_table['code'] == index]
            if not tmp[tmp['amount'] < 0].empty:
                tmp = tmp.iloc[
                      tmp[tmp['amount'] < 0].tail(1).index.values[0] + 1:]
            result = tmp if result.empty else pd.concat([result, tmp])

        return result

    def hold_price_total(self):
        """计算当前持仓的**总**成本金额（原购买资金总额）"""
        t = self.hold_table_Ext()
        t['buy_price'] = t['price'] * t['amount']
        return t.groupby('code')['buy_price'].sum()

    def hold_price_Ext(self, datetime=None):
        """计算持仓成本，与基类的 hold_table 不同，这里不计算已卖出的交易的成本
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
            return self.hold_table_Ext().set_index(
                'datetime',
                drop=False
            ).sort_index().groupby('code').apply(weights).dropna()
        else:
            return self.hold_table_Ext().set_index(
                'datetime',
                drop=False
            ).sort_index().loc[:datetime].groupby('code').apply(weights
                                                                ).dropna()
