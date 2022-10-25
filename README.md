# Install
`pip install --upgrade -q git+https://github.com/jinyiabc/china_stock_lib.git    `

# Or download and build
`git clone https://github.com/jinyiabc/china_stock_lib.git`  \
`python -m build` \
`cd dist` \
` pip install helper_jinyi-<version>-py3-none-any.whl`

# Configuration for MySQL
Update mysql.cfg under directory. Checked the path by: \
`from importlib import resources` \
`with resources.path('helper', 'mysql.cfg') as p:
    print(str(p))`

# Usage
`from helper import get_data ` \
`get_data.get_module_3('300144-2.csv')`

`from helper.WSDLoader import WSDLoader`\
`loader = WSDLoader(start_date, end_date, database, table_name)`\
`wind_codes = loader.get_windcodes(sector)`\
`loader.fetch_historical_data(wind_codes)`

`data = get_data_sql(codes, start_date, end_date, database, table_name, field, options)
`

# Script Usage: 
`wsd -s "20211231" -e "20211231" -d test1 -t test_wsd3` \
`wset -s "20220121" -e "20220121" -d test1 -t test_wset1 -se '000300.SH' --github` \
`wss -s "20201231" -e "20201231" -d test1 -t wind_energy_cbond -w '000001.SZ,110034.SH'` \


# build 
Open linux command window.
python -m build --wheel
cd dist 
pip install helper_jinyi-1.0.17-py3-none-any.whl
