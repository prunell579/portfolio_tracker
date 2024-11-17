from flask import Flask, json, render_template
import sys
import datetime as dt

sys.path.append('.')
import model.portfoliov2 as pf

app = Flask(__name__)

def generate_dates_vector(starting_date: dt.datetime) -> list:
    today = dt.datetime.today()

    dates = [starting_date]
    current_date = starting_date

    while current_date < today:
        current_date = current_date + dt.timedelta(15)
        dates.append(current_date)

    dates[-1] = today

    return dates


@app.route('/')
def index():
    my_pf = pf.load_portfolio_db()
    comp = my_pf.composition(percentage_form=True)

    return render_template('index.html', tickers=list(comp.keys()),
                           weights=list(comp.values()))

@app.route('/timeseries')
def pf_time_series():
    my_pf = pf.load_portfolio_db()

    values = []
    max_attempts = 5
    dates_iso8601 = []
    for date in generate_dates_vector(my_pf.get_first_purchase_date()):
        dates_iso8601.append(dt.datetime.isoformat(date))
        for attempt in range(1,max_attempts + 1):
            try:
                values.append(my_pf.get_portfolio_value_at_date(date))
                break
            except ValueError:
                if attempt == max_attempts:
                    raise ValueError(f'Problem retrieving portfolio value after {max_attempts} retries')
                date -= dt.timedelta(-1)

    return render_template('time_series.html',
                           dates=json.dumps(dates_iso8601),
                           values=json.dumps(values)
                           )


if __name__ == '__main__':
    app.run(debug=True)
