from fabric.api import *

import socket
import re

@task
def check(input_params):
    """ Check if a given TCP port is open
        input_params parameter is a string, with the following fields:
        port:tcp|udp
    """
    # split up the input_params, and make sense of it
    if not re.search("^([0-9]+):(tcp|udp)$", input_params):
        raise AttributeError("The given input_params '%s' doesn't match the requirements!" % input_params)
    try:
        port = int(input_params.split(":")[0])
    except Exception as e:
        raise ValueError("Can't convert port to integer: %s" % str(e))
    protocol = input_params.split(":")[1]
    return check_port(env.host_string, port, protocol)

def check_port(host, port, protocol):
    """ Do the actual port check, internal function, not exposed via @task """
    if protocol == "tcp":
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(int(env.timeout))
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            return True
        else:
            return False
    elif protocol == "udp":
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(int(env.timeout))
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            return True
        else:
            return False
    else:
        raise ValueError("type must be either 'tcp' or 'udp'")

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")    