from fabric.api import *

import re
import os.path

import logging
import utils.log

import xml.etree.ElementTree as ET

l = logging.getLogger()
l = utils.log.CustomLogAdapter(l, None)

@task(default=True)
def check(input_params, cluster):
    """ check if the given node is the active node

        Accepts no input parameters
    """
    # split up the input_params, and make sense of it
    m = re.search("^\s*$", input_params)
    if not m:
        raise AttributeError("The given input_params '%s' doesn't match the requirements!" % input_params)

    try:
        result = sudo("test -e /usr/sbin/crm_mon")
    except:
        return False

    if result.failed:
        raise RuntimeError("%s: Command '/usr/sbin/crm_mon' doesn't exist!" % env.command)
    
    return check_node_active()

def check_node_active():
    """ Check if a node is online via crm_mon """

    command = "/usr/sbin/crm_mon --one-shot --as-xml"

    try:
        result = sudo(command)
    except:
        raise RuntimeError("%s: failed running crm_mon command: %s" % (env.command, command))

    if not result.succeeded:
        return False
    else:
        # parse the output
        try:
            root = ET.fromstring(result)
        except Exception as e:
            raise RuntimeError("Failed to parse xml output from crm_mon: %s" % str(e))

        for e in root.findall('./crm_mon/resources/group/*/node/@name'):
            print e
        return False