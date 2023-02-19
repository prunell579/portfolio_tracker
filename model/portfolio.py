from datetime import datetime as dt
from pprint import pprint

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

    def __init__(self, value=0, composition={}, net_contribution=0, gross_contribution=0, performance=0, history={}) -> None:
        self.value = value
        self._composition = composition
        self._net_contributions = net_contribution
        self._gross_contributions = gross_contribution
        self._performance = performance
        self._history = history

    @classmethod
    def from_operations_list(cls, operations):
        pf = Portfolio()

        for operation in operations:
            pf.add_operation(operation)

        return pf


    def add_operation(self, operation: Operation):
        try:
            previous_ticker_value = self._composition[operation.ticker_id] * operation.stock_price
            self._composition[operation.ticker_id] += operation.quantity
        except KeyError:
            assert(operation.ticker_id in [PE500, PCEU, PAEEM])
            previous_ticker_value = 0
            self._composition[operation.ticker_id] = operation.quantity

        delta_in_value = self._composition[operation.ticker_id] * operation.stock_price - previous_ticker_value

        self.value += delta_in_value
        self._net_contributions += operation.gross_amount
        self._gross_contributions += operation.net_amount

        self._performance = (self.value - self._net_contributions) / self._net_contributions

        self._update_history(operation)

    def _update_history(self, operation: Operation):
        if operation.date in self._history.keys():
            portfolio_in_history = self._history[operation.date]
            if portfolio_in_history._get_total_quantity_of_shares() <= self._get_total_quantity_of_shares():
                self._history[operation.date] = self
        else:
            self._history[operation.date] = self

    def _get_total_quantity_of_shares(self):
        total_quantity_of_shares = 0
        for ticker_quantity in self._composition.values():
            total_quantity_of_shares += ticker_quantity
        return total_quantity_of_shares

if __name__ == '__main__':
    operations = FortuneoInterface().extract_operations_from_csv('sample_fortuneo_data.csv')
    pf = Portfolio.from_operations_list(operations)

    print('shares no: {}\ngross contributions: {}\nnet contributions: {}\nvalue {}'.format(pf._get_total_quantity_of_shares,
                                                                                           pf._gross_contributions,
                                                                                           pf._net_contributions,
                                                                                           pf.value
                                                                                           ))





