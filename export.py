from paramiko.client import SSHClient
import config


def push_orders(output_file):
    host = config.ftpHost
    port = config.ftpPort
    username = config.ftpUserName
    password = config.ftpPassword

    client = SSHClient()
    client.connect(hostname=host,
                   port=port,
                   username=username,
                   password=password,
                   banner_timeout=30)

    sftp = client.open_sftp()

    path = './inbox/' + output_file
    local_path = output_file
    sftp.put(local_path, path)

    sftp.close()
    client.close()
