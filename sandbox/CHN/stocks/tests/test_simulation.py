import unittest

from ..simulation import BBands
from ..simulation import simulate_buy_sale

class MyTestCase(unittest.TestCase):
    def test_BBands(self):
        df = BBands('000002')
        print(df)
        record=simulate_buy_sale(df)
        print(record)


if __name__ == '__main__':
    unittest.main()
