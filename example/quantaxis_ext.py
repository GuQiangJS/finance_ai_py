# Copyright (C) 2018 GuQiangJs.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

import pandas as pd
from QUANTAXIS import QA_fetch_index_day_adv
from QUANTAXIS import QA_fetch_stock_day_adv
from QUANTAXIS import QA_fetch_stock_list


# QUANTAXIS扩展

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
