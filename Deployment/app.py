from flask import Flask, render_template, request

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.preprocessing import MinMaxScaler
from keras.preprocessing.sequence import TimeseriesGenerator
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
import math 

app = Flask(__name__)

# def marks_prediction():
#     a=4
#     return a
def marks_prediction():
    df_Makanan = pd.read_csv('/content/fix 02 - Makanan.csv')
    df_Minuman = pd.read_csv('/content/fix 02 - Minuman.csv')
    df_Rumah = pd.read_csv('/content/fix 03 - Rumah.csv')
    df_Sandang = pd.read_csv('/content/fix 04 - Sandang.csv')
    df_Transportasi = pd.read_csv('/content/fix 07 - Transportasi.csv')

    df_Makanan = df_Makanan[['KOTA MEULABOH','BULAN']]
    df_Makanan.columns = ['y', 'ds']

    df_Makanan.y = pd.to_datetime(df_Makanan.y)

    m = Prophet(interval_width=0.95, daily_seasonality=True)
    model = m.fit(df_Makanan)

    future = m.make_future_dataframe(periods=100,freq='M')
    forecast = m.predict(future)

    forecast_value = forecast.loc[forecast.ds == '2018-01-01',['trend']].values[0]

    return forecast_value

@app.route("/", methods = ["GET","POST"])
def marks():
    mk=""
    if request.method == "POST":
        marks_pred = marks_prediction()
        # print(marks_pred)
        mk = marks_pred
    
    return render_template("index.html",my_marks = mk)

# @app.route("/", methods = ['POST'])
# def submit():
#     # HTML -> py
#     if request.method == "POST":
        
#         value = request.form['value']
#         city = request.form['city']
#         sector = request.form['sector']
#         date = request.form['date']

#         marks_pred = marks.marks_prediction()
#         mk = marks_pred
#     #py -> HTML
#     return render_template("index.html" , mymarks = mk)

if __name__== "__main__":
    app.run(debug = True)