from fabric.api import *

import re

import logging
import utils.log

l = logging.getLogger()
l = utils.log.CustomLogAdapter(l, None)

@task(default=True)
def custom_cmd(input_params, cluster):
    """ Execute a custom command

        input_params parameter is a string, with the following fields:
        sudo:command[:exit_code[,exit_code2]

        The sudo parameter is optional, and if present, a sudo call will be done instead of a simple run()
        The command parameter is mandatory
        The success of the command will be judged by the exit code. Multiple exit codes can be provided, with comma as separator
    """
    # split up the input_params, and make sense of it
    with_sudo, command, exit_codes_array = parse(input_params)

    # tell fabric which return codes we interpret as 'ok'
    env.ok_ret_codes = exit_codes_array

    # run _any_ command. Very dangerous. You have been warned!
    if with_sudo is None:
        try:
            l.debug("Executing: '%s'" % command, env.host_string, cluster)
            result = run(command)
        except:
            return False
    else:
        try:
            l.debug("Executing via sudo: '%s'" % command, env.host_string, cluster)
            result = sudo(command)
        except Exception as e:
            return False

    if result.succeeded:
        return True
    else:
        return False

@task
def parse(input_params):
    """ parse input parameters, in a reusable form, might be called from taskmgr directly """
    m = re.search("^(?:(sudo):)?(.*?)(?::([0-9,]+))?$", input_params)

    if not m:
        raise AttributeError("The given input_params '%s' doesn't match the requirements!" % input_params)

    with_sudo, command, exit_codes = m.groups()    

    if command is None:
        raise AttributeError("Message parameter must not be empty!")

    if exit_codes is None:
        exit_codes = "0"

    exit_codes_array = [ int(x) for x in exit_codes.split(",") ]

    return with_sudo, command, exit_codes_array