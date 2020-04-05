#!/usr/local/bin/python

import infoblox #Uses Igor Feoktistov's infoblox.py
import json
import os
import argparse
from recordtype import recordtype #pip install recordtype

#Open a connetion to IPAM, using the authentication tokens in conf.json
# @return [Infoblox] 
# @raise [SystemExit] when the 1. conf.json can't be read, or 2, when a connection can't be established
def ipam_open():
  conf_file = os.path.abspath( os.path.join( os.path.dirname(__file__), '../conf/conf.json' ) )
  #conf_file = '/home/ntradm/etc/ipam.json'
  try:
    with open( conf_file ) as f:
      conf = json.load(f)
  except Exception as e:
    print e
    raise SystemExit(1)
    
  try:
    api_fd = infoblox.Infoblox('ipam.auckland.ac.nz', conf['user'], conf['password'], '2.5', 'default', 'default', True)
    return api_fd
  except Exception as e:
    print e
    raise SystemExit(2)

#wrapper around infoblox.create_host_record to catch any exceptions
#Prints and ignores exceptions raised by Infoblox calls, which may be a bad idea
# @param api_fd [Infoblox] from ipam_open
# @param hostname [String] Hostname for record created
# @param ip [String] IPV4 ip address, as a string
def create_host_record(api_fd, host_name, ip):
    try:
      print "creating A record", host_name, " ", ip
      api_fd.create_host_record(address=ip,fqdn=host_name)
    except Exception as e:
      print e

#wrapper around infoblox.delete_host_record to catch any exceptions
#Prints and ignores exceptions raised by Infoblox calls, which may be a bad idea
# @param api_fd [Infoblox] from ipam_open
# @param hostname [String] Hostname for record created
def delete_host_record(api_fd, host_name):
    try:
      print "Deleting A record", host_name
      api_fd.delete_host_record(fqdn=host_name)
    except Exception as e:
      print e

#wrapper around infoblox.add_host_alias to catch any exceptions
#Prints and ignores exceptions raised by Infoblox calls, which may be a bad idea
#Infoblox ALIAS records are mapped to DNS A records. 
#This is a way to group hostnames within infoblox. ALIAS does not exist in DNS
# @param api_fd [Infoblox] from ipam_open
# @param hostname [String] Hostname, used as key to add alias
# @param alias [String] Second DNS A record name for this host.
def add_host_alias(api_fd, host_name, alias):
    try:
      print "creating alias ", host_name, " ", alias
      api_fd.add_host_alias(host_fqdn=host_name, alias_fqdn=alias)
    except Exception as e:
      print e

#wrapper around infoblox.delete_host_alias to catch any exceptions
#Prints and ignores exceptions raised by Infoblox calls, which may be a bad idea
#Infoblox ALIAS records are mapped to DNS A records. 
#This is a way to group hostnames within infoblox. ALIAS does not exist in DNS
# @param api_fd [Infoblox] from ipam_open
# @param hostname [String] Hostname, used as key to delete alias from
# @param alias [String] Second DNS A record name for this host.
def delete_host_alias(api_fd, host_name, alias):
    try:
      print "removing alias ", host_name, " ", alias
      api_fd.delete_host_alias(host_fqdn=host_name, alias_fqdn=alias)
    except Exception as e:
      print e

#wrapper around infoblox.create_cname_record to catch any exceptions
#Prints and ignores exceptions raised by Infoblox calls, which may be a bad idea
#DNS CNAME records are mappings to A records, using the A record hostname as the key 
# @param api_fd [Infoblox] from ipam_open
# @param hostname [String] Hostname, used as key to add CNAME
# @param cname [String] DNS CNAME hostname for this host.
def add_host_cname(api_fd, host_name, cname):
    try:
      print "creating cname ", host_name, " ", alias
      api_fd.create_cname_record(self, canonical=cname, name=host_name)
    except Exception as e:
      print e

