from flask import Flask, render_template, request

import os
import pandas as pd
from fbprophet import Prophet
from datetime import date
from datetime import datetime
import json
import plotly
import math
app = Flask(__name__)

import io
import random
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import plotly.graph_objects as go

def my_plot(data,plot_var):
    data_plot = go.Scatter(x=data["ds"],y=data[plot_var], line=dict(color="#CE285E",width=2))
    layout=go.Layout(title=dict(text="This is a Line Chart of Variable"+" "+str(plot_var),x=0.5),
    xaxis_title="Record Number", yaxis_title="Values"
    )
    fig =go.Figure(data=data_plot, layout=layout)
    # This is conversion step...
    fig_json = fig.to_json()
    graphJSON = json.dumps(fig_json, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

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

    mask = (forecast['ds'] > start_date) & (forecast['ds'] <= end_date)
    
    graph_mask = forecast['ds'] <= end_date

    forecast_mask = forecast.loc[mask]

    forecast_graph_mask = forecast.loc[graph_mask]
    forecast_graph_mask['value'] = forecast_graph_mask['yhat']*value

    if forecast_mask.empty:
        return value

    inflation_average_rate = (forecast_mask['yhat'].sum())/forecast_mask.shape[0]

    value += inflation_average_rate*0.01*value

    forecast_graph_mask['value'] = value + forecast_graph_mask['yhat']*value*0.01

    forecast_graph_mask.value = forecast_graph_mask.value.astype(int)

    chart_from_python=my_plot(forecast_graph_mask,"value")

    value = int(value)

    return value,chart_from_python

@app.route("/", methods = ["GET","POST"])
def marks():
    mk=""
    chart_from_python=""
    if request.method == "POST":
        
        value = request.form['value']
        city = request.form['city']
        sector = request.form['sector_option']
        start_date = date.today()
        end_date = request.form['inflation_date_end']

        value = float(value)
        end_date = pd.to_datetime(end_date)
        start_date = pd.to_datetime(start_date)
        print(type(end_date))
        marks_pred,chart_from_python = marks_prediction(value,city, sector, start_date, end_date)
        print(marks_pred)
        mk = marks_pred
    
    return render_template("index.html",my_marks = mk,chart_for_html=chart_from_python)

if __name__== "__main__":
    app.run(debug = True)