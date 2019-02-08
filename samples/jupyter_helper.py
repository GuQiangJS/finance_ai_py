# jupyter 部分帮助方法
import os

import QUANTAXIS as QA
import numpy as np
import pandas as pd
import pyfolio as pf
from QUANTAXIS.QAUtil.QADate import QA_util_datetime_to_strdate as date_to_str
from pandas import DataFrame


def _test_index(code, start='2018-01-01', end='2018-12-31'):
    """测试指数数据是否在本地能读取到
    
    Return:
        如果数据读取正常，则返回True，否则返回False
    """
    return not QA.QA_fetch_index_day_adv(code, start, end).data.empty


def get_benchmark_code():
    """获取示例时的指数（沪深300）代码，返回000300或者399300"""

    zs_code = ['399300', '000300']  # 指数代码。沪深300
    for code in zs_code:
        if _test_index(code):
            return code
    if not isinstance(zs_code, str):
        raise AssertionError


def get_start_end_date(benchmark_code: str = None):
    """根据指数代码获取开始日期和结束日期

    Args:
        benchmark_code: 指数代码。如果为空则会调用get_benchmark_code获取。

    Returns:(datetime.datetime,datetime.datetime)
    """
    if not benchmark_code:
        benchmark_code = get_benchmark_code()
    ds = QA.QA_fetch_index_day_adv(benchmark_code,
                                   QA.QAUtil.QADate_trade.trade_date_sse[0],
                                   QA.QAUtil.QADate.QA_util_today_str()).date
    return ds[0], ds[-1]


def get_year_stats(start, end, benchmark_code=None, lst=None, auto_save=True,
                   filename=None) -> pd.DataFrame:
    """
    读取指定股票的年度分析数据。如果文件不存在或有部分内容不存在，则读取部分内容。

    部分内容以单支股票为单位。加入只是有部分年份不存在，又或者上次生成文件时2018年，但现在时2020年，缺少2019年的数据时，也不会重新生成。

    Args:
        auto_save: 有新数据时是否保存
        filename: 文件名。如果为None，则为datas/stock_stas_year.h5。
        start: 开始时间
        end: 结束时间
        benchmark_code: 指数代码。如果为空则会调用get_benchmark_code获取。
        lst: 股票代码列表。为None时，自动获取所有列表。

    Returns:
    """
    if not filename:
        filename = os.path.join(os.getcwd(), 'datas', 'stock_stats_year.h5')
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    if not benchmark_code:
        benchmark_code = get_benchmark_code()

    if lst is None or len(lst) == 0:
        lst = QA.QA_fetch_stock_list_adv().code.values

    stats_by_year = pd.DataFrame()  # type: DataFrame
    if os.path.exists(filename):
        stats_by_year = pd.read_hdf(
            filename, key='year', mode='r').astype('float64')
    has_new = False
    for stock in lst:
        if stats_by_year.empty:
            stats_by_year = calc_perf_stats_by_year(
                stock, benchmark_code, start, end)
            has_new = True
        elif stock not in stats_by_year.index.unique(0).values:
            d = calc_perf_stats_by_year(stock, benchmark_code, start, end)
            if d.empty:
                continue
            stats_by_year = stats_by_year.append(d)
            has_new = True
    if has_new and auto_save:
        stats_by_year.to_hdf(filename, key='year', mode='w')
        print('{0} updated.'.format(filename))
    return stats_by_year


def calc_daily_return(s: pd.Series) -> pd.Series:
    '''计算日收益'''
    return (s / s.shift(1) - 1)[1:]


def calc_perf_stats_by_year(code: str, benchmark_code: str, start,
                            end) -> pd.DataFrame:
    """计算指定股票年度数据指标。
    计算 benchmark_code 开始年份 ~ 当前年份的前一年

    Args:
        code:
        benchmark_code:
        start:
        end:
    """
    start_str = start if isinstance(start, str) else date_to_str(start)
    end_str = end if isinstance(end, str) else date_to_str(end)
    zs_data = QA.QA_fetch_index_day_adv(benchmark_code, start_str,
                                        end_str)  # 指数日线数据

    result = pd.DataFrame()

    stock_data_bfq = QA.QA_fetch_stock_day_adv(code, start_str,
                                               end_str)  # 不复权的日线数据
    if stock_data_bfq is None or stock_data_bfq.data.empty:
        return result

    stock_data_qfq = stock_data_bfq.to_qfq()  # 前复权日线数据
    for year in range(start.year, end.year):
        s = pd.Series()
        zs_daily_return = calc_daily_return(
            zs_data.data[zs_data.date.year == year]['close'])  # 指数日收益
        stock_daily_return_qfq = calc_daily_return(
            stock_data_qfq[stock_data_qfq.date.year == year]['close'])  # 股票日收益

        if not stock_daily_return_qfq.empty:
            stock_daily_return_qfq_remove_code = stock_daily_return_qfq.reset_index(
            ).drop(columns=['code']).set_index('date')
            zs_daily_return_remove_code = zs_daily_return.reset_index().drop(
                columns=['code']).set_index('date')

            stock_daily_return_qfq_remove_code_year = \
                stock_daily_return_qfq_remove_code[
                    stock_daily_return_qfq_remove_code.index.year == year]  # 当年股票日收益（前复权）
            zs_daily_return_remove_code_year = zs_daily_return_remove_code[
                zs_daily_return_remove_code.index.year == year]
            s = pf.timeseries.perf_stats(
                stock_daily_return_qfq_remove_code_year.close,
                zs_daily_return_remove_code_year.close)
        else:
            s = pf.timeseries.perf_stats(stock_daily_return_qfq,
                                         zs_daily_return)

        if not s.empty:
            s['code'] = code
            s['year'] = year
            if result.empty:
                result = s.to_frame().T.set_index(['code', 'year'])
            else:
                result = result.append(s.to_frame().T.set_index(
                    ['code', 'year']))
    return result.astype(np.float64)
