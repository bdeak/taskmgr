from fabric.api import *

import re

@task(default=True)
def check(input_params, cluster):
    """ Dummy check to always return true or false, depending on the input
    
        input_params parameter is a string, with the following fields:
        true|false|ok|fail|1|0
    """
    # split up the input_params, and make sense of it
    if not re.search("^(true|false|ok|fail|0|1)$", input_params):
        raise AttributeError("The given input_params '%s' doesn't match the requirements!" % input_params)

    return str2bool(input_params)

def str2bool(v):
    return v.lower() in ("ok", "true", "1")