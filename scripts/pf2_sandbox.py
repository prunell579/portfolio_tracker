import sys
sys.path.append('.')
import model.ticker_codes as tc
import model.portfoliov2 as pf
import json


if __name__ == "__main__":
    my_pf = pf.load_portfolio_db()
    
    with open('portfolio_db.json', 'w') as f:
        json.dump(my_pf.jsonfy(), f, indent=4)

    pf2 = pf.PorfolioV2.from_json()
    print('bl')