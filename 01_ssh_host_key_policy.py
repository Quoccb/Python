import paramiko
import logging
import re
import os

LOG = logging.getLogger()
LOG_FILE = re.sub(r'\.py$', r'.log', os.path.basename(__file__))

def ssh(host, username, password, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#    client.load_system_host_keys()
    client.connect(hostname=host, username=username, password=password)
    stdin1, stdout1, stderr1 = client.exec_command(command)
    message = stderr1
    if stdout1.channel.recv_exit_status() != 0:
        LOG.error('Command \"%s\" failed in \"%s\": %s', command, host, stderr1.read().decode())

#    else break
    return stdin1, stdout1, message

def _config_logging(verbose=False):
    LOG.setLevel(logging.INFO)
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

if __name__ == "__main__":
    _host = "192.168.56.102"
    _username = "quoccb"
    _password = "1"
    _command = 'df h'

    _config_logging()
    _stdin, _stdout, _stderr = ssh(_host, _username, _password, _command)

#    print(type(_stderr))
    print(_stderr.read().decode())

    LOG.error('Sending heartbeat...error, exception: %s', )
    LOG.error('2-Sending heartbeat...error, exception: %s', )
    # print(LOG)
