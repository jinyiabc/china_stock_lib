from WindPy import w
from src.helper.mysql_dbconnection import mysql_dbconnection

from src.helper.WSETLoader import WSETLoader

if __name__ == '__main__':
    w.start()
    w.isconnected()  # 判断WindPy是否已经登录成功
    sector = '000300.SH'
    start = '20220121'
    end = '20220121'
    database = 'test1'
    table_name = 'test_wset1'

    # db_engine = mysql_dbconnection(database=database)
    loader = WSETLoader(start, end, database, table_name, sector)
    loader.fetch_historical_data(UPLOAD_GITHUB=True)

    # loader.upload_csv()
    # data = loader.fetchall_data('601989.SH', table_name)
    # print(data)
    # w.stop()

    # wse -s "20220121" -e "20220121" -d test1 -t test_wset1 -se '000300.SH' --github