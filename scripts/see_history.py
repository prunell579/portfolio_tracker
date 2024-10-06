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
    performances = []
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
    
        performance = portfolio.get_performance_at_date(date)
        performances.append(performance)

    if write_to_db:
        pf.write_to_db(portfolio)

    # Create a figure with two subplots, one for portfolio value and one for performance
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))

    # Plot the portfolio value over time on the first subplot
    ax1.plot(dates, values, label="Portfolio Value")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Value")
    ax1.set_title("Portfolio Value Over Time")
    ax1.legend()
    ax1.grid(True)

    # Plot the portfolio performance over time on the second subplot
    ax2.plot(dates, performances, label="Portfolio Performance", color='orange')
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Performance")
    ax2.set_title("Portfolio Performance Over Time")
    ax2.legend()
    ax2.grid(True)

    # Adjust the x-axis date format for both subplots
    fig.autofmt_xdate()

    # Show the plots
    plt.tight_layout()
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