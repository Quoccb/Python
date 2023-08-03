import paramiko
import logging
import re
import os


LOG = logging.getLogger()
LOG_FILE = re.sub(r'\.py$', r'.log', os.path.basename(__file__))


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


class Ssh(object):
    def __init__(self, hostname, username=None, password=None, port=22, pkey=None, timeout=60):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.pkey = pkey
        self.timeout = timeout
        self._client = paramiko.SSHClient()
        self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        try:
            self._client.connect(hostname=self.hostname,
                                 username=self.username,
                                 password=self.password,
                                 port=self.port,
                                 pkey=self.pkey,
                                 timeout=self.timeout)
            return True
        except Exception:
            LOG.error("Failed to access to %s@%s", self.username, self.hostname)
            # print("Failed to access to " + self.username + "@" + self.hostname)
            return False

    def exec_command(
            self,
            command,
            timeout):
        _stdin, _stdout, _stderr = self._client.exec_command(command, timeout=timeout)
        return _stdin, _stdout, _stderr


    def Check_acc_pass_expires(self):
        chage_command = "chage -l " + self.username
        _stdin, _stdout, _stderr = self._client.exec_command(command=chage_command)
        x = _stdout.readlines()
        pass_expires = x[1].split(":")[1].replace("\n", "").replace(" ", "")
        acc_expires = x[3].split(":")[1].replace("\n", "").replace(" ", "")
        if (pass_expires == "never" and acc_expires == "never"):
            print("OK")
        else:
            print("not OK")


if __name__ == "__main__":
    host = "192.168.56.102"
    username = "quoccb"
    password = "1"
    command = 'cat test.txt'
    timeout = 1

    _config_logging()
    Vm1 = Ssh(hostname=host, username=username, password=password, timeout=timeout)
    Vm2 = Ssh(hostname=host, username="red17", password=password,timeout=timeout)
    connect1 = Vm1.connect()
    connect2 = Vm2.connect()
    if connect1:
        Vm1.Check_acc_pass_expires()
    if connect2:
        Vm2.Check_acc_pass_expires()