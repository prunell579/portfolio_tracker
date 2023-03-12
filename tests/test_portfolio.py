import unittest
import model.portfolio as pftools


class TestPortfolio(unittest.TestCase):

    def setUp(self):
        from datetime import datetime as dt
        self.operation_1 = pftools.Operation(
                                        pftools.PE500,
                                        date=dt.fromisoformat('2022-03-27'),
                                        quantity=12,
                                        stock_price=37.66,
                                        gross_amount=12*37.66+1.2,
                                        net_amount=12*37.66,
                                        )
        self.operation_2 = pftools.Operation(
                                        pftools.PCEU,
                                        date=dt.fromisoformat('2022-04-22'),
                                        quantity=8,
                                        stock_price=24.69,
                                        gross_amount=8*24.69+0.85,
                                        net_amount=8*24.69,
                                        )

    def tearDown(self):
        self.operation_1 = None
        self.operation_2 = None

    def test_tickers_are_added(self):
        small_pf =  pftools.Portfolio.from_operations_list([self.operation_1, self.operation_2])
        tickers_in_pf = small_pf.get_portfolio_tickers()
        self.assertEqual(len(tickers_in_pf), 2)
        self.assertIn(pftools.PE500, tickers_in_pf)
        self.assertIn(pftools.PCEU, tickers_in_pf)

        self.assertEqual(small_pf.get_stock_by_ticker(pftools.PCEU).get_quantity(), 8)
        self.assertEqual(small_pf.get_stock_by_ticker(pftools.PE500).get_quantity(), 12)

    def test_portfolio_is_updated_when_adding_operations(self):
        small_pf =  pftools.Portfolio.from_operations_list([self.operation_1, self.operation_2])
        self.assertEqual(small_pf.get_gross_contributions(), 651.49)
        self.assertEqual(small_pf.get_net_contributions(), 649.44)

if __name__ == '__main__':
    unittest.main()