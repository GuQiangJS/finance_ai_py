# Copyright (C) 2018 GuQiangJs.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

import unittest

from src.simulations import BBands


class MyTestCase(unittest.TestCase):
    def test_get_buy_sale_point(self):
        df = BBands.get_buy_sale_point('000002')
        self.assertFalse(df.empty)
        self.assertTrue('Close' in df.columns)
        self.assertTrue('opt' in df.columns)
        self.assertEqual(2, len(df.columns))

        print(df)

    def test_plot_line(self):
        BBands.plot_line('000002', s=400, e=800)


if __name__ == '__main__':
    unittest.main()
