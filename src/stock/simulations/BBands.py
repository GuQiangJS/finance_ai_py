# Copyright (C) 2018 GuQiangJs.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

# 布林带相关模拟

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from ... import Operate
from ... import Transaction
from ... import reader


def _get_data(symbol, window: int = 20, k: int = 2,
              use_sand_data: bool = True, col_name='Close'):
    """读取数据

    Args:
        symbol:
        window:
        k:
        use_sand_data:
        col_name:

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
        if not col_name or col_name not in df.columns:
            raise ValueError('数据列 {} 不存在'.format(col_name))

        series = df[col_name]  # 使用后复权价格
    if not isinstance(df, pd.DataFrame) or series.empty:
        raise ValueError('收盘价数据为空或者不是pandas.Series')

    mean = series.rolling(window=window).mean()  # 平均值
    deviation = np.std(series[window:] - mean[window:])  # window时间段的标准差
    upper = mean + k * deviation  # 上轨
    lower = mean - k * deviation  # 下轨

    return [df, series, mean, upper, lower]


def plot_line(symbol, save_file=None, window: int = 20, k: int = 2,
              use_sand_data: bool = True, col_name='Close', s=-1, e=-1):
    """绘制布林线

    Args:
        save_file: 保存文件的路径。默认为None，表示不保存。
        symbol:
        window:
        k:
        use_sand_data:
        col_name:
        s: 绘制开始下标-1表示绘制所有。默认-1。
        e: 绘制结束下标。-1表示绘制所有。默认-1。

    """

    df, series, mean, upper, lower = _get_data(symbol, window=window,
                                               k=k,
                                               use_sand_data=use_sand_data,
                                               col_name=col_name)
    sns.lineplot(data=_get_series(series, s, e), color='b', label='原值')
    plt.title('移动平均\n窗口大小 = {0}'.format(window))
    sns.lineplot(data=_get_series(mean, s, e), color='g', label='移动平均线')
    sns.lineplot(data=_get_series(upper, s, e), color='coral',
                 linestyle='--', label='上轨')
    sns.lineplot(data=_get_series(lower, s, e), color='coral',
                 linestyle='--', label='下轨')
    plt.xticks([])
    plt.show()
    if save_file:
        plt.savefig(fname=save_file)


def _get_series(series, s, e):
    """获取 数组或元组 的指定区间内容

    Args:
        series: 数组或元组
        s: 开始下标。为-1时表示不指定。
        e: 结束下标。为-1时表示不指定。

    Returns:
        返回筛选后的 数组或元组。

    """
    if s == -1 and e == -1:
        return series
    if s != -1 and e != -1:
        return series[s:e]
    if s != -1:
        return series[s:]
    return series[:e]


def get_buy_sale_point(symbol, window: int = 20, k: int = 2,
                       use_sand_data: bool = True,
                       col_name='Close',
                       append_col_name: tuple = None) -> (
        [Transaction], pd.DataFrame):
    """模拟布林带的计算方式，从上往下穿越上轨为卖出点，从下往上穿越下轨为买入点

    Args:
        append_col_name: 返回结果中的pd.DataFrame附加的列名。（当 symbol 不是 pd.Series 时，才会有效）
        col_name:  计算用的价格列名。默认为 'Close'。（当 symbol 不是 pd.Series 时，
            需要读取数据时，取读取到的数据中的指定列作为计算用的主数据列。）
        use_sand_data: 是否使用沙盒数据。默认为 True。
        symbol: 股票代码或者单一股票收盘价的pd.Series
        window: 窗口期。默认为 20。
        k: 多少倍标准差。默认为 2。

    Returns:
        返回元组。
        * 下标0的元素为：Transaction类型的列表。
        * 下标1的元素为：pd.DataFrame类型的对象。包含的数据信息更多。附加了参数中指定的append_col_name。

    Raises:
        ValueError: 指定数据列 col_name 不存在 或者 无法按照 symbol 读取到数据时。

    """
    df, series, mean, upper, lower = _get_data(symbol, window=window,
                                               k=k,
                                               use_sand_data=use_sand_data,
                                               col_name=col_name)

    # 符合购买条件的数据
    sb = series[(series < lower) & (series.shift(1) > lower.shift(1))]
    # 符合卖出条件的数据
    ss = series[(series > upper) & (series.shift(1) < upper.shift(1))]

    result = []
    for index, value in sb.iteritems():
        result.append(Transaction(index, operate=Operate.Buy))
    for index, value in ss.iteritems():
        result.append(Transaction(index, operate=Operate.Sale))

    d = pd.DataFrame(sb)
    d['opt'] = Operate.Buy
    d = d.append(pd.DataFrame(ss), sort=False)
    d = d.fillna({'opt': Operate.Sale})

    if not df.empty and append_col_name:
        for n in append_col_name:
            if n in df.columns:
                d = d.join(df.loc[result.index][n])

    return sorted(result, key=lambda t: t.date), d.sort_index()
