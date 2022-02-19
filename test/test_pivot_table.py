import pandas as pd

from src.helper.Loader import Loader
from src.helper.get_data import get_data_sql, pivot_table_all


def test_get_data_sql():
    # file_path = 'resource/composition.xlsx'
    # df0 = pd.read_excel(file_path,
    #                     converters={
    #                         "证券代码":str
    #
    #                     }
    #                     ).rename(
    #                             columns={
    #                                 "证券代码": "ticker",
    #                                 "个股仓位%": "weights",
    #                                 "交易市场": "trader"
    #                             },
    # )
    # df0['wind_code'] = df0["ticker"] + df0["trader"].apply(lambda x: '.SZ' if x == '深市A股' else '.SH')
    # df1 = df0[["wind_code", "weights"]]
    # df1['weights'] = df1['weights']/df1['weights'].sum()
    # print(df1)
    # print(df1['percentage'].sum())
    # wind_codes = df1['wind_code'].values.tolist()
    # start_date = '2011-01-01'
    # end_date = '2022-01-24'
    # table_name = 'portfolio0124b'
    # database = 'test1'
    # field = "trade_code,close,windcode"
    # options = "PriceAdj=B",

    # Add data to MySQL from wind api.
    # loader.fetch_historical_data(wind_codes,)

    # database = 'bond'
    # table_name = 'convertible_bond'
    # start_date = "2022-01-04"
    # end_date = "2022-01-26"
    # wind_codes = ["110038.SH", "110043.SH"]
    # field = "CONVPRICE" # single vlaue to compare along time. format = date x windcode(field)
    #
    # data = get_data_sql(wind_codes, start_date, end_date, database, table_name, field)
    # print(data)

    database = 'bond'
    table_name = 'convertible_bond'
    start_date = "2022-01-04"
    end_date = "2022-01-26"

    loader = Loader(start_date, end_date, database, None, None, None)
    field = "windcode, CONVVALUE, convpremiumratio"
    bond_data = loader.fetchall_data('convertible_bond', field)
    bond_data['CLOSE'] = bond_data["CONVVALUE"] * (1 + bond_data["CONVPREMIUMRATIO"] / 100)
    # bond_data.to_csv('resource/bond_data.csv')
    # prices_bond = get_data_sql(start_date, end_date, bond_data, 'CLOSE')
    prices_bond = pivot_table_all(bond_data, ['index'], ['WINDCODE'], ['CLOSE'])
    # print(prices_bond)

    # # convert columns from multiindex to single index.
    # df = prices_bond.columns
    # columns = [x[1] for x in df.to_list()]
    # prices_bond.columns = columns
    # # rename index name to date.
    # prices_bond.index.name = 'date'

    prices_bond.to_csv('resource/test_pivot_table.csv')

