# Copyright (C) 2018 GuQiangJs.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

# 帮助类

import os

from .settings import Default


def get_his_data_path(symbol, in_sand_box=True, market=Default.market()):
    """获取 **每日成交汇总数据文件路径**

    Args:
        in_sand_box: 是否从沙盒中读取数据。默认 True。
        market: 国家代码。默认 `settings.Default.market()`。
        symbol: 指定股票代码。

    Returns:
        返回完整的文件路径。

    .. todo::
        不支持读取非沙箱数据

    """
    if in_sand_box:
        return os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            'sandbox', market, 'stocks', 'datas', 'his',
                            '{0}.csv'.format(symbol))
    else:
        raise NotImplementedError
