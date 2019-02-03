# Copyright (C) 2018 GuQiangJs.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

# 计算器
from datetime import date
import pandas as pd
from QUANTAXIS.QAUtil.QADate import QA_util_datetime_to_strdate as date_to_str
from QUANTAXIS import QA_fetch_index_day_adv
from QUANTAXIS import QA_fetch_stock_day_adv
import pyfolio as pf
import numpy as np

def calc_daily_return(s: pd.Series):
    return (s / s.shift(1) - 1)[1:]


def calc_perf_stats_by_year(code: str, benchmark_code: str, start,
                            end) -> [pd.DataFrame]:
    """计算指定股票年度数据指标。
    计算 benchmark_code 开始年份 ~ 当前年份的前一年

    返回：[结果]
    """
    start_str = start if isinstance(start,str) else date_to_str(start)
    end_str = end if isinstance(end,str) else  date_to_str(end)
    zs_data = QA_fetch_index_day_adv(benchmark_code, start_str,
                                     end_str)  # 指数日线数据

    result = pd.DataFrame()

    stock_data_bfq = QA_fetch_stock_day_adv(code, start_str,
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
            stock_daily_return_qfq_remove_code = stock_daily_return_qfq.reset_index().drop(
                columns=['code']).set_index('date')
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
                result = result.append(
                    s.to_frame().T.set_index(['code', 'year']))
    return result.astype(np.float64)
