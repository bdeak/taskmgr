from fabric.api import *

import re
import os.path

import logging
import utils.log

l = logging.getLogger()
l = utils.log.CustomLogAdapter(l, None)

@task(default=True)
def check(input_params, cluster):
    """ check if the galera cluster is in sync

        input_params is a string:
        mysql_username:mysql_password:required_cluster_size:(socket|host:port)

        If no socket and host/port is provided, '/tmp/mysql.sock' will be used as a socket

        The user needs the USAGE privilege, but nothing else.
        The query "SHOW STATUS WHERE variable_name = 'wsrep_cluster_size'" will be executed
    """
    # split up the input_params, and make sense of it
    m = re.search("^([^:]+):([^:]+):([0-9]+)(?::(.+))?$", input_params)
    if not m:
        raise AttributeError("The given input_params '%s' doesn't match the requirements!" % input_params)

    user, password, size, sock_or_host = m.groups()

    size = int(size)

    host = None
    port = None
    socket = None

    if sock_or_host is None:
        socket = "/tmp/mysql.sock"
    else:
        if sock_or_host.find("=") != -1:
            host = sock_or_host.split("=")[0]
            port = sock_or_host.split("=")[1]
        else:
            socket = sock_or_host

    try:
        result = sudo("test -e /usr/bin/mysql")
    except:
        return False

    if result.failed:
        raise RuntimeError("%s: Command '/usr/bin/mysql' doesn't exist!" % env.command)
    
    return check_cluster_in_sync(user, password, size, socket, host, port, cluster)

def check_cluster_in_sync(user, password, size, socket, host, port, cluster):
    """ Check if the Galera cluster is in sync using a comparison of the current nodes in the cluster against a pre-defined value """

    if socket is None:
        sock_args = "--host %s --port %s" % (host, port)
    else:
        sock_args = "--socket %s" % socket

    command = "/usr/bin/mysql -u%s -p%s %s --batch -s -e \"SHOW STATUS WHERE variable_name = 'wsrep_cluster_size'\"" % (user, password, sock_args)

    try:
        result = sudo(command)
    except:
        raise RuntimeError("%s: failed running command: %s" % (env.command, command))

    if not result.succeeded:
        return False
    else:
        cluster_size = int(result.split("\t")[1])
        if size == cluster_size:
            return True
        else:
            l.debug("There are %d nodes in the cluster, but %d was required" % (cluster_size, size), env.host_string, cluster)
            return False
