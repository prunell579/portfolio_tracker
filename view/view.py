import tkinter as tk
from tkinter import ttk

import sys
sys.path.append('.')

from model import portfolio as pftools


class PorftolioMainWindow(object):
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.table = ttk.Treeview(self.root, columns=('qty', 'value', 'pctg'))

        self.table.heading('#0', text='Ticker')
        self.table.heading('qty', text='Quantity')
        self.table.heading('value', text='Value')
        self.table.heading('pctg', text='% share')

        self.table.pack()

        pe500_label = tk.Label(self.root, text='PE500')
        pe500_label.pack()

    def fill_table(self, portfolio_summary: dict):
        """
        Some fixing to do here wrt column order
        """
        for ticker_name, ticker_summary in portfolio_summary.items():
            if ticker_name == 'total_value':
                continue
            row_vals = (ticker_summary['quantity'],ticker_summary['value'],ticker_summary['weight'])
            self.table.insert('', tk.END, text=ticker_name, values=row_vals)


        total_row_iid = self.table.insert('', tk.END, text='TOTAL')
        self.table.set(total_row_iid, 'value', portfolio_summary['total_value'])

class PortfolioApp(object):
    """
    Class controlling the interactions between a Portfolio object and its view.
    """
    def __init__(self, model: pftools.Portfolio, view: PorftolioMainWindow, fetch_stock_prices=False) -> None:
        self.model: pftools.Portfolio = model
        self.view: PorftolioMainWindow = view

        if fetch_stock_prices:
            prices = pftools.YFInterface.get_last_stock_price(self.model.get_portfolio_tickers())
            self.model.set_stock_prices(prices)

        if self.model.get_portfolio_tickers():
            self.view.fill_table(self.model.get_portfolio_summary())


if __name__ == '__main__':
    operations_list = pftools.FortuneoInterface.extract_operations_from_csv(
    'data/HistoriqueOperationsBourse_015207052916_du_24_03_2021_au_24_03_2023.csv'
                                                                            )
    # operations_list=[]
    app = PortfolioApp(pftools.Portfolio.from_operations_list(operations_list), PorftolioMainWindow(), fetch_stock_prices=True)

    app.view.root.mainloop()
