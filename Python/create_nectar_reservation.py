#!/usr/local/bin/python

import infoblox #Uses Igor Feoktistov's infoblox.py
import json
import os

conf_file = os.path.abspath( os.path.join( os.path.dirname(__file__), '../conf/conf.json' ) )
with open( conf_file ) as f:
    conf = json.load(f)


iba_api = infoblox.Infoblox('ipam.auckland.ac.nz', conf['user'], conf['password'], '2.5', 'default', 'default', True)


for i in range(2, 9):
  try:
      if( i != 69 ):
          host = "ivm{:0>2d}.nectar.auckland.ac.nz".format(i)
          ip = "130.216.189.{:d}".format(i)
          print "creating ", host, " ", ip
          iba_api.create_host_record(address=ip,fqdn=host)
  except Exception as e:
      print e

print "done"
