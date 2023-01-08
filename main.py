""" Server Backuper -> make backups using ssh connection    """
import yaml
import pathlib

from paramiko.ssh_exception import NoValidConnectionsError

from modules.ssh import SSHContextManager
from modules.ftp import FTPUploader

if __name__ == '__main__':
    with open('config.yml', mode='r') as file:
        servers = yaml.safe_load_all(file)

        for server in servers:
            try:
                with SSHContextManager(connection_config=server) as ssh:
                    print(f'connect OK (IP: {server["host"]})')
                    ssh.zipping_files()
                    ssh.get_files()
                    ssh.delete_files()

                    ftp = FTPUploader()
                    ftp.upload_files([ssh.filename])
                    
                    file = pathlib.Path(ssh.filename)
                    file.unlink()

            except NoValidConnectionsError as e:
                print(str(e)[13:])
            