from fabric.api import *

import re
import os.path
import socket

import logging
import utils.log

l = logging.getLogger()
l = utils.log.CustomLogAdapter(l, None)

@task(default=True)
def simple(input_params, cluster):
    """ Enable/disble traffic using simple iptables rules

        input_params parameter is a string, with the following fields:
        enable|disable|add|remove:protocol:ports[:REJECT|DROP]

        If the target is not provided, REJECT will be used.
        To allow working of the http checks, an allow rule for the given ports will be added
        for the host running taskmgr

        The enable/disable/add/remove is a bit controversial:
            enable/disable: enable or disable _traffic_:
                enable (traffic) -> remove iptables rules 
                disable (traffic) -> add iptables rules

            add/remove
                add (iptables rules) -> add iptables rules
                remove (iptables rules) -> remove iptables rules
    """
    # split up the input_params, and make sense of it
    m = re.search("^(enable|disable|add|remove):(tcp|udp):((?:[0-9]+,?)+)(?::(input|output|forward))?(?::(reject|drop))?$", input_params, re.IGNORECASE)
    if not m:
        raise AttributeError("The given input_params '%s' doesn't match the requirements!" % input_params)

    action, protocol, ports, chain, target = m.groups()

    if target is None:
        target = "REJECT"
    else:
        target = target.uppercase()

    if chain is None:
        chain = "INPUT"
    else:
        chain = chain.uppercase()

    ports = [ int(x) for x in ports.split(",") ]

    # disable means to disable firewall => -D
    if action == "enable" or action == "remove":
        action_string = "-D"
    elif action == "disable" or action == "add":
        action_string = "-A"

    # get the source ip address(es) of the local machine
    ips = detect_local_ipaddress()

    # check if iptables exists
    try:
        result = sudo("iptables -L")
    except:
        return False

    if result.failed:
        raise RuntimeError("%s: There seems to be a problem with iptables: %s" % (env.command, result))
    

    # add/remove firewall rules for allowing ourselves
    for port in sorted(ports):
        for source_ip in ips:
            command = "iptables %s %s -p %s -s %s --dport %d -j ACCEPT" % (action_string, chain, protocol, source_ip, port)
            try:
                result = sudo(command)
            except:
                return False

            if result.failed:
                raise RuntimeError("%s: failed running iptables command: %s" % (env.command, command))

    # add/remove rules for everybody else
    for port in sorted(ports):
        command = "iptables %s %s -p %s --dport %d -j %s" % (action_string, chain, protocol, port, target)
        try:
            result = sudo(command)
        except:
            return False

        if result.failed:
            raise RuntimeError("%s: failed running iptables command: %s" % (env.command, command))

    # if here, all went well
    return True

def detect_local_ipaddress():
    # try to get the fqdn using hostname -f, and use that
    result = None
    try:
        with quiet():
			result = local("hostname -I", capture=True)
			ips = list()
			for ip in result.split(" "):
				try:
					socket.inet_aton(ip)
					ips.append(ip)
				except:
					continue
			if len(ips):
				return ips
			else:
				raise RuntimeError("%s: failed to detect IP address via 'hostname -I'!" % env.command)
			return ips
    except:
        pass
    
    if result is None or result.failed:
        # do some heuristics and use ips that are found in the output of iproute
        try:
            with quiet():
                result = local("/sbin/ip a|grep inet|grep -v inet6|grep -v 127.0.0|awk '{print $2}'|cut -d'/' -f1", capture=True)

        except Exception as e:
            raise RuntimeError("%s: failed to detect IP address for local machine: %s" % (env.command, str(e)))

        if result.succeeded:
            return result.split("\n")
        else:
            raise RuntimeError("%s: failed to detect IP address for local machine" % env.command)

