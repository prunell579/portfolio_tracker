from flask import Flask, render_template
import sys

sys.path.append('.')
import model.portfoliov2 as pf

app = Flask(__name__)

@app.route('/')
def index():
    my_pf = pf.load_portfolio_db()
    comp = my_pf.composition(percentage_form=True)

    return render_template('index.html', tickers=list(comp.keys()),
                           weights=list(comp.values()))

@app.route('/timeseries')
def pf_time_series():
    return render_template('time_series.html')


if __name__ == '__main__':
    app.run(debug=True)
