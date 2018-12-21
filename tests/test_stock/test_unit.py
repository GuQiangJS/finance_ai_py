# Copyright (C) 2018 GuQiangJs.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

import unittest
from datetime import datetime as dt
from datetime import timedelta as td

from src import Operate
from src.stock import TransactionStock as Ts
from src.stock import unit
from src.stock.simulations import BBands


class MyTestCase(unittest.TestCase):
    def test_calculate_buy_sale_record(self):
        t, df = BBands.get_buy_sale_point('000002')
        tr = unit.calculate_buy_sale('000002', t)
        self.assertEqual(18, len(tr))
        self.assertEqual(14, len([x for x in tr if x.operate == Operate.Buy]))
        self.assertEqual(4, len([x for x in tr if x.operate == Operate.Sale]))
        print('\n'.join(x.__str__() for x in tr))

    @staticmethod
    def test_calculate_buy_sale_report():
        t, df = BBands.get_buy_sale_point('000002')
        tr = unit.calculate_buy_sale('000002', t)
        print(unit.calculate_buy_sale_report(tr))

    def test_can_buy(self):
        self.assertTrue(unit._can_buy(1, 100, 101))
        self.assertFalse(unit._can_buy(1, 100, 100))
        self.assertFalse(unit._can_buy(1, 100, 99))

    def test_get_hold(self):
        lst = []
        d = dt.today()
        lst.append(Ts('', 1, date=d + td(days=1), operate=Operate.Buy))
        lst.append(Ts('', 1, date=d + td(days=2), operate=Operate.Buy))
        self.assertEqual(2, len(unit._get_hold(lst)))
        lst.insert(0, Ts('', 1, date=d, operate=Operate.Sale))
        self.assertEqual(2, len(unit._get_hold(lst)))
        lst.append(Ts('', 1, date=d + td(days=3), operate=Operate.Buy))
        self.assertEqual(3, len(unit._get_hold(lst)))
        lst.append(Ts('', 1, date=d + td(days=4), operate=Operate.Sale))
        lst.append(Ts('', 1, date=d + td(days=5), operate=Operate.Buy))
        self.assertEqual(1, len(unit._get_hold(lst)))
        lst.append(Ts('', 1, date=d + td(days=6), operate=Operate.Sale))
        self.assertEqual(0, len(unit._get_hold(lst)))


if __name__ == '__main__':
    unittest.main()
