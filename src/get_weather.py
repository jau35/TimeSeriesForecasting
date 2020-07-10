import argparse
import os
import requests
import json
from calendar import monthrange
from datetime import date

API_ROOT_URL = 'https://api.weather.com/v1'
API_HISTORICAL_ENDPOINT = 'location/%s/observations/historical.json'

PHL_LOCATION_CODE = 'KPHL:9:US'

# Shape of params object
# params = {
#     'apiKey': 'abc123',
#     'units': 'e',
#     'startDate': '20180624',
#     'endDate': '20180624'
# }


def parseArgs():
    ''' 
    Parse command line arguments
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--key',      '-k',     required=True,
                        help='API key')
    parser.add_argument('--location', '-l',     default=PHL_LOCATION_CODE,
                        type=str,   help='Location code. Default: \'KPHL:9:US\'')
    parser.add_argument('--start-date', '-s',   default=str(date.today()),
                        type=str,   help='Start date (YYYY-mm-dd). Default: date.today()')
    parser.add_argument('--end-date', '-e',     default=str(date.today()),
                        type=str,   help='End date (YYYY-mm-dd). Default: date.today()')
    parser.add_argument('--units',    '-u',     default='e',
                        type=str,   help='Unit code. Default: \'e\'')
    parser.add_argument('--outdir',    '-o',    default='./target',
                        type=str,   help='Output directory. Default: \'./target\'')
    args = parser.parse_args()
    return args


def params_to_string(params):
    params_list = ['%s=%s' % (k, v) for k, v in params.items()]
    return '&'.join(params_list)


def send_request(base_url, params):
    request_url = '%s?%s' % (
        base_url,
        params_to_string(params)
    )

    response = requests.get(request_url)
    return response


def collect_data(base_url, params, start_date, end_date, target_dir):
    '''There's a 31 day limit for each request, so fetch data one month at a time'''
    s_YYYY, s_mm, s_dd = [int(x) for x in start_date.split('-')]
    e_YYYY, e_mm, e_dd = [int(x) for x in end_date.split('-')]

    for y in range(s_YYYY, e_YYYY+1):
        m1 = s_mm if y == s_YYYY else 1
        m2 = e_mm if y == e_YYYY else 12
        for m in range(m1, m2+1):
            d1 = s_dd if y == s_YYYY and m == s_mm else 1
            d2 = e_dd if y == e_YYYY and m == e_mm else monthrange(y, m)[1]

            params['startDate'] = '%04d%02d%02d' % (y, m, d1)
            params['endDate'] = '%04d%02d%02d' % (y, m, d2)

            response = send_request(base_url, params)
            if response.status_code != 200:
                print("Error retrieving data for time frame: %s -> %s" %
                      (params['startDate'], params['endDate']))
                print(response.reason)
                continue

            # write response to file
            out_file = os.path.join(target_dir, '%s_%s.json' % (
                params['startDate'], params['endDate']))
            with open(out_file, 'w') as f:
                json.dump(response.json(), f, indent=4)


def main():
    args = parseArgs()

    if not os.path.isdir(args.outdir):
        os.makedirs(args.outdir)

    start_date = args.start_date
    end_date = args.end_date

    params = {
        'apiKey': args.key,
        'units': args.units
    }

    base_url = '%s/%s' % (
        API_ROOT_URL,
        API_HISTORICAL_ENDPOINT % args.location
    )

    collect_data(base_url, params, start_date, end_date, args.outdir)


if __name__ == '__main__':
    main()
