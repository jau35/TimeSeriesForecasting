# get_weather.py

Utility script used to collect the raw weather data I am using

## Usage

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

## Example

```
$ python src/get_weather.py -k {key} -o data/raw/phl.historical.weather -u e -l KPHL:9:US -s 2018-10-01 -e 2020-06-25
```

# process_data.py

Utility script to process and combine the USGS and weather data into one dataset. This pairs
up the two datasets by their timestamps, matching each weather observation with the closest USGS
observation. Optionally, gaps in the data can be filled in using either LOCF or linear interpolation.

## Usage

```
usage: process_data.py [-h] [--indir INDIR] [--usgs-file USGS_FILE]
                    [--weather-dir WEATHER_DIR] [--outdir OUTDIR]
                    [--fill {omit,locf,interpolate}]
                    [--preprocessed PREPROCESSED]

optional arguments:
  -h, --help            show this help message and exit
  --indir INDIR, -i INDIR
                        Input directory for raw data files. Default: './data/raw'
  --usgs-file USGS_FILE, -usgs USGS_FILE
                        USGS Water data file. Default:
                        'nwis.waterdata.usgs.gov.txt'
  --weather-dir WEATHER_DIR, -wdir WEATHER_DIR
                        Directory for weather data files. Default:
                        'phl.historical.weather'
  --outdir OUTDIR, -o OUTDIR
                        Output directory. Default: './target'
  --fill {omit,locf,interpolate}, -f {omit,locf,interpolate}
                        Method for missing data imputation. Default: 'omit'
  --preprocessed PREPROCESSED, -p PREPROCESSED
                        Path to a combined, preprocessed csv file. If
                        specified, this file will be used to initialize the
                        combined data rather than calculating it all again
```

## Example

```
$ python src/process_data.py -i data/raw -o data/processed -f omit
Progress: |███████████████████████████████████████████████| 100%
$ python src/process_data.py -i data/raw -o data/processed -f locf -p data/processed/combined_omit.csv
$ python src/process_data.py -i data/raw -o data/processed -f interpolate -p data/processed/combined_omit.csv
```
