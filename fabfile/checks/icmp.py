from fabric.api import *

import re
import os

@task(default=True)
def check(input_params, cluster):
    """ Check if a given host is alive using ICMP packets (ping)
    
        input_params parameter is a string, with the following fields:
        number_of_packets
    """
    # split up the input_params, and make sense of it
    m = re.search("^([0-9]+)?$", input_params)
    if m:
        if not m.group(1) is None:
            try:
                numpackets = int(input_params)
            except Exception as e:
                raise ValueError("Can't convert number of packets to send to integer: %s" % str(e))
        else:
            numpackets = 3
    else:        
        raise AttributeError("The given input_params '%s' doesn't match the requirements!" % input_params)
    
    return check_icmp(env.host_string, numpackets)

def check_icmp(host, numpackets):
    """ Do the actual pinging """
    response = os.system("ping -c %d -W5 %s > /dev/null 2>&1" % (numpackets, host))

    if response == 0:
        return True
    else:
        return False

