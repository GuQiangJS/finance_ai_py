# Copyright 2019 The GuQiangJS. All Rights Reserved.
# ==============================================================================

import units
import settings
import QUANTAXIS as QA

df=units.fetch_stock_day_adv('000002','2018-01-01','2018-12-31')
l=units.calc_bbands_cross(df['close'],0,timeperiod=30)
print(l)
pass