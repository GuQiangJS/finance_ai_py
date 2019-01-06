# Copyright 2019 The GuQiangJS. All Rights Reserved.
# ==============================================================================

import units
import settings
import QUANTAXIS as QA

code_list = QA.QA_fetch_stock_list_adv()

df=units.get_daily_return(code_list['code'][0:10].values,'000010',settings.stock_daily_start,settings.stock_daily_end)
pass