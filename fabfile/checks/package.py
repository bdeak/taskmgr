from fabric.api import *

import re
import os.path

import logging
import utils.log

l = logging.getLogger()
l = utils.log.CustomLogAdapter(l, None)

@task(default=True)
def check(input_params):
    """ Check the version of a given package
        Can support multiple backends 

        input_params parameter is a string, with the following fields:
        package:version

        The backend to be used for package management is autodetected.
        For adapting to various systems this needs to be extended.
    """
    # split up the input_params, and make sense of it
    m = re.search("^([^:]+)(?::(.+))?$", input_params)
    if not m:
        raise AttributeError("The given input_params '%s' doesn't match the requirements!" % input_params)
    package = m.group(1)
    version = m.group(2) if m.group(2) else None

    try:
        result = run("test -e /usr/bin/dpkg")
    except:
        return False
    if result.failed:
        raise RuntimeError("%s: Failed to execute remote command for detecting backend" % env.command)
    if result.return_code == 0:
        backend = "dpkg"
    else:
        # check for other backends - note yet implemented    
        raise SystemError("%s: only backend 'dpkg' is currently supported." % env.command)

    backends = { 'dpkg': check_package_dpkg }

    if not backend in backends.keys():
        raise ValueError("function for detected backend '%s' is not found!" % backend) 

    return backends[backend](package, version)

def check_package_dpkg(package, version):
    """ Do the actual http check, internal function, not exposed via @task """
    try:
        with settings(combine_stderr=False):
            result = run("/usr/bin/dpkg -s %s" % package)
    except:
        return False

    # if no version was provided, the mere existence of the package is questioned
    if version is None:
        if result.succeeded:
            return True
        else:
            return False

    # compare the versions            
    for line in result.split("\n"):
        try:
            # line.index will raise an exception for every line which doesn't match
            index = line.index("Version:")
            found_version = line.replace("Version: ", "").rstrip()
            if found_version == version:
                return True
            else:
                l.debug("Version for package '%s' is '%s'" % (package, version), env.host_string)
                return False
        except:
            continue

    # if here, there was no Version: found in the output
    return False
