# Copyright (C) 2018 GuQiangJs.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

# 数据读取器

import pandas as pd

from src import settings
from src import unit


def get_symbol_data(symbol, use_sand_data=True) -> pd.DataFrame:
    """读取指定股票的每日成交汇总数据

    Args:
        symbol: 股票代码
        use_sand_data: 是否使用沙盒数据（默认为True）

    Returns:

    Raises:
        ValueError: 参数 symbol 为空时。

    .. todo::
        不支持读取非沙箱数据

    """
    if not symbol:
        raise ValueError('symbol')
    if use_sand_data:
        df = pd.read_csv(unit.get_his_data_path(symbol),
                         encoding=settings.Default.encoding())
        df.set_index('Date', inplace=True)
        return df
    else:
        raise NotImplementedError
