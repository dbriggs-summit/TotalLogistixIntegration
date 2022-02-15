from sqlalchemy import exc
import csv
import logging
from logging.config import dictConfig
import config
from ftp_ops import push_orders, pull_shipments
from db import get_db
import argparse
import sys


def export_orders():
    dictConfig(config.log_config)
    logging.getLogger('paramiko').setLevel(logging.INFO)

    dynacom = get_db()

    with dynacom.connect() as con:
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


def import_shipments():
    ship_list = pull_shipments()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="perform actions that transfer data between Dynacom and Total Logistix")
    parser.add_argument('action', help="the action to perform. either 'import' or 'export' ")
    parser.add_argument('ship_type', required='import' in sys.argv,
                        help="the type of file to import. 'ready' for 'Ready to Ship, ""'ship' for 'Shipped'")
    args = parser.parse_args()
    export_orders()