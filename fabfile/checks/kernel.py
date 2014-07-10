from fabric.api import *

import re
import os.path

import logging
import utils.log

l = logging.getLogger()
l = utils.log.CustomLogAdapter(l, None)

@task(default=True)
def check(input_params, cluster):
    """ Check the kernel version

        input_params parameter is a string, with the following fields:
        version
    """
    # split up the input_params, and make sense of it
    m = re.search("^[0-9a-zA-Z.\-_+~]+$", input_params)
    if not m:
        raise AttributeError("The given input_params '%s' doesn't match the requirements!" % input_params)

    version = input_params

    # check if lsb_release command exists
    # extend this later to allow getting this info using different ways
    try:
        result = run("uname -a | cut -d' ' -f7")
    except:
        return False

    if result.failed:
        raise RuntimeError("%s: Can't detect the kernel version due to an error running 'uname -v'" % env.command)

    if result.rstrip() == version:
        return True
    else:
        return False
