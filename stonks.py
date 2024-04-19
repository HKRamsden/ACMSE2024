
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout

def create_dataset(dataset, time_step = 1):
    dataX,dataY = [],[]
    for i in range(len(dataset)-time_step-1):
                   a = dataset[i:(i+time_step),0]
                   dataX.append(a)
                   dataY.append(dataset[i + time_step,0])
    return np.array(dataX),np.array(dataY)

stock_data = pd.read_csv('training.csv')
#d = {'id': [1, 2, 3, 4, 4, 3, 2, 1], 'day_number': [3, 4, 5, 6, 2, 8, 9, 10]}
#stock_data = pd.DataFrame(data=d)

stock_groups = stock_data.groupby(stock_data['id'])

dataListFull = []
dataListStockData = []
for name, df in stock_groups:
  df = df.sort_values(by='day_number', ascending=True)
  new_col = df['close'].shift(-1).values
  #print(new_col)
  new_data = {'future_price': new_col}
  #print(new_data)
  df = df.assign(**new_data)
  #print(df)
  df = df.dropna()
  #print(df)
  #print(df)
  dataListFull.append(df)
  dataListStockData.append(df.drop('future_price', axis=1))

labels = []
for data in dataListFull:
  labels.append(data.pop("future_price"))

modelLabels = pd.concat(labels)
dataListModel = pd.concat(dataListFull)
features = dataListModel[[
    'day_number', 'open',  'low', 'close', 'volume'
]]

closeData=dataListModel.reset_index()['close']
scaler=MinMaxScaler()
closeData=scaler.fit_transform(np.array(closeData).reshape(-1,1))

train_size = int(len(closeData)*0.65)
test_size = len(closeData) - train_size
train_data,test_data = closeData[0:train_size,:],closeData[train_size:len(closeData),:1]

time_step=100
X_train,Y_train=create_dataset(train_data,time_step)
X_test,Y_test=create_dataset(test_data,time_step)

model=Sequential()
model.add(LSTM(50,return_sequences=True,input_shape=(X_train.shape[1],1)))
model.add(LSTM(25,return_sequences=True))
model.add(LSTM(10))
model.add(Dense(1))
model.compile(loss='mean_squared_error',optimizer='adam')
model.fit(X_train,Y_train,validation_data = (X_test,Y_test),epochs = 10,batch_size = 256,verbose = 1)
model.save('bawls',save_format='tf')

