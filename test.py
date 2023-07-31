# #!/usr/bin/env python
#
# import paramiko
# from paramiko.ssh_exception import SSHException
# import threading
# import select
# import time
# import logging
# import re
# import os
#
# SSH_PORT = 22
# SSH_CONNECT_TIMEOUT = 60
# SSH_COMMAND_TIMEOUT = 60
# SSH_HEARTBEAT_COMMAND = 'sleep 10'
# SSH_HEARTBEAT_COMMAND_TIMEOUT = 5
# SSH_HEARTBEAT_INTERVAL = 5
#
#
# LOG = logging.getLogger()
# LOG_FILE = re.sub(r'\.py$', r'.log', os.path.basename(__file__))
#
# print(os.path.basename(__file__))
# print(LOG_FILE)
# print(LOG)


import builtins
#create a boolean variable for verbose check and set it false by default
verbose = True

#now, to implement verbose in Python, you have to write your custom print function
if verbose:
    def print(*args):
        return builtins.print(*args,sep="\n")