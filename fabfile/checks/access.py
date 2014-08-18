from fabric.api import *

import re
import os.path

import logging
import utils.log

l = logging.getLogger()
l = utils.log.CustomLogAdapter(l, None)

@task(default=True)
def check(input_params, cluster):
    """ Check if ssh access or sudo access is working on the target machine
        Can support multiple backends 

        input_params parameter is a string, with the following fields:
        ssh|sudo

        If no parameter is given, ssh access is tested.

    """
    # split up the input_params, and make sense of it
    m = re.search("^(ssh|sudo)?$", input_params)
    if not m:
        raise AttributeError("The given input_params '%s' doesn't match the requirements!" % input_params)
    method = input_params if input_params else "ssh"

    if method == "ssh":
        return check_ssh(cluster)
    else:
        return check_sudo(cluster)


def check_ssh(cluster):
    """ Do the actual ssh check """
    try:
        result = run("uname")
    except Exception as e:
        l.info("Received exception while executing 'uname': %s" % str(e), env.host_string, cluster)
        return False

    if result.succeeded:
        return True
    else:
        return False

def check_sudo(cluster):
    """ Do the actual sudo check """
    try:
        result = sudo("uname")
    except Exception as e:
        l.info("Received exception while executing 'sudo uname': %s" % str(e), env.host_string, cluster)
        return False

    if result.succeeded:
        return True
    else:
        return False