#wrapper around infoblox.delete_cname_record to catch any exceptions
#Prints and ignores exceptions raised by Infoblox calls, which may be a bad idea
#DNS CNAME records are mappings to A records, using the A record hostname as the key 
# @param api_fd [Infoblox] from ipam_open
# @param cname [String] DNS CNAME hostname for a host (we don't need the A record Hostname to delete a CNAME record).
def delete_host_cname(api_fd, cname):
    try:
      print "removing cname ", cname
      api_fd.delete_cname_record(self, fqdn=cname)
    except Exception as e:
      print e

#wrapper around infoblox.get_host_by_regexp to catch any exceptions
#Current call does not pick up infoblox ALIAS or CNAME records for the hostname
# @param api_fd [Infoblox] from ipam_open
# @param re [String] Hostname as regular expression, 
# @param fields [String] list of fields for infoblox to return (see infoblox api docs
# @return [Dictionary] Result of Rest api call by 'request', parsed by reqest.json
def get_host_by_re(api_fd, re):
  try:
    return api_fd.get_host_by_regexp(fqdn=re)
  except Exception as e:
    print e

#add missing infoblox get_host_by_alias
# @param api_fd [Infoblox] from ipam_open
# @param alais [String] ALIAS for hostname
# @param fields [String] list of fields for infoblox to return (see infoblox api docs
# @return [Dictionary] Result of Rest api call by 'request', parsed by reqest.json
import requests
def get_host_by_alias(api_fd, alias, fields=None):
  """ Implements IBA REST API call to retrieve host record fields
  Returns hash table of fields with field name as a hash key
  :param fqdn: hostname in FQDN
  :param fields: comma-separated list of field names (optional)
  """
  if fields:
      rest_url = 'https://' + api_fd.iba_host + '/wapi/v' + api_fd.iba_wapi_version + '/record:host?alias=' + alias + '&view=' + api_fd.iba_dns_view + '&_return_fields=' + fields
  else:
      rest_url = 'https://' + api_fd.iba_host + '/wapi/v' + api_fd.iba_wapi_version + '/record:host?alias=' + alias + '&view=' + api_fd.iba_dns_view
  try:
      r = requests.get(url=rest_url, auth=(api_fd.iba_user, api_fd.iba_password), verify=api_fd.iba_verify_ssl)
      r_json = r.json()
      if r.status_code == 200:
  	if len(r_json) > 0:
  	    return r_json[0]
  	else:
  	    raise infoblox.InfobloxNotFoundException("No hosts found: " + alias)
      else:
  	if 'text' in r_json:
  	    raise infoblox.InfobloxNotFoundException(r_json['text'])
  	else:
  	    r.raise_for_status()
  except ValueError:
      raise Exception(r)
  except Exception:
      raise


#wrapper around infoblox.get_host to catch any exceptions
#Current call does not pick up infoblox ALIAS or CNAME records for the hostname
# @param api_fd [Infoblox] from ipam_open
# @param hostname [String] Hostname
# @param fields [String] list of fields for infoblox to return (see infoblox api docs
# @return [Dictionary] Result of Rest api call by 'request', parsed by reqest.json
def get_host(api_fd, host_name, fields=None):
    try:
      #print "Getting host details for: ", host_name
      return api_fd.get_host(fqdn=host_name, fields=fields)
    except infoblox.InfobloxNotFoundException as e:
      try:
        return get_host_by_alias(api_fd=api_fd, alias = host_name, fields=fields)
      except Exception as e:
        print e
    except Exception as e:
      print e

#wrapper around infoblox.create_cname_record to catch any exceptions
#Current call does not pick up infoblox ALIAS or CNAME records for the hostname
# @param api_fd [Infoblox] from ipam_open
# @param ip_v4 [String] IPV4 address of record
# @return [Dictionary] Result of Rest api call by 'request', parsed by reqest.json
def get_host_by_ip(api_fd, ip_v4):
    try:
      return api_fd.get_host_by_ip(ip_v4=ip_v4)
    except Exception as e:
      print e
      
