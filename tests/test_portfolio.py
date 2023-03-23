import unittest
import model.portfolio as pftools


class TestPortfolio(unittest.TestCase):

    def setUp(self):
        from datetime import datetime as dt
        operation_1 = pftools.Operation(
                                        pftools.PE500,
                                        date=dt.fromisoformat('2022-03-27'),
                                        quantity=12,
                                        stock_price=37.66,
                                        gross_amount=12*37.66+1.2,
                                        net_amount=12*37.66,
                                        )
        operation_2 = pftools.Operation(
                                        pftools.PCEU,
                                        date=dt.fromisoformat('2022-04-22'),
                                        quantity=8,
                                        stock_price=24.69,
                                        gross_amount=8*24.69+0.85,
                                        net_amount=8*24.69,
                                        )
        self.small_pf =  pftools.Portfolio.from_operations_list([operation_1, operation_2])

    def tearDown(self):
        self.small_pf = None

    def test_tickers_are_added(self):
        tickers_in_pf = self.small_pf.get_portfolio_tickers()
        self.assertEqual(len(tickers_in_pf), 2)
        self.assertIn(pftools.PE500, tickers_in_pf)
        self.assertIn(pftools.PCEU, tickers_in_pf)

        self.assertEqual(self.small_pf.get_stock_by_ticker(pftools.PCEU).get_quantity(), 8)
        self.assertEqual(self.small_pf.get_stock_by_ticker(pftools.PE500).get_quantity(), 12)

    def test_portfolio_is_updated_when_adding_operations(self):
        self.assertEqual(self.small_pf.get_gross_contributions(), 651.49)
        self.assertEqual(self.small_pf.get_net_contributions(), 649.44)

    def test_portfolio_value_setter(self):
        self.small_pf.get_stock_by_ticker(pftools.PE500).set_price(38.53)
        self.small_pf.get_stock_by_ticker(pftools.PCEU).set_price(24.12)

        self.assertEqual(self.small_pf.get_value(), 655.32)

    def test_portfolio_performance(self):
        self.small_pf.get_stock_by_ticker(pftools.PE500).set_price(38.53)
        self.small_pf.get_stock_by_ticker(pftools.PCEU).set_price(24.12)

        self.assertEqual(self.small_pf.get_net_performance(), round(0.9053, 2))

    def test_fortuneo_parser(self):
        operations = pftools.FortuneoInterface.extract_operations_from_csv('./model/small_sample_fortuneo.csv')

        self.assertEqual(len(operations), 11)

        pf = pftools.Portfolio.from_operations_list(operations)

        tickers_in_pf = pf.get_portfolio_tickers()

        self.assertEqual(len(tickers_in_pf), 3)

        self.assertIn(pftools.PE500, tickers_in_pf)
        self.assertIn(pftools.PCEU, tickers_in_pf)
        self.assertIn(pftools.PAEEM, tickers_in_pf)

        self.assertEqual(pf.get_stock_by_ticker(pftools.PE500).get_quantity(), 63)
        self.assertEqual(pf.get_stock_by_ticker(pftools.PAEEM).get_quantity(), 28)
        self.assertEqual(pf.get_stock_by_ticker(pftools.PCEU).get_quantity(), 13)

        self.assertEqual(pf.get_net_contributions(), 2875.24)
        self.assertEqual(pf.get_gross_contributions(), 2888.2)

if __name__ == '__main__':
    unittest.main()