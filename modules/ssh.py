''' Remote client works on SSH'''
import os
import pathlib
import sys
import datetime

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
    # pylint: disable=too-many-instance-attributes

    def __init__(self, connection_config: dict) -> None:
        self.client = SSHClient()

        self.dir_to_zip = pathlib.Path(connection_config.get('dir_to_zip', ''))
        self.host = connection_config.get('host', None)
        self.known_hosts_path = connection_config.get('known_hosts_path', None)
        self.password = connection_config.get('password', None)
        self.port = connection_config.get('port', None)
        self.server_name = connection_config.get('server_name', None)
        self.ssh_key_path = connection_config.get('ssh_key_path', None)
        self.system = connection_config.get('system', None).lower()
        self.username = connection_config.get('username', None)

        if self.known_hosts_path is None:
            actual_os = sys.platform
            self.known_hosts_path = DEFAULT_KNOWS_HOST_PATHS.get(actual_os)

        self.destination_path = (
            self.dir_to_zip.parent if self.system == 'linux' else pathlib.Path(
                "\\".join(str(self.dir_to_zip).split("\\")[:-1]))
        ).joinpath(
            f'{self.server_name if self.server_name else self.host}_{datetime.datetime.now().strftime("%Y-%m-%d")}.zip')

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

    def get_files(self, files_paths: list[str] = None):
        '''
        Getting files from the server.
        '''
        if files_paths is None:
            files_paths = [self.destination_path]

        scp = SCPClient(self.client.get_transport())
        for file_path in files_paths:
            scp.get(file_path)
        scp.close()

    def zipping_files(self):
        '''
        Zipping files on the remote server.
        '''
        if self.system == 'windows':
            print('Zipping in Windows')
            command = f'Compress-Archive -Path {self.dir_to_zip} -DestinationPath {self.destination_path}'
        elif self.system == 'linux':
            print('Zipping in Linux')
            command = f'zip -r {self.destination_path} {self.dir_to_zip}'

        _, _, stderr = self.client.exec_command(command)
        if stderr:
            print(stderr.read().decode('utf8'))
