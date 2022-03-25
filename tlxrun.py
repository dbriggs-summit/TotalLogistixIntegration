from sqlalchemy import exc
from sqlalchemy.sql import text
import csv
import logging
from logging.config import dictConfig
import config
from ftp_ops import push_orders, pull_shipments
from db import get_db
from carrier_codes import carrier_codes
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


def import_shipments(ship_type):
    dictConfig(config.log_config)
    logging.getLogger('paramiko').setLevel(logging.INFO)
    ship_list = pull_shipments(ship_type)
    dynacom = get_db()

    with dynacom.connect() as con:
        statement = text("""update invoihdr set x04472490_UniCarrier = :CarrierSCAC, x04472490_UniRate = :Amount,
        TrackingNo = :PRONumber, shipvia = :shipvia where orderid = :OrderNumber""")
        for line in ship_list:
            if line['Amount'] == 'null':
                line['Amount'] = 0.00
            try:
                line['shipvia'] = carrier_codes[line['CarrierSCAC']]
            except KeyError:
                line['shipvia'] = line['CarrierSCAC']
            try:
                con.execute(statement, **line)
                logging.info(f"Order {line['OrderNumber']} updated: carrier {line['CarrierSCAC']} with tracking"
                             f"number {line['PRONumber']} for amount {line['Amount']}")
            except exc.SQLAlchemyError as e:
                logging.error(e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="perform actions that transfer data between Dynacom and Total Logistix")
    parser.add_argument('action', help="the action to perform. either 'import' or 'export' ")
    parser.add_argument('-s', '--shiptype',  required='import' in sys.argv,
                        help="the type of file to import. 'ready' for 'Ready to Ship, ""'ship' for 'Shipped'")
    args = parser.parse_args()
    if args.action == 'import':
        if args.shiptype == 'ship':
            ship_type = 'ship'
        elif args.shiptype == 'ready':
            ship_type = 'ready'
        else:
            raise Exception("shiptype must be 'ship' or 'ready' ")
        import_shipments(ship_type)
    elif args.action == 'export':
        export_orders()
    else:
        raise Exception("action must be 'import or 'export'")
