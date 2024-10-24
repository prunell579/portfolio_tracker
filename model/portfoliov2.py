import datetime as dt
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


def is_weekend(date: dt.datetime):
    if date.weekday() > 4:
        return True
    return False

def get_previous_business_day(date: datetime.datetime):
    # If it's Saturday, go back to Friday
    if date.weekday() == 5:  # Saturday
        return date - dt.timedelta(days=1)
    # If it's Sunday, go back to Friday
    elif date.weekday() == 6:  # Sunday
        return date - dt.timedelta(days=2)
    # For Monday to Friday, return the previous day
    else:
        return date - dt.timedelta(days=1)


class Purchase(object):
    def __init__(self, ticker: str, quantity: int, date: datetime.datetime):
        self.ticker = ticker
        self.quantity = quantity
        self.purchase_date = date

class PorfolioV2(object):
    def __init__(self, purchases=None):
        self.purchases = copy.deepcopy(purchases) if purchases else []
        self.stock_price_history = {}

    def get_purchases(self):
        return self.purchases.copy()

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

    def composition(self, percentage_form=False):
        """
        Returns a dictionary with the tickers as keys, and 
        their composition in VALUE as value
        """
        pf_value = self.get_portfolio_value()
        composition = {}

        # TODO: logic to distinguish BD and non BD shold be where?
        today = datetime.datetime.today()
        if is_weekend(today):
            today = get_previous_business_day(today)
        for ticker in self.get_portfolio_tickers():
            ticker_value = self.get_ticker_shares(ticker) * self.get_stock_price_at_date(ticker, date=today)
            if percentage_form:
                stock_weight = 100 * ticker_value / pf_value
            else:
                stock_weight = ticker_value / pf_value

            composition[ticker] = stock_weight

        return composition
        

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

    return(ticker, quantity, date_time)

def purchase_object_from_email(eml_file_path):
    text_content = get_text_content_from_eml(eml_file_path)
    ticker, qty, date_time = search_for_purchase_info(text_content)

    if ticker == tc.PE500_LONG_FORMAT or ticker == 'Amundi PEA S&P 500 ESG UCITS ETF Acc':
        shorthand_ticker = tc.PE500
    elif ticker == tc.PCEU_LONG_FORMAT or ticker == ('Amundi ETF PEA MSCI Europe UCITS ETF'):
        shorthand_ticker = tc.PCEU
    elif ticker == tc.PAEEM_LONG_FORMAT or ticker == 'Amundi PEA MSCI Emerging Markets ESG Leaders UCITS ETF - EUR':
        shorthand_ticker = tc.PAEEM
    else:
        raise ValueError("Unknwon ticker {}".format(ticker))

    date_time_obj = datetime.datetime.strptime(date_time, '%d/%m/%y à %H:%M')

    return Purchase(shorthand_ticker, int(float(qty)), date_time_obj)

def generate_portfolio_db_from_eml(emls_folder='data/order-emails'):
    purchases_list = []
    for eml_file in Path(emls_folder).rglob("*.eml"):
        purchase_obj = purchase_object_from_email(eml_file)
        purchases_list.append(purchase_obj)

    return PorfolioV2(purchases_list)

def load_portfolio_db() -> PorfolioV2: 
    with open('portfolio_db.pkl', 'rb') as f:
        return pickle.load(f)

def write_to_db(portfolio: PorfolioV2):
    with open('portfolio_db.pkl', 'wb') as f:
        pickle.dump(portfolio, f)