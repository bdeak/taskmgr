from fabric.api import *

import re
import os.path

import logging
import utils.log

l = logging.getLogger()
l = utils.log.CustomLogAdapter(l, None)

@task(default=True)
def check(input_params, cluster):
    """ Check the distribution name or version against a regex
        Can support multiple backends, currently supporting only platforms having 'lsb_release'

        input_params parameter is a string, with the following fields:
        name|release:pattern

    """
    # split up the input_params, and make sense of it
    m = re.search("^(name|release):(.*)$", input_params)
    if not m:
        raise AttributeError("The given input_params '%s' doesn't match the requirements!" % input_params)

    method, pattern = m.groups()

    # check if lsb_release command exists
    # extend this later to allow getting this info using different ways
    try:
        result = run("lsb_release")
    except:
        return False

    if result.failed:
        raise RuntimeError("%s: Can't detect the release, due to missing 'lsb_release' command. checks.release needs to be extended" % env.command)

    return check_with_lsb_release(method, pattern, cluster)


def check_with_lsb_release(method, pattern, cluster):
    """ Check the release codename or version using data from 'lsb_release' """
    if method == "name":
        switch = "-c"
    else:
        switch = "-r"

    try:
        with settings(combine_stderr=False):
            result = run("lsb_release -s %s" % switch)
    except:
        return False

    if not result.succeeded:
        return False
    else:
        if re.search(pattern, result.rstrip(), re.IGNORECASE):
            return True
        else:
            l.info("The release is: '%s'" % result.rstrip(), env.host_string, cluster)
            return False


