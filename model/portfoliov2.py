import datetime as dt
import json
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

    @classmethod
    def from_json_data(cls, json_data: dict):
        return cls(
                    json_data['ticker'],
                    json_data['quantity'],
                    datetime.datetime.fromisoformat(json_data['purchase_date']),
                    json_data['purchase_price'],
                    )



    def __init__(self, ticker: str, quantity: int, date: datetime.datetime, purchase_price:float):
        self.ticker = ticker
        self.quantity = quantity
        self.purchase_date = date
        self.purchase_price = purchase_price

    def jsonfy(self):
        dict_repr = self.__dict__
        dict_repr['purchase_date'] = self.purchase_date.isoformat()
        return dict_repr

class PorfolioV2(object):

    @classmethod
    def from_json(cls):
        with open('portfolio_db.json', 'r') as f:
            pf_json_repr = json.load(f)
            purchases = [Purchase.from_json_data(purchase_json_data) for purchase_json_data in pf_json_repr['purchases']]
            stock_history = PorfolioV2._stock_history_from_json_data(pf_json_repr['stock_price_history'])

        pf_instance = cls(purchases)
        pf_instance.stock_price_history = stock_history.copy()
        return pf_instance

    @staticmethod
    def _stock_history_from_json_data(jsonified_stock_history: dict):

        stock_history_info = dict.fromkeys(jsonified_stock_history.keys())
        for ticker, json_stock_history_info in jsonified_stock_history.items():
            stock_history_info[ticker] = {}
            for json_stock_data_timestamp, stock_price in json_stock_history_info.items():
                stock_history_info[ticker][datetime.datetime.fromisoformat(json_stock_data_timestamp)] = stock_price

        return stock_history_info


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
    
    def get_stock_price_at_date(self, ticker: str, date: datetime.datetime, update_pf_file=True):
        try:
            return self.stock_price_history[ticker][date]
        except KeyError:
            if ticker not in self.stock_price_history:
                self.stock_price_history[ticker] = {}
            
            self.stock_price_history[ticker][date] = pf.YFInterface.stock_close_price(ticker, date)

            if update_pf_file:
                write_to_db(self)

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

    def _jsonify_stock_history(self):
        jsonified_dict = dict.fromkeys(self.stock_price_history.keys())
        for ticker_name, stock_history_info in self.stock_price_history.items():
            jsonified_dict[ticker_name] = {}
            for stock_time_stamp, stock_price in stock_history_info.items():
                jsonified_dict[ticker_name][stock_time_stamp.isoformat()] = stock_price

        return jsonified_dict
        
    def jsonfy(self):
        pf_dict_form = dict.fromkeys(self.__dict__)
        
        purchases_list_json_repr = [purchase.jsonfy() for purchase in self.purchases]
        stock_price_history_json_repr = self._jsonify_stock_history()

        pf_dict_form['purchases'] = purchases_list_json_repr
        pf_dict_form['stock_price_history'] = stock_price_history_json_repr

        return pf_dict_form

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