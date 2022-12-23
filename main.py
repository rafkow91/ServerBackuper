""" Server Backuper -> make backups using ssh connection    """
from json import load
import yaml

from paramiko.ssh_exception import NoValidConnectionsError

from modules.ssh import SSHContextManager

if __name__ == '__main__':
    with open('config.yml', mode='r') as file:
        servers = yaml.safe_load_all(file)

        for server in servers:
            try:
                with SSHContextManager(username=server['username'], host=server['host'], ssh_key_path=server.get('ssh_key', None), password=server.get('password', None)) as ssh:
                    print(f'connect OK (IP: {server["host"]})')

                    ssh.get_files(['D:\\test.txt'])
            except NoValidConnectionsError as e:
                print(str(e)[13:])
