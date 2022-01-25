
import time

import pandas as pd
from WindPy import w
from helper.Loader import Loader


class WSDLoader(Loader):

    def __init__(self, start_date, end_date, database, table_name, field, options, sector=None):
        super().__init__(start_date, end_date, database, table_name, field, options, sector)

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
        """
        Retrieve the WSD data of specified windcodes
        :param wind_codes: List[str], the windcodes of specified securities
        :param sleep_time: number, the sleep time for the loop when an error occurs
        :return: None
        """
        print(self.current_time, ": Start to Download A-Share Stocks")
        start_date = self._start_date
        end_date = self._end_date
        db_engine = self._db_engine
        table_name = self._table_name
        field = self._field
        options = self._options

        w.start()

        for wind_code in wind_codes:
            print(self.current_time, ": {0}".format(wind_code))
            # The code can be generated using Code Generator. To get data in format DataFrame, add usedf=True in the parameter list
            error_code, data = w.wsd(wind_code,
                                     # "trade_code,close,windcode",
                                     field,
                                     start_date,
                                     end_date,
                                     # "PriceAdj=B",
                                     options,
                                     usedf=True)
            # Check if Wind API runs successfully. If error_code is not 0, it indicators an error occurs
            err_name = wind_code
            if error_code != 0:
                # Output log
                self.__error_logger(err_name, '{0}'.format(int(error_code)))
                # Print error message
                print(self.current_time, ":data %s : ErrorCode :%s" % (err_name, error_code))
                print(data)
                # Pause the loop for the specified time when an error occurs
                time.sleep(sleep_time)
                # Skip the present iteration
                continue
            # codes_or_portofolio_or_tablename = wind_codes if wind_codes is not None else sector
            self.save_to_sql(data, err_name, UPLOAD_GITHUB=UPLOAD_GITHUB)

        print(self.current_time, ": Downloading A-Share Stock Finished .")
