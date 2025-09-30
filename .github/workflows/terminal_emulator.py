import os
import sys
import subprocess
import paramiko
import readline
import getpass
import logging
import configparser
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class TerminalEmulator:
    """
    A class to emulate a Linux terminal interface.

    Attributes
    ----------
    prompt : str
        The prompt displayed to the user.
    ssh_client : Optional[SSHClient]
        An optional SSH client for remote command execution.
    command_history : list
        A list to store the history of commands executed.
    config : ConfigParser
        Configuration settings loaded from a file.

    Methods
    -------
    start()
        Starts the terminal emulator.
    execute_command(command: str)
        Executes a command entered by the user.
    run_local_command(command: str)
        Runs a local shell command.
    handle_ssh(command: str)
        Handles SSH commands.
    load_config()
        Loads configuration settings from a file.
    """
    def __init__(self):
        self.prompt = 'user@system:~/$ '
        self.ssh_client: Optional[SSHClient] = None
        self.command_history = []
        self.config = self.load_config()
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self.complete)

    def start(self):
        """
        Starts the terminal emulator.
        """
        print("Welcome to the Linux Terminal Emulator!")
        print("Type 'exit' to quit.")
        while True:
            try:
                command = input(self.prompt)
                if command.lower() == 'exit':
                    break
                self.execute_command(command)
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\nCommand interrupted.")
            except Exception as e:
                logging.error(f"Error executing command: {e}")

    def execute_command(self, command):
        """
        Executes a command entered by the user.

        Parameters
        ----------
        command : str
            The command to execute.
        """
        if command.startswith('ssh '):
            self.handle_ssh(command)
        elif command.startswith('env '):
            self.manage_environment(command)
        elif command.startswith('scp '):
            self.handle_scp(command)
        else:
            self.run_local_command(command)

    def run_local_command(self, command):
        """
        Runs a local shell command.

        Parameters
        ----------
        command : str
            The local command to execute.
        """
        try:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(result.stdout.decode())
            self.command_history.append(command)
        except subprocess.CalledProcessError as e:
            print(e.stderr.decode(), file=sys.stderr)
            logging.error(f"Command failed: {command}")
        except FileNotFoundError:
            print(f"Command not found: {command}", file=sys.stderr)
            logging.error(f"Command not found: {command}")
        except PermissionError:
            print(f"Permission denied: {command}", file=sys.stderr)
            logging.error(f"Permission denied: {command}")
        except Exception as e:
            logging.error(f"Error running local command: {e}")

    def handle_ssh(self, command):
        """
        Handles SSH commands.

        Parameters
        ----------
        command : str
            The SSH command to execute.
        """
        parts = command.split()
        if len(parts) < 3:
            print("Usage: ssh <hostname> <command>")
            return
        hostname = parts[1]
        cmd = ' '.join(parts[2:])
        if self.ssh_client is None or self.ssh_client.hostname != hostname:
            self.ssh_client = SSHClient(hostname, 22, self.config['SSH']['username'], self.config['SSH']['key_path'])
            self.ssh_client.connect()
        self.ssh_client.execute_command(cmd)

    def manage_environment(self, command):
        """
        Manages environment variables.

        Parameters
        ----------
        command : str
            The environment command to execute.
        """
        parts = command.split()
        if len(parts) < 3:
            print("Usage: env <set|get|unset> <variable> [value]")
            return
        action = parts[1]
        variable = parts[2]
        if action == 'set' and len(parts) > 3:
            value = ' '.join(parts[3:])
            os.environ[variable] = value
            print(f"Environment variable {variable} set to {value}")
        elif action == 'get':
            value = os.environ.get(variable, 'Not set')
            print(f"Environment variable {variable}: {value}")
        elif action == 'unset':
            if variable in os.environ:
                del os.environ[variable]
                print(f"Environment variable {variable} unset")
            else:
                print(f"Environment variable {variable} not set")
        else:
            print("Invalid action. Use 'set', 'get', or 'unset'.")

    def handle_scp(self, command):
        """
        Handles SCP commands for file transfer.

        Parameters
        ----------
        command : str
            The SCP command to execute.
        """
        parts = command.split()
        if len(parts) < 4:
            print("Usage: scp <source> <destination> <hostname>")
            return
        source = parts[1]
        destination = parts[2]
        hostname = parts[3]
        if self.ssh_client is None or self.ssh_client.hostname != hostname:
            self.ssh_client = SSHClient(hostname, 22, self.config['SSH']['username'], self.config['SSH']['key_path'])
            self.ssh_client.connect()
        self.ssh_client.transfer_file(source, destination)

    def load_config(self):
        """
        Loads configuration settings from a file.

        Returns
        -------
        ConfigParser
            The configuration settings.
        """
        config = configparser.ConfigParser()
        config.read('config.ini')
        return config

    def complete(self, text, state):
        """
        Tab completion for commands.

        Parameters
        ----------
        text : str
            The text to complete.
        state : int
            The state of the completion.
        """
        options = [cmd for cmd in self.command_history if cmd.startswith(text)]
        if state < len(options):
            return options[state]
        else:
            return None

    def get_command_index(self):
        """
        Returns a list of all commands entered in the session.
        """
        return self.command_history

