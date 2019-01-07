import matplotlib.pyplot as plt
import pandas as pd
import talib
from QUANTAXIS import QA_fetch_index_day_adv
from QUANTAXIS import QA_fetch_stock_day_adv


def _translate_ma_type(ma_type: talib.MA_Type):
    """获取 `talib.MA_Type` 对应的中文信息"""
    if ma_type == talib.MA_Type.SMA:
        return '简单移动平均线'
    elif ma_type == talib.MA_Type.EMA:
        return '指数移动平均线'
    elif ma_type == talib.MA_Type.WMA:
        return '加权移动平均线'
    elif ma_type == talib.MA_Type.DEMA:
        return '双指数移动平均线'
    elif ma_type == talib.MA_Type.TEMA:
        return '三倍指数移动平均线'
    elif ma_type == talib.MA_Type.TRIMA:
        return '三角移动平均线'
    elif ma_type == talib.MA_Type.KAMA:
        return '考夫曼自适应移动平均线'
    elif ma_type == talib.MA_Type.MAMA:
        return 'MESA自适应移动平均线'
    elif ma_type == talib.MA_Type.T3:
        return '三倍广义双指数移动平均线'


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
    return s[lower>s],s[upper<s]

def plot_bbands(s: pd.Series, ma_type: talib.MA_Type, timeperiod=5, nbdevup=2,
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
    plt.title('布林带\n移动平均计算方式：{0}\n窗口：{1}'.format(_translate_ma_type(ma_type),
                                                 timeperiod))
    upper, middle, lower = talib.BBANDS(s, matype=ma_type,
                                        timeperiod=timeperiod, nbdevup=nbdevup,
                                        nbdevdn=nbdevdn)
    upper.plot(color='r', label="Upper")
    middle.plot(color='g', label="Middle")
    lower.plot(color='r', label="Lower")
    s.plot(color='b', label="原始")


def calc_daily_return(s: pd.Series) -> pd.Series:
    """计算日收益"""
    return (s / s.shift(1) - 1).dropna()


def fetch_index_day_adv(code, start, end) -> pd.DataFrame:
    """扩展`QUANTAXIS.QA_fetch_index_day_adv`。
    会重新设置索引列。（原本的索引列为[date,code]）。返回的索引列会丢弃 `code`。

    Args:
        code: 指数代码
        start: 开始日期
        end: 结束日期
    """
    result = QA_fetch_index_day_adv(code, start, end)
    return result.reset_index().drop(columns=['code']).set_index('date')


def fetch_stock_day_adv(code, start, end) -> pd.DataFrame:
    """扩展`QUANTAXIS.QA_fetch_stock_day_adv`。
    会重新设置索引列。（原本的索引列为[date,code]）。返回的索引列会丢弃 `code`。

    Args:
        code: 指数代码
        start: 开始日期
        end: 结束日期
    """
    result = QA_fetch_stock_day_adv(code, start, end)
    return result.reset_index().drop(columns=['code']).set_index(
        'date') if not result else result


def get_daily_return(symbol, zs, start, end) -> pd.DataFrame:
    """计算指定股票和指定指数合并后的日收益表

    Args:
        symbol: 指定股票代码
        zs: 指定指数代码
        start: 开始日期
        end: 结束日期
    """
    zs_df = fetch_index_day_adv(zs, start, end)
    zs_daily_return = calc_daily_return(zs_df['close']).rename('zs_' + zs)
    result = pd.DataFrame(zs_daily_return)
    lst = []
    if isinstance(symbol, str):
        lst.append(symbol)
    else:
        lst = symbol
    for s in lst:
        symbol_df = fetch_stock_day_adv(s, start, end)
        if symbol_df.empty:
            continue
        symbol_daily_return = calc_daily_return(symbol_df['close']).rename(s)
        result = result.join(symbol_daily_return)
    return result
