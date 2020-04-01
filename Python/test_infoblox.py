#!/usr/local/bin/python
import infoblox #Uses Igor Feoktistov's infoblox.py
import json
import os

conf_file = os.path.abspath( os.path.join( os.path.dirname(__file__), '../conf/conf.json' ) )
with open( conf_file ) as f:
    conf = json.load(f)


iba_api = infoblox.Infoblox('ipam.auckland.ac.nz', conf['user'], conf['password'], '2.5', 'default', 'default', True)
print "**** By IP ****"
try:
    #iba_api.create_host_record('130.216.218.66', 'mytardis.nectar.auckland.ac.nz') #Attach a name to an IP address
    hosts = iba_api.get_host_by_ip('130.216.216.45') #Check that the name is attached.
    print hosts
except Exception as e:
    print e

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

print "**** get network *****"
try:
    hosts = iba_api.get_network(network='130.216.161.0/24')
    print hosts
except Exception as e:
  print e


#print "**** deleting host record ****"
#try:
#    iba_api.delete_host_record(fqdn='dashboard.uoa.nesi.org.nz')
#except Exception as e:
#    print e

print "**** Done ****"
