# Copyright (C) 2018 GuQiangJs.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>


import itertools

# 股票帮助类
from . import Operate
from . import Transaction
from . import TransactionStock
from . import TransactionStockRecord as Tsr
from .. import reader
from ..settings import Default


def calculate_buy_sale(symbol: str, ts: [Transaction],
                       use_sand_data=True, market=Default.market(),
                       price_column='Open', shift_days=1,
                       fund=10000, per_count=100) -> [TransactionStock]:
    """根据参数 Ts 计算买入/卖出的记录

    Args:
        symbol: 股票代码
        ts: symbol 股票 的 Transaction集合
        use_sand_data: 是否使用沙盒数据
        market: 市场。默认 `settings.Default.market()`
        price_column: 从交易数据中读取计算价格时需要用到的列名。
        shift_days: 参数 Ts 中记录的是提示可交易的日期，这里可以设置提前或推后的天数。
        取实际交易日期时，会在 Ts 中记录的日期后加上这里标记的数值。
        默认为1。也就是第二个交易日为购买日。
        fund: 总资金。当总资金不足时，就算遇到 参数 Ts 中标记可买时，也无法购买。
        per_count: 每次购买数量。默认 100 （一手）。

    Returns:
        返回 TransactionStock 数组。

    """
    result = []
    if not ts or not symbol:
        raise ValueError('参数 Ts 或 symbol 不能为空')
    df = reader.get_symbol_data(symbol, use_sand_data=use_sand_data)
    if df.empty:
        raise ValueError('没有成交汇总数据')
    for t in sorted(ts, key=lambda x: x.date):
        p = df.loc[t.date:].iloc[shift_days][price_column]  # 单价(计算日后第n天的价格）
        m = per_count * p  # 总价
        o = t.operate

        if o == Operate.Buy and _can_buy(p, per_count, fund):
            # 按照默认数量购买
            t_b = TransactionStock(symbol, p, t.date, t.operate, per_count,
                                   market)
            result.append(t_b)
            fund = fund - m
            continue
        h = _get_hold(result)  # 当前可卖的集合
        if o == Operate.Sale and h:
            count = per_count * len(h)  # 可卖总数
            m = count * p  # 卖出总价
            # 一次性卖出所有的
            t_s = TransactionStock(symbol, p, t.date, t.operate, count, market)
            result.append(t_s)
            fund = fund + m
            continue
    return result


def calculate_buy_sale_report(ls: [TransactionStock], use_sand_data=True):
    """产生股票交易的报告"""
    d = _trans_to_record(ls)
    result = ''
    for k, v in d.items():
        result = result + '\n'
        result = result + _trans_to_report(v)
        result = result + '\n'
    return result


def _trans_to_record(ls: [TransactionStock]):
    """将 :py:class:TransactionStock 集合转换为 :py:class:TransactionStockRecord 集合

    Returns:
        字典对象。key值为 股票代码。value值为 :py:class:TransactionStockRecord 集合
    """

    result = {}
    for key, group in itertools.groupby(ls, key=lambda x: x.symbol):
        lst = list(group)
        # key值为symbol，lst为按symbol分组后的列表
        for l in lst:
            if key not in result.keys():
                result[key] = []
            if l.operate == Operate.Buy:
                result[key].append(Tsr(key, l.price, l.date, l.count, l.market))
                continue
            if l.operate == Operate.Sale:
                sale_count = l.count  # 可卖总数
                hold = _get_hold(result[key])
                for h in hold:
                    if 0 < h.hold <= sale_count:
                        # 当可卖数量大于等于当前交易明细的持仓数量时
                        h.sale_date = l.date
                        h.sale_price = l.price
                        h.sale_count = h.hold
                        sale_count = sale_count - h.sale_count
                    elif sale_count < h.hold:
                        break
    return result


def _trans_to_report(ls):
    """从 :py:class:TransactionStockRecord 集合产生分析报告字符串

    Args:
        ls ([TransactionStockRecord]):

    """
    hold_count = 0  # 最终持仓数量
    profit = 0  # 总利润
    fund = 0  # 资金占用
    for t in ls:
        profit = profit + t.profit
        if t.hold > 0:
            hold_count = hold_count + t.hold
            fund = fund + t.hold * t.buy_price
    result = '最终持仓数量：{0}\n'.format(hold_count)
    result = result + '总利润：{0}\n'.format(profit)
    result = result + '资金占用：{0}\n'.format(fund)
    result = result + '交易明细：\n'
    result = result + Tsr.to_str_header() + '\n'
    result = result + '\n'.join(x.__str__() for x in ls)
    return result


def _can_buy(price, count, fund):
    """根据单价，数量，当前资金 计算是否可买"""
    return price * count < fund


def _get_hold(lst):
    """获取当前交易记录中的可卖数量。
    反向查询，当遇到第一个被标记为卖出操作的数据时，返回从该值开始的所有数据

    **传入的集合中的元素类型必须包含 `.operate` 属性。类型为 `:py:class:Operate`**
    """
    index = len(lst)
    for x in reversed(lst):
        if x.operate == Operate.Sale:
            break
        index = index - 1
    return lst[index:]
