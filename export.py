import logging
from paramiko.client import SSHClient
import config
import os


def push_orders(output_file):
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

    sftp = client.open_sftp()

    # Need to hardcode when accessing windows files from linux due to how os.path.basename works
    # path = 'TL Orders.csv'
    path = os.path.basename(output_file)
    logging.debug(path)

    local_path = output_file
    sftp.put(local_path, path)

    sftp.close()
    client.close()
