# Copyright (C) 2018 GuQiangJs.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

import calculator
import numpy as np
import pandas as pd
import talib


def simulate_buy_sale(s: pd.Series, ma_type: talib.MA_Type, timeperiod=5,
                      nbdevup=2, nbdevdn=2, sale_up_cost=True, print_log=False):
    """模拟买入卖出

    Args:
        s: 原始值
        ma_type:
        timeperiod: 时间段
        nbdevup: 上轨与平均值无偏差的标准差的数量
        nbdevdn: 下轨与平均值无偏差的标准差的数量
        sale_up_cost: 只有当当前价格超过持仓平均价时才卖出

    Returns:
        [当前持仓数量, 当前持仓成本, 当前资金, 盈亏, 最后一个交易日价格,
            最大资金占用, 买入次数, 卖出次数]

    """
    # 计算买入点和卖出点
    l, u = calculator.calc_bbands_cross(s, ma_type, timeperiod=timeperiod,
                                        nbdevup=nbdevup, nbdevdn=nbdevdn)

    # 可买时间点和价格
    df_b = pd.DataFrame(l)
    df_b['o'] = 'b'
    # 可卖时间点和价格
    df_s = pd.DataFrame(u)
    df_s['o'] = 's'

    df_bs = df_b.append(df_s).sort_index()
    buy_time = 0
    sale_time = 0

    amount = 0  # 当前资金占用
    max_amount = 0  # 最大资金占用
    hold = 0  # 当前持仓数量
    size = 100  # 每次交易数量
    cost = []  # 每次交易成本价
    for i in df_bs.index:
        turnover = 0
        if df_bs.loc[i, 'o'] == 'b':
            turnover = -(df_bs.loc[i, 'close'] * size)
            amount = amount + turnover
            hold = hold + size
            cost.append(df_bs.loc[i, 'close'])
            buy_time = buy_time + 1
        elif df_bs.loc[i, 'o'] == 's' and hold > 0:
            if df_bs.loc[i, 'close'] <= np.average(cost):
                if sale_up_cost:
                    if print_log:
                        print('skip。持仓价格过高。持仓价格:{}，当前价格:{}'.format(
                            np.average(cost),
                            df_bs.loc[
                                i, 'close']))
                    continue
            turnover = df_bs.loc[i, 'close'] * hold
            amount = amount + turnover
            hold = 0
            cost = []
            sale_time = sale_time + 1
        elif df_bs.loc[i, 'o'] == 's' and hold <= 0:
            if print_log:
                print('skip')
            continue
        if max_amount > amount:
            max_amount = amount
        if print_log:
            print(
                'date={0},o={5},amount={1},max_amount={2},hold={3},turnover={4}'.format(
                    i, amount, max_amount, hold, turnover, df_bs.loc[i, 'o']))
    if print_log:
        print('当前持仓数量:{}'.format(hold))
        print('当前持仓成本:{}'.format(np.average(cost)))
        print('当前资金:{}'.format(amount))
        print('盈亏:{}'.format(np.sum(cost) * size + amount))
        print('最后一个交易日价格:{}'.format(s[-1]))
        print('最大资金占用:{}'.format(np.abs(max_amount)))
        print('买入次数:{}'.format(buy_time))
        print('卖出次数:{}'.format(sale_time))
    return [hold, np.average(cost), amount, np.sum(cost) * size + amount, s[-1],
            np.abs(max_amount), buy_time, sale_time]
