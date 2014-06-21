from fabric.api import *

import re
import time

import logging
import utils.log

l = logging.getLogger()
l = utils.log.CustomLogAdapter(l, None)

@task(default=True)
def wait(input_params, cluster):
    """ Wait for a pre-defined time.

        input_params parameter is a string, with the following fields:
        wait_time

        wait_time is interpreted as seconds
    """
    # split up the input_params, and make sense of it
    if re.search("^[0-9]+$", input_params):
        wait_time = int(input_params)
    else:
        raise AttributeError("The given input_params '%s' doesn't match the requirements!" % input_params)

    # wait in a loop, until the time is up, and print progress information every minute
    counter = 0
    l.info("%s: starting wait for '%d' seconds." % (env.command, wait_time), env.host_string, cluster)
    while counter < wait_time:
        time.sleep(60)
        counter += 60
        l.info("%s: '%d' seconds remaining before end of wait" % (env.command, wait_time - counter), env.host_string, cluster)

    return True
    