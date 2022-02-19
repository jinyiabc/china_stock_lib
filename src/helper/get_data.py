import numpy as np
import os
import zipfile
import urllib.request
from urllib.error import HTTPError

import pandas as pd

# from helper.Loader import Loader

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


def get_data_sql(start_date, end_date, dataframe, field):
    '''
    wind_codes = list of wind_code
    start_date = '2011-01-01'
    end_date = '2022-01-24'
    table_name = 'portfolio0124b'
    database = 'test1'
    field = "trade_code,close,windcode"
    options =  "PriceAdj=B",
    '''
    # Get data from mysql.
    date = pd.date_range(start_date, end_date)
    data = pd.DataFrame(index=date, columns=['dummy_column'])
    data.index.name = 'date'
    # data = pd.DataFrame(index=dataframe['index'])
    wind_codes = dataframe['WINDCODE'].drop_duplicates().to_list()
    for index, wind_code in enumerate(wind_codes):
        # wsd_data = Loader.fetch_data(database, table_name, wind_code, field)
        wsd_data = dataframe.query(f"WINDCODE=='{wind_code}'")
        # wsd_data = wsd_data.copy(deep=True)
        wsd_data = wsd_data.rename(columns={field: wind_code,})
        data = data.join(wsd_data.set_index('index')[wind_code])

    data.drop(columns=["dummy_column", ], inplace=True)
    data.drop_duplicates(inplace=True)
    # drop bond due to negative close price due to "PriceAdj=F".
    # data.drop(columns=["sector", "113017.SH", "128062.SZ"], inplace=True)
    # Drop sector only.
    # data.drop(columns=["dummy_column", ], inplace=True)
    # print(data)
    # data.to_csv(f'resource/portfolio0124b.csv', mode='a')
    return data

def pivot_table_all(dataframe, index, columns, values,):

    table = pd.pivot_table(dataframe, values=values, index=index,
                           columns=columns, aggfunc=np.sum)

    # convert columns from multiindex to single index.
    df = table.columns
    columns = df.to_list()
    table.columns = columns
    # rename index name to date.
    table.index.name = 'date'

    return table