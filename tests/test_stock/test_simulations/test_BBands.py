# Copyright (C) 2018 GuQiangJs.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

import unittest

from src.stock.simulations import BBands


class MyTestCase(unittest.TestCase):
    def test_get_buy_sale_point(self):
        lst, df = BBands.get_buy_sale_point('000002')
        self.assertFalse(df.empty)
        self.assertTrue('Close' in df.columns)
        self.assertTrue('opt' in df.columns)
        self.assertEqual(2, len(df.columns))
        self.assertEqual(len(df.index), len(lst))
        for i in range(len(lst)):
            self.assertEqual(lst[i].date, df.index[i])
            self.assertEqual(lst[i].operate, df.iloc[i]['opt'])
        print('\n'.join(x.__str__() for x in lst))
        print(df.head())
        print(df.tail())

    @staticmethod
    def test_plot_line():
        BBands.plot_line('000002', s=600, e=700)


if __name__ == '__main__':
    unittest.main()
