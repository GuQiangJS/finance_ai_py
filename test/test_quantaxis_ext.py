# Copyright (C) 2018 GuQiangJs.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

import unittest

import QUANTAXIS as QA
import pandas as pd

from finance_ai_py import quantaxis_ext
from . import TestBase


class QuantaxisExtTestCase(TestBase):

    def _calc_daily_return(s: pd.Series) -> pd.Series:
        '''计算日收益'''
        return (s / s.shift(1) - 1)[1:]

    def _prepare_account_single_stock(self, lst: dict = None,
                                      init_cash=10000) -> quantaxis_ext.QA_Account_Ext:
        stock_account = quantaxis_ext.QA_Account_Ext(init_cash=init_cash)
        Broker = QA.QA_BacktestBroker()
        for item in lst:
            order = stock_account.send_order(
                code=item['code'],
                time=item['time'],
                amount=item['amount'],
                towards=item['towards'],
                price=item['price'],
                order_model=item['order_model'],
                amount_model=item['amount_model'],
            )
            Broker.receive_order(QA.QA_Event(order=order))
            trade_mes = Broker.query_orders(stock_account.account_cookie,
                                            'filled')
            res = trade_mes.loc[order.account_cookie, order.realorder_id]
            order.trade(res.trade_id, res.trade_price, res.trade_amount,
                        res.trade_time)
            stock_account.settle()
        return stock_account

    def test_hold_table_lifo_1(self):
        """测试按照先进先出卖出顺序后的内容是否正确"""
        orders = []
        stock_code = '600436'
        orders.append({'code': stock_code, 'time': '2006-08-04', 'amount': 100,
                       'towards': QA.ORDER_DIRECTION.BUY, 'price': 0,
                       'order_model': QA.ORDER_MODEL.CLOSE,
                       'amount_model': QA.AMOUNT_MODEL.BY_AMOUNT})
        orders.append({'code': stock_code, 'time': '2006-08-07', 'amount': 100,
                       'towards': QA.ORDER_DIRECTION.BUY, 'price': 0,
                       'order_model': QA.ORDER_MODEL.CLOSE,
                       'amount_model': QA.AMOUNT_MODEL.BY_AMOUNT})
        orders.append({'code': stock_code, 'time': '2006-08-08', 'amount': 100,
                       'towards': QA.ORDER_DIRECTION.BUY, 'price': 0,
                       'order_model': QA.ORDER_MODEL.CLOSE,
                       'amount_model': QA.AMOUNT_MODEL.BY_AMOUNT})
        orders.append({'code': stock_code, 'time': '2007-10-29', 'amount': 100,
                       'towards': QA.ORDER_DIRECTION.BUY, 'price': 0,
                       'order_model': QA.ORDER_MODEL.CLOSE,
                       'amount_model': QA.AMOUNT_MODEL.BY_AMOUNT})
        orders.append({'code': stock_code, 'time': '2008-06-10', 'amount': 100,
                       'towards': QA.ORDER_DIRECTION.BUY, 'price': 0,
                       'order_model': QA.ORDER_MODEL.CLOSE,
                       'amount_model': QA.AMOUNT_MODEL.BY_AMOUNT})
        orders.append({'code': stock_code, 'time': '2010-11-24', 'amount': 100,
                       'towards': QA.ORDER_DIRECTION.SELL, 'price': 0,
                       'order_model': QA.ORDER_MODEL.CLOSE,
                       'amount_model': QA.AMOUNT_MODEL.BY_AMOUNT})
        account = self._prepare_account_single_stock(lst=orders)
        df = account.hold_table_fifo()
        # 先买了5次，卖了1次，应该保留购买的后4次记录
        for o in orders[1:-1]:
            self.assertTrue(o['time'] in df.index)
        # 第一次的记录不应该包含在内
        self.assertFalse(orders[0]['time'] in df.index)

        self.assertEqual(df['price'].mean(),account.hold_price_fifo().at[stock_code][0])#持仓均价

    def test_hold_table_lifo_2(self):
        """测试按照先进先出卖出顺序后的内容是否正确"""
        orders = []
        stock_code = '600436'
        orders.append(
            {'code': stock_code, 'time': '2006-08-04', 'amount': 100,
             'towards': QA.ORDER_DIRECTION.BUY, 'price': 0,
             'order_model': QA.ORDER_MODEL.CLOSE,
             'amount_model': QA.AMOUNT_MODEL.BY_AMOUNT})  # 按数量下单
        orders.append(
            {'code': stock_code, 'time': '2006-08-07', 'amount': 100,
             'towards': QA.ORDER_DIRECTION.BUY, 'price': 0,
             'order_model': QA.ORDER_MODEL.CLOSE,
             'amount_model': QA.AMOUNT_MODEL.BY_AMOUNT})  # 按数量下单
        orders.append(
            {'code': stock_code, 'time': '2006-08-08', 'amount': 100,
             'towards': QA.ORDER_DIRECTION.BUY, 'price': 0,
             'order_model': QA.ORDER_MODEL.CLOSE,
             'amount_model': QA.AMOUNT_MODEL.BY_AMOUNT})  # 按数量下单
        orders.append(
            {'code': stock_code, 'time': '2007-10-29', 'amount': 100,
             'towards': QA.ORDER_DIRECTION.BUY, 'price': 0,
             'order_model': QA.ORDER_MODEL.CLOSE,
             'amount_model': QA.AMOUNT_MODEL.BY_AMOUNT})  # 按数量下单
        orders.append(
            {'code': stock_code, 'time': '2008-06-10', 'amount': 100,
             'towards': QA.ORDER_DIRECTION.BUY, 'price': 0,
             'order_model': QA.ORDER_MODEL.CLOSE,
             'amount_model': QA.AMOUNT_MODEL.BY_AMOUNT})  # 按数量下单
        orders.append(
            {'code': stock_code, 'time': '2010-11-24', 'amount': 300,
             'towards': QA.ORDER_DIRECTION.SELL, 'price': 0,
             'order_model': QA.ORDER_MODEL.CLOSE,
             'amount_model': QA.AMOUNT_MODEL.BY_AMOUNT})  # 按数量下单
        account = self._prepare_account_single_stock(lst=orders)
        df = account.hold_table_fifo()
        # 先买了5次，卖了1次，但是一次卖了300,，应该保留购买的后2次记录
        for o in orders[-3:-1]:
            self.assertTrue(o['time'] in df.index, msg=o['time'])
        for o in orders[:2]:
            # 前三次次的记录不应该包含在内
            self.assertFalse(o['time'] in df.index, msg=o['time'])

        self.assertEqual(df['price'].mean(),account.hold_price_fifo().at[stock_code][0])#持仓均价

    def test_hold_table_lifo_3(self):
        """测试按照先进先出卖出顺序后的内容是否正确"""
        orders = []
        stock_code = '600436'
        orders.append(
            {'code': stock_code, 'time': '2006-08-04', 'amount': 100,
             'towards': QA.ORDER_DIRECTION.BUY, 'price': 0,
             'order_model': QA.ORDER_MODEL.CLOSE,
             'amount_model': QA.AMOUNT_MODEL.BY_AMOUNT})  # 按数量下单
        orders.append(
            {'code': stock_code, 'time': '2006-08-07', 'amount': 100,
             'towards': QA.ORDER_DIRECTION.BUY, 'price': 0,
             'order_model': QA.ORDER_MODEL.CLOSE,
             'amount_model': QA.AMOUNT_MODEL.BY_AMOUNT})  # 按数量下单
        orders.append(
            {'code': stock_code, 'time': '2006-08-08', 'amount': 100,
             'towards': QA.ORDER_DIRECTION.BUY, 'price': 0,
             'order_model': QA.ORDER_MODEL.CLOSE,
             'amount_model': QA.AMOUNT_MODEL.BY_AMOUNT})  # 按数量下单
        orders.append(
            {'code': stock_code, 'time': '2007-10-29', 'amount': 100,
             'towards': QA.ORDER_DIRECTION.BUY, 'price': 0,
             'order_model': QA.ORDER_MODEL.CLOSE,
             'amount_model': QA.AMOUNT_MODEL.BY_AMOUNT})  # 按数量下单
        orders.append(
            {'code': stock_code, 'time': '2008-06-10', 'amount': 100,
             'towards': QA.ORDER_DIRECTION.BUY, 'price': 0,
             'order_model': QA.ORDER_MODEL.CLOSE,
             'amount_model': QA.AMOUNT_MODEL.BY_AMOUNT})  # 按数量下单
        orders.append(
            {'code': stock_code, 'time': '2010-11-24', 'amount': 500,
             'towards': QA.ORDER_DIRECTION.SELL, 'price': 0,
             'order_model': QA.ORDER_MODEL.CLOSE,
             'amount_model': QA.AMOUNT_MODEL.BY_AMOUNT})  # 按数量下单
        account = self._prepare_account_single_stock(lst=orders)
        df = account.hold_table_fifo()
        # 先买了5次，卖了1次，但是一次卖了500,，应该不保留任何数据
        for o in orders[:-1]:
            self.assertFalse(o['time'] in df.index, msg=o['time'])


if __name__ == '__main__':
    unittest.main()
