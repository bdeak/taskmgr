from fabric.api import *

import re

import logging
import utils.log

l = logging.getLogger()
l = utils.log.CustomLogAdapter(l, None)

@task(default=True)
def icli(input_params, cluster):
    """ Enable/Disable monitoring for a given host using icli (internal tool)

        input_params parameter is a string, with the following fields:
        enable|disable

        The hostname of the given machine is fetched from the fabric 'env' variable
        This command is run on the local machine, therefore the icli command must be available.
    """
    # split up the input_params, and make sense of it
    if re.search("^(enable|disable)$", input_params):
        action = input_params
    else:
        raise AttributeError("The given input_params '%s' doesn't match the requirements!" % input_params)

    # check if icli is available
    try:
        with quiet():
            if action == "disable":
                result_1 = local("icli -d -h %s -D 12h -m 'downtime set by taskmgr'" % env.host_string)   
                result_2 = local("icli -d -h %s -s . -D 12h -m 'downtime set by taskmgr'" % env.host_string)
            else:
                result_1 = local("icli -c -h %s" % env.host_string)   
                result_2 = local("icli -c -h %s -s ." % env.host_string)    
    except:
        return False

    if result_1.succeeded and result_2.succeeded:
        return True
    else:
        return False

