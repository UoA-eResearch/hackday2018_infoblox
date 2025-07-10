#!/usr/bin/env python3
import json
import os
from infoblox_client import connector
from infoblox_client import objects


conf_file = os.path.abspath( os.path.join( os.path.dirname(__file__), '../conf/conf.json' ) )
with open( conf_file ) as f:
    conf = json.load(f)

opts = {'host': 'ipam.auckland.ac.nz', 'username': conf['user'], 'password': conf['password']}
conn = connector.Connector(opts)
# get all network_views
network_views = conn.get_object('networkview')
# search network by cidr in specific network view
network = conn.get_object('network', {'network': '0.0.0.0/0', 'network_view': 'default'})

print(network_views)

print(network)
