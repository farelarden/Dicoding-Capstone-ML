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

from math import radians, cos, sin, asin, sqrt

def dist(lat1, long1, lat2, long2): 
    lat1, long1, lat2, long2 = map(radians, [lat1, long1, lat2, long2])
    dlon = long2 - long1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371* c
    return km


def my_plot(data,plot_var,city):
    data_plot = go.Scatter(x=data["ds"],y=data[plot_var], line=dict(color="#CE285E",width=2))
    layout=go.Layout(title=dict(text="This is the value of your item in "+" "+str(city),x=0.5),
    xaxis_title="Date", yaxis_title="Values"
    )
    fig =go.Figure(data=data_plot, layout=layout)

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
    start_date = start_date - dateutil.relativedelta.relativedelta(months=1)
    end_date = end_date + dateutil.relativedelta.relativedelta(months=1)
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

    chart_from_python_city_1=my_plot(forecast_graph_mask,"value",city)

    value = int(value)

    return value,chart_from_python_city_1

def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    hav = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
    return 12742 * asin(sqrt(hav))

def closest(data, v):
    return min(data, key=lambda p: distance(v['lat'],v['lon'],p['lat'],p['lon']))

def city_comparison(city):
    dataset_1 = pd.read_csv('longitude, latitude.csv')
    dataset_2 = pd.read_csv('longitude, latitude.csv')
    dataset_1=dataset_1.rename(columns = {'Latitude':'lat','Longitude':'lon'})
    dataset_2=dataset_2.rename(columns = {'Latitude':'lat','Longitude':'lon'})
    Kota_Pilihan = city
    dataset_2_1 = dataset_2[dataset_2.Kota != Kota_Pilihan]
    dataset_2_1_1 = dataset_2.set_index("Kota")
    dataset_2_1 = dataset_2_1.to_dict('records')
    dataset_2_1_2 = dataset_2_1_1.loc[[Kota_Pilihan]]

    v = {'lat': dataset_2_1_2['lat'], 'lon': dataset_2_1_2['lon']}
    closest_1 = closest(dataset_2_1, v)

    First_city = closest_1.get('Kota')

    for i in range(len(dataset_2_1)):
        if dataset_2_1[i]['Kota'] == First_city:
            del dataset_2_1[i]
            break
    
    v = {'lat': dataset_2_1_2['lat'], 'lon': dataset_2_1_2['lon']}
    closest_2 = closest(dataset_2_1, v)

    Second_city = closest_2.get('Kota')

    return First_city, Second_city

def get_sector_value(product):

    dataset= pd.read_csv('Product Names - Sheet1.csv')
    dataset=dataset.rename(columns = {'Nama Produk':'Nama_Produk'})
    new = dataset.query('Nama_Produk.str.contains(@product)', engine='python')
    if new.empty:
        return 0,0
    else:
        value = new.at[0,'Harga(IDR)']
        sector = new.at[0,'Sektor']
        return value,sector

    

@app.route("/", methods = ["GET","POST"])
def marks():
    mk=""
    chart_from_python=""
    second_chart=""
    third_chart=""
    value=""
    marks=""
    if request.method == "POST":
        
        product = request.form['product']
        city = request.form['city']
        start_date = date.today()
        end_date = request.form['inflation_date_end']
        value,sector = get_sector_value(product)
        value = float(value)
   
        if product =="" or city=="" or end_date=="":
            mk = "Please fill in the inputs to get the inflation result."
            return render_template("index.html",my_marks = mk)
        elif end_date <= start_date:
            mk = "The date must not from the previous month"
            return render_template("index.html",my_marks = mk)
        else:

            if value == 0:
                return render_template("product.html",my_marks = "Sorry, but There is no Product")
            else:
                end_date = pd.to_datetime(end_date)
                start_date = pd.to_datetime(start_date)
                second_city,third_city = city_comparison(city)
                marks_pred,chart_from_python = marks_prediction(value,city, sector, start_date, end_date)
                marks_pred_2, second_chart = marks_prediction(value,second_city, sector, start_date, end_date)
                marks_pred_3, third_chart = marks_prediction(value,third_city, sector, start_date, end_date)
                print(marks_pred)
                mk = "The predicted value of your item is Rp "+ str(marks_pred)
        
    return render_template("product.html",my_marks = mk,chart_for_html=chart_from_python,chart_for_html_2=second_chart,chart_for_html_3=third_chart)
        
if __name__== "__main__":
    app.run(debug = True)