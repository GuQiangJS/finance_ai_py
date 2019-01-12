# Copyright (C) 2018 GuQiangJs.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

# 计算器

import numpy as np
import pandas as pd
import talib
from .quantaxis_ext import fetch_index_stock_daily_adv


def calc_bbands_cross(s: pd.Series, ma_type: talib.MA_Type, timeperiod=5,
                      nbdevup=2,
                      nbdevdn=2):
    """计算穿越布林带的数据

    Args:
        timeperiod: 时间段
        nbdevup: 上轨与平均值无偏差的标准差的数量
        nbdevdn: 下轨与平均值无偏差的标准差的数量
        s: 原始值
        ma_type:

    Returns:
        [低于下轨的`pd.Series`，超过上轨的`pd.Series`]

    """
    upper, middle, lower = talib.BBANDS(s, matype=ma_type,
                                        timeperiod=timeperiod, nbdevup=nbdevup,
                                        nbdevdn=nbdevdn)
    return s[lower > s], s[upper < s]


def _calc_daily_return(s):
    """计算日收益"""
    return (s / s.shift(1) - 1).dropna()


def calc_normalize_data(df: pd.DataFrame) -> pd.DataFrame:
    """数据归一化。所有数据的第一条从1开始。

    Args:
        df:

    Returns:

    """
    return df / df.iloc[0]


def calc_sharp_radio(symbol, zs, start, end, c='00') -> pd.Series:
    """计算指定股票相对指定指数的夏普比率

    Args:
        symbol:
        zs:
        start:
        end:
        c: 周期。
            * '00':年
            * '01':季度
            * '02':月
            * '03':日

    Returns:

    """
    daily_return = calc_daily_return(symbol, zs, start, end)
    zs_returns = daily_return[['zs_' + zs]]
    stock_returns = daily_return.drop(columns=['zs_' + zs])
    # 股票日收益相对于指数日收益的差额
    excess_returns = stock_returns.sub(zs_returns['zs_' + zs], axis='index')
    # 股票日收益相对于指数日收益的差额的均值
    avg_excess_return = excess_returns.mean().dropna()
    # 股票日收益相对于指数日收益的差额的标准差
    std_excess_return = excess_returns.std().dropna()

    # 计算日 Sharpe ratio
    daily_sharpe_ratio = avg_excess_return.div(std_excess_return)

    if c == '03':
        return daily_sharpe_ratio

    if c == '00':
        # 计算年化 sharpe ratio。根据指数记录的实际交易日计算
        return daily_sharpe_ratio.mul(np.sqrt(zs_returns.shape[0]))

    if c == '01':
        # 计算季度
        return daily_sharpe_ratio.mul(np.sqrt(4))

    if c == '02':
        # 计算月度
        return daily_sharpe_ratio.mul(12)


def calc_daily_return(symbol, zs, start, end) -> pd.DataFrame:
    """计算指定股票和指定指数合并后的日收益表

    Args:
        symbol: 指定股票代码
        zs: 指定指数代码
        start: 开始日期
        end: 结束日期

    Returns:
        返回的 `pd.DataFrame` 中的指数列会在传入参数指数前添加 **zs_** 字样。
        例如：传入参数为 `000300` 那么返回的列名为 `zs_000300` 。
        其他股票列名不变，依旧为股票代码。
    """
    return _calc_daily_return(
        fetch_index_stock_daily_adv(symbol, zs, start, end))
