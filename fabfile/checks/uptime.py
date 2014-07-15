from fabric.api import *

import time
import re

import logging
import utils.log

l = logging.getLogger()
l = utils.log.CustomLogAdapter(l, None)

@task(default=True)
def check(input_params, cluster):
    """ Check the uptime for a machine and compare it against a pre-defined value
    
        input_params parameter is a string, with the following fields:
        uptime[unit]|[sleep_before_returning]

        Example:
        1d|2h
        1w
        60m
        60s

        If no unit is used, _minute_ is used! (seconds in terms of uptime doesn't make much sense)
        If the parameter 'sleep_before_returning' is defined, when the uptime is less than the desired, 
        the check will sleep this time before returning - this can be used to do less frequent checking,
        which results less frequent ssh connections to be made.
        Default is not to sleep before returning.

    """
    # split up the input_params, and make sense of it
    m = re.search("^([0-9.]+)([dwms])?(?::([0-9.]+)?([dwms])?)?$", input_params)
    if not m:
        raise AttributeError("The given input_params '%s' doesn't match the requirements!" % input_params)
    value, unit, sleep, sleep_unit = m.groups()
    try:
        value = float(value)
    except Exception as e:
        raise ValueError("Can't convert value to float: %s" % str(e))
    
    if unit is None:
        unit = "m"

    sleep_sec = None
    if not sleep is None and sleep_unit is None:
        sleep_unit = "m"

    # convert value to seconds
    uptime_req_sec = convert_human_readable_duration_to_seconds(value, unit)
    
    if not sleep is None:
        sleep_sec = convert_human_readable_duration_to_seconds(sleep, sleep_unit)

    return check_uptime(uptime_req_sec, unit, cluster, sleep_sec)

def check_uptime(uptime_req_sec, unit, cluster, sleep_sec=None):
    """ Compare the actual uptime (in seconds) against a pre-defined value (in seconds) """
    try:
        result = run("cat /proc/uptime")
    except:
        raise RuntimeError("%s: failed running 'cat /proc/uptime': %s" % (env.command, command))

    if not result.succeeded:
        return False
    else:
        uptime_real = float(result.split(" ")[0])
        uptime_human = convert_seconds_to_human_readable_duration(uptime_real, unit)
        if uptime_real > uptime_req_sec:
            l.debug("Uptime is '%.2f'" % uptime_human, env.host_string, cluster)
            return True
        else:
            l.info("Uptime is '%.2f%s'" % (uptime_human, unit), env.host_string, cluster)
            if not sleep_sec is None:
                l.info("Sleeping '%d' seconds before returning" % int(sleep_sec), env.host_string, cluster)
                time.sleep(sleep_sec)
            return False


def convert_human_readable_duration_to_seconds(value, unit):
    """ convert 5m to 300, 1h to 3600 """
    value = float(value)
    if unit == "s":
        time_seconds = value
    elif unit == "m":
        time_seconds = value * 60
    elif unit == "h":
        time_seconds = value * 60 * 60
    elif unit == "d":
        time_seconds = value * 60 * 60 * 24
    elif unit == "w":
        time_seconds = value * 60 * 60 * 24 * 7
    else:
        raise ValueError("Unknown unit '%s' was used" % unit)

    return float(time_seconds)

def convert_seconds_to_human_readable_duration(time_seconds, unit):
    """ convert (300, m) to 5, (240, h) to 4 """
    if unit == "s":
        value = float(time_seconds)
    elif unit == "m":
        value = float(time_seconds) / 60
    elif unit == "h":
        value = float(time_seconds) / 60 / 60
    elif unit == "d":
        value = float(time_seconds) / 60 / 60 / 24
    elif unit == "w":
        value = float(time_seconds) / 60 / 60 / 24 / 7
    else:
        raise ValueError("Unknown unit '%s' was used" % unit)

    return float(value)