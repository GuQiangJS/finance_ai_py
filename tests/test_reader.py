# Copyright (C) 2018 GuQiangJs.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

import unittest

from src import reader


class MyTestCase(unittest.TestCase):
    @staticmethod
    def test_get_symbol_data():
        reader.get_symbol_data('000002')

    def test_get_symbol_data_raise_error(self):
        # 不从沙箱内读取数据时抛出异常
        self.assertRaises(NotImplementedError,
                          reader.get_symbol_data,
                          '000002',
                          False)
        # 股票代码不存在时抛出异常
        self.assertRaises(ValueError, reader.get_symbol_data, '')


if __name__ == '__main__':
    unittest.main()
