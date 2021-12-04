from flask import Flask, render_template, request

import os
import pandas as pd
from fbprophet import Prophet
from datetime import date
from datetime import datetime

app = Flask(__name__)

def sector_chosen(argument):

    df_Makanan = pd.read_csv('fix 02 - Makanan.csv')
    df_Minuman = pd.read_csv('fix 02 - Minuman.csv')
    df_Rumah = pd.read_csv('fix 03 - Rumah.csv')
    df_Sandang = pd.read_csv('fix 04 - Sandang.csv')
    df_Transportasi = pd.read_csv('fix 07 - Transportasi.csv')

    switcher = {
        "MAKANAN": df_Makanan,
        "MINUMAN_TAK_BERALKOHOL": df_Minuman,        
    }
 
    return switcher.get(argument, "nothing")

def marks_prediction(value,city, sector, start_date, end_date):
    df_Makanan = pd.read_csv('fix 02 - Makanan.csv')
    df_Minuman = pd.read_csv('fix 02 - Minuman.csv')
    df_Rumah = pd.read_csv('fix 03 - Rumah.csv')
    df_Sandang = pd.read_csv('fix 04 - Sandang.csv')
    df_Transportasi = pd.read_csv('fix 07 - Transportasi.csv')

    sector = sector_chosen(sector)

    sector = sector[[city,'BULAN']]
    sector.columns = ['y', 'ds']

    sector.ds = pd.to_datetime(sector.ds)

    m = Prophet(interval_width=0.95, daily_seasonality=True)
    model = m.fit(sector)

    future = m.make_future_dataframe(periods=100,freq='M')
    forecast = m.predict(future)

    # forecast_value = forecast.loc[forecast.ds == '2014-01-01',['yhat']].values[0]

    mask = (forecast['ds'] > '2021-10-31') & (forecast['ds'] <= '2021-12-31')
    forecast_mask = forecast.loc[mask]

    inflation_average_rate = (forecast_mask['yhat'].sum())/forecast_mask.shape[0]

    value += inflation_average_rate*value
    return value

@app.route("/", methods = ["GET","POST"])
def marks():
    mk=""
    if request.method == "POST":
        
        value = request.form['value']
        city = request.form['city']
        sector = request.form['sector_option']
        start_date = date.today()
        end_date = request.form['inflation_date_end']

        value = float(value)

        # start_date = datetime.strptime(start_date, '%m-%d-%Y').date()
        # end_date = datetime.strptime(end_date, '%m-%d-%Y').date()
        print(type(end_date))
        marks_pred = marks_prediction(value,city, sector, start_date, end_date)
        print(marks_pred)
        mk = marks_pred
    
    return render_template("index.html",my_marks = mk)

if __name__== "__main__":
    app.run(debug = True)