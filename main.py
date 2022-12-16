""" Server Backuper -> make backups using ssh connection    """
from json import load

from paramiko.ssh_exception import NoValidConnectionsError

from modules.ssh import SSHContextManager

if __name__ == '__main__':
    with open('config.json', mode='r') as file:
        servers = load(file)
    # with SSHContextManager()
    print(servers)
    for server in servers:
        try:
            with SSHContextManager(username=server['username'], host=server['host'], ssh_key_path=server.get('ssh_key', None), password=server.get('password', None)):
                print(f'connect OK (IP: {server["host"]})')
        except NoValidConnectionsError as e:
            print(e)