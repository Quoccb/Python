#!/usr/bin/env python

import paramiko
from paramiko.ssh_exception import SSHException
import threading
import select
import time
import logging
import re
import os

SSH_PORT = 22
SSH_CONNECT_TIMEOUT = 60
SSH_COMMAND_TIMEOUT = 60
SSH_HEARTBEAT_COMMAND = 'sleep 10'
SSH_HEARTBEAT_COMMAND_TIMEOUT = 5
SSH_HEARTBEAT_INTERVAL = 5


LOG = logging.getLogger()
LOG_FILE = re.sub(r'\.py$', r'.log', os.path.basename(__file__))


class Heartbeat(threading.Thread):
    def __init__(self, interval, function, args=None, kwargs=None):
        threading.Thread.__init__(self, name='Thread-heartbeat')
        self.interval = interval
        self.function = function
        if args is None:
            self.args = []
        else:
            self.args = args
        if kwargs is None:
            self.kwargs = {}
        else:
            self.kwargs = kwargs
        self.finished = threading.Event()

    def cancel(self):
        self.finished.set()

    def run(self):
        LOG.info('%s starting', self.name)
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)
        LOG.info('%s exiting', self.name)


class AutoBotCmd(object):
    def __init__(
            self,
            hostname,
            username,
            password,
            port=SSH_PORT,
            timeout=SSH_CONNECT_TIMEOUT,
            heartbeat_interval=SSH_HEARTBEAT_INTERVAL):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout
        self._client = paramiko.SSHClient()
        self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._heartbeat = None
        self._heartbeat_interval = heartbeat_interval

    def connect(self):
        self._client.connect(hostname=self.hostname, port=self.port, username=self.username, password=self.password)

    def keep_alive(self):
        if self._heartbeat is not None:
            self._heartbeat.cancel()
            self._heartbeat.join()
        self._heartbeat = Heartbeat(
            self._heartbeat_interval,
            self._exec_heartbeat)
        self._heartbeat.start()

    def close(self):
        if self._heartbeat is not None:
            self._heartbeat.cancel()
            self._heartbeat.join()
        if self._client.get_transport() is not None:
            self._client.close()

    def exec_command(
            self,
            command,
            combine_stderr=False,
            timeout=SSH_COMMAND_TIMEOUT):
        stdin, stdout, _ = self._client.exec_command(command)
        stdin.close()
        channel = stdout.channel
        if combine_stderr:
            channel.set_combine_stderr(True)
        elapsed = 0
        all_stdout = ''
        all_stderr = ''
        select_timeout = 1
        while not channel.exit_status_ready():
            rlist, _, _ = select.select([channel], [], [], select_timeout)
            if rlist:
                elapsed = 0
                while channel.recv_ready():
                    all_stdout += channel.recv(1024)
                while channel.recv_stderr_ready():
                    all_stderr += channel.recv_stderr(1024)
            else:
                elapsed += select_timeout
                if elapsed > timeout:
                    channel.close()
                    raise RuntimeError('Command execution timed out')
            LOG.debug(
                'Command: %s, elapsed: %d, rlist: %s',
                command,
                elapsed,
                rlist)
        status = channel.recv_exit_status()
        while channel.recv_ready():
            all_stdout += channel.recv(1024)
        while channel.recv_stderr_ready():
            all_stderr += channel.recv_stderr(1024)
        return all_stdout, all_stderr, status

    def _send_heartbeat(self):
        try:
            LOG.info('Sending heartbeat...')
            _, _, status = self.exec_command(
                SSH_HEARTBEAT_COMMAND, timeout=SSH_HEARTBEAT_COMMAND_TIMEOUT)
        except Exception as ex:
            LOG.error('Sending heartbeat...error, exception: %s', ex)
            return False
        if status != 0:
            return False
        return True

    def _exec_heartbeat(self):
        if self._send_heartbeat():
            LOG.info('Sending heartbeat...done')
            return
        # Heartbeat failed
        if self._client.get_transport() is not None:
            self._client.close()
        LOG.info('Re-connecting...')
        try:
            self.connect()
        except SSHException as ex:
            LOG.error('Re-connecting...error, exception: %s', ex)
            self.close()
            return
        LOG.info('Re-connecting...done')


def _config_logging(verbose=False):
    LOG.setLevel(logging.DEBUG)
    file_hdl = logging.FileHandler(LOG_FILE)
    file_hdl.setFormatter(logging.Formatter(
        '%(asctime)s - %(funcName)s:%(lineno)d - %(levelname)s - %(message)s'))
    file_hdl.setLevel(logging.DEBUG)
    cons_hdl = logging.StreamHandler()
    cons_hdl.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'))
    if verbose:
        cons_hdl.setLevel(logging.DEBUG)
    else:
        cons_hdl.setLevel(logging.INFO)
    LOG.addHandler(file_hdl)
    LOG.addHandler(cons_hdl)


def test():
    a = AutoBotCmd('192.168.56.102', 'quoccb', '1')
    a.connect()
    a.keep_alive()
    stdout, stderr, status = a.exec_command('df -h')
    LOG.info('\nstdout: %s\nstderr: %s\nstatus: %d', stdout, stderr, status)
    stdout, stderr, status = a.exec_command('hostname')
    LOG.info('\nstdout: %s\nstderr: %s\nstatus: %d', stdout, stderr, status)
    time.sleep(30)
    a.close()


if __name__ == '__main__':
    _config_logging(False)
    test()