from fabric.api import *

import re
import os.path

import logging
import utils.log

l = logging.getLogger()
l = utils.log.CustomLogAdapter(l, None)

@task(default=True)
def node(input_params, cluster):
    """ Execute 'crm node standby' or 'crm node online'

        input_params is a string:
        standby|online

    """
    # split up the input_params, and make sense of it
    m = re.search("^(standby|online)$", input_params)
    if not m:
        raise AttributeError("The given input_params '%s' doesn't match the requirements!" % input_params)

    action = m.group(1)

    try:
        result = sudo("test -e /usr/sbin/crm")
    except:
        return False

    if result.failed:
        raise RuntimeError("%s: Command '/usr/sbin/crm' doesn't exist!" % env.command)
    
    return standby_node(action)

def standby_node(action):
    """ Standby or make a node online using crm """

    if action == "standby":
        command = "crm node standby"
    else:
        command = "crm node online"
        
    try:
        result = sudo(command)
    except:
        raise RuntimeError("%s: failed running crm command: %s" % (env.command, command))

    if result.succeeded:
        return True
    else:
        return False
