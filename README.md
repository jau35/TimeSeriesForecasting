# TimeSeriesForecasting

An exploration of Multivariate Multi-Step Time Series Forecasting for Stream Temperature predictions

## Case Study: Valley Creek

**The Goal:** Train a Long Short-Term Memory network to predict stream temperature trends based on the following variables:

- Recent stream temperature measurements
- Air temperature
- UV index
- Precipitation

## Environment Setup

I'm working with the following environment

- macOS Catalina (Version 10.15.1)
- Python 3.7.2
- Keras 2.4.3
- TensorFlow 2.2.0

#### Create virtualenv

```
python3 -m virtualenv venv
source venv/bin/activate
```

#### Install packages

I've also included a requirements.txt for convenience

```
pip install tensorflow
pip install Keras
pip install scikit-learn
pip install pandas
pip install matplotlib
```

## src/

### get_weather.py

Utility script to collect the raw weather data I will be using.

```
usage: get_weather.py [-h] --key KEY [--location LOCATION]
                      [--start-date START_DATE] [--end-date END_DATE]
                      [--units UNITS] [--outdir OUTDIR]

optional arguments:
  -h, --help            show this help message and exit
  --key KEY, -k KEY     API key
  --location LOCATION, -l LOCATION
                        Location code. Default: 'KPHL:9:US'
  --start-date START_DATE, -s START_DATE
                        Start date (YYYY-mm-dd). Default: date.today()
  --end-date END_DATE, -e END_DATE
                        End date (YYYY-mm-dd). Default: date.today()
  --units UNITS, -u UNITS
                        Unit code. Default: 'e'
  --outdir OUTDIR, -o OUTDIR
                        Output directory. Default: './target'
```

- Example:

```
python src/get_weather.py -k {key} -o data/raw/phl.historical.weather -u e -l KPHL:9:US -s 2018-10-01 -e 2020-06-25
```

<details>
  <summary style='font-size: 18px'>Data</summary>

The dataset I'm using comes from a combination of USGS Water Data provided through the National Water Information System, as well as historical weather data collected from Wunderground.

- USGS Water Data from Valley Creek @ Pennsylvania Turnpike Bridge near Valley Forge, PA
  - Sub-hourly (15 minutes) records dating from 10/01/2018 - 06/25/2020
  - Data includes the following data points, with particular interest in temperature and precipitation
    - Datetime
    - Gage height
    - Discharge
    - Turbidity
    - Precipitation
    - Specific conductance
    - Temperature
  - See data/raw/nwis.waterdata.usgs.gov.txt for the raw dataset
- Weather Data from Philadelphia International Airport Station
  - Hourly records dating from 10/01/2018 - 06/25/2020
  - Data includes the following data points, with particular interest in air temperature and UV index
    - Timestamp (Unix time)
    - Temperature
    - UV index
    - Pressure
    - Dew point
    - Heat index
    - Precipitation
    - Wind speed
    - Wind direction
  - See data/raw/phl.historical.weather for the raw dataset

Additional notes:

- While the USGS Water Data readings fall nicely in 15-minute increments on the hour (at :00, :15, :30, and :45 minutes), the weather data does not. Actually, it doesn't even fall in even increments, as it seems to vary between 15, 30, and 60 minute intervals between successive observations, and the observations never fall on the hour. The data will need some extra preparation to line the two datasets up by their timestamps.
- It's also worth pointing out that the historical weather data was recorded at Philadelphia International Airport, which is roughly 20 miles southeast of where the Valley Creek Water Station is located. I'm making the (potentially incorrect) assumption that this distance is negligible and that the weather observed at PHL would be the same as the weather observed in Valley Forge.
</details>

<details>
  <summary style='font-size: 18px'>Resources</summary>

- USGS Water Data
  - [National Water Information System](https://waterdata.usgs.gov/nwis)
  - [Web services](https://waterservices.usgs.gov/)
  - [Valley Creek - Station data](https://waterdata.usgs.gov/pa/nwis/uv?cb_00010=on&cb_00045=on&cb_00060=on&cb_00065=on&cb_00095=on&cb_63680=on&format=gif_default&site_no=01473169&period=&begin_date=2020-06-18&end_date=2020-06-25)
- Weather Data
  - [NOAA - Land Based Station Data](https://www.ncdc.noaa.gov/data-access/land-based-station-data)
    - Might be able to search for datasets [here](https://www.ncei.noaa.gov/access/search/data-search/global-hourly?pageSize=100)
  - [Wunderground](https://www.wunderground.com/history/daily/us/pa/philadelphia/KPHL)
  - [meteostat](https://dev.meteostat.net/)
    - Free access to historical climate data with non-commercial purposes
    ```
    curl --header "x-api-key: {key}" "https://api.meteostat.net/v2/stations/hourly?station=72408&start=2018-10-01&end=2018-10-01"
    ```
  - [weather.gov API](https://www.weather.gov/documentation/services-web-api)
  </details>

<details>
  <summary style='font-size: 18px'>Related Articles</summary>

- [A Quick Example of Time-Series Prediction Using Long Short-Term Memory (LSTM) Networks](https://medium.com/swlh/a-quick-example-of-time-series-forecasting-using-long-short-term-memory-lstm-networks-ddc10dc1467d)
- [Time Series Forecasting - ARIMA, LSTM, Prophet with Python](https://medium.com/@cdabakoglu/time-series-forecasting-arima-lstm-prophet-with-python-e73a750a9887)
- [Time Series Forecasting with the Long Short-Term Memory Network in Python](https://machinelearningmastery.com/time-series-forecasting-long-short-term-memory-network-python/)
- [Multi-step Time Series Forecasting with Long Short-Term Memory Networks in Python](https://machinelearningmastery.com/multi-step-time-series-forecasting-long-short-term-memory-networks-python)
- [Multivariate Time Series Forecasting with LSTMs in Keras](https://machinelearningmastery.com/multivariate-time-series-forecasting-lstms-keras/)
- [How to Develop Multivariate Multi-Step Time Series Forecasting Models for Air Pollution](https://machinelearningmastery.com/how-to-develop-machine-learning-models-for-multivariate-multi-step-air-pollution-time-series-forecasting/)
- [On the Suitability of Long Short-Term Memory Networks for Time Series Forecasting](https://machinelearningmastery.com/suitability-long-short-term-memory-networks-time-series-forecasting/)
- [How to Convert a Time Series to a Supervised Learning Problem in Python](https://machinelearningmastery.com/convert-time-series-supervised-learning-problem-python/)
</details>
