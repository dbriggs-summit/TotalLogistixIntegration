from sqlalchemy import create_engine, exc
import csv
import logging
from logging.config import dictConfig
import config

dictConfig(config.log_config)

dyna_server = config.dynaServer
dyna_db = config.dynaDBName
dyna_user = config.dynaUserName
dyna_password = config.dynaPassword
dynacom_eng = \
    create_engine(f'mssql+pyodbc://{dyna_user}:{dyna_password}@{dyna_server}/'
                  f'{dyna_db}?driver=SQL Server')

with dynacom_eng.connect() as con:
    try:
        result = con.execute('select * from view_TLOrders')
        orders = result.fetchall()
    except exc.SQLAlchemyError as e:
        logging.error(e)


with open(config.output_file, 'w', newline='') as csvfile:
    try:
        csvwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(result.keys())
        for line in orders:
            csvwriter.writerow(line)
    except FileError as e:
        logging.error(e)
logging.info('process completed successfully')
