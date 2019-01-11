# Copyright 2019 The GuQiangJS. All Rights Reserved.
# ==============================================================================

import units
import settings
import QUANTAXIS as QA
import quantaxis_ext
import pandas as pd
import calculator as calc

#上证所有股票的列表
stock_list=quantaxis_ext.fetch_stock_list()
stock_list=stock_list[stock_list['sse']=='sh']

s='1991-01-01'
e='2018-12-31'
zs_code='000001'
year='2018'
calc.calc_sharp_radio(stock_list['code'],zs_code,'{0}-01-01'.format(year),'{0}-12-31'.format(year))