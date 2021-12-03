import os
import pandas as pd
from fbprophet import Prophet

import warnings; 
warnings.simplefilter('ignore')


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


def marks_prediction():
    a=1
    return a
