import re

def get_short_hostname(fqdn):
    """ Get the short hostname for an FQDN """
    m = re.search("^([^.]+)\.", fqdn)
    if m:
        return m.group(1)
    else:
        # just return the fqdn, it was a hostname after all
        return fqdn