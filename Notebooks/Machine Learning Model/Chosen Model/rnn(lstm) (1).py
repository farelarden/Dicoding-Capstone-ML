# -*- coding: utf-8 -*-
"""RNN(LSTM).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dnf72ZIdc_qmE44Z4Qn7_5sBcGjgGbiO

# RNN(LSTM)

Here we will forecast the future of inflation using RNN(LSTM).

### 1. Preparing the datasets & Importing neccessary libraries
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

!git clone https://github.com/farelarden/Dicoding-Capstone-ML.git

df_Makanan = pd.read_csv('/content/Dicoding-Capstone-ML/Dataset/Fix Dataset/fix 02 - Makanan.csv',index_col='BULAN')
df_Minuman = pd.read_csv('/content/Dicoding-Capstone-ML/Dataset/Fix Dataset/fix 02 - Minuman.csv',index_col='BULAN')
df_Rumah = pd.read_csv('/content/Dicoding-Capstone-ML/Dataset/Fix Dataset/fix 03 - Rumah.csv',index_col='BULAN')
df_Sandang = pd.read_csv('/content/Dicoding-Capstone-ML/Dataset/Fix Dataset/fix 04 - Sandang.csv',index_col='BULAN')
df_Transportasi = pd.read_csv('/content/Dicoding-Capstone-ML/Dataset/Fix Dataset/fix 07 - Transportasi.csv',index_col='BULAN')

"""## 2. Data Preprocessing"""

df_Makanan.index.freq='MS'

df_Makanan = df_Makanan[['KOTA MEULABOH']]

df_Makanan.head()

df_Makanan.shape

df_Makanan.plot(figsize=(12,6))

from statsmodels.tsa.seasonal import seasonal_decompose

"""## 3. Train and Split Data"""

train = df_Makanan.iloc[:math.ceil(df_Makanan.shape[0]*0.8)]
test = df_Makanan.iloc[math.ceil(df_Makanan.shape[0]*0.8):]

train

test

from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()

scaler.fit(train)
scaled_train = scaler.transform(train)
scaled_test = scaler.transform(test)

from keras.preprocessing.sequence import TimeseriesGenerator

scaled_train[:10]

# define generator
n_input = 12
n_features = 1
generator = TimeseriesGenerator(scaled_train, scaled_train, length=n_input, batch_size=1)

X,y = generator[0]
print(f'Given the Array: \n{X.flatten()}')
print(f'Predict this y: \n {y}')

X.shape

generator = TimeseriesGenerator(scaled_train, scaled_train, length=n_input, batch_size=1)

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM

# # define model
# model = Sequential()
# model.add(LSTM(100, activation='relu', input_shape=(n_input, n_features)))
# model.add(Dense(1))
# model.compile(optimizer='adam', loss='mse')

import keras

model = keras.Sequential()
model.add(
  keras.layers.Bidirectional(
    keras.layers.LSTM(
        units=128,
        input_shape=(n_input, n_features)
    )
  )
)
model.add(keras.layers.Dropout(rate=0.2))
model.add(keras.layers.Dense(units=1))

model.compile(loss='mean_squared_error',optimizer='adam')
# history = modet. fit(
#     X_train, y_train,
#     epochs=30,
#     batch_ size=32,
#     validation_split=0.1,
#     shuffle=False
# )

# fit model
model.fit(generator,epochs=100)

loss_per_epoch = model.history.history['loss']
plt.plot(range(len(loss_per_epoch)),loss_per_epoch)

last_train_batch = scaled_train[-12:]
last_train_batch = last_train_batch.reshape((1, n_input, n_features))
model.predict(last_train_batch)

scaled_test[0]

test_predictions = []

first_eval_batch = scaled_train[-n_input:]
current_batch = first_eval_batch.reshape((1, n_input, n_features))

for i in range(len(test)):
    
    # get the prediction value for the first batch
    current_pred = model.predict(current_batch)[0]
    
    # append the prediction into the array
    test_predictions.append(current_pred) 
    
    # use the prediction to update the batch and remove the first value
    current_batch = np.append(current_batch[:,1:,:],[[current_pred]],axis=1)

test['Prediction']=test_predictions

test.head()

test.dtypes

test['Prediction'] = test['Prediction'].astype(float, errors = 'raise')

test.dtypes

test.tail()

test.plot(figsize=(14,5))

from sklearn.metrics import mean_squared_error
from math import sqrt
rmse=mean_squared_error(test['KOTA MEULABOH'],test['Prediction'])
print(rmse)

"""## 4. Forecasting"""

month_vals = []
for i in range(100):
    month_vals.append(i)
forecast_data = pd.DataFrame(month_vals, columns = ['Prediction'])
# forecast_data['URUTAN'] = month_vals

forecast_data['date'] = pd.date_range(start='10/1/2021', periods=len(forecast_data), freq='M')

forecast_data

forecast_data.set_index('date')

forecast_predictions = []

first_eval_batch = scaled_test[-n_input:]
current_batch = first_eval_batch.reshape((1, n_input, n_features))

for i in range(len(forecast_data)):
    
    # get the prediction value for the first batch
    current_pred = model.predict(current_batch)[0]
    
    # append the prediction into the array
    forecast_predictions.append(current_pred) 
    
    # use the prediction to update the batch and remove the first value
    current_batch = np.append(current_batch[:,1:,:],[[current_pred]],axis=1)

forecast_data['Prediction']=forecast_predictions

forecast_data

forecast_data['Prediction'] = forecast_data['Prediction'].astype(float, errors = 'raise')

"""## 5. Masking the dates"""

mask = (forecast_data['date'] > '2021-10-31') & (forecast_data['date'] <= '2021-12-31')

mask2 = forecast_data.loc[mask]

mask2

inflation_average_rate = (mask2['Prediction'].sum())/mask2.shape[0]

print(inflation_average_rate)

