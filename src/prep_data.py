import argparse
import os
import sys
import json
import csv
import time
from datetime import date
from functools import partial
import pandas as pd

USGS_WATER_DATA_FILE = 'nwis.waterdata.usgs.gov.txt'
PHL_WEATHER_HISTORY_DIR = 'phl.historical.weather'

USGS_WATER_DATA_COLS = [
    {'idx': 0, 'cd': 'agency_cd', 'name': 'agency', 'use': False},
    {'idx': 1, 'cd': 'site_no', 'name': 'site_no', 'use': False},
    {'idx': 2, 'cd': 'datetime', 'name': 'datetime', 'use': True, 'primary': True},
    {'idx': 3, 'cd': 'tz_cd', 'name': 'tz', 'use': True, 'primary': True},
    {'idx': 4, 'cd': '121492_00065', 'name': 'gage_height', 'use': False},
    {'idx': 5, 'cd': '121492_00065_cd', 'name': 'gage_cd', 'use': False},
    {'idx': 6, 'cd': '121493_00060', 'name': 'discharge', 'use': False},
    {'idx': 7, 'cd': '121493_00060_cd', 'name': 'discharge_cd', 'use': False},
    {'idx': 8, 'cd': '121495_63680', 'name': 'turbidity', 'use': False},
    {'idx': 9, 'cd': '121495_63680_cd', 'name': 'turbidity_cd', 'use': False},
    {'idx': 10, 'cd': '121496_00045', 'name': 'precip', 'use': True},
    {'idx': 11, 'cd': '121496_00045_cd', 'name': 'precip_cd', 'use': False},
    {'idx': 12, 'cd': '243576_00095', 'name': 'specific_conductance', 'use': False},
    {'idx': 13, 'cd': '243576_00095_cd', 'name': 'conductance_cd', 'use': False},
    {'idx': 14, 'cd': '247057_00010', 'name': 'water_temp', 'use': True},
    {'idx': 15, 'cd': '247057_00010_cd', 'name': 'temperature_cd', 'use': False}
]

WEATHER_DATA_FIELDS = [
    {'attr': 'valid_time_gmt', 'primary': True},
    {'attr': 'temp'},
    {'attr': 'uv_index'},
]


