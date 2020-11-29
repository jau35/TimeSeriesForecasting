import argparse
import os
import sys
import pandas as pd
from math import sqrt
from matplotlib import pyplot
from numpy import concatenate
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM

# order columns for dataframe
DF_COLS = ['precip', 'temp', 'uv_index', 'water_temp']
N_FEATURES = 4

def parseArgs():
    '''
    Parse command line arguments
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--indir',    '-i',   default='./data/processed', type=str,
                        help='Input directory for processed data files. Default: \'./data/processed\'')
    parser.add_argument('--fill',   '-f',     default='locf',   choices=['locf', 'interpolate'],
                        type=str,   help='Method for missing data imputation. Used to determine which data file to use. Default: \'locf\'')
    parser.add_argument('--lag',  default=1,
                        type=int,   help='Number of lag observations. Default: 1')
    parser.add_argument('--lead',  default=1,
                        type=int,   help='Number of steps to forecast. Default: 1')
    parser.add_argument('--outdir',   '-o',    default='./target',
                        type=str,   help='Output directory. Default: \'./target\'')
    args = parser.parse_args()
    return args

def plot(values, columns):
    # plot each column
    pyplot.figure()
    n = values.shape[1]
    for i in range(n):
        pyplot.subplot(n, 1, i+1)
        pyplot.plot(values[:, i])
        pyplot.title(columns[i], y=0.5, loc='right')
    pyplot.show()

def normalize_data(values, scaler=None):
    if scaler is None:
        scaler = MinMaxScaler(feature_range=(0,1))
        scaler = scaler.fit(values)
    
    normalized_values = scaler.transform(values)

    return scaler, normalized_values

def invert_normalized_data(values, X, scaler):
    inv = concatenate((X[:, (1 - N_FEATURES):], values), axis=1)
    inv = scaler.inverse_transform(inv)
    return inv[:,(N_FEATURES-1)]

def convert_to_supervised(df, lag=1, lead=1):
    # number of variables
    n = df.shape[1]

    columns = df.columns
    cols, names = list(), list()
    # construct prior observations (t-lag ... t-1)
    for i in range(lag, 0, -1):
        cols.append(df.shift(i))
        names += [('%s(t-%d)' % (columns[j], i)) for j in range(n)]
        
    # construct future observations (t ... t+lead-1)
    for i in range(0, lead):
        cols.append(df.shift(-i))
        name_format = '%s(t+%d)'
        names += [('%s(t+%d)' % (columns[j], i)) for j in range(n)]
    
    supervised_df = pd.concat(cols, axis=1)
    supervised_df.columns = names
    supervised_df.dropna(inplace=True)

    return supervised_df
    

def prep_data(data_file, lag, lead):
    df = pd.read_csv(data_file, index_col=0).sort_index()
    df = df[DF_COLS] # reorder columns
    df.dropna(axis='index', how='any', inplace=True)

    columns = df.columns
    values = df.values
    values = values.astype('float32')
    #plot(values, columns)

    # normalize features
    scaler, normalized_values = normalize_data(values)
    #plot(normalized_values, columns)

    # convert to supervised dataset
    series_df = pd.DataFrame(normalized_values)
    series_df.columns = columns
    supervised_df = convert_to_supervised(series_df, lag, lead)

    # drop colums we don't want to predict
    n = df.shape[1]
    drop_cols = [x for x in range (n*lag, n*lag + n*lead) if (x+1) % n != 0]
    supervised_df.drop(supervised_df.columns[drop_cols], axis=1, inplace=True)

    return supervised_df, scaler

def train(df, lag, scaler):
    # split up train and test sets (.67/.33 split)
    values = df.values
    n_train = int(0.67 * df.shape[0])
    train = values[:n_train, :]
    test = values[n_train:, :]

    # split up input and output features
    n_x = lag * N_FEATURES
    train_x, train_y = train[:, :n_x], train[:, n_x:]
    test_x, test_y = test[:, :n_x], test[:, n_x:]

    # reshape input to be 3D [samples, lag, features]
    train_x = train_x.reshape((train_x.shape[0], lag, N_FEATURES))
    test_x = test_x.reshape((test_x.shape[0], lag, N_FEATURES))

    # design network
    model = Sequential()
    model.add(LSTM(50, input_shape=(train_x.shape[1], train_x.shape[2])))
    model.add(Dense(1))
    model.compile(loss='mae', optimizer='adam')
    # fit network
    history = model.fit(train_x, train_y, epochs=50, batch_size=72, validation_data=(test_x, test_y), verbose=2, shuffle=False)
    # # plot history
    # pyplot.plot(history.history['loss'], label='train')
    # pyplot.plot(history.history['val_loss'], label='test')
    # pyplot.legend()
    # pyplot.show()
    
    # make a prediction
    yhat = model.predict(test_x)
    test_x = test_x.reshape((test_x.shape[0], test_x.shape[2]*lag))

    # invert scaling for forecast
    inv_yhat = invert_normalized_data(yhat, test_x, scaler)

    # invert scaling for actual
    test_y = test_y.reshape((len(test_y), 1))
    inv_y = invert_normalized_data(test_y, test_x, scaler)

    # calculate RMSE
    rmse = sqrt(mean_squared_error(inv_y, inv_yhat))
    print('Test RMSE: %.3f' % rmse)


def main():
    args = parseArgs()

    lag, lead = args.lag, args.lead

    if not os.path.isdir(args.indir):
        sys.exit('Directory not found: %s' % args.indir)

    data_file = os.path.join(args.indir, f'combined_{args.fill}.csv')

    if not os.path.isdir(args.outdir):
        os.makedirs(args.outdir)
    
    df, scaler = prep_data(data_file, lag, lead)

    train(df, lag, scaler)


if __name__ == '__main__':
    main()
