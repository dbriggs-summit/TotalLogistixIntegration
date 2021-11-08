from sqlalchemy import create_engine, exc
import csv
import logging
from logging.config import dictConfig
import config
import platform
from export import push_orders

dictConfig(config.log_config)

dyna_server = config.dynaServer
dyna_db = config.dynaDBName
dyna_user = config.dynaUserName
dyna_password = config.dynaPassword

dynacom_conn = f'mssql+pyodbc://{dyna_user}:{dyna_password}@{dyna_server}/{dyna_db}'
if platform.system() == 'Windows':
    dynacom_driver = 'SQL Server'
else:
    dynacom_driver = 'ODBC+Driver+17+for+SQL+Server'
dynacom_eng = create_engine(dynacom_conn+'?driver='+dynacom_driver)

with dynacom_eng.connect() as con:
    try:
        result = con.execute('select * from view_TLOrders')
        orders = result.fetchall()
    except exc.SQLAlchemyError as e:
        logging.error(e)


with open(config.output_file, 'w+', newline='') as csvfile:
    try:
        csvwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(result.keys())
        for line in orders:
            csvwriter.writerow(line)
    except IOError as e:
        logging.error(e)

push_orders(config.output_file)
logging.info('process completed successfully')
