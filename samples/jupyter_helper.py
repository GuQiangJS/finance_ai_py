# jupyter 部分帮助方法
import os

import QUANTAXIS as QA
import numpy as np
import pandas as pd
import pyfolio as pf
from QUANTAXIS.QAUtil.QADate import QA_util_datetime_to_strdate as date_to_str
from pandas import DataFrame
from pyecharts import Line


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


def normalize_data(df):
    """数据归一化"""
    return df / df.iloc[0]


def get_qfq_stock_close(code, start, end):
    """读取指定股票的收盘价日线数据"""
    start_str = start if isinstance(start, str) else date_to_str(start)
    end_str = end if isinstance(end, str) else date_to_str(end)

    return QA.QA_fetch_stock_day_adv(code, start_str,
                                     end_str).to_qfq().reset_index().drop(
        columns=['code']).set_index('date').close


def get_qfq_index_close(start, end) -> pd.DataFrame:
    """读取指数的日线收盘价数据"""
    start_str = start if isinstance(start, str) else date_to_str(start)
    end_str = end if isinstance(end, str) else date_to_str(end)
    code = get_benchmark_code()

    return pd.DataFrame.from_dict(
        {code: QA.QA_fetch_index_day_adv(code, start_str,
                                         end_str).reset_index().drop(
            columns=['code']).set_index('date').close})


def plot_line_daily_close(title, codes, start, end,
                          benchmark_code=get_benchmark_code(), legend_top='15%',
                          datazoom_extra_type='both',
                          is_datazoom_extra_show=True,
                          datazoom_extra_orient='horizontal',
                          **kwargs):
    """使用 `pyechart` 绘制Line。使用 **收盘价格** 经过 **归一化** 后绘制。
    绘制图片时横坐标可以缩放。

    使用 `legend_top` 控制图例的位置。使其不会与标题重叠。

    Args:
        datazoom_extra_type: 参见 `line.add` 方法的同名参数
        is_datazoom_extra_show: 参见 `line.add` 方法的同名参数
        datazoom_extra_orient: 参见 `line.add` 方法的同名参数
        legend_top: 参见 `line.add` 方法的同名参数
        datazon
        title: 主标题
        codes: 待绘制的股票代码
        start: 开始日期
        end: 结束日期
        benchmark_code: 指数代码
        **kwargs: 参考 `Line` 中的参数

    Returns:(pyecharts.Line,pd.DataFrame)
    """
    line = Line(title, **kwargs)
    # 读取收盘价
    df = get_qfq_index_close(start, end)
    for code in codes:
        df = df.join(pd.DataFrame.from_dict(
            {code: get_qfq_stock_close(code, start, end)}))  # 取复权收盘价
    df = normalize_data(df.fillna(method='ffill'))  # 归一化，并且填充nan值
    line.add(benchmark_code, df.index.date, np.round(df[benchmark_code], 2))
    for code in codes:
        line.add(code, df.index.date, np.round(df[code], 2),
                 datazoom_extra_type=datazoom_extra_type, legend_top=legend_top,
                 is_datazoom_extra_show=is_datazoom_extra_show,
                 datazoom_extra_orient=datazoom_extra_orient)
    return line,df