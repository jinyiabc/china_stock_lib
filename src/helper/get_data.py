import os
import zipfile
import urllib.request
from urllib.error import HTTPError

import pandas as pd

from helper.WSDLoader import WSDLoader

base_url = "https://github.com/jinyiabc/china_stock_data/raw/main/"


def get_data(rel_url):
    url = base_url + rel_url
    local_file = os.path.basename(url)
    try:
        urllib.request.urlretrieve(url, local_file)
    except HTTPError as err:
        print(err)
        print("Unable to download data")
        return None

    if url.endswith('.zip'):
        z = zipfile.ZipFile(local_file)
        z.extractall()
        info = z.infolist().pop(0)
        print("Downloaded {}".format(os.path.split(info.filename)[0]))
    else:
        print("Downloaded {}".format(local_file))


def get_module_1(username):
    get_data("module-{0:02n}/{1:s}.zip".format(1, username))


def get_module_2(username):
    get_data("module-{0:02n}/{1:s}.zip".format(2, username))

def get_module_3(username):
    get_data("module-{0:02n}/{1:s}".format(3, username))


def get_data_sql(wind_codes, start_date, end_date, database, table_name, field, options):
    '''
    wind_codes = list of wind_code
    start_date = '2011-01-01'
    end_date = '2022-01-24'
    table_name = 'portfolio0124b'
    database = 'test1'
    field = "trade_code,close,windcode"
    options =  "PriceAdj=B",
    '''

    loader = WSDLoader(start_date, end_date, database, table_name, field, options)

    # Get data from wind api.
    # loader.fetch_historical_data(wind_codes,)

    # Get data from mysql.
    date = pd.date_range(start_date, end_date)
    data = pd.DataFrame(index=date, columns=['sector'])
    data.index.name = 'date'

    for wind_code in wind_codes:
        wsd_data = loader.fetchall_data(wind_code)
        # print(wsd_data['CLOSE'])
        wsd_data.rename(columns={'CLOSE': wind_code}, inplace=True)
        # data = data.join(wsd_data[f"{wind_code}"])
        data = data.join(wsd_data.set_index('index')[wind_code])

    # drop bond due to negative close price due to "PriceAdj=F".
    # data.drop(columns=["sector", "113017.SH", "128062.SZ"], inplace=True)
    # Drop sector only.
    data.drop(columns=["sector", ], inplace=True)
    # print(data)
    # data.to_csv(f'resource/portfolio0124b.csv', mode='a')
    return data