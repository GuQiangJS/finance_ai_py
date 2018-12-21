# Copyright (C) 2018 GuQiangJs.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

# 初始化沙盒数据
# 初始数据从 2004-10-08 ~ 2018-12-18

from datetime import date

from finance_datareader_py.csindex import get_stock_holdings
from finance_datareader_py.gtimg.daily import GtimgDailyReader

from src import settings
from src import unit

if __name__ == '__main__':
    df_hs = get_stock_holdings('000903')  # 中证100指数(000903)
    columns = ['Open', 'Close', 'High', 'Low', 'Volume']
    for symbol in df_hs['symbol']:
        df = GtimgDailyReader(symbol, end=date(2018, 12, 18)).read()
        df_qfq = GtimgDailyReader(symbol, type='qfq').read()[columns[:-1]]
        df_hfq = GtimgDailyReader(symbol, type='hfq').read()[columns[:-1]]
        df = df.join(df_hfq, rsuffix='_hfq')
        df = df.join(df_qfq, rsuffix='_qfq')
        df.to_csv(unit.get_his_data_path(symbol),
                  encoding=settings.Default.encoding())
