#!/usr/local/bin/python

import infoblox #Uses Igor Feoktistov's infoblox.py
import json

with open('../conf.json') as f:
    conf = json.load(f)


iba_api = infoblox.Infoblox('ipam.auckland.ac.nz', conf['user'], conf['password'], '2.5', 'default', 'default', False)
print "**** By IP ****"
try:
    hosts = iba_api.get_host_by_ip('130.216.216.98')
    print hosts
except Exception as e:
    print e
    
print "**** By Name *****"
try:
  hosts = iba_api.get_host(fqdn='minty.nectar.auckland.ac.nz')
  print hosts
except Exception as e:
  print e
  