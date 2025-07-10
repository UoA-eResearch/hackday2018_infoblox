#!/usr/bin/env python3
import infoblox #Uses Igor Feoktistov's infoblox.py
import json
import os
#from infoblox_client import connector
#from infoblox_client import objects

conf_file = os.path.abspath( os.path.join( os.path.dirname(__file__), '../conf/conf.json' ) )
with open( conf_file ) as f:
    conf = json.load(f)


iba_api = infoblox.infoblox('ipam.auckland.ac.nz', conf['user'], conf['password'], '2.5', 'default', 'default', True)


'''
print( "**** By IP ****")
try:
    #iba_api.create_host_record('130.216.218.66', 'mytardis.nectar.auckland.ac.nz') #Attach a name to an IP address
    hosts = iba_api.get_host_by_ip('130.216.161.169') #Check that the name is attached.
    print( hosts)
except Exception as e:
    print( e)

print "**** By Name *****"
try:
  hosts = iba_api.get_host(fqdn='akld2d18u15-api.nectar.auckland.ac.nz')
  print hosts
except Exception as e:
  print e

print "**** host by regular expression ****"
try:
  hosts = iba_api.get_host_by_regexp(fqdn='.*ceres.*')
  print hosts
except Exception as e:
  print e
'''
print( "**** get network *****")
try:
    hosts = iba_api.get_network(network='10.31.80.0/24')
    print( hosts)
except Exception as e:
  print( e)
'''

print "**** deleting host record ****"
try:
    iba_api.delete_host_record(fqdn='fred.nectar.auckland.ac.nz')
except Exception as e:
    print e

print "**** Done ****"
'''
