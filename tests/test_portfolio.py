import unittest
import model.portfolio as pftools


class TestPortfolio(unittest.TestCase):

    def test_operation_addition(self):
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
                                        pftools.PE500,
                                        date=dt.fromisoformat('2022-04-22'),
                                        quantity=8,
                                        stock_price=24.69,
                                        gross_amount=8*24.69+0.85,
                                        net_amount=8*24.69,
                                        )
        pf = pftools.Portfolio().from_operations_list([operation_1, operation_2])

if __name__ == '__main__':
    unittest.main()