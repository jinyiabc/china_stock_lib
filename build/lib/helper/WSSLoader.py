
import time
import pandas as pd
from WindPy import w
from helper.Loader import Loader


class WSSLoader(Loader):

    def __init__(self, start_date, end_date, database, table_name, field, options, sector=None):
        super().__init__(start_date, end_date, database, table_name, field, options, sector)

    def fetch_historical_data(self, wind_codes, sleep_time=5, UPLOAD_GITHUB=False):
        """
        Retrieve the WSD data of specified windcodes
        :param wind_codes: List[str], the windcodes of specified securities
        :param sleep_time: number, the sleep time for the loop when an error occurs
        :return: None
        """
        print(self.current_time, ": Start to Download Data")
        start_date = self._start_date
        end_date = self._end_date
        db_engine = self._db_engine
        table_name =  self._table_name
        field = self._field
        options =  self._options
        sector = self._sector
        w.start()
        dti = pd.date_range(start_date, end_date)
        for rpt_date in dti:
            for wind_code in wind_codes:
                print(self.current_time, ": {0}".format(wind_code))
                options = options.format(rpt_date)
                error_code, data = w.wss(wind_code,
                                         # "underlyingcode,clause_conversion2_swapshareprice,clause_conversion_2_forceconvertprice,clause_conversion2_bondlot,clause_conversion2_tosharepriceadjustitem,coupontxt,actualbenchmark,fund_reitsissuesize,fund_redmstartdate,clause_putoption_triggerprice,latestissurercreditrating,couponrate2,clause_calloption_triggerprice",
                                         field,
                                         options,
                                         usedf = True)

                data.index.rename('wind_code', inplace=True)
                data['rpt_date'] = rpt_date.date()
                data.reset_index(inplace=True)
                # data.set_index(['wind_code', 'rpt_date'])

                # Check if Wind API runs successfully. If error_code is not 0, it indicators an error occurs
                err_name = wind_codes if wind_codes is not None else sector
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

        print(self.current_time, ": Downloading Data Finished .")
