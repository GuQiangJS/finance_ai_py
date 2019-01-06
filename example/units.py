import pandas as pd
from QUANTAXIS import QA_fetch_index_day_adv
from QUANTAXIS import QA_fetch_stock_day_adv


def calc_daily_return(s: pd.Series) -> pd.Series:
    """计算日收益"""
    return (s / s.shift(1) - 1).dropna()


def fetch_index_day_adv(code, start, end) -> pd.DataFrame:
    """扩展`QUANTAXIS.QA_fetch_index_day_adv`。会重新设置索引列。（原本的索引列为[date,code]）。返回的索引列会丢弃 `code`。
    :param code: 指数代码
    :param start: 开始日期
    :param end: 结束日期
    :return: 
    """
    result = QA_fetch_index_day_adv(code, start, end)
    return result.reset_index().drop(columns=['code']).set_index('date')


def fetch_stock_day_adv(code, start, end) -> pd.DataFrame:
    """扩展`QUANTAXIS.QA_fetch_stock_day_adv`。会重新设置索引列。（原本的索引列为[date,code]）。返回的索引列会丢弃 `code`。
    :param code: 指数代码
    :param start: 开始日期
    :param end: 结束日期
    :return:
    """
    result = QA_fetch_stock_day_adv(code, start, end)
    return result.reset_index().drop(columns=['code']).set_index('date') if not result.data.empty else result


def get_daily_return(symbol, zs, start, end) -> pd.DataFrame:
    """计算指定股票和指定指数合并后的日收益表"""
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