# Copyright (C) 2018 GuQiangJs.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

import pandas as pd
from QUANTAXIS import QA_fetch_index_day_adv
from QUANTAXIS import QA_fetch_stock_day_adv
from QUANTAXIS import QA_fetch_stock_list


# QUANTAXIS扩展

def fetch_index_stock_daily_adv(symbol, zs, start, end,
                                column='close') -> pd.DataFrame:
    """计算指定股票和指定指数合并后的日线数据

    Args:
        column: 使用的列名。默认为收盘价。
        symbol: 指定股票代码
        zs: 指定指数代码
        start: 开始日期
        end: 结束日期

    Returns:
        返回的 `pd.DataFrame` 中的指数列会在传入参数指数前添加 **zs_** 字样。
        例如：传入参数为 `000300` 那么返回的列名为 `zs_000300` 。
        其他股票列名不变，依旧为股票代码。
    """
    zs_df = fetch_index_day_adv(zs, start, end)[column].rename('zs_' + zs)
    result = pd.DataFrame(zs_df)
    lst = []
    if isinstance(symbol, str):
        lst.append(symbol)
    else:
        lst = symbol
    for s in lst:
        symbol_df = fetch_stock_day_adv(s, start, end)
        if symbol_df.empty:
            continue
        result = result.join(symbol_df[column].rename(s))
    return result


def fetch_index_day_adv(code, start, end) -> pd.DataFrame:
    """扩展`QUANTAXIS.QA_fetch_index_day_adv`。
    会重新设置索引列。（原本的索引列为[date,code]）。返回的索引列会丢弃 `code`。

    Args:
        code: 指数代码
        start: 开始日期
        end: 结束日期

    Returns:
        如果没有找到数据则返回 空的 `DataFrame` 参考：`pd.DataFrame.empty`
    """
    result = QA_fetch_index_day_adv(code, start, end)
    return result.data.reset_index().drop(columns=['code']).set_index(
        'date') if result is not None and result.data is not None and not result.data.empty else pd.DataFrame


def fetch_stock_day_adv(code, start, end) -> pd.DataFrame:
    """扩展`QUANTAXIS.QA_fetch_stock_day_adv`。
    会重新设置索引列。（原本的索引列为[date,code]）。返回的索引列会丢弃 `code`。

    Args:
        code: 指数代码
        start: 开始日期
        end: 结束日期

    Returns:
        如果没有找到数据则返回 空的 `DataFrame` 参考：`pd.DataFrame.empty`
    """
    result = QA_fetch_stock_day_adv(code, start, end)
    return result.data.reset_index().drop(columns=['code']).set_index(
        'date') if result is not None and result.data is not None and not result.data.empty else pd.DataFrame


def fetch_stock_list() -> pd.DataFrame:
    """从本地数据库中获取股票列表"""
    return QA_fetch_stock_list()
