""" Server Backuper -> make backups using ssh connection    """
import yaml

from paramiko.ssh_exception import NoValidConnectionsError

from modules.ssh import SSHContextManager

if __name__ == '__main__':
    with open('config.yml', mode='r') as file:
        servers = yaml.safe_load_all(file)

        for server in servers:
            try:
                with SSHContextManager(connection_config=server) as ssh:
                    print(f'connect OK (IP: {server["host"]})')
                    ssh.zipping_files()
                    ssh.get_files()
                    
            except NoValidConnectionsError as e:
                print(str(e)[13:])
