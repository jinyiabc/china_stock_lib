import argparse

from helper.WSDLoader import WSDLoader
from helper.WSETLoader import WSETLoader
from helper.WSSLoader import WSSLoader
from helper.mysql_dbconnection import mysql_dbconnection


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description='Wind API.')

    parser.add_argument('-s',
                        '--start_date',
                        # action='store_true',
                        dest='start_date',
                        required=True,
                        help='start date')
    parser.add_argument('-e',
                        '--end_date',
                        # action='store_true',
                        dest='end_date',
                        required=True,
                        help='end date')
    parser.add_argument('-t',
                        '--table_name',
                        # action='store_true',
                        dest='table_name',
                        required=True,
                        help='table name')
    parser.add_argument('-d',
                        '--database',
                        # action='store_true',
                        dest='database',
                        required=True,
                        help='database')
    parser.add_argument('-se',
                        '--sector',
                        # action='store_true',
                        dest='sector',
                        required=False,
                        help='sector')
    parser.add_argument('--github', action='store_true', default=False,
                        help='Updoad to Github')

    parser.add_argument('--wind_codes', '-w', action='store',
                        required=False, default='000001.SZ,110034.SH,110055.SH',
                        help='wind codes')

    return parser.parse_args(args)

def run_wsd(args=None):
    res = parse_args(args)
    loader = WSDLoader(res.start_date, res.end_date, res.database, res.table_name)
    wind_codes = loader.get_windcodes()

    if type(wind_codes) is not int:
        loader.fetch_historical_data(wind_codes)
    else:
        print('ErrorCode:', wind_codes)

def run_wset(args=None):
    res = parse_args(args)
    loader = WSETLoader(res.start_date, res.end_date, res.database, res.table_name, res.sector)

    loader.fetch_historical_data(UPLOAD_GITHUB=res.github)


def run_wss(args=None):
    res = parse_args(args)
    wind_codes = res.wind_codes.split(sep=',')
    loader = WSSLoader(res.start_date, res.end_date, res.database, res.table_name)
    loader.fetch_historical_data(wind_codes)

    keyarg = {'table_name': res.table_name}
    set_data_type = (
        "ALTER TABLE {table_name} MODIFY `wind_code` VARCHAR(10);"
    ).format(**keyarg)
    set_primary = (
        "ALTER TABLE {table_name} ADD PRIMARY KEY (`rpt_date`,`wind_code`);"
    ).format(**keyarg)
    db_engine = mysql_dbconnection(database=res.database)
    with db_engine.connect() as con:
        con.execute(set_data_type)
        con.execute(set_primary)




