import sys
sys.path.append('.')
import model.ticker_codes as tc
import model.portfoliov2 as pf

if __name__ == "__main__":
    my_pf = pf.load_portfolio_db()
    for ticker in my_pf.get_portfolio_tickers():
        print(my_pf.get_ticker_shares(ticker))

    print(my_pf.get_portfolio_value())
    print(my_pf.composition())