from datetime import datetime

import pandas as pd
import backtrader as bt
from backtrader import TimeFrame
from backtrader.utils.dateintern import date2num

def read_wind_excel(ticker, start, end, skiprows, header):
    custom_col_converter = lambda x: float(x.replace('--', '0'))
    df0 = pd.read_excel(ticker,
                        engine='openpyxl',
                        # encoding='GB2312',
                        parse_dates=['交易日期'],
                        thousands=',',
                        converters={'开盘点位': custom_col_converter,
                                    "最高点位": custom_col_converter,
                                    "最低点位": custom_col_converter,
                                    "收盘价": custom_col_converter,
                                    "成交量(万股)": custom_col_converter,
                                    },
                        index_col=0,
                        skiprows=skiprows,
                        header=header,
                        ) \
        .rename(
        columns={
            "交易日期": "datetime",
            "开盘点位": "open",
            "最高点位": "high",
            "最低点位": "low",
            "收盘价": "close",
            "成交量(万股)": "volume",
        },
    )
    df0.sort_index(inplace=True)

    return df0[start:end]

def read_wind_csv(ticker, start, end, skiprows, header):
    custom_col_converter = lambda x: float(x.replace('--', '0'))
    df0 = pd.read_csv(ticker,
                        encoding='GB2312',
                        parse_dates=['日期'],
                        thousands=',',
                        converters={'开盘点位': custom_col_converter,
                                    "最高点位": custom_col_converter,
                                    "最低点位": custom_col_converter,
                                    "收盘价": custom_col_converter,
                                    "成交量(万股)": custom_col_converter,
                                    },
                        index_col=0,
                        skiprows=skiprows,
                        header=header,
                        ) \
        .rename(
        columns={
            "日期": "datetime",
            "开盘点位": "open",
            "最高点位": "high",
            "最低点位": "low",
            "收盘价": "close",
            "成交量(万股)": "volume",
        },
    )
    df0.set_index('datetime', inplace=True)
    df0.sort_index(inplace=True)

    return df0[start:end]


class PandasDataFeed(bt.feeds.PandasDirectData):
    params = (
        ('dtformat', '%Y-%m-%d'),
        ('datetime', 0),
        ('open', 1),
        ('high', 2),
        ('low', 3),
        ('close', 4),
        ('volume', 9),
        ('openinterest', -1),
    )


class CSVDataFeed(bt.feeds.GenericCSVData):
    params = (
        ('dtformat', '%Y-%m-%d'),
        ('datetime', 0),
        ('time', -1),
        ('open', 1),
        ('high', 2),
        ('low', 3),
        ('close', 4),
        ('volume', 5),
        ('openinterest', -1),
    )

    def _loadline(self, linetokens):
        # Datetime needs special treatment
        dtfield = linetokens[self.p.datetime]
        if self._dtstr:
            dtformat = self.p.dtformat

            if self.p.time >= 0:
                # add time value and format if it's in a separate field
                dtfield += 'T' + linetokens[self.p.time]
                dtformat += 'T' + self.p.tmformat

            dt = datetime.strptime(dtfield, dtformat)
        else:
            dt = self._dtconvert(dtfield)

        if self.p.timeframe >= TimeFrame.Days:
            # check if the expected end of session is larger than parsed
            if self._tzinput:
                dtin = self._tzinput.localize(dt)  # pytz compatible-ized
            else:
                dtin = dt

            dtnum = date2num(dtin)  # utc'ize

            dteos = datetime.combine(dt.date(), self.p.sessionend)
            dteosnum = self.date2num(dteos)  # utc'ize

            if dteosnum > dtnum:
                self.lines.datetime[0] = dteosnum
            else:
                # Avoid reconversion if already converted dtin == dt
                self.l.datetime[0] = date2num(dt) if self._tzinput else dtnum
        else:
            self.lines.datetime[0] = date2num(dt)

        # The rest of the fields can be done with the same procedure
        for linefield in (x for x in self.getlinealiases() if x != 'datetime'):
            # Get the index created from the passed params
            csvidx = getattr(self.params, linefield)

            if csvidx is None or csvidx < 0:
                # the field will not be present, assignt the "nullvalue"
                csvfield = self.p.nullvalue
            else:
                # get it from the token
                csvfield = linetokens[csvidx]

            if csvfield == '':
                # if empty ... assign the "nullvalue"
                csvfield = self.p.nullvalue

            if csvfield == '--':
                # if empty ... assign the "nullvalue"
                csvfield = 0

            # get the corresponding line reference and set the value
            line = getattr(self.lines, linefield)
            line[0] = float(float(csvfield))

        return True
