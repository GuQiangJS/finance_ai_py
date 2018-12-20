# 模拟
import numpy as np
import pandas as pd

from . import reader


def BBands(symbol, window: int = 20,
           K: int = 2) -> pd.DataFrame:
    """模拟布林带的计算方式，从上往下穿越上轨为卖出点，从下往上穿越下轨为买入点

    Args:
        symbol: 股票代码或者单一股票收盘价的pd.Series
        window: 窗口期
        K: 多少倍标准差

    Returns:

    """
    df = None
    series = None
    if isinstance(symbol, str) or isinstance(symbol, int):
        df = reader.get_symbol_data(symbol)
        if df.empty:
            raise ValueError('数据为空')
        series = df['Close_hfq']  # 使用后复权价格
    if not isinstance(df, pd.DataFrame) or series.empty:
        raise ValueError('收盘价数据为空或者不是pandas.Series')
    mean = series.rolling(window=window).mean()  # 平均值
    deviation = np.std(series[window:] - mean[window:])  # window时间段的标准差
    upper_band = mean + K * deviation  # 上轨
    lower_band = mean - K * deviation  # 下轨
    # series[400:800].plot()
    # lower_band[400:800].plot()
    # plt.show()
    result = pd.DataFrame(
        series[(series > lower_band) & (series.shift(1) < lower_band.shift(1))])
    result['opt'] = 'b'
    result = result.append(pd.DataFrame(series[(series < lower_band) & (
            series.shift(1) > lower_band.shift(1))]))
    result = result.fillna({'opt': 's'})
    result = result.join(df.loc[result.index]['Close'])
    result = result.join(df.loc[result.index]['Close_qfq'])
    return result


def simulate_buy_sale(df: pd.DataFrame, price: int = 10000, per_max_count=100):
    df = df.sort_index().reset_index()
    result = []
    remaining_funds = price
    for index in range(len(df.index)):
        # [买入日期，买入价格，数量，卖出日期，卖出价格]
        m = per_max_count * df.iloc[index]['Close']
        hfq_c = df.iloc[index]['Close_hfq']
        qfq_c = df.iloc[index]['Close_qfq']
        d = df.iloc[index]['Date']
        c = df.iloc[index]['Close']
        if df.iloc[index]['opt'] == 'b':
            if remaining_funds > m:
                result.append([d, c, hfq_c,qfq_c, per_max_count])
                remaining_funds = remaining_funds - m
        elif df.iloc[index]['opt'] == 's':
            for i in range(len(result)):
                if len(result[i]) <= 5:
                    result[i].append(d)
                    result[i].append(c)
                    result[i].append(hfq_c)
                    result[i].append(qfq_c)
                    remaining_funds = remaining_funds + m
    return result
