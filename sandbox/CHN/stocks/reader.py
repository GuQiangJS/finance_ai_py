# 数据读取器
import os

import pandas as pd

from . import globalSettings

def get_symbol_data(symbol, use_sand_data=True) -> pd.DataFrame:
    """读取指定股票的数据

    Args:
        symbol: 股票代码
        use_sand_data: 是否使用沙盒数据（默认为True）

    Returns:

    Raises:
        ValueError: 参数 symbol 为空时。

    """
    if not symbol:
        raise ValueError('symbol')
    if use_sand_data:
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            'datas', '{0}.csv'.format(symbol))
        df=pd.read_csv(path, encoding=globalSettings.encoding)
        df.set_index('Date',inplace=True)
        return df
    else:
        raise NotImplementedError
