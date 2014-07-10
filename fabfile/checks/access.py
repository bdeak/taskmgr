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
        return check_ssh()
    else:
        return check_sudo()


def check_ssh():
    """ Do the actual ssh check """
    try:
        with settings(combine_stderr=False):
            result = run("uname")
    except:
        return False

    if result.succeeded:
        return True
    else:
        return False

def check_sudo():
    """ Do the actual sudo check """
    try:
        with settings(combine_stderr=False):
            result = sudo("uname")
    except:
        return False

    if result.succeeded:
        return True
    else:
        return False

