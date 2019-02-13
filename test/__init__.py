# Copyright (C) 2018 GuQiangJs.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

import unittest

import QUANTAXIS as QA


class TestBase(unittest.TestCase):

    def _test_index(self, code, start='2018-01-01', end='2018-12-31'):
        """测试指数数据是否在本地能读取到

        Return:
            如果数据读取正常，则返回True，否则返回False
        """
        return not QA.QA_fetch_index_day_adv(code, start, end).data.empty

    def get_benchmark_code(self):
        """获取示例时的指数（沪深300）代码，返回000300或者399300"""

        zs_code = ['399300', '000300']  # 指数代码。沪深300
        for code in zs_code:
            if self._test_index(code):
                return code
        if not isinstance(zs_code, str):
            raise AssertionError

    def get_start_end_date(self, benchmark_code: str = None):
        """根据指数代码获取开始日期和结束日期

        Args:
            benchmark_code: 指数代码。如果为空则会调用get_benchmark_code获取。

        Returns:(datetime.datetime,datetime.datetime)
        """
        if not benchmark_code:
            benchmark_code = self.get_benchmark_code()
        ds = QA.QA_fetch_index_day_adv(benchmark_code,
                                       QA.QAUtil.QADate_trade.trade_date_sse[0],
                                       QA.QAUtil.QADate.QA_util_today_str()).date
        return ds[0], ds[-1]
