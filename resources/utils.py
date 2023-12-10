from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn import tree
from sklearn import linear_model
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from sklearn.model_selection import train_test_split
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import numpy
import pandas as pd
import math
from sklearn.linear_model import ElasticNet
import os

# convert an array of values into a dataset matrix
def create_dataset(dataset, look_back=1):
    dataX, dataY = [], []
    for i in range(len(dataset) - look_back):
        a = dataset[i:(i + look_back), 0]
        dataX.append(a)
        dataY.append(dataset[i + look_back, 0])
    return numpy.array(dataX), numpy.array(dataY)

# create dataset from the dataframe
def create_preprocessed_Dataset(df):
    df.drop(df.columns.difference(['date', 'open']), 1, inplace=True)
    df = df['open']
    dataset = df.values
    dataset = dataset.reshape(-1, 1)
    dataset = dataset.astype('float32')

    # split into train and test sets
    train_size = len(dataset) - 2
    train, test = dataset[0:train_size, :], dataset[train_size:len(dataset), :]

    # reshape into X=t and Y=t+1
    look_back = 1
    trainX, trainY = create_dataset(train, look_back)
    testX, testY = create_dataset(test, look_back)

    # reshape input to be [samples, time steps, features]
    # trainX = numpy.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
    # testX = numpy.reshape(testX, (testX.shape[0], 1, testX.shape[1]))

    return trainX, trainY, testX, testY