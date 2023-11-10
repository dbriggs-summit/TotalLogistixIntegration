import logging
from paramiko.client import SSHClient, AutoAddPolicy
import config
import os
import csv
import io


def conn_setup():
    host = config.ftpHost
    port = config.ftpPort
    username = config.ftpUserName
    password = config.ftpPassword

    client = SSHClient()

    # Arty - added for local ftp testing
    if config.mode == "development":
        print('development mode')
        client.set_missing_host_key_policy(AutoAddPolicy())

    client.load_system_host_keys()

    client.connect(hostname=host,
                   port=port,
                   username=username,
                   password=password,
                   banner_timeout=30)
    return client


def push_orders(output_file):

    client = conn_setup()
    sftp = client.open_sftp()

    # Need to hardcode when accessing windows files from linux due to how os.path.basename works
    # path = os.path.join(config.output_dir, 'tl_orders.csv')
    path = os.path.join(config.output_dir, os.path.basename(output_file))
    logging.debug(path)

    local_path = output_file
    sftp.put(local_path, path)

    sftp.close()
    client.close()


def pull_shipments(ship_type):
    client = conn_setup()
    sftp = client.open_sftp()
    if ship_type == 'ready':
        file_type = 'SA138_ReadyToShip'
    elif ship_type == 'deferred':
        file_type = 'SA138_Deferred'
    elif ship_type == 'shipreport':
        file_type = 'SA138_DailyShipmentReport'
    elif ship_type == 'parcel':
        file_type = 'SA138_DailyParcelShipmentReport'
    else:
        file_type = 'SA138_Shipped'
    file_list = sftp.listdir(config.input_dir)
    # logging.info(file_list)
    #file_list = ['SA138_ReadyToShip_202202081630.csv', 'SA138_Shipped_202202081845.csv']
    rs_list = [x for x in file_list if file_type in x]
    rs_list.sort(reverse=True)
    # logging.info(rs_list)
    import_list = [rs_list[0]]

    ship_list = []
    for in_file in import_list:
        # Need to hardcode when accessing windows files from linux due to how os.path.basename works
        in_path = os.path.join(config.input_dir, in_file)
        logging.info(f'getting import file {in_path}')

        with sftp.file(in_path, 'r') as f:

            reader = csv.DictReader(f)
            for row in reader:
                ship_list.append(row)

    sftp.close()
    client.close()

    return ship_list
