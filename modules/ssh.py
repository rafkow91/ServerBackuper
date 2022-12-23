''' Remote client works on SSH'''
import os
import sys

from getpass import getpass
from paramiko import SSHClient, AutoAddPolicy, AuthenticationException
from scp import SCPClient

USER = os.environ.get('USERNAME')

DEFAULT_KNOWS_HOST_PATHS = {
    'linux': f'/home/{USER}/.ssh/known_hosts',
    'windows': f'C:\\users\\{USER}\\ssh',
    'darwin': f'/users/{USER}/.ssh/known_hosts'
}


class SSHContextManager:
    '''
    > This function is used to get files from a remote server

    :param host: The hostname or IP address of the server
    :type host: str
    :param username: The username to use for the SSH connection
    :type username: str
    :param ssh_key_path: The path to the SSH key file
    :type ssh_key_path: str
    :param password: The password for the user
    :type password: str
    :param port: The port to connect to on the remote server, defaults to 22
    :type port: int (optional)
    :param known_hosts_path: The path to the known_hosts file. If not provided, it will be set to
    the default path for the current OS
    :type known_hosts_path: str
    '''

    def __init__(self, host: str, username: str, ssh_key_path: str = None,
                 password: str = None, port: int = 22, known_hosts_path: str = None) -> None:
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

    def get_files(self, files_paths: list[str]):
        '''
        Getting files from the server.
        '''
        scp = SCPClient(self.client.get_transport())
        for file_path in files_paths:
            scp.get(file_path)
        scp.close()
