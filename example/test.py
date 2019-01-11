# Copyright 2019 The GuQiangJS. All Rights Reserved.
# ==============================================================================

import units
import settings
import QUANTAXIS as QA
import quantaxis_ext
import pandas as pd
import calculator as calc


start_date = '2018-01-01' # 初始投资日期
end_date = '2018-12-31' # 结束投资日期
df=quantaxis_ext.fetch_index_stock_daily_adv(['600519','601318','600036','000651'],'000300',start_date,end_date)
print(df)

print((df / df.shift(1) - 1).dropna())