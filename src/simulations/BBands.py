# Copyright (C) 2018 GuQiangJs.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

# 布林带相关模拟

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src import reader


def _getData(symbol, window: int = 20, K: int = 2,
             use_sand_data: bool = True, colName='Close'):
    """读取数据

    Args:
        symbol:
        window:
        K:
        use_sand_data:
        colName:

    Returns:
        [
        所有数据 -> DataFrame,
        原始值 -> Series,
        平均值 -> Series,
        上轨 -> Series,
        下轨 -> Series
        ]

    """
    df = pd.DataFrame()
    series = None
    if isinstance(symbol, str) or isinstance(symbol, int):
        df = reader.get_symbol_data(symbol, use_sand_data=use_sand_data)
        if df.empty:
            raise ValueError('数据为空')
        if not colName or colName not in df.columns:
            raise ValueError('数据列 {} 不存在'.format(colName))

        series = df[colName]  # 使用后复权价格
    if not isinstance(df, pd.DataFrame) or series.empty:
        raise ValueError('收盘价数据为空或者不是pandas.Series')

    mean = series.rolling(window=window).mean()  # 平均值
    deviation = np.std(series[window:] - mean[window:])  # window时间段的标准差
    upper_band = mean + K * deviation  # 上轨
    lower_band = mean - K * deviation  # 下轨

    return [df, series, mean, upper_band, lower_band]


def plot_line(symbol, window: int = 20, K: int = 2,
              use_sand_data: bool = True, colName='Close', s=-1, e=-1):
    """绘制布林线

    Args:
        symbol:
        window:
        K:
        use_sand_data:
        colName:
        s: 绘制开始下标-1表示绘制所有。默认-1。
        e: 绘制结束下标。-1表示绘制所有。默认-1。

    """

    df, series, mean, upper_band, lower_band = _getData(symbol, window=window,
                                                        K=K,
                                                        use_sand_data=use_sand_data,
                                                        colName=colName)
    sns.lineplot(data=_get_series(series, s, e), color='b', label='原值')
    plt.title('移动平均\n窗口大小 = {0}'.format(window))
    sns.lineplot(data=_get_series(mean, s, e), color='g', label='移动平均线')
    sns.lineplot(data=_get_series(upper_band, s, e), color='coral',
                 linestyle='--', label='上轨')
    sns.lineplot(data=_get_series(lower_band, s, e), color='coral',
                 linestyle='--', label='下轨')
    plt.show()


def _get_series(series, s, e):
    if s == -1 and e == -1:
        return series
    if s != -1 and e != -1:
        return series[s:e]
    if s != -1:
        return series[s:]
    return series[:e]


def get_buy_sale_point(symbol, window: int = 20, K: int = 2,
                       use_sand_data: bool = True, colName='Close',
                       appendColName: tuple = None) -> pd.DataFrame:
    """模拟布林带的计算方式，从上往下穿越上轨为卖出点，从下往上穿越下轨为买入点

    Args:
        appendColName: 返回结果中附加的列名。（当 symbol 不是 pd.Series 时，才会有效）
        colName:  计算用的价格列名。默认为 'Close'。（当 symbol 不是 pd.Series 时，
            需要读取数据时，取读取到的数据中的指定列作为计算用的主数据列。）
        use_sand_data: 是否使用沙盒数据。默认为 True。
        symbol: 股票代码或者单一股票收盘价的pd.Series
        window: 窗口期。默认为 20。
        K: 多少倍标准差。默认为 2。

    Returns:


    Raises:
        ValueError: 指定数据列 colName 不存在 或者 无法按照 symbol 读取到数据时。

    """
    df, series, mean, upper_band, lower_band = _getData(symbol, window=window,
                                                        K=K,
                                                        use_sand_data=use_sand_data,
                                                        colName=colName)

    # 符合购买条件的数据
    sb = series[(series < lower_band) & (series.shift(1) > lower_band.shift(1))]
    # 符合卖出条件的数据
    ss = series[(series > upper_band) & (series.shift(1) < upper_band.shift(1))]

    result = pd.DataFrame(sb)
    result['opt'] = 'b'
    result = result.append(pd.DataFrame(ss))
    result = result.fillna({'opt': 's'})

    if not df.empty and appendColName:
        for n in appendColName:
            if n in df.columns:
                result = result.join(df.loc[result.index][n])

    return result.sort_index()
