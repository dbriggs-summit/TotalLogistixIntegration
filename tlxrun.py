from sqlalchemy import exc
from sqlalchemy.sql import text
import csv
import logging
from logging.config import dictConfig
import config
from ftp_ops import push_orders, pull_shipments
from db import get_db
# from carrier_codes import carrier_codes
from helpers import clean_amount, clean_delayed_reason, format_tracking, get_carrier_name, valid_date_format, get_parcel_carrier_name, set_delivered_date
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
        if ship_type == 'deferred':
            statement = text("""update invoihdr set x04472490_UniCarrier = :CarrierSCAC, x04472490_UniRate = :Amount,
            TrackingNo = :PRONumber, shipvia = :shipvia, x04472474_DelayedReason = :ReasonCode,
            x04472474_DelayedDate = :DelayedDate, x04472474_Delayed = 1 where orderid = :OrderNumber""")
            for line in ship_list:
                line['Amount'] = clean_amount(line['Amount'])
                line['PRONumber'] = format_tracking(line['CarrierSCAC'], line['PRONumber'])
                line['shipvia'] = get_carrier_name(line['CarrierSCAC'])
                line['ReasonCode'] = clean_delayed_reason(line['ReasonCode'])
                if not valid_date_format(line['DelayedDate']):
                    line['DelayedDate'] = ''

                try:
                    con.execute(statement, **line)
                    logging.info(f"Order {line['OrderNumber']} delayed '{line['ReasonCode']}' on {line['DelayedDate']}. Updated: carrier {line['CarrierSCAC']} with tracking"
                                f"number {line['PRONumber']} for amount {line['Amount']}")
                except exc.SQLAlchemyError as e:
                    logging.error(e)
        elif ship_type == 'shipreport':
            statement = text("""update invoihdr set usrTMSSignedDate = :SignedOn where orderid = :BL""")
            for line in ship_list:
                if line['SignedOn'].lower() == 'null':
                    continue
                try:
                    con.execute(statement, **line)
                    logging.info(f"Order {line['BL']} updated: signed on {line['SignedOn']}")
                except exc.SQLAlchemyError as e:
                    logging.error(e)
        elif ship_type == 'parcel':
            statement = text("""update invoihdr set x04472490_UniCarrier = :CarrierSCAC, x04472474_Delivered = :Delivered, x04472474_DeliveredBy = :DeliveredBy, x04472474_DeliveredDate = :DeliveredDate,
            TrackingNo = :TrackingNumber, shipvia = :shipvia where orderid = :SONumber""")
            for line in ship_list:
                line['shipvia'] = get_parcel_carrier_name(line['CarrierSCAC'])
                line['Delivered'] = 1
                line['DeliveredBy'] = 'Postback'
                line['DeliveredDate'] = set_delivered_date(line['Pick Up Date'])
                try:
                    con.execute(statement, **line)
                    logging.info(f"Order {line['SONumber']} updated: carrier {line['CarrierSCAC']} with tracking"
                                f"number {line['TrackingNumber']}")
                except exc.SQLAlchemyError as e:
                    logging.error(e)
        else:
            statement = text("""update invoihdr set x04472490_UniCarrier = :CarrierSCAC, x04472490_UniRate = :Amount,
            TrackingNo = :PRONumber, shipvia = :shipvia where orderid = :OrderNumber""")
            for line in ship_list:
                line['Amount'] = clean_amount(line['Amount'])
                line['PRONumber'] = format_tracking(line['CarrierSCAC'], line['PRONumber'])
                line['shipvia'] = get_carrier_name(line['CarrierSCAC'])
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
                        help="the type of file to import. 'ready' for 'Ready to Ship, ""'ship' for 'Shipped', 'deferred' for 'Deferred', 'shipreport' for 'ShipmentReport'")
    args = parser.parse_args()
    if args.action == 'import':
        if args.shiptype == 'ship':
            ship_type = 'ship'
        elif args.shiptype == 'ready':
            ship_type = 'ready'
        elif args.shiptype == 'deferred':
            ship_type = 'deferred'
        elif args.shiptype == 'shipreport':
            ship_type = 'shipreport'
        elif args.shiptype == 'parcel':
            ship_type = 'parcel'
        else:
            raise Exception("shiptype must be 'ship', 'ready', 'deferred', 'shipreport' or 'parcel'")
        import_shipments(ship_type)
    elif args.action == 'export':
        export_orders()
    else:
        raise Exception("action must be 'import or 'export'")
