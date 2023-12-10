from flask import abort, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_cors import cross_origin
import base64

from stocks import get_stock_data
from flask import current_app

from resources.utils import create_dataset

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import matplotlib.dates as mandates
import matplotlib
matplotlib.use('agg')

from datetime import date


# from matplotlib import pyplot as plt
from sklearn import linear_model
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, r2_score

import keras.backend as K
from keras.layers import LSTM, Dense, Dropout
from keras.models import Sequential
from keras.layers import Dense
from keras.callbacks import EarlyStopping
from keras.optimizers import Adam
from keras.models import load_model
from keras.layers import LSTM
from keras.utils import plot_model

import io
from base64 import encodebytes
from PIL import Image

from stocks import update_pse_data_cache

charts_blp = Blueprint("Charts", "charts", description="Chart Operation")

def getImageBytes(filePath):
    pil_img = Image.open(filePath, mode='r') # reads the PIL image
    byte_arr = io.BytesIO()
    pil_img.save(byte_arr, format='PNG') # convert the PIL image to byte array
    encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii') # encode as base64
    return encoded_img

@charts_blp.route("/api/charts/simple/<string:symbol>")
class Charts(MethodView):
    @charts_blp.response(200)
    def get(self,symbol):
        total_epochs = 50
        today = date.today().strftime('%Y-%m-%d')
        stock = symbol.upper()
        chartname = stock + '-' + today + '.png'
        chart_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'] + '/charts', chartname) 

        if os.path.isfile(chart_filepath):
          with open(chart_filepath, 'rb') as image_file:
            base64_bytes = base64.b64encode(image_file.read())

            return {
                'img_base64': base64_bytes.decode("utf-8")
            }

        # Training Data    
        dataset_train = get_stock_data(stock, '2022-01-03', '2023-06-01', 'phisix')

        training_set = dataset_train.iloc[:,3:4].values

        training_set_len = training_set.shape[0]

        print(training_set.shape)
        print(training_set_len)

        # Normalizing the dataset
        scaler = MinMaxScaler(feature_range=(0,1))
        scaled_set = scaler.fit_transform(training_set)

        # Create X and y train data structures
        X_train=[]
        y_train=[]
        for i in range (60, training_set_len):
            X_train.append(scaled_set [i - 60:i, 0])
            y_train.append(scaled_set [i, 0])

        X_train = np.array(X_train)
        y_train = np.array(y_train)

        # print(X_train.shape)
        # print(y_train.shape)

        # reshape the data
        X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

        # print(X_train.shape)
        # print(X_train[:10])

        # building the LSTM Model
        regressor = Sequential()
        regressor.add(LSTM(units=50, return_sequences=True, input_shape= ( X_train.shape[1], 1) ))
        regressor.add(Dropout(0.2))

        regressor.add(LSTM(units=50, return_sequences=True))
        regressor.add(Dropout(0.2))

        regressor.add(LSTM(units=50, return_sequences=True))
        regressor.add(Dropout(0.2))

        regressor.add(LSTM(units=50, return_sequences=False))
        regressor.add(Dropout(0.2))

        regressor.add(Dense(units=1))

        # Fitting the model
        regressor.compile(optimizer="Adam",loss="mean_squared_error")
        regressor.fit(X_train, y_train, epochs=total_epochs, batch_size=32)


        # Predict Data Start
        # Get the actual stock prices after the training price   
        dataset_test = get_stock_data(stock, '2023-06-01', today, 'phisix')
        actual_stock_price = dataset_test.iloc[:,3:4].values

        print('** actual ***')
        print(actual_stock_price[:5])

        dataset_total = pd.concat( (dataset_train.close, dataset_test.close), axis=0 )
        inputs = dataset_total[len(dataset_total) - len(dataset_test) - 60: ].values


        # print(dataset_total.shape)
        # print(inputs.shape)
        inputs_len = inputs.shape[0]

        inputs = inputs.reshape(-1, 1)
        
        inputs = scaler.transform(inputs)

        print('** inputs ***')
        # print(inputs.shape)


        X_test=[]
        for i in range (60,inputs_len):
            X_test.append( inputs[i-60:i, 0] )
        
        X_test = np.array(X_test)

        print('** X_test before reshape***')
        print(X_test.shape)

        X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

        print('** X_test after reshape***')
        print(X_test.shape)

        # predict the values
        predicted_stock_price = regressor.predict(X_test)
        predicted_stock_price = scaler.inverse_transform(predicted_stock_price)

        #Predicted vs Close Value – LSTM
        # fig, ax = plt.subplots()
        # fig.canvas.draw()
        # ax.set_xticklabels(dataset_test.index, rotation=15)

        plt.figure(figsize=(10,6))
        plt.plot(actual_stock_price, color='blue', label='Actual Stock Price')
        plt.plot(predicted_stock_price, color='red', label='Predicted Stock Price')
        plt.title(stock + " Prediction by LSTM")
        plt.xlabel('Time Scale')
        plt.ylabel('Price')
        plt.legend()
        plt.savefig(chart_filepath)
        plt.close()

        # TEST DATA 
        # chartname = 'MER' + '2020-01-01' + '2020-12-30' + '.png'
        # chart_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'] + '/charts', chartname) 
        with open(chart_filepath, 'rb') as image_file:
            base64_bytes = base64.b64encode(image_file.read())

        return {
            'img_base64': base64_bytes.decode("utf-8")
        }
        
    
@charts_blp.route("/api/charts/update_cache")
class UpdateStockCache(MethodView):
    @charts_blp.response(200)
    def get(self):
        update_pse_data_cache(start_date='2022-01-01', verbose=True)
        return "Cache Updated"
            