import os
import pandas as pd
import shutil

from src.helper import get_data
from src.helper.Loader import Loader
from src.helper.get_data import holiday2businessday, day2month
from src.helper.wind import read_wind_excel, read_wind_csv


def test_get_data():
    get_data.get_module_1('survivorship_free')
    assert os.path.isdir("survivorship_free")
    shutil.rmtree("survivorship_free")
    os.remove("survivorship_free.zip")

def test_read_wind_excel():
    dir = os.path.join('..', '../quant/_notebooks')
    df = read_wind_excel(f'{dir}/csi300.xlsx', '2015-6-18', '2018-6-18',
                                 skiprows=0,   # false
                                 header=0,)    # start from 1st line
    print(df)
    pass

def test_read_wind_csv():
    dir = os.path.join('..', '../quant/CSI/wind_csi300')
    df = read_wind_csv(f'{dir}/600602.SH.CSV', '2015-6-18', '2018-6-18',
                                skiprows=0,
                                 header=0,)
    print(df)
    pass

def test_get_data1():
    get_data.get_module_3('300072.csv')
    # assert os.path.isdir("survivorship_free")
    # shutil.rmtree("survivorship_free")
    # os.remove("survivorship_free.zip")

def test_holiday2businessday():
    import pandas as pd
    datelist = pd.period_range(start='2018-01-01', end='2018-12-31', freq='D')
    print(holiday2businessday(datelist))

def test_day2month():
    database = 'market_research'
    table_name = 'ohlc'
    start_date = "2012-01-01"
    end_date = "2022-01-26"
    # Get Close data
    wind_codes = pd.read_csv('resource/sample.txt', sep=' ', header=None, )
    wind_codes = wind_codes[0].to_list()
    field = "symbol,date,close,open,high,low"
    loader = Loader(start_date, end_date, database, table_name, field, None)
    df = loader.fetch_data(database, table_name, wind_codes, field)

    table2 = (
        df
            .groupby(['date', 'symbol'])
            .mean()
            .unstack('symbol')
    )
    olhc_month = day2month(table2, swaplevel=True)
    print(olhc_month)