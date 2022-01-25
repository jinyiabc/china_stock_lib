
import time
import pandas as pd
from WindPy import w
from helper.Loader import Loader

class WSETLoader(Loader):

    def __init__(self, database, table_name, wind_tableName, options):
        super().__init__(None, None, database, table_name, None, options, None)
        self._wind_tableName = wind_tableName

    def fetch_historical_data(self, rpt_date, wind_code, sleep_time=5, UPLOAD_GITHUB=False):
        """
        Retrieve the WSET data of specified windcodes
        :param wind_codes: List[str], the windcodes of specified securities
        :param sleep_time: number, the sleep time for the loop when an error occurs
        :return: None
        """
        print(self.current_time, ": Start to Download Data")
        options =  self._options
        wind_tableName = self._wind_tableName
        w.start()
        w.isconnected()
        options = options.format(rpt_date, wind_code)
        error_code, data = w.wset(wind_tableName,
                                  options,
                                  usedf=True)

        # Check if Wind API runs successfully. If error_code is not 0, it indicators an error occurs
        if error_code != 0:
            # Output log
            self.__error_logger(wind_code, '{0}'.format(int(error_code)))
            # Print error message
            print(self.current_time, ":data %s : ErrorCode :%s" % (wind_code, error_code))
            print(data)
            # Pause the loop for the specified time when an error occurs
            time.sleep(sleep_time)
        self.save_to_sql(data, wind_code, UPLOAD_GITHUB=UPLOAD_GITHUB)

        print(self.current_time, ": Downloading A-Share Stock Finished .")


