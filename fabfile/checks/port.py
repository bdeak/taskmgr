from fabric.api import *

import socket
import re

@task
def check(input_params):
    """ Check if a given TCP port is open
        input_params parameter is a string, with the following fields:
        port1,port2,portN:tcp|udp:multiple=true|false
    """
    # split up the input_params, and make sense of it
    print "input params are: %s" % input_params
    if not re.search("^([0-9]+,?)+:(tcp|udp)(:(true|false))?$", input_params):
        raise AttributeError("The given input_params doesn't match the requirements!")
    port = input_params.split(":")[0].split(",")
    # convert strings to integers
    port = [ int(x) for x in port ]
    protocol = input_params.split(":")[1]
    try:
        need_all = str2bool(input_params.split(":")[2])
    except IndexError:
        need_all = True

    for element in port:
        if not type(element) is int:
            raise ValueError("Array input was provided but not all elements are ints!")
    results = list()
    for p in port:
        results.append(check_port(env.host_string, p, protocol))
    if need_all:
        return all(res == True for res in results)
    else:
        return any(res == True for res in results)

def check_port(host, port, protocol, timeout=5):
    """ Do the actual port check, internal function, not exposed via @task """
    if protocol == "tcp":
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            puts("port is open")
            return True
        else:
            puts("port is closed")
            return False
    elif protocol == "udp":
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            return False
        else:
            return True
    else:
        raise ValueError("type must be either 'tcp' or 'udp'")

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")    