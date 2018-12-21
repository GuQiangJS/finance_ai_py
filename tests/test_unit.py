# Copyright (C) 2018 GuQiangJs.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

import os
import unittest

from src import unit


class MyTestCase(unittest.TestCase):
    def test_get_his_data_path_in_SandBox(self):
        """测试从沙盒中读取每日成交汇总数据"""
        current_path = os.path.dirname(__file__)  # tests 目录
        p_path = os.path.dirname(current_path)
        p = os.path.join(p_path, 'sandbox', 'CHN', 'stocks', 'datas', 'his',
                         '123.csv')
        self.assertEqual(p, unit.get_his_data_path('123'))

    def test_get_his_data_path_raise_error(self):
        """不从沙箱内读取数据会抛出异常"""
        self.assertRaises(NotImplementedError, unit.get_his_data_path
                          , '', False)


if __name__ == '__main__':
    unittest.main()
