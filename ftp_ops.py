import logging
from paramiko.client import SSHClient
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
    else:
        file_type = 'SA138_Shipped'
    file_list = sftp.listdir(config.input_dir)
    logging.info(file_list)
    #file_list = ['SA138_ReadyToShip_202202081630.csv', 'SA138_Shipped_202202081845.csv']
    rs_list = [x for x in file_list if file_type in x]
    rs_list.sort(reverse=True)
    in_file = rs_list[0]

    # Need to hardcode when accessing windows files from linux due to how os.path.basename works
    in_path = os.path.join(config.input_dir, in_file)
    logging.debug(in_path)

    with(io.StringIO("")) as f:
        sftp.getfo(in_path, f)
        ship_list = []
        reader = csv.DictReader(f)
        for row in reader:
            ship_list.append(row)
        sftp.close()
        client.close()

    return ship_list
