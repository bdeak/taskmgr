from fabric.api import *

import socket
import re
import urllib
import urllib2

@task(default=True)
def check(input_params, cluster):
    """ Check a HTTP or HTTPS service
        input_params parameter is a string, with the following fields:
        url:HTTP_STATUS|pattern[POST:value1=x,value2=y]

        Parameters:
            Mandatory:
                url: must be a fully qualified url, with protocol, port (if not the default should be used), and context path

                HTTP_STATUS: numeric value of the desirec http status in the response
                pattern: a regex pattern to look for in the response

            Optional:
                POST parameters: optionally key-value pairs can be provided (key1=value1,key2=value2), in this case a POST 
                                 request will be done instead of a GET.
                                 The method POST must be present in this case

        Note: URL _MUST_ contain context, at least a '/'

        Example:
            http://hostname:8080/:200
            http://hostname/index.html:some text
            http://some-virtual-host:8090/cgi-bin/login.cgi:SUCCESS:POST:user=some_user,password=some_password

        Fixme:
            add basic authentication support

    """
    # split up the input_params, and make sense of it
    m = re.search("^(https?://[a-zA-Z0-9._-]+(?::[0-9]+)?/[^:]*):(.+(?!POST:.+)$|.+:POST:(?:[^=]+:[^=]+:?)+)", input_params)
    if not m:
        raise AttributeError("The given input_params '%s' doesn't match the requirements!" % input_params)
    
    # parse input
    url = m.group(1)
    required_result = m.group(2)
    m = re.search("^(.+):POST:(.+)", required_result, flags=re.IGNORECASE)
    post_data = dict()
    if m:
        method = 'POST'
        required_result = m.group(1)
        # convert post data from key1=value1,key2=value2 format to dict
        post_data = dict(s.split("=") for s in m.group(2).split(","))
    else:
        method = 'GET'
        # required result is unchanged
    return check_http(url, method, required_result, post_data)

def check_http(url, method, required_result, post_data):
    """ Do the actual http check, internal function, not exposed via @task """

    if method == "POST":
        data = urllib.urlencode(post_data)
    if method == "GET":
        data = None
    else:
        raise AttributeError("Unknown method '%s', check_http is only prepared to operate with methods 'GET' and 'POST'" % method)

    required_result_numeric = False
    if re.search("^[2-5][0-9][0-9]$", required_result):
        required_result_numeric = True
        required_result = int(required_result)

    socket.setdefaulttimeout(env.timeout)
    req = urllib2.Request(url, data)
    try:
        response = urllib2.urlopen(req)
    except urllib2.URLError as e:
        if required_result_numeric and required_result == 401 and e.reason == "Unauthorized":
            return True
        else:
            return False
    except urllib2.HTTPError as e:
        # the request failed, unless response is numeric, and is matched, return false
        if required_result_numeric:
            if e.code == required_result:
                return True
            else:
                return False
        else:
            return False
    except socket.timeout:
    	# timeout should not be considered fatal
    	return False
    except Exception as e:
    	raise RuntimeError("Fatal problem occured while fetching result for '%s': %s" % (url, str(e)))

    # the request succeeded, inspect the result
    if required_result_numeric:
        # this is a http status, check if it's matched
        if response.getcode() == required_result:
            return True
        else:
            return False 
    else:
        # need to check a regex in the response body
        content = response.read()
        if re.search(required_result, content):
            return True
        else:
            return False
