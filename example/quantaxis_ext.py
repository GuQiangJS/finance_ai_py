"""QUANTAXIS 扩展"""

import QUANTAXIS as QA
from QUANTAXIS.QAUtil.QADate import QA_util_datetime_to_strdate as data_to_str
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


#
# def _get_qfq_history_table(account: QA.QA_Account, enddate) -> pd.DataFrame:
#     """取 `QA.QA_Account.history_table` 在结果中增加前复权价格 `price_qfq`。
#     方法会调用 `QA.QA_fetch_stock_day_adv` ，所以要求数据是存在本地的。
#     Args:
#         account:
#         enddate:
#
#     Returns:在原本`QA.QA_Account.history_table`的结果列中增加`price_qfq`列。
#     这列表示从 `history_table` 的每一行的 索引 (`datetime`) 开始至 `enddate` 结束期间
#     按照 **前复权** 方式计算后当前行的 **前复权价格**。
#     """
#     hold_df = account.history_table.set_index('datetime',
#                                               drop=False).sort_index()
#     hold_df['price_qfq'] = -1.0
#     if not isinstance(enddate, str):
#         enddate = QA.QAUtil.QADate.QA_util_datetime_to_strdate(enddate)
#     for idx in hold_df.index:
#         new_value = QA.QA_fetch_stock_day_adv(hold_df.loc[idx, 'code'], idx,
#                                               enddate).to_qfq()
#         hold_df.loc[idx, 'price_qfq'] = np.round(new_value.close[0], 4)
#     return hold_df
#
#
# def get_qfq_hold_price(account: QA.QA_Account, enddate):
#     '''扩展原本 `QA.QA_Account.hold_price` 。改为获取的是前复权价格。
#
#     Args:
#         account:
#         enddate:
#
#     Returns:
#
#     '''
#
#     # pylint: disable=C0103
#     def weights(x):
#         return np.average(
#             x['price_qfq'],
#             weights=x['amount'],
#             returned=True
#         ) if sum(x['amount']) != 0 else np.nan
#
#     # pyline: enable=C0103
#
#     return _get_qfq_history_table(account, enddate).loc[:enddate].groupby(
#         'code').apply(weights).dropna()
#
#
# class QA_Account_Ext(QA.QA_Account):
#     '''重写部分 `QA.QA_Account` 中的方法。'''
#
#     def _history_table_qfq(self, enddate) -> pd.DataFrame:
#         '''交易历史的table。根据 enddate 计算前复权价格。
#
#         Args:
#             enddate:
#         '''
#         result = self.history_table.copy()
#
#         result['price_qfq'] = -1.0
#         if not isinstance(enddate, str):
#             enddate = QA.QAUtil.QADate.QA_util_datetime_to_strdate(enddate)
#         for idx in result.index:
#             s = result.loc[idx, 'datetime']
#             new_value = QA.QA_fetch_stock_day_adv(result.loc[idx, 'code'],
#                                                   s, enddate).to_qfq()
#             result.loc[idx, 'price_qfq'] = np.round(
#                 new_value.select_day(s).close[0], 4)
#         return result
#
#     def hold_price_qfq(self, datetime):
#         '''计算持仓成本  如果给的是日期,则返回当日开盘前的持仓
#         **相对于 `QA.QA_Account.hold_price` 方法。改为使用前复权价格。**
#
#         Args:
#             datetime: **必须传入值。**
#             如果没有传值则使用 `QA.QA_Account.hold_price` 方法。
#
#         Returns:
#
#         '''
#
#         def weights(x):
#             if sum(x['amount']) != 0:
#                 return np.average(
#                     x['price_qfq'],
#                     weights=x['amount'],
#                     returned=True
#                 )
#             else:
#                 return np.nan
#
#         if datetime is None:
#             return super(QA_Account_Ext, self).hold_price(datetime)
#         else:
#             return self._history_table_qfq(datetime).set_index(
#                 'datetime',
#                 drop=False
#             ).sort_index().loc[:datetime].groupby('code').apply(weights
#                                                                 ).dropna()
#
#
# def _get_qfq_price(code, start, end):
#     qfq = QA.QA_fetch_stock_day_adv(code, start, end).to_qfq()
#     return np.round(qfq.select_day(start).close[0], 4)
#

