# TimeSeriesForecasting

An exploration of Multivariate Multi-Step Time Series Forecasting for Stream Temperature predictions

## Case Study: Valley Creek

**The Goal:** Train a Long Short-Term Memory network to predict stream temperature trends based on the following variables:

- recent stream temperature measurements
- air temperature
- uv index
- precipitation

### Resources:

- USGS Water Data
  - [National Water Information System](https://waterdata.usgs.gov/nwis)
  - [Web services](https://waterservices.usgs.gov/)
  - [Valley Creek - Station data](https://waterdata.usgs.gov/pa/nwis/uv?cb_00010=on&cb_00045=on&cb_00060=on&cb_00065=on&cb_00095=on&cb_63680=on&format=gif_default&site_no=01473169&period=&begin_date=2020-06-18&end_date=2020-06-25)
- Weather Data
  - [NOAA - Land Based Station Data](https://www.ncdc.noaa.gov/data-access/land-based-station-data)
    - Might be able to search for datasets [here](https://www.ncei.noaa.gov/access/search/data-search/global-hourly?pageSize=100)
  - [Wunderground](https://www.wunderground.com/history/daily/us/pa/philadelphia/KPHL)
    - They discontinued their API, but daily, sub-hourly data can be acquired using a GET request like this, max 31 day span:  
      `GET https://api.weather.com/v1/location/KPHL:9:US/observations/historical.json?apiKey=6532d6454b8aa370768e63d6ba5a832e&units=e&startDate=20180624&endDate=20180624`
    - Data of interest:
      - valid_time_gmt
      - temp
      - uv_index
  - [meteostat](https://dev.meteostat.net/)
    - Free access to historical climate data with non-commercial purposes

### Related Articles:

- [A Quick Example of Time-Series Prediction Using Long Short-Term Memory (LSTM) Networks](https://medium.com/swlh/a-quick-example-of-time-series-forecasting-using-long-short-term-memory-lstm-networks-ddc10dc1467d)
- [Time Series Forecasting - ARIMA, LSTM, Prophet with Python](https://medium.com/@cdabakoglu/time-series-forecasting-arima-lstm-prophet-with-python-e73a750a9887)
- [Time Series Forecasting with the Long Short-Term Memory Network in Python](https://machinelearningmastery.com/time-series-forecasting-long-short-term-memory-network-python/)
- [Multi-step Time Series Forecasting with Long Short-Term Memory Networks in Python](https://machinelearningmastery.com/multi-step-time-series-forecasting-long-short-term-memory-networks-python)
- [Multivariate Time Series Forecasting with LSTMs in Keras](https://machinelearningmastery.com/multivariate-time-series-forecasting-lstms-keras/)
- [How to Develop Multivariate Multi-Step Time Series Forecasting Models for Air Pollution](https://machinelearningmastery.com/how-to-develop-machine-learning-models-for-multivariate-multi-step-air-pollution-time-series-forecasting/)
- [On the Suitability of Long Short-Term Memory Networks for Time Series Forecasting](https://machinelearningmastery.com/suitability-long-short-term-memory-networks-time-series-forecasting/)
