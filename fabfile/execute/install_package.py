from fabric.api import *

import re
import os.path

import logging
import utils.log

l = logging.getLogger()
l = utils.log.CustomLogAdapter(l, None)

@task(default=True)
def check(input_params):
    """ Install a given version of a given package
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

    # auto detect the backend
    try:
        result = run("test -e /usr/bin/apt-get")
    except:
        return False

    if result.failed:
        raise RuntimeError("%s: Failed to execute remote command for detecting backend" % env.command)
    
    if result.return_code == 0:
        backend = "apt_get"
    else:
        # check for other backends - note yet implemented    
        raise SystemError("%s: only backend 'apt_get' is currently supported." % env.command)

    backends = { 'apt_get': install_package_apt_get }

    if not backend in backends.keys():
        raise ValueError("function for detected backend '%s' is not found!" % backend) 

    return backends[backend](package, version)

def install_package_apt_get(package, version):
    """ Install the package, internal function, not exposed via @task """

    if version is None:
        # just install the package
        command = "apt-get -qq update && apt-get -qq install -y %s" % package
    else:
        command = "apt-get -qq update && apt-get -qq install -y %s=%s" % (package, version)

    try:
        result = sudo(command)
    except:
        return False

    if result.succeeded:
        return True
    else:
        return False