#Generate the IP address and Hostname, from the TDC rack and u. 
#Called from run when args.tdc_rack is not None.
# @param args [Record] Either generated by parse_args() or from fake_cli_args()
# @yield new_args [Record] yield the IP and Hostname, with all other 'args' copied to new_args, except tdc_rack, tdc_rack_u and tdc_rack_x
def enumerate_hosts(args):
  rack_to_subnet = { 'b15': [82,100], 'd15': [81,150], 'e15': [81,50], 'h15': [83,150], 'i15': [83,50], 'b18': [82,0], 'd18': [81,100], 'e18': [81,0], 'h18': [83,100], 'i18': [83,0]}
  r2s = rack_to_subnet[args.tdc_rack]
  if r2s is None:
    print "Unknown Rack %s"%(args.tdc_rack)
    raise SystemExit(2)
  else:
    subnet = r2s[0]
    ip = r2s[1] + int(args.tdc_rack_u)
    uchar = 'x' if args.tdc_rack_x else 'u'
    short_hostname = "%s%s%02d"%(args.tdc_rack, uchar, int(args.tdc_rack_u))
    
  new_args = args
  new_args.tdc_rack=None
  new_args.tdc_rack_u=None
  new_args.tdc_rack_x=False
  
  if args.management:
    new_args.host_ip = "172.31.%s.%s"%(subnet,ip) 
    new_args.hostname="akld2%s-m.nectar.auckland.ac.nz"%(short_hostname)
    yield new_args
    
    #If we get the inband 172.31.84.0/22 allocated, then we want these -m2 addresses too
    #new_args.host_ip = "172.31.%s,%s"%(subnet+4,ip) 
    #new_args.hostname="akld2%s-m2.nectar.auckland.ac.nz"%(short_hostname)
    #yield new_args
    
  if args.provisioning:
    new_args.host_ip = "10.31.%s.%s"%(subnet,ip) 
    new_args.hostname="akld2%s-p.nectar.auckland.ac.nz"%(short_hostname)
    yield new_args
    
  if args.api:
    new_args.host_ip = "10.31.%s.%s"%(subnet+4,ip) 
    new_args.hostname="akld2%s-api.nectar.auckland.ac.nz"%(short_hostname)
    yield new_args
    
  if args.ceph:
    new_args.host_ip = "10.31.%s.%s"%(subnet+8,ip) 
    new_args.hostname="akld2%s-ceph.nectar.auckland.ac.nz"%(short_hostname)
    yield new_args
    
  if args.replication:
    new_args.host_ip = "10.31.%s.%s"%(subnet+12,ip) 
    new_args.hostname="akld2%s-repl.nectar.auckland.ac.nz"%(short_hostname)
    yield new_args
  
from argparse import RawTextHelpFormatter
#Process sys.argv arguments
# @return [argparse.Namespace] All the arguments (including unused ones), are return as args.<x> where <x> is defined by dest=
def parse_args():
  parser = argparse.ArgumentParser(description='UoA NeCTar IPAM queries', add_help=False, formatter_class=RawTextHelpFormatter)
  parser.add_argument('-?', '--help', action='help', default=argparse.SUPPRESS, help=argparse._('show this help message and exit'))
  parser.add_argument('-i', '--ip', dest='host_ip', help='action against this host ip')
  parser.add_argument('-h', '--hostname', dest='hostname', help='host name')
  parser.add_argument('-H', '--re_hostname', dest='re_hostname', help='host name as regular expression (ensure you use ^ and $)')
  parser.add_argument('-a', '--alias', dest='alias',  help='alias for dns entry')
  parser.add_argument('-c', '--cname', dest='cname',  help='cname for dns entry')
  parser.add_argument('-n', '--new', dest='new_entry', action='store_true', help='create new dns entry')
  parser.add_argument('-m', '--modify', dest='modify_entry', action='store_true', help='modify existing dns entry')
  parser.add_argument('-d', '--delete', dest='delete_entry',  help='delete dns entry')
  parser.add_argument('-r', '--rack', dest='tdc_rack', help='TDC Rack (when using autogeneration)')
  parser.add_argument('-u', '--u', dest='tdc_rack_u', help='TDC Rack U (when using autogeneration)')
  parser.add_argument('-x', '--switch', dest='tdc_rack_x', action='store_true', help='TDC Rack U is a switch (so name is <rack>x<u>)')
  parser.add_argument('--mgmt', dest='management', action='store_true', help='Generate management address. Needs --rack and --u')
  parser.add_argument('--prov', dest='provisioning', action='store_true', help='Generate provisioning address. Needs --rack and --u')
  parser.add_argument('--api', dest='api', action='store_true', help='Generate api address. Needs --rack and --u')
  parser.add_argument('--ceph', dest='ceph', action='store_true', help='Generate ceph storage network address. Needs --rack and --u')
  parser.add_argument('--repl', dest='replication', action='store_true', help='Generate replication address. Needs --rack and --u')
  return parser.parse_args()
  
