# 初始化数据

from finance_datareader_py.csindex import get_stock_holdings
from finance_datareader_py.gtimg.daily import GtimgDailyReader

from . import globalSettings

if __name__ == '__main__':
    df_hs = get_stock_holdings('000903')
    columns = ['Open', 'Close', 'High', 'Low', 'Volume']
    for symbol in df_hs['symbol']:
        df = GtimgDailyReader(symbol).read()
        df_qfq = GtimgDailyReader(symbol, type='qfq').read()[columns[:-1]]
        df_hfq = GtimgDailyReader(symbol, type='hfq').read()[columns[:-1]]
        df = df.join(df_hfq, rsuffix='_hfq')
        df = df.join(df_qfq, rsuffix='_qfq')
        df.to_csv('{0}.csv'.format(symbol), encoding=globalSettings.encoding)
