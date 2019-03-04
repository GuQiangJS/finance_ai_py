import QUANTAXIS as QA
import pandas as pd
import numpy as np

STOCK_CODE='601398'
BENCHMARK_CODE='399300'

START_TIME='2005-01-01'
END_TIME='2018-12-31'

def get_raw_data(stock_code=STOCK_CODE,start_time=START_TIME,end_time=END_TIME)->pd.DataFrame:
    """

    Examples:
    ```
        	        code	open	high	low	close	volume	amount	preclose	adj
        date									
        2006-10-27	601398	1.992133	2.01557	1.910104	1.921823	4.407654e+07	8.725310e+09	NaN	0.585922
    ```
    """
    return QA.QA_fetch_stock_day_adv(stock_code, start_time, end_time).to_qfq().data.reset_index().set_index('date')

def get_benchmark_raw_data(code=BENCHMARK_CODE,start_time=START_TIME,end_time=END_TIME,columns=['open','high','low','close','volume'])->pd.DataFrame:
    return QA.QA_fetch_index_day_adv(code, start_time, end_time).data.reset_index().set_index('date')[columns]

def augFeatures(data:pd.DataFrame)->pd.DataFrame:
    df=data.copy()
    df["year"] = df.index.year
    df["month"] = df.index.month
    df["date"] = df.index.day
    df["day"] = df.index.dayofweek
    return df

def normalize(df):
    """正则化"""
    return df.apply(lambda x: (x - np.mean(x)) / (np.max(x) - np.min(x)))

def buildData(df,pastDays=30,futureDays=5,skipDays=0)->([pd.DataFrame],[pd.Series]):
    """取 `pastDays` 的数据作为计算数据，取 `futureDays` 的 `close` %save据作为测算数据。
    返回的X集合中包含类型为 `DataFrame` ，Y集合中包含为 `Series`。"""
    X,Y=[],[]
    for i in range(df.shape[0]-pastDays-futureDays):
        X.append(df.iloc[i:i+pastDays])
        Y.append(df.iloc[i+pastDays+skipDays:i+pastDays+futureDays+skipDays]['close'])
    return X,Y


def toNpArray(d:[pd.DataFrame])->np.array:
    return np.array([np.array(x.values) for x in d])