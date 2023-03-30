import datetime as dt
import yfinance as yf

PE500_LONG_FORMAT = 'AMUNDI ETF PEA S&P 500 UCITS ETF - EUR'
PCEU_LONG_FORMAT = 'AMUNDI ETF PEA MSCI EUROPE UCITS ETF - EUR'
PAEEM_LONG_FORMAT = 'AMUNDI ETF PEA MSCI EMERGING MARKETS UCITS ETF - EUR'

PE500 = 'PE500'
PCEU = 'PCEU'
PAEEM = 'PAEEM'


class Operation(object):

    def __init__(self, ticker_id: str, date: dt.datetime.date, quantity: int, stock_price: float, gross_amount: float,
                 net_amount: float):
        self.ticker_id = ticker_id
        self.date = date
        self.quantity = quantity
        self.stock_price = stock_price
        self.gross_amount = gross_amount
        self.net_amount = net_amount


class FortuneoInterface(object):

    @staticmethod
    def get_id_from_long_ftn_format(id_long_format: str):
        if id_long_format == PE500_LONG_FORMAT:
            return PE500
        if id_long_format == PCEU_LONG_FORMAT:
            return PCEU
        if id_long_format == PAEEM_LONG_FORMAT:
            return PAEEM
        raise ValueError('Ticker {} not supported'.format(id_long_format))

    @staticmethod
    def extract_operations_from_csv(filepath: str):
        TICKER_COLUMN = 0
        DATE_COLUMN = 3
        QTY_COLUMN = 4
        STOCKPRICE_COLUMN = 5
        # on client side, net and gross are inversed
        NETAMOUNT_COLUMN = 8
        GROSSAMOUNT_COLUMN = 6
        import csv
        operations = []
        with open(filepath, encoding='ISO-8859-1') as f:
            reader = csv.reader(f, delimiter=';')
            next(reader)
            for row in reader:
                ticker_id = FortuneoInterface.get_id_from_long_ftn_format(row[TICKER_COLUMN])
                date = dt.datetime.strptime(row[DATE_COLUMN], "%d/%m/%Y")
                operation = Operation(
                                        ticker_id,
                                        date,
                                        int(float(row[QTY_COLUMN])),
                                        float(row[STOCKPRICE_COLUMN]),
                                        abs(float(row[NETAMOUNT_COLUMN])),
                                        abs(float(row[GROSSAMOUNT_COLUMN])),
                                      )

                operations.append(operation)

        return operations


class Portfolio(object):

    @staticmethod
    def _get_performance(investment, current_value, round_result=True):
        performance = 1e2*(current_value - investment) / investment
        if round_result:
            return round(performance, 2)
        else:
            return performance

    def __init__(self) -> None:

        self._composition = []
        self._net_contributions = 0
        self._gross_contributions = 0
        self._operations = []


    # Defined as an inner class since it only makes sense in the context of a Portfolio
    class StockInPortfolio(object):
        def __init__(self, name):
            self.name = name
            self.value = 0
            self._price = 0
            self.quantity = 0

        def increase_quantity(self, quantity_increase):
            self.quantity += quantity_increase

        def get_quantity(self):
            return self.quantity
        
        def set_price(self, price):
            self._price = price

        def get_value(self):
            return self._price * self.quantity

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
        else:
            self._composition.append(self.StockInPortfolio(name=operation.ticker_id))
            self._update_composition(operation)

    def get_stock_by_ticker(self, ticker_id:str) -> StockInPortfolio: 
        for stock in self._composition:
            if stock.name == ticker_id:
                return stock
        raise KeyError('The stock of ticker {} does not exist in portfolio'.format(ticker_id))

    def get_stock_weight(self, ticker_id: str) -> float:
        try:
            return round(100 * (self.get_stock_by_ticker(ticker_id).get_value() / self.get_value()), 2)
        except ZeroDivisionError:
            return 0.0
            
    def get_portfolio_tickers(self):
        tickers = []
        if self._composition:
            for stock in self._composition:
                tickers.append(stock.name)
        return tickers

    def set_stock_prices(self, prices: dict):
        """
        prices is a dictionary whose keys are ticker_ids and whose values are the prices to set
        the method searches for the ticker and sets the price if found
        """

        for ticker_id, price in prices.items():
            try:
                self.get_stock_by_ticker(ticker_id).set_price(price)
            except KeyError:
                pass

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
    
    def get_value(self):
        value = 0
        for stock in self._composition:
            value += stock.get_value()
        return value
    
    def get_net_performance(self):
        return self._get_performance(self._net_contributions, self.get_value())
    
    def get_portfolio_summary(self):
        '''
        Returns a dictionary with the following keys:
            ticker1: 
                    :quantity: int
                    :value: float
                    :share: float
            tickern:
                    :quantity: int
                    :value: float
                    :share: float
        '''
        summary = {}
        for stock in self._composition:
            summary[stock.name] = {
                                    'value': stock.get_value(),
                                    'quantity': stock.get_quantity(),
                                    'weight': self.get_stock_weight(stock.name)
                                  }
        return summary            


class BuyEstimatorHelper(object):

    @staticmethod
    def simulate_buy(current_pf: Portfolio, buy_list) -> Portfolio:
        """
        buy list can be a list of tuples: [(ticker_name, quantity, current_price)]
        the current_price_element might not be necessary with the yahoo api
        """
        for ticker_name, quantity, current_price in buy_list:
            date = dt.datetime.now()
            net_amount = quantity * current_price
            gross_amount = net_amount

            current_pf.add_operation(Operation(ticker_name, date, quantity, current_price, gross_amount, net_amount))

        return current_pf

class YFInterface(object):

    @staticmethod
    def yahoo_stock_ticker(ticker_name):
        if ticker_name == PE500 or ticker_name == PCEU or ticker_name == PAEEM:
            return ticker_name + '.PA' 
        else:
            raise ValueError('Ticker {} not supported'.format(ticker_name))

    @staticmethod
    def stock_close_price(ticker_name, date:dt):
        end = date + dt.timedelta(days=1)
        data = yf.Ticker(YFInterface.yahoo_stock_ticker(ticker_name)).history(start=date, end=end, actions=False)
        return data['Close'][0]
    
    @staticmethod
    def get_last_stock_price(tickers: list):
        """Returns a dictionary containing the ticker names as key values and the last stock price as 
        items
        """
        if isinstance(tickers, str):
            tickers = [tickers]

        stock_prices = {}
        for ticker_name in tickers:
            ticker_yahoo_name = YFInterface.yahoo_stock_ticker(ticker_name)
            data =  yf.download(ticker_yahoo_name, period='1d')
            stock_prices[ticker_name] = data['Close'][0]
        return stock_prices




if __name__ == '__main__':
    operation_1 = Operation(
                            PE500,
                            date=dt.datetime.fromisoformat('2022-03-27'),
                            quantity=12,
                            stock_price=37.66,
                            gross_amount=12*37.66+1.2,
                            net_amount=12*37.66,
                            )
    operation_2 = Operation(
                            PCEU,
                            date=dt.datetime.fromisoformat('2022-04-22'),
                            quantity=8,
                            stock_price=24.69,
                            gross_amount=8*24.69+0.85,
                            net_amount=8*24.69,
                            )
    small_pf =  Portfolio.from_operations_list([operation_1, operation_2])

    print(small_pf.get_stock_by_ticker(PE500).get_quantity())

    small_pf =  Portfolio()

    print(small_pf.get_stock_by_ticker(PE500).get_quantity())