class QA_Performance_Ext(QA.QA_Performance):
    '''扩展 :py:class:QA.QA_Performance'''

    @property
    def report_qfq(self):
        result = {}
        result['总投入'] = self.pnl_fifo_qfq.buy_price * self.pnl_fifo_qfq.amount
        result['总收益'] = self.pnl_fifo_qfq.pnl_money_qfq.sum()
        result['交易次数'] = self.pnl_fifo_qfq.shape[0]
        result['胜率'] = self.win_rate_qfq()

        return self.pnl_fifo_qfq[
            ['pnl_money_qfq', 'pnl_ratio_qfq', 'hold_days']].agg(
            {'mean', 'max', 'min', 'std'})

    def average_profit_qfq(self, methods='qfq'):
        '''收益平均数'''
        if methods not in ['qfq']:
            return self.average_profit(methods)
        return (self.pnl_fifo_qfq.pnl_money_qfq.mean())

    def win_rate_qfq(self, methods='qfq'):
        '''胜率。当 methods 不为 `qfq` 时，调用基类的 `win_rate()` 方法'''
        if methods not in ['qfq']:
            return self.win_rate(methods)
        data = self.pnl_fifo_qfq
        return round(len(data.query('pnl_money_qfq>0')) / len(data), 2)

    @property
    def pnl_fifo_qfq(self) -> pd.DataFrame:
        '''相对原本的 :py:func:pnl_filo 增加了按照复权价计算成本和收益的列'''
        pnl = super(QA_Performance_Ext, self).pnl_fifo
        pnl = pnl.reset_index()
        for idx in pnl.index:
            s = data_to_str(pnl.loc[idx, 'buy_date'])
            e = data_to_str(pnl.loc[idx, 'sell_date'])
            c = pnl.loc[idx, 'code']
            new_value = QA.QA_fetch_stock_day_adv(c, s, e).to_qfq()
            pnl.loc[idx, 'buy_price_qfq'] = np.round(
                new_value.select_day(s).close[0], 2)
        pnl = pnl.assign(
            pnl_money_qfq=(pnl.sell_price - pnl.buy_price_qfq) * pnl.amount
        )  # 前复权计算后的收益（考虑了分红配送）
        pnl = pnl.assign(
            hold_days=(pnl.sell_date - pnl.buy_date).dt.days
        )  # 持仓天数
        pnl = pnl.assign(
            pnl_ratio_qfq=np.round(
                (pnl.sell_price / pnl.buy_price_qfq - 1) * 100, 2)
        )  # 收益率
        return pnl.set_index('code')


class QA_Risk_Ext(QA.QA_Risk):
    '''扩展 :py:class:QA.QA_Risk'''
    @property
    def message_min(self):
        '''简化版的 :py:func:QA.QA_Risk.message'''
        return {
            'account_cookie': self.account.account_cookie,
            'portfolio_cookie': self.account.portfolio_cookie,
            'user_cookie': self.account.user_cookie,
            'annualize_return': round(self.annualize_return,
                                      2),
            'profit': round(self.profit,
                            2),
            'max_dropback': self.max_dropback,
            'time_gap': self.time_gap,
            'volatility': self.volatility,
            'benchmark_code': self.benchmark_code,
            'bm_annualizereturn': self.benchmark_annualize_return,
            'bm_profit': self.benchmark_profit,
            'beta': self.beta,
            'alpha': self.alpha,
            'sharpe': self.sharpe,
            'init_cash': "%0.2f" % (float(self.init_cash)),
            'last_assets': "%0.2f" % (float(self.assets.iloc[-1])),
            'total_tax': self.total_tax,
            'total_commission': self.total_commission,
            'profit_money': self.profit_money,
            'ir': self.ir
                                                                    # 'init_assets': round(float(self.init_assets), 2),
                                                                    # 'last_assets': round(float(self.assets.iloc[-1]), 2)
        }