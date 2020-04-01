#!/usr/local/bin/python

import infoblox #Uses Igor Feoktistov's infoblox.py
import json
import os
import argparse
from collections import namedtuple

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
    raise SystemExit(1)

def create_host_record(api_fd, host_name, ip):
    try:
      print "creating A record", host_name, " ", ip
      api_fd.create_host_record(address=ip,fqdn=host_name)
    except Exception as e:
      print e
      raise SystemExit(1)

def delete_host_record(api_fd, host_name):
    try:
      print "Deleting A record", host_name
      api_fd.delete_host_record(fqdn=host_name)
    except Exception as e:
      print e

def add_host_alias(api_fd, host_name, alias):
    try:
      print "creating alias ", host_name, " ", alias
      api_fd.add_host_alias(host_fqdn=host_name, alias_fqdn=alias)
    except Exception as e:
      print e

def delete_host_alias(api_fd, host_name, alias):
    try:
      print "removing alias ", host_name, " ", alias
      api_fd.delete_host_alias(host_fqdn=host_name, alias_fqdn=alias)
    except Exception as e:
      print e

def add_host_cname(api_fd, host_name, cname):
    try:
      print "creating cname ", host_name, " ", alias
      api_fd.create_cname_record(self, canonical=cname, name=host_name)
    except Exception as e:
      print e

def delete_host_cname(api_fd, cname):
    try:
      print "removing cname ", cname
      api_fd.create_cname_record(self, fqdn=cname)
    except Exception as e:
      print e

def get_host(api_fd, host_name, fields=None):
    try:
      print "Getting host details ", host_name
      return api_fd.get_host(fqdn=host_name, fields=fields)
    except Exception as e:
      print e

def get_host_by_ip(api_fd, ip_v4, fields=None):
    try:
      return api_fd.get_host_by_ip(ip_v4=ip_v4)
    except Exception as e:
      print e
      
def parse_args():
  parser = argparse.ArgumentParser(description='UoA NeCTar IPAM queries')
  #parser.add_argument('-s', '--show', dest='show', action='store_true', help='show current dns entry')
  parser.add_argument('-i', '--ip', dest='host_ip', help='action against this host ip')
  parser.add_argument('-H', '--hostname', dest='hostname', help='host name')
  parser.add_argument('-a', '--alias', dest='alias',  help='alias for dns entry')
  parser.add_argument('-c', '--cname', dest='cname',  help='cname for dns entry')
  parser.add_argument('-n', '--new', dest='new_entry', action='store_true', help='create new dns entry')
  parser.add_argument('-m', '--modify', dest='modify_entry', action='store_true', help='modify existing dns entry')
  parser.add_argument('-d', '--delete', dest='delete_entry',  help='delete dns entry')
  return parser.parse_args()
  
def run(args):
  api_fd = ipam_open()

  if args.new_entry:
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
      res = get_host(api_fd=api_fd, host_name = r1[0], fields="ipv4addrs,name,dns_name,aliases,dns_aliases") 
    elif args.hostname:
      res = get_host(api_fd=api_fd, host_name = args.hostname, fields="ipv4addrs,name,dns_name,aliases,dns_aliases") 
    else:
      print "require hostname or ip address"
      
  if res is not None:
    #print res
    for r in res['ipv4addrs']:
      print r['ipv4addr'], ' ', r['host']
    for a in res['dns_aliases']:
      print "  ALIAS ", a

def add_node_body(short_hostname, suffix, ip):
  args = Args(host_ip = ip , hostname="akld2%s%s.nectar.auckland.ac.nz"%(short_hostname,suffix), new_entry=True)
  run(args=args)
  args = Args(hostname="akld2%s%s.nectar.auckland.ac.nz"%(short_hostname, suffix), alias="%s%s.nectar.auckland.ac.nz"%(short_hostname,suffix), modify_entry=True)
  run(args=args)

def add_nectar_node(short_hostname, ipv4_subnet, ipv4_host, mgmt=True, prov=True, api=True, ceph=False):
  #Mimic argv argument list
  if mgmt:
    add_node_body(short_hostname=short_hostname, suffix='-m', ip="172.31.%d.%d"%(net_prefix, ipv4_subnet,ipv4_host) )
  if prov:
    add_node_body(short_hostname=short_hostname, suffix='-p', ip="10.31.%d.%d"%(net_prefix, ipv4_subnet,ipv4_host) )
  if api:
    add_node_body(short_hostname=short_hostname, suffix='-api', ip="10.31.%d.%d"%(net_prefix, ipv4_subnet+4,ipv4_host) )
  if ceph:
    add_node_body(short_hostname=short_hostname, suffix='-ceph', ip="10.31.%d.%d"%(net_prefix, ipv4_subnet+8,ipv4_host) )
    

def print_basic_nectar_host(short_hostname):
  args = Args(hostname="akld2%s-m.nectar.auckland.ac.nz"%(short_hostname))
  run(args=args)
  args = Args(hostname="akld2%s-p.nectar.auckland.ac.nz"%(short_hostname))
  run(args=args)
  args = Args(hostname="akld2%s-api.nectar.auckland.ac.nz"%(short_hostname))
  run(args=args)
  
def print_host(host_name=None, ip=None):
  if ip is not None:
    args = Args(host_ip=ip)
  else:
    args = Args(hostname=host_name)
  run(args=args)
  

Args = namedtuple('Args', ["host_ip", "hostname", "alias", "cname", "delete_entry", "modify_entry", "new_entry"],  verbose=False, rename=False)
Args.__new__.func_defaults = (None,   None,        None,    None,    False,         False,           False)

#add_basic_nectar_node(short_hostname='i15u34', ipv4_subnet=83, ipv4_host=84)
#print_basic_nectar_host(short_hostname='h18u02')
print_host(host_name='ntr-sto02-p.nectar.auckland.ac.nz')
print_host(host_name='akld2h18u03-p.nectar.auckland.ac.nz')
print_host(ip='10.31.80.65')

exit(0)

############# Command line version, but doesn't work on NeCTaR, as we look to have been firewalled again #########

run(args=parse_args())