class SSHClient:
    """
    A class to handle SSH connections and commands.

    Attributes
    ----------
    hostname : str
        The hostname of the SSH server.
    port : int
        The port number for the SSH connection.
    username : str
        The username for the SSH connection.
    key_path : str
        The path to the SSH key for authentication.
    client : paramiko.SSHClient
        The paramiko SSH client instance.

    Methods
    -------
    connect()
        Establishes an SSH connection.
    execute_command(command: str)
        Executes a command on the remote server.
    transfer_file(source: str, destination: str)
        Transfers a file to or from the remote server.
    close()
        Closes the SSH connection.
    """
    def __init__(self, hostname: str, port: int, username: str, key_path: str):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.key_path = key_path
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        """
        Establishes an SSH connection.
        """
        try:
            key = paramiko.RSAKey(filename=self.key_path)
            self.client.connect(self.hostname, port=self.port, username=self.username, pkey=key)
            logging.info("SSH connection established.")
        except paramiko.AuthenticationException:
            logging.error("Authentication failed, please verify your credentials")
        except paramiko.SSHException as sshException:
            logging.error(f"Unable to establish SSH connection: {sshException}")
        except paramiko.BadHostKeyException as badHostKeyException:
            logging.error(f"Unable to verify server's host key: {badHostKeyException}")
        except Exception as e:
            logging.error(f"Exception in connecting: {e}")

    def execute_command(self, command: str):
        """
        Executes a command on the remote server.

        Parameters
        ----------
        command : str
            The command to execute.
        """
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            if output:
                print(output)
            if error:
                print(error, file=sys.stderr)
        except Exception as e:
            logging.error(f"Error executing SSH command: {e}")

    def transfer_file(self, source: str, destination: str):
        """
        Transfers a file to or from the remote server.

        Parameters
        ----------
        source : str
            The source file path.
        destination : str
            The destination file path.
        """
        try:
            sftp = self.client.open_sftp()
            sftp.put(source, destination)
            sftp.close()
            logging.info(f"File transferred from {source} to {destination}")
        except Exception as e:
            logging.error(f"Error transferring file: {e}")

    def close(self):
        """
        Closes the SSH connection.
        """
        try:
            self.client.close()
            logging.info("SSH connection closed.")
        except Exception as e:
            logging.error(f"Error closing SSH connection: {e}")

def ask_permission():
    """
    Asks the user for permission to modify the system.

    Returns
    -------
    bool
        True if permission is granted, False otherwise.
    """
    response = input("Do you grant permission to modify your system? (yes/no): ")
    return response.lower() == 'yes'

def main():
    """
    The main function to start the terminal emulator.
    """
    if ask_permission():
        terminal = TerminalEmulator()
        terminal.start()
    else:
        print("Permission denied. Exiting.")
        sys.exit(0)

if __name__ == "__main__":
    main()