# Copyright 2019 The GuQiangJS. All Rights Reserved.
# ==============================================================================

# 画图相关

# 设定绘图的默认大小
# 设定绘图的默认大小
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.rcParams["figure.figsize"] = [16, 8]

# 加载 seaborn，并且设置默认使用 seaborn
import seaborn as sns

sns.set()

matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

import units
from talib import MA_Type
import talib
import numpy as np


def plot_daily_return_hist(s: pd.Series, bins=50):
    """以直方图方式绘制日收益数据"""
    # 使用直方图查看日收益
    s.hist(bins=bins)
    # 均值
    mean = s.mean()
    # 中位数
    median = s.median()
    # 标准差
    std = s.std()
    plt.axvline(mean, color='g', label='均值')
    plt.axvline(median, color='k', linestyle=':', label='中位数')
    plt.axvline(std, color='r', linestyle='--', label='标准差')
    plt.axvline(-1 * std, color='r', linestyle='--', label='标准差')
    plt.title('日收益直方图')

def plot_bbands(s: pd.Series, ma_type: MA_Type, timeperiod=5, nbdevup=2,
                nbdevdn=2):
    """绘制布林带

    Args:
        timeperiod: 时间段
        nbdevup: 上轨与平均值无偏差的标准差的数量
        nbdevdn: 下轨与平均值无偏差的标准差的数量
        s: 原始值
        ma_type:

    Returns:

    """
    plt.title(
        '布林带\n移动平均计算方式：{0}\n窗口：{1}'.format(units._translate_ma_type(ma_type),
                                           timeperiod))
    upper, middle, lower = talib.BBANDS(s, matype=ma_type,
                                        timeperiod=timeperiod, nbdevup=nbdevup,
                                        nbdevdn=nbdevdn)
    upper.plot(color='r', label="Upper")
    middle.plot(color='g', label="Middle")
    lower.plot(color='r', label="Lower")
    s.plot(color='b', label="原始")
