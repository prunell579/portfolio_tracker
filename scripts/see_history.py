import datetime
import sys
import pandas as pd
from pandas.tseries.offsets import CustomBusinessDay
from pandas.tseries.holiday import USFederalHolidayCalendar

import matplotlib.pyplot as plt


sys.path.append('.')
import model.ticker_codes as tc
import model.portfoliov2 as pf

def see_portfolio_history(portfolio: pf.PorfolioV2, write_to_db=False):
    # Generate a list of dates for the plot
    dates = pd.date_range(start=portfolio.get_first_purchase_date(), end=datetime.datetime.today(), freq='W-MON')
    custom_bday = CustomBusinessDay(calendar=USFederalHolidayCalendar())

    # Calculate portfolio value for each date
    values = []
    for date in dates:
        print('processing date: {} ({} out of {})'.format(date, dates.get_loc(date), len(dates)))
        is_business_day = True
        # is_business_day = date + custom_bday in pd.date_range(start=date, periods=1, freq=custom_bday)
        # todo: check if date is a business day
        if date.month == 12 and date.day == 25:
            is_business_day = False

        if not is_business_day:
            # print('skipping non-business day: ', date)
            date = date + datetime.timedelta(days=1)
            print('replacing christmas day for next business day: ', date)

        value = portfolio.get_portfolio_value_at_date(date)
        values.append(value)

    if write_to_db:
        pf.write_to_db(portfolio)

    # Plot the portfolio value over time
    plt.figure(figsize=(10, 6))
    plt.plot(dates, values, label="Portfolio Value")
    plt.xlabel("Date")
    plt.ylabel("Value")
    plt.title("Portfolio Value Over Time")
    plt.gcf().autofmt_xdate()
    plt.legend()
    plt.grid(True)
    plt.show()

def dummy_porfolio():
    """
    PE500 has 33 shares
    PCEU has 35 shares
    PAEEM has 2 shares
    """
    purchase1 = pf.Purchase(tc.PE500, 10, datetime.datetime(2024, 1, 2))
    purchase2 = pf.Purchase(tc.PCEU, 14, datetime.datetime(2024, 1, 15))
    purchase3 = pf.Purchase(tc.PAEEM, 2, datetime.datetime(2024, 2, 20))
    purchase4 = pf.Purchase(tc.PCEU, 21, datetime.datetime(2024, 3, 2))
    purchase5 = pf.Purchase(tc.PE500, 23, datetime.datetime(2024, 3, 4))
    return pf.PorfolioV2([purchase1, purchase2, purchase3, purchase4, purchase5])


if __name__ == "__main__":
    portfolio = pf.load_portfolio_db()
    see_portfolio_history(portfolio, write_to_db=True)