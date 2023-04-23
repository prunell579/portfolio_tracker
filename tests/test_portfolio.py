import unittest
import sys
sys.path.append('.')
import model.portfolio as pftools


class TestPortfolio(unittest.TestCase):

    def setUp(self):
        from datetime import datetime as dt
        import copy
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


        self.small_pf_with_prices = copy.deepcopy(self.small_pf)
        self.small_pf_with_prices.get_stock_by_ticker(pftools.PE500).set_price(38.53)
        self.small_pf_with_prices.get_stock_by_ticker(pftools.PCEU).set_price(24.12)


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
        """
        Given a portfolio with the following composition
        TICKER  QTY P/STOCK
        PE500   12  38.53
        PCEU    8   24.12

        The TOTAL value of the portfolio must be: 655.32
        the value of PE500 must be: 462.36
        the value of PCEU must be: 192.96
        """
        self.small_pf.get_stock_by_ticker(pftools.PE500).set_price(38.53)
        self.small_pf.get_stock_by_ticker(pftools.PCEU).set_price(24.12)

        self.assertEqual(self.small_pf.get_value(), 655.32)
        self.assertEqual(self.small_pf.get_stock_by_ticker(pftools.PE500).get_value(), 462.36)
        self.assertEqual(self.small_pf.get_stock_by_ticker(pftools.PCEU).get_value(), 192.96)

    def test_portfolio_values_setter(self):
        """
        Given a portfolio with the following composition
        TICKER  QTY P/STOCK
        PE500   12  38.53
        PCEU    8   24.12

        The TOTAL value of the portfolio must be: 655.32
        the value of PE500 must be: 462.36
        the value of PCEU must be: 192.96
        """
        prices = {
                    pftools.PE500: 38.53,
                    pftools.PCEU: 24.12
                 }
        self.small_pf.set_stock_prices(prices)

        self.assertEqual(self.small_pf.get_stock_by_ticker(pftools.PE500).get_value(), 462.36)
        self.assertEqual(self.small_pf.get_stock_by_ticker(pftools.PCEU).get_value(), 192.96)


    def test_portfolio_performance(self):
        self.small_pf.get_stock_by_ticker(pftools.PE500).set_price(38.53)
        self.small_pf.get_stock_by_ticker(pftools.PCEU).set_price(24.12)

        self.assertEqual(self.small_pf.get_net_performance(), round(0.9053, 2))

    def test_stock_weights(self):
        """
        Given a portfolio of the following composition:
        TICKER  QTY VALUE
        PE500   12  462.36
        PCEU    8   192.96

        TOTAL VALUE = 655.32

        THEN the weight of each stock must be:
        PE500   70.55
        PCEU    29.45
        """

        self.assertEqual(self.small_pf_with_prices.get_stock_weight(pftools.PE500), 70.55)
        self.assertEqual(self.small_pf_with_prices.get_stock_weight(pftools.PCEU), 29.45)

    def test_portfolio_summary(self):
        """
        Given a portfolio of the following composition:
        TICKER  QTY VALUE
        PE500   12  462.36
        PCEU    8   192.96

        TOTAL VALUE = 655.32

        THEN the weight of each stock must be:
        PE500   70.55
        PCEU    29.45
        """

        expected_dict = {
                            pftools.PE500: {
                                            'value': 462.36,
                                            'quantity': 12,
                                            'weight': 70.55
                                            },
                            pftools.PCEU: {
                                            'value': 192.96,
                                            'quantity': 8,
                                            'weight': 29.45
                                            },
                            'total_value': 655.32
                        }
        
        self.assertDictEqual(self.small_pf_with_prices.get_portfolio_summary(), expected_dict)


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

    def test_stock_close_price(self):
        import datetime as dt
        close_price = pftools.YFInterface.stock_close_price(pftools.PAEEM, dt.datetime.fromisoformat('2023-03-20'))
        self.assertAlmostEqual(close_price, 19.79, places=2)

    def test_buy_estimator(self):
        print(self.small_pf_with_prices.get_portfolio_summary())

        buy_list = [(pftools.PE500, 2), (pftools.PCEU, 4)]

        current_prices = {pftools.PE500: 42.35, pftools.PCEU: 23.89}

        simulated_pf = pftools.BuyEstimatorHelper.simulate_buy(self.small_pf_with_prices, buy_list, current_prices=current_prices)

        expected_dict = {
                            pftools.PE500: {
                                            'value': 592.9,
                                            'quantity': 14,
                                            'weight': 67.41
                                            },
                            pftools.PCEU: {
                                            'value': 286.68,
                                            'quantity': 12,
                                            'weight': 32.59
                                            },
                            'total_value': 879.58
                        }


        self.assertDictEqual(simulated_pf.get_portfolio_summary(), expected_dict)
        
if __name__ == '__main__':
    unittest.main()