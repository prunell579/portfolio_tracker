from datetime import datetime as dt
from pprint import pprint
import abc

PE500_LONG_FORMAT = 'AMUNDI ETF PEA S&P 500 UCITS ETF - EUR'
PCEU_LONG_FORMAT = 'AMUNDI ETF PEA MSCI EUROPE UCITS ETF - EUR'
PAEEM_LONG_FORMAT = 'AMUNDI ETF PEA MSCI EMERGING MARKETS UCITS ETF - EUR'

PE500 = 'PE500'
PCEU = 'PCEU'
PAEEM = 'PAEEM'


class Operation(object):

    def __init__(self, ticker_id: str, date: dt.date, quantity: int, stock_price: float, gross_amount: float,
                 net_amount: float):
        self.ticker_id = ticker_id
        self.date = date
        self.quantity = quantity
        self.stock_price = stock_price
        self.gross_amount = gross_amount
        self.net_amount = net_amount


class FortuneoInterface(object):

    TICKER_COLUMN = 0
    DATE_COLUMN = 3
    QTY_COLUMN = 4
    STOCKPRICE_COLUMN = 5
    GROSSAMOUNT_COLUMN = 6
    NETAMOUNT_COLUMN = 8

    def extract_operations_from_csv(self, filepath: str):
        import csv
        operations = []
        with open(filepath) as f:
            reader = csv.reader(f, delimiter=';')
            next(reader)
            for row in reader:
                ticker_id = self._get_id_from_long_ftn_format(row[self.TICKER_COLUMN])
                date = dt.strptime(row[self.DATE_COLUMN], "%d/%m/%Y")
                operation = Operation(
                                        ticker_id,
                                        date,
                                        int(float(row[self.QTY_COLUMN])),
                                        float(row[self.STOCKPRICE_COLUMN]),
                                        abs(float(row[self.GROSSAMOUNT_COLUMN])),
                                        abs(float(row[self.NETAMOUNT_COLUMN])),
                                      )

                operations.append(operation)

        return operations


    def _get_id_from_long_ftn_format(self, id_long_format: str):
        if id_long_format == PE500_LONG_FORMAT:
            return PE500
        if id_long_format == PCEU_LONG_FORMAT:
            return PCEU
        if id_long_format == PAEEM_LONG_FORMAT:
            return PAEEM
        raise ValueError('Ticker {} not supported'.format(id_long_format))



class Portfolio(object):

    def __init__(self, value=0, composition=None, net_contribution=0, gross_contribution=0, performance=0, history=None) -> None:
        self._value = value
        self._performance = performance

        self._composition = []
        self._net_contributions = net_contribution
        self._gross_contributions = gross_contribution
        self._operations = []
        self._history = history

    # Defined as an inner class since it only makes sense in the context of a Portfolio
    class StockInPortfolio(object):
        def __init__(self, name):
            self.name = name
            self.value = 0
            self.quantity = 0

        def increase_quantity(self, quantity_increase):
            self.quantity += quantity_increase

        def get_quantity(self):
            return self.quantity

    @classmethod
    def from_operations_list(cls, operations):
        pf = cls()

        for operation in operations:
            pf.add_operation(operation)

        return pf

    def add_operation(self, operation: Operation):
        self._operations.append(operation)

        # update portfolio properties
        self._net_contributions += operation.net_amount
        self._gross_contributions += operation.gross_amount
        self._net_contributions = round(self._net_contributions, 2)
        self._gross_contributions = round(self._gross_contributions, 2)
        self._update_composition(operation)

        return
        self._performance = (self.value - self._net_contributions) / self._net_contributions
        self._update_history(operation)

    def _update_composition(self, operation: Operation):
        if operation.ticker_id in self.get_portfolio_tickers():
            stock = self.get_stock_by_ticker(operation.ticker_id)
            stock.increase_quantity(operation.quantity)
            # print('putting {} stocks in {}'.format(operation.quantity, operation.ticker_id))
        else:
            self._composition.append(self.StockInPortfolio(name=operation.ticker_id))
            self._update_composition(operation)

    def get_stock_by_ticker(self, ticker_id:str) -> StockInPortfolio: 
        for stock in self._composition:
            if stock.name == ticker_id:
                return stock
            
    def get_portfolio_tickers(self):
        tickers = []
        if self._composition:
            for stock in self._composition:
                tickers.append(stock.name)
        return tickers

    def _update_history(self, operation: Operation):
        return
        if operation.date in self._history.keys():
            portfolio_in_history = self._history[operation.date]
            if portfolio_in_history._get_total_quantity_of_shares() <= self._get_total_quantity_of_shares():
                self._history[operation.date] = self
        else:
            self._history[operation.date] = self

    def get_portfolio_ticker_names(self):
        names  = []
        for ticker in self._composition:
            names.append(ticker.name)

        return names

    def _get_total_quantity_of_shares(self):
        return
        total_quantity_of_shares = 0
        for ticker_quantity in self._composition.values():
            total_quantity_of_shares += ticker_quantity
        return total_quantity_of_shares

    def get_net_contributions(self):
        return self._net_contributions

    def get_gross_contributions(self):
        return self._gross_contributions



class BuyEstimatorHelper(object):

    @staticmethod
    def simulate_buy(current_pf: Portfolio, buy_list) -> Portfolio:
        """
        buy list can be a list of tuples: [(ticker_name, quantity, current_price)]
        the current_price_element might not be necessary with the yahoo api
        """
        for ticker_name, quantity, current_price in buy_list:
            date = dt.now()
            net_amount = quantity * current_price
            gross_amount = net_amount

            current_pf.add_operation(Operation(ticker_name, date, quantity, current_price, gross_amount, net_amount))

        return current_pf



if __name__ == '__main__':
    from datetime import datetime as dt
    operation_1 = Operation(
                            PE500,
                            date=dt.fromisoformat('2022-03-27'),
                            quantity=12,
                            stock_price=37.66,
                            gross_amount=12*37.66+1.2,
                            net_amount=12*37.66,
                            )
    operation_2 = Operation(
                            PCEU,
                            date=dt.fromisoformat('2022-04-22'),
                            quantity=8,
                            stock_price=24.69,
                            gross_amount=8*24.69+0.85,
                            net_amount=8*24.69,
                            )
    small_pf =  Portfolio.from_operations_list([operation_1, operation_2])

    print(small_pf.get_stock_by_ticker(PE500).get_quantity())

    small_pf =  Portfolio()

    print(small_pf.get_stock_by_ticker(PE500).get_quantity())



