#!/bin/env python3
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
import random as rand
import sys
import operator
# read in the simulation portfolio information
day = int(input())
cash = float(input())
value = float(input())
nstocks = int(input())
stocks = {}

for i in range(nstocks):
  line = input()
  id, shares = line.split()
  id = int(id)
  shares = int(shares)
  stocks[id] = shares

# read in the stock data
data = pd.read_csv(sys.stdin)

model_close = tf.keras.models.load_model('bawls.keras')
model_open = tf.keras.models.load_model('nuts.keras')

stock_predictions_close={}
stock_predictions_open={}

for ind in data.index:
    data_X=[]
    for i in range(0,10):
        data_X.append(rand.uniform(float(data['low'][ind]),float(data['high'][ind])))
    data_X.append(float(data['close'][ind]))
    scaler=MinMaxScaler()
    data_X=scaler.fit_transform(np.array(data_X).reshape(-1,1))

    #prediction=data_X
    prediction = model_close.predict(data_X,verbose=0)

    #stock_predictions_close.update({int(data['id'][ind]):[prediction[0],float(data['close'][ind])]})
    stock_predictions_close.update({int(data['id'][ind]):[scaler.inverse_transform(prediction).mean(),float(data['close'][ind])]})


for ind in data.index:
    data_X=[]
    for i in range(0,10):
        data_X.append(rand.uniform(float(data['low'][ind]),float(data['high'][ind])))
    data_X.append(float(data['open'][ind]))
    scaler=MinMaxScaler()
    data_X=scaler.fit_transform(np.array(data_X).reshape(-1,1))

    #prediction=data_X
    prediction = model_open.predict(data_X,verbose=0)

    stock_predictions_open.update({int(data['id'][ind]):[scaler.inverse_transform(prediction).mean(),float(data['open'][ind])]})
    #stock_predictions_open.update({int(data['id'][ind]):[prediction[0],float(data['open'][ind])]})

for key in stocks.keys():
    if key in stock_predictions_close.keys():  
        if stock_predictions_open[key][0] <= stock_predictions_open[key][1]:
            print(f"SO {key} {stocks[key]}")
    if key in stock_predictions_close.keys():
        if stock_predictions_close[key][0] <= stock_predictions_close[key][1]:
            print(f"SC {key} {stocks[key]}")

futureValues={'open':[],'close':[]}

for stock_id in stock_predictions_close.keys():
    futureValues['close'].append({'id':stock_id,'future value':stock_predictions_close[stock_id][0]-stock_predictions_close[stock_id][1]})
for stock_id in stock_predictions_open.keys():
    futureValues['open'].append({'id':stock_id,'future value':stock_predictions_open[stock_id][0]-stock_predictions_open[stock_id][1]})

sorted_opening_stocks = sorted(futureValues['open'], key=operator.itemgetter('future value'), reverse=True)
sorted_closing_stocks = sorted(futureValues['close'], key=operator.itemgetter('future value'), reverse=True)

stock_id_to_buy=sorted_opening_stocks[0]['id']
print(f"BO {int(stock_id_to_buy)} {int((cash*0.15)/stock_predictions_open[stock_id_to_buy][1])}")
stock_id_to_buy=sorted_opening_stocks[1]['id']
#stock_id_to_buy=next(iter(sorted_opening_stocks['id']))
print(f"BO {stock_id_to_buy} {int((cash*0.10)/stock_predictions_open[stock_id_to_buy][1])}")
#stock_id_to_buy=next(iter(sorted_opening_stocks['id']))
stock_id_to_buy=sorted_opening_stocks[2]['id']
print(f"BO {stock_id_to_buy} {int((cash*0.10)/stock_predictions_open[stock_id_to_buy][1])}")



stock_id_to_buy=sorted_closing_stocks[0]['id']
print(f"BC {int(stock_id_to_buy)} {int((cash*0.15)/stock_predictions_close[stock_id_to_buy][1])}")
stock_id_to_buy=sorted_closing_stocks[1]['id']
#stock_id_to_buy=next(iter(sorted_opening_stocks['id']))
print(f"BC {int(stock_id_to_buy)} {int((cash*0.10)/stock_predictions_close[stock_id_to_buy][1])}")
#stock_id_to_buy=next(iter(sorted_opening_stocks['id']))
stock_id_to_buy=sorted_closing_stocks[2]['id']
print(f"BC {int(stock_id_to_buy)} {int((cash*0.10)/stock_predictions_close[stock_id_to_buy][1])}")
#stock_id_to_buy=next(iter(sorted_closing_stocks['id']))
#print("BC {stock_id_to_buy} {(cash*0.15)/stock_predictions_close[stock_id_to_buy][1]}")
#stock_id_to_buy=next(iter(sorted_closing_stocks['id']))
#print("BC {stock_id_to_buy} {(cash*0.10)/stock_predictions_close[stock_id_to_buy][1]}")
#stock_id_to_buy=next(iter(sorted_closing_stocks['id']))
#print("BC {stock_id_to_buy} {(cash*0.10)/stock_predictions_close[stock_id_to_buy][1]}")
