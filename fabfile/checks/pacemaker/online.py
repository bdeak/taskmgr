from fabric.api import *

import re
import os.path

import logging
import utils.log

l = logging.getLogger()
l = utils.log.CustomLogAdapter(l, None)

@task(default=True)
def check(input_params, cluster):
    """ check if the given node is online

        Accepts no input parameters

    """
    return True
    # split up the input_params, and make sense of it
#    m = re.search("^\s*$", input_params)
#    if not m:
#        raise AttributeError("The given input_params '%s' doesn't match the requirements!" % input_params)
#
#    try:
#        result = sudo("test -e /usr/sbin/crm_mon")
#    except:
#        return False
#
#    if result.failed:
#        raise RuntimeError("%s: Command '/usr/sbin/crm_mon' doesn't exist!" % env.command)
#    
#    return check_node_online(cluster)
#
#def check_node_online(cluster):
#    """ Check if a node is online via crm_mon """
#
#    command = "/usr/sbin/crm_mon --group-by-node -1"
#
#    try:
#        result = sudo(command)
#    except:
#        raise RuntimeError("%s: failed running crm_mon command: %s" % (env.command, command))
#
#    if not result.succeeded:
#        return False
#    else:
#        # parse the output
#        for line in result.split("\n"):
#            m = re.search("^Node %s (?:\([a-zA-Z0-9-]+\)): (.+)" % env.host_string, line, re.IGNORECASE)
#            if m:
#                state = m.group(1)
#                if state == "online":
#                    return True
#                else:
#                    l.info("State is %s" % state, env.host_string, cluster)
#                    return False
#        
#        # if here, no matching lines were found, return an exception
#        raise RuntimeError("%s: can't determine the status based on the crm_mon output, no matching line was found!" % (env.command, command))#