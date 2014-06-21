from fabric.api import *

import re
import os.path

import logging
import utils.log

l = logging.getLogger()
l = utils.log.CustomLogAdapter(l, None)

@task(default=True)
def reboot(input_params, cluster):
    """ Reboot the target system

        input_params parameter is a string, with the following fields:
        wait_time:message

        Both arguments are optional.
        Wait_time means to wait this many minutes before doing a reboot. By default a wait time of 0 minutes is used (=now)
        Message will be broadcasted locally on the machine (via shutdown) before doing the reboot.
    """
    # split up the input_params, and make sense of it
    m = re.search("^([0-9]+)?(?::?(.+))?$", input_params)
    if not m:
        raise AttributeError("The given input_params '%s' doesn't match the requirements!" % input_params)
    wait = m.group(1) if m.group(1) else "now"
    message = m.group(2) if m.group(2) else ""

    try:
        result = sudo("/sbin/shutdown -r %s %s" % (wait, message))
    except:
        return False

    if result.succeeded:
        return True
    else:
        return False
