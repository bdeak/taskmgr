from fabric.api import *

import socket
import re
import urllib
import urllib2
import base64
import json
import logging

import utils.log

l = logging.getLogger()
l = utils.log.CustomLogAdapter(l, None)

@task(default=True)
def check(input_params, cluster):
    """ Check the number of Tomcat sessions using multiple backends.
        The available backend is Jolokia, but can be extended to support plain JMX.

        input_params parameter is a string, with the following fields:
        jolokia_user:jolokia_password@jolokia_url:jolokia_port/jolokia_context:appliaction_context:<|>:session_number[:backend]

        Parameters:
            Mandatory:
                jolokia_user:           The user to use when authenticating to Jolokia
                jolokia_password:       The pasword to use when authenticating to Jolokia
                jolokia_url:            must be a fully qualified url, with protocol, port (if not the default should be used), and context path
                application_context:    The context of the application for which the session information should be fetched
                <|>                     The direction of the comparison to do between the current sessions and the session number
                                        provided as an argument
                session_number:         The number of sessions to check against.

            Optional:
                backend:            Which backend to use. Currently only jolokia is supported, and that is the default

        Note: URL _MUST_ contain the jolokia context, at least a '/'

        Example:
            http://jolokia:jolokia@hostname:8080/jolokia:/:<:2000
            http://jolokia:jolokia@hostname:8080/jolokia:/my-app:>:10:jolokia

    """
    # split up the input_params, and make sense of it
    m = re.search("^(https?://)(?:([^:]+):([^:]+)(@))?([^/]+(?::[0-9]+)?/[^:]+):([^:]+):([<>]):([0-9]+)(?::(jolokia))?$", input_params)
    if not m:
        raise AttributeError("The given input_params '%s' doesn't match the requirements!" % input_params)

    # parse input
    if m.group(4) == "@":
        # there was a username/password provided, indexing is different
        protocol, username, password, at, url_segment, context, operation, session_num, backend = m.groups()
    else:
        protocol, url_segment, context, at, operation, session_num, backend = m.groups()

    if backend is None:
        backend = "jolokia"

    url = "%s%s" % (protocol, url_segment)
    session_num = int(session_num)

    backends = { 'jolokia': check_sessions_jolokia }

    if not backend in backends.keys():
        raise ValueError("provided backend '%s' is not allowed!" % backend) 

    return backends[backend](url, operation, session_num, context, username=username, password=password)

def check_sessions_jolokia(url, operation, session_num, context, username=None, password=None, host="localhost"):
    """ Do the actual http check, internal function, not exposed via @task """

    session_url = "%s/read/Catalina:context=%s,host=%s,type=Manager" % (url, context.replace("/", "!/"), host)

    socket.setdefaulttimeout(env.timeout)
    req = urllib2.Request(session_url)

    if not username == None and not password == None:
        authstring_base64 = base64.encodestring('%s:%s' % (username, password))[:-1]
        req.add_header("Authorization", "Basic %s" % authstring_base64)
    try:
        response = urllib2.urlopen(req)
    except (urllib2.URLError, urllib2.HTTPError) as e:
        return False

    # the request succeeded, inspect the result
    result = json.loads(response.read())
    sessions = int(result["value"]["activeSessions"])

    l.debug('Session number is %d, limit is %d' % (sessions, session_num), env.host_string)

    if operation == '>':
        if sessions > session_num:
            return True
        else:
            return False
    else:
        if sessions < session_num:
            return True
        else:
            return False 
