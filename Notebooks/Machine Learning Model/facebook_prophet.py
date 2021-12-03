# -*- coding: utf-8 -*-
"""Facebook Prophet.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1K9UqAb02lYv6DbxA7FeGP3W1eG9-wZ6l
"""

import os
import pandas as pd
from fbprophet import Prophet

import warnings; 
warnings.simplefilter('ignore')

!pip install pystan
!pip install fbprophet

!git clone https://github.com/farelarden/Dicoding-Capstone-ML.git

df_Makanan = pd.read_csv('/content/Dicoding-Capstone-ML/Dataset/Fix Dataset/fix 02 - Makanan.csv')
df_Minuman = pd.read_csv('/content/Dicoding-Capstone-ML/Dataset/Fix Dataset/fix 02 - Minuman.csv')
df_Rumah = pd.read_csv('/content/Dicoding-Capstone-ML/Dataset/Fix Dataset/fix 03 - Rumah.csv')
df_Sandang = pd.read_csv('/content/Dicoding-Capstone-ML/Dataset/Fix Dataset/fix 04 - Sandang.csv')
df_Transportasi = pd.read_csv('/content/Dicoding-Capstone-ML/Dataset/Fix Dataset/fix 07 - Transportasi.csv')

df_Makanan.head()
df_Makanan= df_Makanan.drop(['URUTAN'], axis=1)

df_Makanan.head()

df_Makanan = df_Makanan[['KOTA MEULABOH','BULAN']]
df_Makanan.columns = ['y', 'ds']

df_Makanan.head()

df_Makanan.dtypes

df_Makanan.y = pd.to_datetime(df_Makanan.y)

df_Makanan.head()

df_Makanan.shape

m = Prophet(interval_width=0.95, daily_seasonality=True)
model = m.fit(df_Makanan)

future = m.make_future_dataframe(periods=100,freq='M')

future

forecast = m.predict(future)
forecast.head()

plot1 = m.plot(forecast)

plt2 = m.plot_components(forecast)

forecast.dtypes

forecast_value = forecast.loc[forecast.ds == '2018-01-01',['trend']].values[0]

forecast_value