#Show, Modify, Delete or Create IPAM DNS entries in Infoblox
# @param args [Record] Either generated by parse_args() or from fake_cli_args()
def run(args):
  api_fd = ipam_open()
  #print args
  res = None
  
  if args.tdc_rack is not None:
    if args.tdc_rack_u is None:
      print "Require rack U"
      raise SystemExit(2)
      
    for new_args in enumerate_hosts(args):
      run(new_args)
    return #finished enumeration
    
  elif args.re_hostname is not None:
    host_list = get_host_by_re(api_fd=api_fd, re=args.re_hostname)
    if host_list is not None:
      for h in host_list:
        run(args = Args(hostname=h))
    return

  elif args.new_entry:
    if args.host_ip is not None and args.hostname is not None:
      create_host_record(api_fd=api_fd, host_name=args.hostname, ip=args.host_ip)
      res = get_host(api_fd=api_fd, host_name=args.hostname, fields="ipv4addrs,name,dns_name,aliases,dns_aliases")
    else:
      print "Creating new entry requires hostname and ip address."
      
  elif args.modify_entry:
    if args.hostname is None:
      print "Require hostname"
    else:
      if args.alias is not None:
        add_host_alias(api_fd=api_fd, host_name=args.hostname, alias=args.alias)
      if args.cname is not None:
        add_host_cname(api_fd=api_fd, host_name=args.hostname, cname=args.cname)
      res = get_host(api_fd=api_fd, host_name=args.hostname, fields="ipv4addrs,name,dns_name,aliases,dns_aliases")
      
  elif args.delete_entry:
    if args.hostname is None:
      print "Require hostname"
    else:
      if args.alias is not None:
        delete_host_alias(api_fd=api_fd, host_name=args.hostname, alias=args.alias)
      if args.cname is not None:
        delete_host_cname(api_fd=api_fd, cname=args.cname)
      res = get_host(api_fd=api_fd, host_name=args.hostname, fields="ipv4addrs,name,dns_name,aliases,dns_aliases")

  else: # args.show
    if args.host_ip is not None:
      r1 = get_host_by_ip(api_fd=api_fd, ip_v4=args.host_ip)
      if r1 is None:
        res = None
      else:
        res = get_host(api_fd=api_fd, host_name = r1[0], fields="ipv4addrs,name,dns_name,aliases,dns_aliases") 
    elif args.hostname:
      res = get_host(api_fd=api_fd, host_name = args.hostname, fields="ipv4addrs,name,dns_name,aliases,dns_aliases") 
    else:
      print "require hostname or ip address"
      
  if res is not None:
    #print res
    if 'ipv4addrs' in res.keys():
      for r in res['ipv4addrs']:
        print r['ipv4addr'], ' ', r['host']
    if 'dns_aliases' in res.keys():
      for a in res['dns_aliases']:
        print "  ALIAS ", a

#Test run, with fake arguments, so we don't need to run from the command line.
def fake_cli_args():

  #args = Args(tdc_rack="h15",tdc_rack_u="35",management=True,api=True,ceph=True,replication=True)
  args = Args(hostname='h15u35.nectar.auckland.ac.nz')
  #args = Args(host_ip='130.216.81.226')
  run(args=args)
  
#Create an Args record, so we can create dummy ARGV entries for testing.
Args = recordtype('Args', [ ("host_ip", None), ("hostname", None), ("alias", None), ("cname", None), ("delete_entry", False), ("modify_entry", False), ("new_entry", False), ("management", False), ("provisioning", False), ("api", False), ("ceph", False), ("replication", False), ("tdc_rack", None), ("tdc_rack_u", None), ("tdc_rack_x", False), ("re_hostname", None) ] )

#fake_cli_args()
#exit(0)

run(args=parse_args())

