import unittest
from unittest.mock import patch, MagicMock
import os
import paramiko
from terminal_emulator import TerminalEmulator, SSHClient

class TestTerminalEmulator(unittest.TestCase):
    """
    Unit tests for the TerminalEmulator class.
    """
    def setUp(self):
        self.terminal = TerminalEmulator()

    def test_run_local_command(self):
        """
        Test running a local command.
        """
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout=b'success', stderr=b'')
            self.terminal.run_local_command('echo hello')
            mock_run.assert_called_with('echo hello', shell=True, check=True, stdout=-1, stderr=-1)

    def test_handle_ssh(self):
        """
        Test handling an SSH command.
        """
        with patch.object(SSHClient, 'connect') as mock_connect, patch.object(SSHClient, 'execute_command') as mock_execute:
            self.terminal.handle_ssh('ssh example.com ls -l')
            mock_connect.assert_called_once()
            mock_execute.assert_called_with('ls -l')

    def test_manage_environment(self):
        """
        Test managing environment variables.
        """
        with patch.dict(os.environ, {}, clear=True):
            self.terminal.manage_environment('env set MYVAR value')
            self.assertEqual(os.environ['MYVAR'], 'value')
            self.terminal.manage_environment('env get MYVAR')
            self.terminal.manage_environment('env unset MYVAR')
            self.assertNotIn('MYVAR', os.environ)

    def test_handle_scp(self):
        """
        Test handling an SCP command.
        """
        with patch.object(SSHClient, 'connect') as mock_connect, patch.object(SSHClient, 'transfer_file') as mock_transfer:
            self.terminal.handle_scp('scp source.txt destination.txt example.com')
            mock_connect.assert_called_once()
            mock_transfer.assert_called_with('source.txt', 'destination.txt')

class TestSSHClient(unittest.TestCase):
    """
    Unit tests for the SSHClient class.
    """
    def setUp(self):
        self.ssh_client = SSHClient('example.com', 22, 'user', '/path/to/key')

    def test_connect(self):
        """
        Test establishing an SSH connection.
        """
        with patch.object(paramiko.SSHClient, 'connect') as mock_connect:
            self.ssh_client.connect()
            mock_connect.assert_called_with('example.com', port=22, username='user', pkey=MagicMock())

    def test_execute_command(self):
        """
        Test executing a command on the remote server.
        """
        with patch.object(paramiko.SSHClient, 'exec_command') as mock_exec_command:
            mock_exec_command.return_value = (MagicMock(), MagicMock(stdout=b'output'), MagicMock(stderr=b'error'))
            self.ssh_client.execute_command('ls -l')
            mock_exec_command.assert_called_with('ls -l')

    def test_transfer_file(self):
        """
        Test transferring a file to or from the remote server.
        """
        with patch.object(paramiko.SSHClient, 'open_sftp') as mock_open_sftp:
            mock_sftp = MagicMock()
            mock_open_sftp.return_value = mock_sftp
            self.ssh_client.transfer_file('source.txt', 'destination.txt')
            mock_sftp.put.assert_called_with('source.txt', 'destination.txt')

    def test_close(self):
        """
        Test closing the SSH connection.
        """
        with patch.object(paramiko.SSHClient, 'close') as mock_close:
            self.ssh_client.close()
            mock_close.assert_called_once()

if __name__ == '__main__':
    unittest.main()