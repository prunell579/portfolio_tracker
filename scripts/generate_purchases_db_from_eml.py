import pickle
import sys

sys.path.append('.')
import model.portfoliov2 as pf

if __name__ == "__main__":
    portfolio = pf.generate_portfolio_db_from_eml()
    pf.write_to_db(portfolio)
