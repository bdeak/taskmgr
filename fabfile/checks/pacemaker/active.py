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

        nodes = list()
        
        # get the number of resources
        try:
            number_resources = int(root.find('.//resources/group').attrib['number_resources'])
        except Exception as e:
            l.debug("Failed to read number_resources from xml output. The xml output was:")
            l.debug(result)
            #raise RuntimeError("Failed to get the number of resources from the xml output of crm_mon: %s" % str(e))
            pass

        try:
            for e in root.findall('.//resources/group/*/node'):
                nodes.append(e.attrib["name"])
        except Exception as e:
            # don't raise an exception, possibly there's a failover ongoing
            return False

        # get rid of duplicates
        nodes_unique = set(nodes)

        # check if the current node is in nodes
        if env.host_string in nodes_unique:
            # yes, it's an active node
            # there should be 'number_resources' many entries in 'nodes' of our hostname
            if sum(x == env.host_string for x in nodes) == number_resources:
                return True
            else:
                l.warning("Some resources are not active on this node, that should be. %d vs %d" % (sum(x == env.host_string for x in nodes), number_resources))
                return False
        else:
            return False
