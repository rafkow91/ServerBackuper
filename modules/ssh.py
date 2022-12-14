import getpass
from paramiko import SSHClient, AutoAddPolicy, AuthenticationException

class SSHContextManager:
    def __init__(self, known_hosts_path: str, host: str, username: str, ssh_key_path: str) -> None:
        self.client = SSHClient()
        self.host = host
        self.known_hosts_path = known_hosts_path
        self.ssh_key_path = ssh_key_path
        self.username = username

    def __enter__(self):
        self.client.load_host_keys(self.known_hosts_path)
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.client.load_system_host_keys()
        try:
            self.client.connect(self.host, username=self.username, key_filename=self.ssh_key_path)
        except AuthenticationException:
            print('Authentication with ssh key failed!')
            password = getpass(f'Input password for user "{self.username}": ')
            self.client.connect(self.host, username=self.username, password=password)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
