
import time
import config
import mysql.connector
import pandas as pd
from WindPy import w
from importlib import resources
from helper.mysql_dbconnection import mysql_dbconnection
from helper.upload_github import upload_github
with resources.path('helper', 'mysql.cfg') as p:
    resource_path = str(p)
cfg = config.Config(resource_path)

class Loader:

    def __init__(self, start_date, end_date, database, table_name, field, options, sector=None):
        db_engine = mysql_dbconnection(database=database)
        self._start_date = start_date
        self._end_date = end_date
        self._db_engine = db_engine
        self._table_name = table_name
        self._sector = sector
        self._field = field
        self._options = options

    @property
    def current_time(self):
        return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))

    def __error_logger(self, wind_code, status, info=None):
        """
        Log the errors occuring when retriving or saving data
        :param wind_code: str, wind code of the present security
        :param status: status parameters, e.g. the ErrorCode returned by Wind API
        :return: None
        """
        error_log = pd.DataFrame(index=[wind_code])
        error_log.loc[wind_code, 'start_date'] = self._start_date
        error_log.loc[wind_code, 'end_date'] = self._end_date
        error_log.loc[wind_code, 'status'] = status
        error_log.loc[wind_code, 'table'] = 'stock_daily_data'
        error_log.loc[
            wind_code, 'args'] = 'Symbol: ' + wind_code + ' From ' + self._start_date + ' To ' + self._end_date
        error_log.loc[wind_code, 'error_info'] = info
        error_log.loc[wind_code, 'created_date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        error_log.to_sql('stock_error_log', self._db_engine, if_exists='append')

    def fetch_historical_data(self, wind_codes, sleep_time=5, UPLOAD_GITHUB=False):
        pass

    def get_windcodes(self, trade_date=None, sector=None):
        """
        Retrieve the windcodes of CSI300 (沪深300) constituents
        :param trade_date: the date to retrieve the windcodes of the constituents
        :return: Error code or a list of windcodes
        TO-DO :     argument with windtablename and options only.
        # wind_codes = loader.get_windcodes(trade_date='2022-01-26', sectorid='61efa6df695d4c9354451c77.U')
        """
        if sector is None:
            if self._sector is None:
                print("The sector is not define.")
                return
            sector = self._sector
        w.start()
        if trade_date is None:
            trade_date = self._end_date
        # Retrieve the windcodes of CSI300 constituents.
        # Users can use Sector Constituents and Index Constituents of WSET to retrieve the constituents of a sector or an index
        stock_codes = w.wset("sectorconstituent", f"date={trade_date};windcode={sector};field=wind_code")
        if stock_codes.ErrorCode != 0:
            # Return the error code when an error occurs
            return stock_codes.ErrorCode
        else:
            # Return a list of windcodes if the data is achieved
            return stock_codes.Data[0]

    # @staticmethod
    def fetchall_data(self, wind_code):
        """
        Fetch data from SQLite database
        :param str, wind_code:
        :return: None
        """
        table_name = self._table_name
        db_engine = self._db_engine
        # db_engine = mysql_dbconnection(database)
        query = ("SELECT * FROM " + table_name + " "
                 "WHERE WINDCODE ='" + wind_code + "'")

        data = pd.read_sql(query, db_engine)

        pd.set_option('display.expand_frame_repr', False)

        if len(data) > 0:
            print("Data found!")
        else:
            print("No data found!")
        # db_engine.close()

        return data



    @staticmethod
    def fetchall_log():
        """
        Retrieve the error log
        :return: None
        """
        config = {
            'user': cfg['user'],
            'password': cfg['password'],
            'host': cfg['host'],
            'database': 'china_stock_wiki',
            'raise_on_warnings': True,
            'allow_local_infile': False,
            'table_name': 'stock_error_log',
        }

        cnx = mysql.connector.connect(**config)
        c = cnx.cursor()
        c.execute("SELECT * FROM stock_error_log")
        for row in c.fetchall():
            # Print error log
            print(row)
        cnx.close()

    def upload_csv(self):
        table_name = self._table_name
        file_path = f'resource/{table_name}.csv'
        upload_github(file_path)

    def save_to_sql(self, data, err_name, UPLOAD_GITHUB=False):

        db_engine = self._db_engine
        table_name = self._table_name
        try:
            # Save the data into the database
            data.to_sql(table_name, db_engine, if_exists='append')
        except Exception as e:
            self.__error_logger(err_name, None)
            print(self.current_time, ": SQL Exception :%s" % e)

        if UPLOAD_GITHUB is True:
            data.to_csv(f'resource/{table_name}.csv', mode='a')
            print(self.current_time, f": Saved {table_name}.CSV.")

