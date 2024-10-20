import datetime
import model.portfolio as pf
import copy


import datetime
from email import policy
from email.parser import BytesParser
import re
from pathlib import Path
import sys
import pickle

sys.path.append('.')
import model.ticker_codes as tc

class Purchase(object):
    def __init__(self, ticker: str, quantity: int, date: datetime.datetime, purchase_price:float):
        self.ticker = ticker
        self.quantity = quantity
        self.purchase_date = date
        self.purchase_price = purchase_price

class PorfolioV2(object):
    def __init__(self, purchases=None):
        """
        Format of the stock_price_history dictionary:
        {
            'AAPL': {
                datetime.datetime(2021, 1, 1): 100,
                datetime.datetime(2021, 1, 2): 102,
                ...
            },
            'MSFT': {
                datetime.datetime(2021, 1, 1): 200,
                datetime.datetime(2021, 1, 2): 202,
                ...
            },
            ...
        }
        """
        self.purchases = copy.deepcopy(purchases) if purchases else []
        self.stock_price_history = {}

    def get_purchases(self):
        return self.purchases.copy()
    
    def get_purchases_at_date(self, date: datetime.datetime):
        return [purchase for purchase in self.purchases if purchase.purchase_date <= date]

    def add_purchase(self, purchase: Purchase):
        self.purchases.append(purchase)

    def get_ticker_shares(self, ticker: str):
        return sum([purchase.quantity for purchase in self.purchases if purchase.ticker == ticker])
    
    def get_ticker_shares_at_date(self, ticker: str, date: datetime.datetime):
        return sum([purchase.quantity for purchase in self.purchases if purchase.ticker == ticker and purchase.purchase_date <= date])
    
    def get_portfolio_tickers(self):
        return set([purchase.ticker for purchase in self.purchases])
    
    def get_stock_price_at_date(self, ticker: str, date: datetime.datetime):
        try:
            return self.stock_price_history[ticker][date]
        except KeyError:
            if ticker not in self.stock_price_history:
                self.stock_price_history[ticker] = {}
            
            self.stock_price_history[ticker][date] = pf.YFInterface.stock_close_price(ticker, date)
            return self.stock_price_history[ticker][date]

    def get_portfolio_value(self):
        value = 0
        for ticker in self.get_portfolio_tickers():
            value += pf.YFInterface.get_last_stock_price(ticker) * self.get_ticker_shares(ticker)

        return value
    
    def get_portfolio_value_at_date(self, date: datetime.datetime):
        value = 0
        for ticker in self.get_portfolio_tickers():
            value += self.get_stock_price_at_date(ticker, date) * self.get_ticker_shares_at_date(ticker, date)

        return value

    def get_first_purchase_date(self):
        return min([purchase.purchase_date for purchase in self.purchases])

    def get_total_investment(self):
        return sum([purchase.purchase_price * purchase.quantity for purchase in self.purchases])
    
    def get_total_investement_at_date(self, date: datetime.datetime):
        return sum([purchase.purchase_price * purchase.quantity for purchase in self.get_purchases_at_date(date)])

    def get_performance(self, brute=False):
        if brute:
            return self.get_portfolio_value() - self.get_total_investment()
        else:
            return (self.get_portfolio_value() - self.get_total_investment()) / self.get_total_investment()
        
    def get_performance_at_date(self, date: datetime.datetime, brute=False):
        if brute:
            return self.get_portfolio_value_at_date(date) - self.get_total_investement_at_date(date)
        else:
            return (self.get_portfolio_value_at_date(date) - self.get_total_investement_at_date(date)) / self.get_total_investment()

### DB operations
def get_text_content_from_eml(eml_file_path):
    with open(eml_file_path, 'rb') as f:
        # Parse the .eml file
        msg = BytesParser(policy=policy.default).parse(f)

    # Extract subject, from, to (headers)
    subject = msg['subject']
    from_ = msg['from']
    to = msg['to']

    # Extract email content (both plain text and HTML)
    if msg.is_multipart():
        # If email has multiple parts, iterate through them
        for part in msg.iter_parts():
            content_type = part.get_content_type()
            if content_type == 'text/plain':
                text_content = part.get_payload(decode=True).decode(part.get_content_charset())
            elif content_type == 'text/html':
                html_content = part.get_payload(decode=True).decode(part.get_content_charset())
    else:
        # For non-multipart emails, just extract the payload
        content_type = msg.get_content_type()
        if content_type == 'text/plain':
            text_content = msg.get_payload(decode=True).decode(msg.get_content_charset())
        elif content_type == 'text/html':
            html_content = msg.get_payload(decode=True).decode(msg.get_content_charset())

    return text_content

def search_for_purchase_info(text_content, verbose=False):
    # Search for the line containing "Votre ordre d'achat"
    order_match = re.search(r"Votre ordre d'achat sur (.+?) \(.+?\) a été exécuté", text_content)
    ticker = order_match.group(1) if order_match else None

    # extract purchase price
    purchase_price_match = re.search(r"à (\d+\,?\d*) EUR pour", text_content)
    purchase_price = purchase_price_match.group(1) if purchase_price_match else None

    # Extracting quantity (number after 'pour une quantité de')
    quantity_match = re.search(r"quantité de (\d+\.?\d*)", text_content)
    quantity = quantity_match.group(1) if quantity_match else None

    # Extracting date and time (after 'le' and before '(réf')
    date_time_match = re.search(r"le (\d{2}/\d{2}/\d{2} à \d{2}:\d{2})", text_content)
    date_time = date_time_match.group(1) if date_time_match else None

    if verbose:
        # Print the extracted information
        print("Ticker:", ticker)
        print("Quantity:", quantity)
        print("Date and Time:", date_time)
        print("purchase price:", purchase_price)

    return (ticker, quantity, date_time, purchase_price)

def purchase_object_from_email(eml_file_path):
    text_content = get_text_content_from_eml(eml_file_path)
    ticker, qty, date_time, purchase_price = search_for_purchase_info(text_content)

    if ticker == tc.PE500_LONG_FORMAT or ticker == 'Amundi PEA S&P 500 ESG UCITS ETF Acc':
        shorthand_ticker = tc.PE500
    elif ticker == tc.PCEU_LONG_FORMAT or ticker == ('Amundi ETF PEA MSCI Europe UCITS ETF'):
        shorthand_ticker = tc.PCEU
    elif ticker == tc.PAEEM_LONG_FORMAT or ticker == 'Amundi PEA MSCI Emerging Markets ESG Leaders UCITS ETF - EUR':
        shorthand_ticker = tc.PAEEM
    else:
        raise ValueError("Unknwon ticker {}".format(ticker))

    date_time_obj = datetime.datetime.strptime(date_time, '%d/%m/%y à %H:%M')
    purchase_price_dot_notation = purchase_price.replace(',', '.')

    return Purchase(shorthand_ticker, int(float(qty)), date_time_obj, float(purchase_price_dot_notation))

def generate_portfolio_db_from_eml():
    purchases_list = []
    for eml_file in Path("data\order-emails").rglob("*.eml"):
        purchase_obj = purchase_object_from_email(eml_file)
        purchases_list.append(purchase_obj)

    return PorfolioV2(purchases_list)

def load_portfolio_db():
    with open('portfolio_db.pkl', 'rb') as f:
        return pickle.load(f)

def write_to_db(portfolio: PorfolioV2):
    with open('portfolio_db.pkl', 'wb') as f:
        pickle.dump(portfolio, f)