def parseArgs():
    '''
    Parse command line arguments
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--indir',    '-i', default='./data', type=str,
                        help='Input directory for raw data files. Default: \'./data\'')
    parser.add_argument('--usgs-file',    '-usgs', default=USGS_WATER_DATA_FILE, type=str,
                        help='USGS Water data file. Default: \'%s\'' % USGS_WATER_DATA_FILE)
    parser.add_argument('--weather-dir',    '-wdir', default=PHL_WEATHER_HISTORY_DIR, type=str,
                        help='Directory for weather data files. Default: \'%s\'' % PHL_WEATHER_HISTORY_DIR)
    parser.add_argument('--outdir',   '-o',    default='./target',
                        type=str,   help='Output directory. Default: \'./target\'')
    parser.add_argument('--fill',   '-f',    default='omit',   choices=['omit', 'locf', 'interpolate'],
                        type=str,   help='Method for missing data imputation. Default: \'omit\'')
    parser.add_argument('--preprocessed',   '-p', default=None,
                        type=str,   help='Path to a combined, preprocessed csv file. If specified, this file will be used to initialize the combined data rather than calculating it all again')
    args = parser.parse_args()
    return args


def progress(iterable, total=None):
    fill = '█'
    width = 100

    if total is None:
        total = len(iterable)

    def printProgress(i):
        percent = '%d' % (100 * (i / float(total)))
        fillWidth = int(width * i // total)
        bar = fill * fillWidth + '-' * (width - fillWidth)
        print(f'Progress: |{bar}| {percent}%\r', end='')
        if i == total:
            print()

    printProgress(0)
    for i, item in enumerate(iterable):
        printProgress(i + 1)
        yield item


def convert_time(timestamp, multi_index):
    timestamp_format = "%Y-%m-%d %H:%M"
    if multi_index:
        timestamp = "%s %s" % timestamp
        timestamp_format = timestamp_format + " %Z"

    t = time.strptime(timestamp, timestamp_format)
    return int(time.mktime(t))


def read_usgs_data(usgs_data_file):
    usecols = [col for col in USGS_WATER_DATA_COLS if col['use']]
    index_col = [usecols.index(col)
                 for col in usecols if 'primary' in col and col['primary']]

    df = pd.read_csv(usgs_data_file,
                     sep='\t',
                     comment='#',
                     usecols=[col['idx'] for col in usecols],
                     index_col=index_col,
                     header=1,
                     names=[col['name'] for col in usecols],
                     skipinitialspace=True,
                     skip_blank_lines=True,
                     error_bad_lines=False,
                     warn_bad_lines=True
                     ).sort_index()

    to_epoch = partial(convert_time, multi_index=len(index_col) > 1)
    df.index = df.index.map(to_epoch)
    df.index.rename('time_gmt', inplace=True)

    return df


def read_weather_data(weather_data_dir):
    keep_cols = [field['attr'] for field in WEATHER_DATA_FIELDS]
    index = [field['attr']
             for field in WEATHER_DATA_FIELDS if 'primary' in field and field['primary']]

    weather_df = pd.DataFrame(columns=keep_cols)
    weather_df.set_index(index, inplace=True)

    for file in os.listdir(weather_data_dir):
        if os.path.splitext(file)[1] != '.json':
            continue
        file = os.path.join(weather_data_dir, file)
        with open(file, 'r') as f:
            obs = json.load(f)['observations']

        df = pd.DataFrame.from_dict(obs)

        drop_cols = [col for col in list(df.columns) if col not in keep_cols]
        df.drop(columns=drop_cols, inplace=True)
        df.set_index(index, inplace=True)

        weather_df = pd.concat([weather_df, df])

    return weather_df.sort_index()


def combine_data(usgs_df, weather_df, fill='omit', preprocessed=None):
    # use index from usgs dataframe
    index = [usgs_df.index.name]

    if preprocessed is not None and os.path.exists(preprocessed):
        df = pd.read_csv(preprocessed)
        df.set_index(index, inplace=True)
    else:
        cols = index.copy()
        cols.extend(list(usgs_df.columns))
        cols.extend(list(weather_df.columns))

        df = pd.DataFrame(columns=cols)
        df.set_index(index, inplace=True)

        # copy usgs_df data into df and augment it with the weather data
        df = df.append(usgs_df)
        df = augment(df, weather_df)

    if fill == 'interpolate':
        return df.astype(float).interpolate(method='linear',
                                            limit_direction='forward',
                                            limit_area='inside').round({
                                                'temp': 0,
                                                'uv_index': 0
                                            })
    elif fill == 'locf':
        return df.fillna(method='ffill').astype(float)
    else:
        return df.astype(float)


def save_data(df, t, temp, uv_index):
    df.loc[t, 'temp'] = temp
    df.loc[t, 'uv_index'] = uv_index


def augment(df, weather_df):
    '''
    Match up values in weather_df with the closest time values in df
    '''
    try:
        df_iter = df.iterrows()

        t1, _ = next(df_iter)
        t2, _ = next(df_iter)

        for t, data in progress(weather_df.iterrows(), total=weather_df.shape[0]):
            if t1 > t:
                continue
            while t2 < t:
                t1 = t2
                t2, _ = next(df_iter)

            if (t - t1) > (t2 - t):
                t1 = t2
                t2, _ = next(df_iter)

            df.loc[t1, 'temp'] = data.temp
            df.loc[t1, 'uv_index'] = data.uv_index
    except StopIteration:
        pass

    return df


def main():
    args = parseArgs()

    if not os.path.isdir(args.indir):
        sys.exit('Directory not found: %s' % args.indir)

    if not os.path.isdir(args.outdir):
        os.makedirs(args.outdir)

    usgs_df = read_usgs_data(
        os.path.join(args.indir, args.usgs_file)
    )
    usgs_df.to_csv(os.path.join(args.outdir, 'usgs.csv'))

    weather_df = read_weather_data(
        os.path.join(args.indir, args.weather_dir)
    )
    weather_df.to_csv(os.path.join(args.outdir, 'weather.csv'))

    combined_df = combine_data(
        usgs_df, weather_df, fill=args.fill, preprocessed=args.preprocessed)
    combined_df.to_csv(os.path.join(args.outdir, f'combined_{args.fill}.csv'))


if __name__ == '__main__':
    main()
