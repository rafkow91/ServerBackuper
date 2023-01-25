""" Server Backuper -> make backups using ssh connection    """
import pathlib
import yaml
import logging

from paramiko.ssh_exception import NoValidConnectionsError

from modules.ssh import SSHContextManager
from modules.ftp import FTPUploader


def main():
    logging.basicConfig(
        filename='server_backuper.log',
        encoding='utf-8',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s:"%(message)s"',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    with open('config.yml', mode='r', encoding='utf8') as file:
        servers = yaml.safe_load_all(file)

        for server in servers:
            try:
                with SSHContextManager(connection_config=server) as ssh:
                    ssh.zipping_files()
                    ssh.get_files()
                    ssh.delete_files()

                    ftp = FTPUploader()
                    ftp.upload_files([ssh.filename])

                    file = pathlib.Path(ssh.filename)
                    file.unlink()
            except NoValidConnectionsError as e:
                logging.error(str(e)[13:])

if __name__ == '__main__':
    main()
