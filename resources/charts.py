import base64
from flask import Response, abort, jsonify, render_template
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_cors import cross_origin

from stocks import get_stock_data
from flask import current_app

from resources.utils import create_dataset

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import matplotlib.dates as mdates
import matplotlib
matplotlib.use('agg')

import plotly.graph_objects as go
import plotly.io as pio


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
from keras.preprocessing.sequence import TimeseriesGenerator

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

@charts_blp.route("/api/charts/update_cache")
class UpdateStockCache(MethodView):
    @charts_blp.response(200)
    def get(self):
        update_pse_data_cache(start_date='2022-01-01', verbose=True)
        return "Cache Updated"
    
def create_dataset(dataset, time_step = 1):
    dataX,dataY = [],[]
    for i in range(len(dataset)-time_step-1):
                   a = dataset[i:(i+time_step),0]
                   dataX.append(a)
                   dataY.append(dataset[i + time_step,0])
    return np.array(dataX),np.array(dataY)
  

    
@charts_blp.route("/api/charts/simple/<string:symbol>")
class Charts(MethodView):
    @charts_blp.response(200)
    def get(self,symbol):
        total_epochs = 50
        today = date.today().strftime('%Y-%m-%d')
        stock = symbol.upper()
        chartname = stock + '-' + today + '.png'
        chart_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'] + '/charts', chartname) 

        chartname_html = stock + '-' + today + '.html'
        chart_filepath_html = os.path.join('templates', chartname_html) 

        # Full Dataset    
        dataset_train = get_stock_data(stock, '2022-01-03', today, 'phisix')
        
        # get close column 
        close_data = dataset_train.iloc[:,3:4].values

        # Normalizing the dataset
        scaler = MinMaxScaler(feature_range=(0,1))
        scaled_set = scaler.fit_transform(close_data)

        split_percent = 0.70
        split = int(split_percent*len(close_data))

        close_train = scaled_set[:split]
        close_test =  scaled_set[split:]

        date_train = dataset_train.index.values[:split]
        date_test = dataset_train.index.values[split:]

        look_back = 15
        train_generator = TimeseriesGenerator(close_train, close_train, length=look_back, batch_size=20)     
        test_generator = TimeseriesGenerator(close_test, close_test, length=look_back, batch_size=1)

        model = Sequential()
        model.add(LSTM(50,activation='relu',input_shape=(look_back,1)))
        model.add(Dense(1))

        model.compile(loss = 'mean_squared_error',optimizer = 'adam')
        model.fit_generator(train_generator, epochs=total_epochs,verbose = 1)

        prediction = model.predict_generator(test_generator)

        close_train = scaler.inverse_transform(close_train)
        close_train = close_train.reshape((-1))

        close_test = scaler.inverse_transform(close_test)
        close_test = close_test.reshape((-1))

        prediction = scaler.inverse_transform(prediction)
        prediction = prediction.reshape((-1))

        # Plot
        trace1 = go.Scatter(
            x = date_train,
            y = close_train,
            mode = 'lines',
            name = 'Training Data'
        )
        trace3 = go.Scatter(
            x = date_test,
            y = prediction,
            mode = 'lines',
            name = 'Prediction'
        )
        trace2 = go.Scatter(
            x = date_test,
            y = close_test,
            mode='lines',
            name = 'Testing Data'
        )

        layout = go.Layout(
            title = "Stock",
            xaxis = {'title' : "Date"},
            yaxis = {'title' : "Close"}
        )
        

        # Forecasting 
        scaled_set = scaled_set.reshape((-1))

        def predict(num_prediction, model):
            prediction_list = scaled_set[-look_back:]
            
            for _ in range(num_prediction):
                x = prediction_list[-look_back:]
                x = x.reshape((1, look_back, 1))
                out = model.predict(x)[0][0]
                prediction_list = np.append(prediction_list, out)
            prediction_list = prediction_list[look_back-1:]
                
            return prediction_list
            
        def predict_dates(num_prediction):
            last_date = dataset_train.index.values[-1]
            prediction_dates = pd.date_range(last_date, periods=num_prediction+1).tolist()
            return prediction_dates
        
        num_prediction = 30
        forecast = predict(num_prediction, model)
        forecast = scaler.inverse_transform(forecast.reshape(-1, 1))

        forecast = forecast.reshape((-1))

        forecast_dates = predict_dates(num_prediction)

        # Add our prediction data to the chart
        trace4 = go.Scatter(
            x = forecast_dates,
            y = forecast,
            mode='lines',
            name = 'Forecast (30 Days)'
        )

        fig = go.Figure(data=[trace1, trace2, trace3, trace4], layout=layout)
        # fig.show()

        pio.write_image(fig, chart_filepath) 
        fig.write_html(chart_filepath_html)

        return render_template(chartname_html)

        

        