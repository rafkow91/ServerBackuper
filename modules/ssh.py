import os
import sys

import getpass
from paramiko import SSHClient, AutoAddPolicy, AuthenticationException

USER = os.environ.get('USERNAME')

DEFAULT_KNOWS_HOST_PATHS = {
    'linux': f'/home/{USER}/.ssh/known_hosts',
    # 'windows': f'C:\users\{USER}\ssh',
    # 'darwin': f'/users/{USER}/.ssh/known_hosts'
}


class SSHContextManager:
    def __init__(self, host: str, username: str, ssh_key_path: str = None, password: str = None, port: int = 22, known_hosts_path: str = None) -> None:
        self.client = SSHClient()
        self.host = host
        self.known_hosts_path = known_hosts_path
        self.password = password
        self.port = port
        self.ssh_key_path = ssh_key_path
        self.username = username

        if self.known_hosts_path is None:
            actual_os = sys.platform
            self.known_hosts_path = DEFAULT_KNOWS_HOST_PATHS.get(actual_os)

    def __enter__(self):
        self.client.load_host_keys(self.known_hosts_path)
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.client.load_system_host_keys()

        try:
            if self.ssh_key_path is not None:
                self.client.connect(self.host, username=self.username,
                                    key_filename=self.ssh_key_path, allow_agent=False)
            else:
                self.client.connect(self.host, username=self.username,
                                    password=self.password, allow_agent=False)

        except AuthenticationException:
            print('Authentication with ssh key failed!')
            password = getpass(f'Input password for user "{self.username}": ')
            self.client.connect(self.host, username=self.username, password=password)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
