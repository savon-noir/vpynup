#!/usr/bin/env python

import sys
import getopt
import glob
import json
from vpynup.vpnbootstrap import VpnBootstrap

# debug
from pprint import pprint

def main(argv):
    default_config = "default.json"
    args_config = handle_args(argv)

    configs = glob.glob('*.json')

    if args_config is not None and args_config in configs:
        config_file = args_config
    elif args_config is None and default_config in configs:
        config_file = default_config
    else:
        sys.stderr.write("No config file provided or default.json "
                         "does not exists in local folder\n")
        usage()
    with open(config_file) as json_file:
        json_obj = json.load(json_file)

    vpnup = VpnBootstrap(json_obj)
    vpnup.start()
#    vpnup.instance.create()
#    vpnup.instance.start()
#    vpnup.instance.install("puppet")
#    vpnup.instance.provider.configure()
#    vpnup.instance.get_openvpn_certs()
#
#    print vpnup.instance.settings()


def handle_args(argv):
    config_file = None
    try:
        opts, args = getopt.getopt(argv, "hc:", ["help", "config="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()                     
            sys.exit()                  
        elif opt in ("-c", "--config"): 
            config_file = arg
    return config_file


def usage():
    print "usage: vpnup.py [--config <config_name.json>]"
    sys.exit(1)

if __name__ == "__main__":
    main(sys.argv[1:])




