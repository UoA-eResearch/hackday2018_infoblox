#!/usr/local/bin/python

import infoblox #Uses Igor Feoktistov's infoblox.py
import json
import os

conf_file = os.path.abspath( os.path.join( os.path.dirname(__file__), '../conf/conf.json' ) )
with open( conf_file ) as f:
    conf = json.load(f)

iba_api = infoblox.Infoblox('ipam.auckland.ac.nz', conf['user'], conf['password'], '2.5', 'default', 'default', True)

def delete_host_alias(host_name, alias):
    try:
        print "removing alias ", host_name, " ", alias
        iba_api.delete_host_alias(host_fqdn=host_name, alias_fqdn=alias)
    except Exception as e:
        print e

def create_host_record(host_name, ip):
    try:
      print "creating A record", host_name, " ", ip
      iba_api.create_host_record(address=ip,fqdn=host_name)
    except Exception as e:
      print e

def delete_host_record(host_name):
    try:
      print "Deleting A record", host_name
      iba_api.delete_host_record(fqdn=host_name)
    except Exception as e:
      print e

def add_host_alias(host_name, alias):
    try:
      print "creating alias ", host_name, " ", alias
      iba_api.add_host_alias(host_fqdn=host_name, alias_fqdn=alias)
    except Exception as e:
      print e

def get_host(host_name, fields=None):
    try:
      print "Getting host details ", host_name
      return iba_api.get_host(fqdn=host_name, fields=fields)
    except Exception as e:
      print e

def get_host_by_ip(ip_v4):
    try:
      return iba_api.get_host_by_ip(ip_v4=ip_v4)
    except Exception as e:
      print e

idrac_hosts = {
    #Switches
    "172.31.80.1": ["akld2g18x40", "ntr-x1-mgmt","x1-m","x1","g18x40-m","g18x40"],
    "172.31.80.2": ["akld2g18x37","ntr-x2-prov1","x2-m","x2","g18x37-m","g18x37"],
    "172.31.80.3": ["akld2h18x27","ntr-x3-prov2","x3-m","x3","h18x37-m","h18x37"],
    "172.31.80.4": ["akld2g18x32","ntr-x4-core1","x4-m","x4","g18x32-m","g18x32"],
    "172.31.80.5": ["akld2h18x32","ntr-x5-core2","x5-m","x5","h18x32-m","h18x32"],
    "172.31.80.6": ["akld2g18x31","ntr-x6-core3","x6-m","x6","g18x31-m","g18x31"],
    "172.31.80.7": ["akld2h18x31","ntr-x7-core4","x7-m","x7","h18x31-m","h18x31"],
    "172.31.80.8": ["ntr-x8-core4","x8-m","x8"],
    "172.31.80.9": ["ntr-x9-core4","x9-m","x9"],
    "172.31.80.10": ["akld2e18x21","ntr-x10","x10-m","x10","e18x21-m","e18x21"],
    "172.31.80.11": ["akld2e18x22","ntr-x11","x11-m","x11","e18x22-m","e18x22"],
    "172.31.80.12": ["akld2e18xb4","ntr-x12","x12-m","x12","e18xb4-m","e18xb4"],
    "172.31.80.13": ["akld2d18xd4","ntr-x13","x13-m","x13","d18xd4-m","d18xd4"],
    "172.31.80.14": ["akld2d18x42","ntr-x14","x14-m","x14","d18x41-m","d18x41"],
    "172.31.80.15": ["akld2d18x43","ntr-x15","x15-m","x15","d18x42-m","d18x42"],
    "172.31.80.16": ["akld2b18x19","ntr-x16","x16-m","x16","b18x19-m","b18x19"],
    "172.31.80.17": ["akld2b18x20","ntr-x17","x17-m","x17","b18x20-m","b18x20"],
    "172.31.80.18": ["akld2b19x21","ntr-x18","x18-m","x18","b18x21-m","b18x21"],
    "172.31.80.19": ["akld2b15x42","ntr-x19","x19-m","x19","b15x42-m","b15x42"],
    "172.31.80.20": ["akld2b15x41","ntr-x20","x20-m","x20","b15x41-m","b15x41"],
    #
    "172.31.80.128": ["akld2g18u24-m","g18u24-m","d2ntrcop01-idrac","ntr-cop01-m","cop01-m"],
    "172.31.80.129": ["akld2g18u25-m","g18u25-m","d2ntrcop02-idrac","ntr-cop02-m","cop02-m"],
    "172.31.80.130": ["akld2g18u26-m","g18u26-m","d2ntrcop03-idrac","ntr-cop03-m","cop03-m"],
    "172.31.80.131": ["akld2h18u23-m","h18u23-m","d2ntrcop04-idrac","ntr-cop04-m","cop04-m"],
    "172.31.80.132": ["akld2h18u24-m","h18u24-m","d2ntrcop05-idrac","ntr-cop05-m","cop05-m"],
    "172.31.80.133": ["akld2h18u25-m","h18u25-m","d2ntrcop06-idrac","ntr-cop06-m","cop06-m"],
    "172.31.80.134": ["akld2h18u26-m","h18u26-m","d2ntrcop07-idrac","ntr-cop07-m","cop07-m"],
    "172.31.80.135": ["akld2g18u44-m","g18u44-m","d2ntrcop08-idrac","ntr-cop08-m","cop08-m"],
    "172.31.80.136": ["akld2g18u27-m","g18u27-m","d2ntrcop09-idrac","ntr-cop09-m","cop09-m"],
    "172.31.80.137": ["akld2h18u27-m","h18u27-m","d2ntrcop10-idrac","ntr-cop10-m","cop10-m"],
    "172.31.80.138": ["akld2g18u28-m","g18u28-m","d2ntrcop11-idrac","ntr-cop11-m","cop11-m"],
    #
    "172.31.80.31": ["akld2g18a17-m","g18a17-m","d2ntradm01-idrac","ntr-adm01-m","adm01-m"],
    "172.31.80.32": ["akld2h18a17-m","h18a17-m","d2ntradm02-idrac","ntr-adm02-m","adm02-m"],
    "172.31.80.41": ["akld2g18a18-m","g18a18-m","d2ntrctr01-idrac","ntr-ctr01-m","ctr01-m"],
    "172.31.80.42": ["akld2h18a18-m","h18a18-m","d2ntrctr02-idrac","ntr-ctr02-m","ctr02-m"],
    "172.31.80.43": ["akld2g18a19-m","g18a19-m","d2ntrctr03-idrac","ntr-ctr03-m","ctr03-m"],
    #
    "172.31.80.64": ["akld2g18s01-m","g18s01-m","d2ntrsto01-idrac","ntr-sto01-m","sto01-m"],
    "172.31.80.65": ["akld2g18s03-m","g18s03-m","d2ntrsto02-idrac","ntr-sto02-m","sto02-m"],
    "172.31.80.66": ["akld2g18s05-m","g18s05-m","d2ntrsto03-idrac","ntr-sto03-m","sto03-m"],
    "172.31.80.67": ["akld2g18s07-m","g18s07-m","d2ntrsto04-idrac","ntr-sto04-m","sto04-m"],
    "172.31.80.68": ["akld2h18s01-m","h18s01-m","d2ntrsto05-idrac","ntr-sto05-m","sto05-m"],
    "172.31.80.69": ["akld2h18s03-m","h18s03-m","d2ntrsto06-idrac","ntr-sto06-m","sto06-m"],
    "172.31.80.70": ["akld2h18s05-m","h18s05-m","d2ntrsto07-idrac","ntr-sto07-m","sto07-m"],
    "172.31.80.71": ["akld2h18s07-m","h18s07-m","d2ntrsto08-idrac","ntr-sto08-m","sto08-m"],
    "172.31.80.72": ["akld2g18s09-m","g18s09-m","d2ntrsto09-idrac","ntr-sto09-m","sto09-m"],
    "172.31.80.73": ["akld2h18s09-m","h18s09-m","d2ntrsto10-idrac","ntr-sto10-m","sto10-m"],
    "172.31.80.74": ["akld2g18s11-m","g18s11-m","d2ntrsto11-idrac","ntr-sto11-m","sto11-m"],
    "172.31.80.75": ["akld2h18s11-m","h18s11-m","d2ntrsto12-idrac","ntr-sto12-m","sto12-m"],
    "172.31.80.76": ["akld2g18s13-m","g18s13-m","d2ntrsto13-idrac","ntr-sto13-m","sto13-m"],
    "172.31.80.77": ["akld2h18s13-m","h18s13-m","d2ntrsto14-idrac","ntr-sto14-m","sto14-m"],
}

e18_d18_management = {
#Management E18 Rack
    "172.31.81.1": ["akld2e18u01-m", "e18u01-m"],
    "172.31.81.2": ["akld2e18u02-m", "e18u02-m"],
    "172.31.81.3": ["akld2e18u03-m", "e18u03-m"],
    "172.31.81.4": ["akld2e18u04-m", "e18u04-m"],
    "172.31.81.5": ["akld2e18u05-m", "e18u05-m"],
    "172.31.81.6": ["akld2e18u06-m", "e18u06-m"],
    "172.31.81.7": ["akld2e18u07-m", "e18u07-m"],
    "172.31.81.8": ["akld2e18u08-m", "e18u08-m"],
    "172.31.81.9": ["akld2e18u09-m", "e18u09-m"],
    "172.31.81.10": ["akld2e18u10-m", "e18u10-m"],
    "172.31.81.11": ["akld2e18u11-m", "e18u11-m"],
    "172.31.81.12": ["akld2e18u12-m", "e18u12-m"],
    "172.31.81.13": ["akld2e18u13-m", "e18u13-m"],
    "172.31.81.14": ["akld2e18u14-m", "e18u14-m"],
    "172.31.81.15": ["akld2e18u15-m", "e18u15-m"],
    "172.31.81.16": ["akld2e18u16-m", "e18u16-m"],
    "172.31.81.17": ["akld2e18u17-m", "e18u17-m"],
    "172.31.81.18": ["akld2e18u18-m", "e18u18-m"],
    "172.31.81.19": ["akld2e18u19-m", "e18u19-m"],
    "172.31.81.20": ["akld2e18u20-m", "e18u20-m"],
    "172.31.81.21": ["akld2e18u21-m", "e18u21-m"],
    "172.31.81.22": ["akld2e18u22-m", "e18u22-m"],
    "172.31.81.23": ["akld2e18u23-m", "e18u23-m"],
    "172.31.81.24": ["akld2e18u24-m", "e18u24-m"],
    "172.31.81.25": ["akld2e18u25-m", "e18u25-m"],
    "172.31.81.26": ["akld2e18u26-m", "e18u26-m"],
    "172.31.81.27": ["akld2e18u27-m", "e18u27-m"],
    "172.31.81.28": ["akld2e18u28-m", "e18u28-m"],
    "172.31.81.29": ["akld2e18u29-m", "e18u29-m"],
    "172.31.81.30": ["akld2e18u30-m", "e18u30-m"],
    "172.31.81.31": ["akld2e18u31-m", "e18u31-m"],
    "172.31.81.32": ["akld2e18u32-m", "e18u32-m"],
    "172.31.81.33": ["akld2e18u33-m", "e18u33-m"],
    "172.31.81.34": ["akld2e18u34-m", "e18u34-m"],
    "172.31.81.35": ["akld2e18u35-m", "e18u35-m"],
    "172.31.81.36": ["akld2e18u36-m", "e18u36-m"],
    "172.31.81.37": ["akld2e18u37-m", "e18u37-m"],
    "172.31.81.38": ["akld2e18u38-m", "e18u38-m"],
    "172.31.81.39": ["akld2e18u39-m", "e18u39-m"],
    "172.31.81.40": ["akld2e18u40-m", "e18u40-m"],
    "172.31.81.41": ["akld2e18u41-m", "e18u41-m"],
    "172.31.81.42": ["akld2e18u42-m", "e18u42-m"],
    #Management D18 Rack
    "172.31.81.101": ["akld2d18u01-m", "d18u01-m"],
    "172.31.81.102": ["akld2d18u02-m", "d18u02-m"],
    "172.31.81.103": ["akld2d18u03-m", "d18u03-m"],
    "172.31.81.104": ["akld2d18u04-m", "d18u04-m"],
    "172.31.81.105": ["akld2d18u05-m", "d18u05-m"],
    "172.31.81.106": ["akld2d18u06-m", "d18u06-m"],
    "172.31.81.107": ["akld2d18u07-m", "d18u07-m"],
    "172.31.81.108": ["akld2d18u08-m", "d18u08-m"],
    "172.31.81.109": ["akld2d18u09-m", "d18u09-m"],
    "172.31.81.110": ["akld2d18u10-m", "d18u10-m"],
    "172.31.81.111": ["akld2d18u11-m", "d18u11-m"],
    "172.31.81.112": ["akld2d18u12-m", "d18u12-m"],
    "172.31.81.113": ["akld2d18u13-m", "d18u13-m"],
    "172.31.81.114": ["akld2d18u14-m", "d18u14-m"],
    "172.31.81.115": ["akld2d18u15-m", "d18u15-m"],
    "172.31.81.116": ["akld2d18u16-m", "d18u16-m"],
    "172.31.81.117": ["akld2d18u17-m", "d18u17-m"],
    "172.31.81.118": ["akld2d18u18-m", "d18u18-m"],
    "172.31.81.119": ["akld2d18u19-m", "d18u19-m"],
    "172.31.81.120": ["akld2d18u20-m", "d18u20-m"],
    "172.31.81.121": ["akld2d18u21-m", "d18u21-m"],
    "172.31.81.122": ["akld2d18u22-m", "d18u22-m"],
    "172.31.81.123": ["akld2d18u23-m", "d18u23-m"],
    "172.31.81.124": ["akld2d18u24-m", "d18u24-m"],
    "172.31.81.125": ["akld2d18u25-m", "d18u25-m"],
    "172.31.81.126": ["akld2d18u26-m", "d18u26-m"],
    "172.31.81.127": ["akld2d18u27-m", "d18u27-m"],
    "172.31.81.128": ["akld2d18u28-m", "d18u28-m"],
    "172.31.81.129": ["akld2d18u29-m", "d18u29-m"],
    "172.31.81.130": ["akld2d18u30-m", "d18u30-m"],
    "172.31.81.131": ["akld2d18u31-m", "d18u31-m"],
    "172.31.81.132": ["akld2d18u32-m", "d18u32-m"],
    "172.31.81.133": ["akld2d18u33-m", "d18u33-m"],
    "172.31.81.134": ["akld2d18u34-m", "d18u34-m"],
    "172.31.81.135": ["akld2d18u35-m", "d18u35-m"],
    "172.31.81.136": ["akld2d18u36-m", "d18u36-m"],
    "172.31.81.137": ["akld2d18u37-m", "d18u37-m"],
    "172.31.81.138": ["akld2d18u38-m", "d18u38-m"],
    "172.31.81.139": ["akld2d18u39-m", "d18u39-m"],
    "172.31.81.140": ["akld2d18u40-m", "d18u40-m"],
    "172.31.81.141": ["akld2d18u41-m", "d18u41-m"],
    "172.31.81.142": ["akld2d18u42-m", "d18u42-m"],
}

h18_g18_hosts = {
    "10.31.80.31": ["akld2g18a17-p","g18a17-p", "ntr-adm01-p","adm01-p", "adm01"],
    "10.31.80.32": ["akld2h18a17-p","h18a17-p", "ntr-adm02-p","adm02-p", "adm02"],
    "10.31.80.41": ["akld2g18a18-p","g18a18-p", "ntr-ctr01-p","ctr01-p", "ctr01"],
    "10.31.80.42": ["akld2h18a18-p","h18a18-p", "ntr-ctr02-p","ctr02-p", "ctr02"],
    "10.31.80.43": ["akld2g18a19-p","g18a19-p", "ntr-ctr03-p","ctr03-p", "ctr03"],
    #
    "10.31.80.64": ["akld2g18s01-p","g18s01-p", "ntr-sto01-p","sto01-p", "sto01"],
    "10.31.80.65": ["akld2g18s03-p","g18s03-p", "ntr-sto02-p","sto02-p", "sto02"],
    "10.31.80.66": ["akld2g18s05-p","g18s05-p", "ntr-sto03-p","sto03-p", "sto03"],
    "10.31.80.67": ["akld2g18s07-p","g18s07-p", "ntr-sto04-p","sto04-p", "sto04"],
    "10.31.80.68": ["akld2h18s01-p","h18s01-p", "ntr-sto05-p","sto05-p", "sto05"],
    "10.31.80.69": ["akld2h18s03-p","h18s03-p", "ntr-sto06-p","sto06-p", "sto06"],
    "10.31.80.70": ["akld2h18s05-p","h18s05-p", "ntr-sto07-p","sto07-p", "sto07"],
    "10.31.80.71": ["akld2h18s07-p","h18s07-p", "ntr-sto08-p","sto08-p", "sto08"],
    "10.31.80.72": ["akld2g18s09-p","g18s09-p", "ntr-sto09-p","sto09-p", "sto09"],
    "10.31.80.73": ["akld2h18s09-p","h18s09-p", "ntr-sto10-p","sto10-p", "sto10"],
    "10.31.80.74": ["akld2g18s11-p","g18s11-p", "ntr-sto11-p","sto11-p", "sto11"],
    "10.31.80.75": ["akld2h18s11-p","h18s11-p", "ntr-sto12-p","sto12-p", "sto12"],
    "10.31.80.76": ["akld2g18s13-p","g18s13-p", "ntr-sto13-p","sto13-p", "sto13"],
    "10.31.80.77": ["akld2h18s13-p","h18s13-p", "ntr-sto14-p","sto14-p", "sto14"],
    #
    "10.31.88.64": ["akld2g18s01-ceph","g18s01-ceph", "ntr-sto01-ceph","sto01-ceph"],
    "10.31.88.65": ["akld2g18s03-ceph","g18s03-ceph", "ntr-sto02-ceph","sto02-ceph"],
    "10.31.88.66": ["akld2g18s05-ceph","g18s05-ceph", "ntr-sto03-ceph","sto03-ceph"],
    "10.31.88.67": ["akld2g18s07-ceph","g18s07-ceph", "ntr-sto04-ceph","sto04-ceph"],
    "10.31.88.68": ["akld2h18s01-ceph","h18s01-ceph", "ntr-sto05-ceph","sto05-ceph"],
    "10.31.88.69": ["akld2h18s03-ceph","h18s03-ceph", "ntr-sto06-ceph","sto06-ceph"],
    "10.31.88.70": ["akld2h18s05-ceph","h18s05-ceph", "ntr-sto07-ceph","sto07-ceph"],
    "10.31.88.71": ["akld2h18s07-ceph","h18s07-ceph", "ntr-sto08-ceph","sto08-ceph"],
    "10.31.88.72": ["akld2g18s09-ceph","g18s09-ceph", "ntr-sto09-ceph","sto09-ceph"],
    "10.31.88.73": ["akld2h18s09-ceph","h18s09-ceph", "ntr-sto10-ceph","sto10-ceph"],
    "10.31.88.74": ["akld2g18s11-ceph","g18s11-ceph", "ntr-sto11-ceph","sto11-ceph"],
    "10.31.88.75": ["akld2h18s11-ceph","h18s11-ceph", "ntr-sto12-ceph","sto12-ceph"],
    "10.31.88.76": ["akld2g18s13-ceph","g18s13-ceph", "ntr-sto13-ceph","sto13-ceph"],
    "10.31.88.77": ["akld2h18s13-ceph","h18s13-ceph", "ntr-sto14-ceph","sto14-ceph"],
    #
    "10.31.92.64": ["akld2g18s01-repl","g18s01-repl", "ntr-sto01-repl","sto01-repl"],
    "10.31.92.65": ["akld2g18s03-repl","g18s03-repl", "ntr-sto02-repl","sto02-repl"],
    "10.31.92.66": ["akld2g18s05-repl","g18s05-repl", "ntr-sto03-repl","sto03-repl"],
    "10.31.92.67": ["akld2g18s07-repl","g18s07-repl", "ntr-sto04-repl","sto04-repl"],
    "10.31.92.68": ["akld2h18s01-repl","h18s01-repl", "ntr-sto05-repl","sto05-repl"],
    "10.31.92.69": ["akld2h18s03-repl","h18s03-repl", "ntr-sto06-repl","sto06-repl"],
    "10.31.92.70": ["akld2h18s05-repl","h18s05-repl", "ntr-sto07-repl","sto07-repl"],
    "10.31.92.71": ["akld2h18s07-repl","h18s07-repl", "ntr-sto08-repl","sto08-repl"],
    "10.31.92.72": ["akld2g18s09-repl","g18s09-repl", "ntr-sto09-repl","sto09-repl"],
    "10.31.92.73": ["akld2h18s09-repl","h18s09-repl", "ntr-sto10-repl","sto10-repl"],
    "10.31.92.74": ["akld2g18s11-repl","g18s11-repl", "ntr-sto11-repl","sto11-repl"],
    "10.31.92.75": ["akld2h18s11-repl","h18s11-repl", "ntr-sto12-repl","sto12-repl"],
    "10.31.92.76": ["akld2g18s13-repl","g18s13-repl", "ntr-sto13-repl","sto13-repl"],
    "10.31.92.77": ["akld2h18s13-repl","h18s13-repl", "ntr-sto14-repl","sto14-repl"],
    #
    "10.31.80.128": ["akld2g18u24-p","g18u24-p", "ntr-cop01-p","cop01-p"],
    "10.31.80.129": ["akld2g18u25-p","g18u25-p", "ntr-cop02-p","cop02-p"],
    "10.31.80.130": ["akld2g18u26-p","g18u26-p", "ntr-cop03-p","cop03-p"],
    "10.31.80.131": ["akld2h18u23-p","h18u23-p", "ntr-cop04-p","cop04-p"],
    "10.31.80.132": ["akld2h18u24-p","h18u24-p", "ntr-cop05-p","cop05-p"],
    "10.31.80.133": ["akld2h18u25-p","h18u25-p", "ntr-cop06-p","cop06-p"],
    "10.31.80.134": ["akld2h18u26-p","h18u26-p", "ntr-cop07-p","cop07-p"],
    "10.31.80.135": ["akld2g18u44-p","g18u44-p", "ntr-cop08-p","cop08-p"],
    "10.31.80.136": ["akld2g18u27-p","g18u27-p", "ntr-cop09-p","cop09-p"],
    "10.31.80.137": ["akld2h18u27-p","h18u27-p", "ntr-cop10-p","cop10-p"],
    "10.31.80.138": ["akld2g18u28-p","g18u28-p", "ntr-cop11-p","cop11-p"],
    #
    "10.31.84.128": ["akld2g18u24-api","g18u24-api", "ntr-cop01-api","cop01-api", "akld2g18u24", "cop01"],
    "10.31.84.129": ["akld2g18u25-api","g18u25-api", "ntr-cop02-api","cop02-api", "akld2g18u25", "cop02"],
    "10.31.84.130": ["akld2g18u26-api","g18u26-api", "ntr-cop03-api","cop03-api", "akld2g18u26", "cop03"],
    "10.31.84.131": ["akld2h18u23-api","h18u23-api", "ntr-cop04-api","cop04-api", "akld2h18u23", "cop04"],
    "10.31.84.132": ["akld2h18u24-api","h18u24-api", "ntr-cop05-api","cop05-api", "akld2h18u24", "cop05"],
    "10.31.84.133": ["akld2h18u25-api","h18u25-api", "ntr-cop06-api","cop06-api", "akld2h18u25", "cop06"],
    "10.31.84.134": ["akld2h18u26-api","h18u26-api", "ntr-cop07-api","cop07-api", "akld2h18u26", "cop07"],
    "10.31.84.135": ["akld2g18u44-api","g18u44-api", "ntr-cop08-api","cop08-api", "akld2g18u44", "cop08"],
    "10.31.84.136": ["akld2g18u27-api","g18u27-api", "ntr-cop09-api","cop09-api", "akld2g18u27", "cop09"],
    "10.31.84.137": ["akld2h18u27-api","h18u27-api", "ntr-cop10-api","cop10-api", "akld2h18u27", "cop10"],
    "10.31.84.138": ["akld2g18u28-api","g18u28-api", "ntr-cop11-api","cop11-api", "akld2g18u28", "cop11"],
    #
    "10.31.88.128": ["akld2g18u24-ceph","g18u24-ceph", "ntr-cop01-ceph","cop01-ceph"],
    "10.31.88.129": ["akld2g18u25-ceph","g18u25-ceph", "ntr-cop02-ceph","cop02-ceph"],
    "10.31.88.130": ["akld2g18u26-ceph","g18u26-ceph", "ntr-cop03-ceph","cop03-ceph"],
    "10.31.88.131": ["akld2h18u23-ceph","h18u23-ceph", "ntr-cop04-ceph","cop04-ceph"],
    "10.31.88.132": ["akld2h18u24-ceph","h18u24-ceph", "ntr-cop05-ceph","cop05-ceph"],
    "10.31.88.133": ["akld2h18u25-ceph","h18u25-ceph", "ntr-cop06-ceph","cop06-ceph"],
    "10.31.88.134": ["akld2h18u26-ceph","h18u26-ceph", "ntr-cop07-ceph","cop07-ceph"],
    "10.31.88.135": ["akld2g18u44-ceph","g18u44-ceph", "ntr-cop08-ceph","cop08-ceph"],
    "10.31.88.136": ["akld2g18u27-ceph","g18u27-ceph", "ntr-cop09-ceph","cop09-ceph"],
    "10.31.88.137": ["akld2h18u27-ceph","h18u27-ceph", "ntr-cop10-ceph","cop10-ceph"],
    "10.31.88.138": ["akld2g18u28-ceph","g18u28-ceph", "ntr-cop11-ceph","cop11-ceph"],
    #
    #VMs
    #"130.216.95.93": ["ntr-ops01", "ntr-ops"],
    "10.31.80.2":   ["ntr-ops-p", "ops-p"],
    "172.31.80.251":   ["ntr-ops-m", "ops-m"],
    #
    #"130.216.95.89": ["ntr-proxy-vip", "ntr-proxy"],
    #
    #"130.216.95.84": ["ntr-proxy01"],
    "10.31.80.3":   ["ntr-proxy01-p", "proxy01-p"],
    "10.31.84.3":   ["ntr-proxy01-api", "proxy01-api"],
    "10.31.88.3":   ["ntr-proxy01-ceph", "proxy01-ceph"],
    "10.31.96.3":   ["ntr-proxy01-cephfs", "proxy01-cephfs"],
    "10.31.61.3":   ["ntr-proxy01-rados", "proxy01-rados"],
    #
    #"130.216.95.92": ["ntr-proxy02"],
    "10.31.80.4":   ["ntr-proxy02-p", "proxy02-p"],
    "10.31.84.4":   ["ntr-proxy02-api", "proxy02-api"],
    "10.31.88.4":   ["ntr-proxy02-ceph", "proxy02-ceph"],
    "10.31.96.4":   ["ntr-proxy02-cephfs", "proxy02-cephfs"],
    "10.31.61.4":   ["ntr-proxy02-rados", "proxy02-rados"],
    #
    "10.31.80.5":	  ["ntr-pxe", "ntr-pxe-p", "pxe-p", "pxe"],
    "10.31.84.5":	  ["ntr-pxe-api", "pxe-api"],
    "10.31.88.5":	  ["ntr-pxe-ceph", "pxe-ceph"],
    #
    "10.31.80.7": ["ntr-ganglia", "ntr-ganglia-p",  "ganglia-p", "ganglia"],
    "10.31.84.7": ["ntr-ganglia-api", "ganglia-api"],
    #
    "10.31.80.8": ["ntr-nagios", "ntr-nagios-p", "nagios-p", "nagios"],
    "10.31.84.8": ["ntr-nagios-api", "nagios-api"],
    #
    "10.31.80.9": ["ntr-log01", "ntr-log01-p", "log01-p", "log01"],
    "10.31.84.9": ["ntr-log01-api", "log01-api"],
    "172.31.80.250": ["ntr-log01-m", "log01-m"],
    #
    "10.31.80.11": ["ntr-rgw01", "ntr-rgw01-p", "rgw01-p", "rgw01"],
    "10.31.88.11": ["ntr-rgw01-ceph", "rgw01-ceph"],
    "10.31.61.11": ["ntr-rgw01-rados", "rgw01-rados"],
    #
    "10.31.80.12": ["ntr-rgw02", "ntr-rgw02-p", "rgw02-p", "rgw02"],
    "10.31.88.12": ["ntr-rgw02-ceph", "rgw02-ceph"],
    "10.31.61.12": ["ntr-rgw02-rados", "rgw02-rados"],
    #MAAS
    "10.31.80.99":   ["ntr-maas", "ntr-maas-p", "maas-p", "maas"],
    "172.31.80.99":   ["ntr-maas-m", "maas-m"],
    #Ceph
    "10.31.80.13": ["ntr-cad01", "ntr-cad01-p", "cad01-p","cad01"],
    "10.31.88.13": ["ntr-cad01-ceph", "cad01-ceph"],
    "10.31.96.13": ["ntr-cad01-cephfs", "cad01-cephfs"],
    #Ceph Monitors
    "10.31.80.14": ["ntr-mon01", "ntr-mon01-p", "ntr-mon01-p", "mon01"],
    "10.31.88.14": ["mon-01-ceph"],
    "10.31.96.14": ["ntr-mon01-cephfs"],
    #
    "10.31.80.15": ["ntr-mon02", "ntr-mon02-p", "ntr-mon02-p", "mon02"],
    "10.31.88.15": ["mon-02-ceph"],
    "10.31.96.15": ["ntr-mon02-cephfs"],
    #
    "10.31.80.16": ["ntr-mon03", "ntr-mon03-p", "ntr-mon03-p", "mon03"],
    "10.31.88.16": ["mon-03-ceph"],
    "10.31.96.16": ["ntr-mon03-cephfs"],
    #
    "10.31.80.17": ["ntr-mon04", "ntr-mon04-p", "ntr-mon04-p", "mon04"],
    "10.31.88.17": ["mon-04-ceph"],
    "10.31.96.17": ["ntr-mon04-cephfs"],
    #
    "10.31.80.18": ["ntr-mon05", "ntr-mon05-p", "mon05-p", "mon05"],
    "10.31.88.18": ["ntr-mon05-ceph"],
    "10.31.96.18": ["ntr-mon05-cephfs"],
    #
    #"130.216.95.86":	["ntr-neutron01", "neutron01"],
    #"130.216.216.1":	["ntr-neutron01-ext", "neutron01-ext"],
    #"130.216.189.1":	["ntr-neutron01-int", "neutron01-int"],
    "10.31.80.21":	["ntr-neutron01-p", "neutron01-p"],
    "10.31.84.21":	["ntr-neutron01-api", "neutron01-api"],
    #"10.31.32.1":	["ntr-neutron01-mido1", "neutron01-mido1"],
    #"10.241.128.2":	["ntr-neutron01-mido", "neutron01-mido],
    #
    #"130.216.95.87":	["ntr-neutron02", "neutron02"],
    #"130.216.216.1":	["ntr-neutron02-ext", "neutron02-ext"],
    #"130.216.189.1":	["ntr-neutron02-int", "neutron02-int"],
    "10.31.80.22":	["ntr-neutron02-p", "neutron02-p"],
    "10.31.84.22":	["ntr-neutron02-api", "neutron02-api"],
    #"10.31.33.1":	["ntr-neutron02-mido2", "neutron02-mido2"],
    #"10.241.128.4":	["ntr-neutron02-mido", "neutron02-mido],
    #
    "10.31.80.25":	["ntr-nfs01", "ntr-nfs01-p", "nfs01"],
    "10.31.88.25":	["ntr-nfs01-ceph", "nfs01-ceph"],
    "10.31.96.25":	["ntr-nfs01-cephfs", "nfs01-cephfs"],
    #
    "10.31.80.26":	["ntr-nfs02", "ntr-nfs02-p", "nfs02"],
    "10.31.88.26":	["ntr-nfs02-ceph", "nfs02-ceph"],
    "10.31.96.26":	["ntr-nfs02-cephfs", "nfs02-cephfs"],
    #
    #"130.216.95.88":	["ntr-novaq01", "novaq01"],
    "10.31.80.36":	["ntr-nova01-p", "nova01-p"],
    "10.31.84.36":	["ntr-nova01-api", "nova01-api"],
    #
    #"130.216.95.91":	["ntr-novaq02", "novaq02"],
    "10.31.80.37":	["ntr-nova02-p", "nova02-p"],
    "10.31.84.37":	["ntr-nova02-api", "nova02-api"],
    #
    "10.31.80.38":	["ntr-cinder01", "ntr-cinder01-p", "cinder01-p"],
    "10.31.84.38":	["ntr-cinder01-api", "cinder01-api"],
    "10.31.88.38":	["ntr-cinder01-ceph", "cinder01-ceph"],
    #
    #
    "10.31.80.46":	["ntr-db01", "ntr-db01-p", "db01-p"],
    "10.31.84.46":	["ntr-db01-api", "db01-api"],
    #
    "10.31.80.47":	["ntr-db02", "ntr-db02-p", "db02-p"],
    "10.31.84.47":	["ntr-db02-api", "db02-api"],
    #
    "10.31.80.48":	["ntr-db03", "ntr-db03-p", "db03-p"],
    "10.31.84.48":	["ntr-db03-api", "db03-api"],
    #
    #"130.216.95.81":	["ntr-mq01", "mq01"],
    "10.31.80.51":	["ntr-mq01-p", "mq01-p"],
    "10.31.84.51":	["ntr-mq01-api", "mq01-api"],
    #
    #"130.216.95.82":	["ntr-mq02", "mq02"],
    "10.31.80.52":	["ntr-mq02-p", "mq02-p"],
    "10.31.84.52":	["ntr-mq02-api", "mq02-api"],
    #
    #"130.216.95.83":	["ntr-mq03", "mq03"],
    "10.31.80.53":	["ntr-mq03-p", "mq03-p"],
    "10.31.84.53":	["ntr-mq03-api", "mq03-api"],
    #
    "10.31.80.56":	["ntr-glance-01", "ntr-glance-01-p", "glance-01"],
    "10.31.84.56":	["ntr-glance-01-api", "glance-01-api"],
    #
    "10.31.80.57":	["ntr-glance-02", "ntr-glance-02-p", "glance-02"],
    "10.31.84.57":	["ntr-glance-02-api", "glance-02-api"],
    #
    #"130.216.95.90": ["ntr-gw02"],
    "10.31.83.253":	["ntr-gw02-p", "gw02-p"],
    "10.31.87.253":	["ntr-gw02-api",  "gw02-api"],
}

didnttake = {
    "10.31.84.38":	["ntr-cinder01-api", "cinder01-api"],
    "10.31.88.38":	["ntr-cinder01-ceph", "cinder01-ceph"],
}

e18_d18_hosts = {
    "10.31.81.1": ["akld2e18u01-p","e18u01-p"],
    "10.31.81.2": ["akld2e18u02-p","e18u02-p"],
    "10.31.81.3": ["akld2e18u03-p","e18u03-p"],
    "10.31.81.4": ["akld2e18u04-p","e18u04-p"],
    "10.31.81.5": ["akld2e18u05-p","e18u05-p"],
    "10.31.81.6": ["akld2e18u06-p","e18u06-p"],
    "10.31.81.7": ["akld2e18u07-p","e18u07-p"],
    "10.31.81.8": ["akld2e18u08-p","e18u08-p"],
    "10.31.81.9": ["akld2e18u09-p","e18u09-p"],
    "10.31.81.10": ["akld2e18u10-p","e18u10-p"],
    "10.31.81.11": ["akld2e18u11-p","e18u11-p"],
    "10.31.81.12": ["akld2e18u12-p","e18u12-p"],
    "10.31.81.13": ["akld2e18u13-p","e18u13-p"],
    "10.31.81.14": ["akld2e18u14-p","e18u14-p"],
    "10.31.81.15": ["akld2e18u15-p","e18u15-p"],
    "10.31.81.16": ["akld2e18u16-p","e18u16-p"],
    "10.31.81.17": ["akld2e18u17-p","e18u17-p"],
    "10.31.81.18": ["akld2e18u18-p","e18u18-p"],
    "10.31.81.19": ["akld2e18u19-p","e18u19-p"],
    "10.31.81.20": ["akld2e18u20-p","e18u20-p"],
    #"10.31.81.21": ["akld2e18u21-p","e18u21-p"],
    #"10.31.81.22": ["akld2e18u22-p","e18u22-p"],
    "10.31.81.23": ["akld2e18u23-p","e18u23-p"],
    "10.31.81.24": ["akld2e18u24-p","e18u24-p"],
    "10.31.81.25": ["akld2e18u25-p","e18u25-p"],
    "10.31.81.26": ["akld2e18u26-p","e18u26-p"],
    "10.31.81.27": ["akld2e18u27-p","e18u27-p"],
    "10.31.81.28": ["akld2e18u28-p","e18u28-p"],
    "10.31.81.29": ["akld2e18u29-p","e18u29-p"],
    "10.31.81.30": ["akld2e18u30-p","e18u30-p"],
    "10.31.81.31": ["akld2e18u31-p","e18u31-p"],
    "10.31.81.32": ["akld2e18u32-p","e18u32-p"],
    "10.31.81.33": ["akld2e18u33-p","e18u33-p"],
    "10.31.81.34": ["akld2e18u34-p","e18u34-p"],
    "10.31.81.35": ["akld2e18u35-p","e18u35-p"],
    "10.31.81.36": ["akld2e18u36-p","e18u36-p"],
    "10.31.81.37": ["akld2e18u37-p","e18u37-p"],
    "10.31.81.38": ["akld2e18u38-p","e18u38-p"],
    "10.31.81.39": ["akld2e18u39-p","e18u39-p"],
    "10.31.81.40": ["akld2e18u40-p","e18u40-p"],
    "10.31.81.41": ["akld2e18u41-p","e18u41-p"],
    "10.31.81.42": ["akld2e18u42-p","e18u42-p"],

    #"10.31.81.101": ["akld2d18u01-p",  "d18u01-p"],
    "10.31.81.102": ["akld2d18u02-p",  "d18u02-p"],
    "10.31.81.103": ["akld2d18u03-p",  "d18u03-p"],
    "10.31.81.104": ["akld2d18u04-p",  "d18u04-p"],
    "10.31.81.105": ["akld2d18u05-p",  "d18u05-p"],
    "10.31.81.106": ["akld2d18u06-p",  "d18u06-p"],
    "10.31.81.107": ["akld2d18u07-p",  "d18u07-p"],
    "10.31.81.108": ["akld2d18u08-p",  "d18u08-p"],
    "10.31.81.109": ["akld2d18u09-p",  "d18u09-p"],
    "10.31.81.110": ["akld2d18u10-p",  "d18u10-p"],
    "10.31.81.111": ["akld2d18u11-p",  "d18u11-p"],
    "10.31.81.112": ["akld2d18u12-p",  "d18u12-p"],
    "10.31.81.113": ["akld2d18u13-p",  "d18u13-p"],
    "10.31.81.114": ["akld2d18u14-p",  "d18u14-p"],
    "10.31.81.115": ["akld2d18u15-p",  "d18u15-p"],
    "10.31.81.116": ["akld2d18u16-p",  "d18u16-p"],
    #"10.31.81.117": ["akld2d18u17-p",  "d18u17-p"],
    "10.31.81.118": ["akld2d18u18-p",  "d18u18-p"],
    #"10.31.81.119": ["akld2d18u19-p",  "d18u19-p"],
    #"10.31.81.120": ["akld2d18u20-p",  "d18u20-p"],
    #"10.31.81.121": ["akld2d18u21-p",  "d18u21-p"],
    "10.31.81.122": ["akld2d18u22-p",  "d18u22-p"],
    #"10.31.81.123": ["akld2d18u23-p",  "d18u23-p"],
    "10.31.81.124": ["akld2d18u24-p",  "d18u24-p"],
    #"10.31.81.125": ["akld2d18u25-p",  "d18u25-p"],
    "10.31.81.126": ["akld2d18u26-p",  "d18u26-p"],
    #"10.31.81.127": ["akld2d18u27-p",  "d18u27-p"],
    "10.31.81.128": ["akld2d18u28-p",  "d18u28-p"],
    #"10.31.81.129": ["akld2d18u29-p",  "d18u29-p"],
    "10.31.81.130": ["akld2d18u30-p",  "d18u30-p"],
    #"10.31.81.131": ["akld2d18u31-p",  "d18u31-p"],
    "10.31.81.132": ["akld2d18u32-p",  "d18u32-p"],
    #"10.31.81.133": ["akld2d18u33-p",  "d18u33-p"],
    "10.31.81.134": ["akld2d18u34-p",  "d18u34-p"],
    #"10.31.81.135": ["akld2d18u35-p",  "d18u35-p"],
    "10.31.81.136": ["akld2d18u36-p",  "d18u36-p"],
    #"10.31.81.137": ["akld2d18u37-p",  "d18u37-p"],
    "10.31.81.138": ["akld2d18u38-p",  "d18u38-p"],
    #"10.31.81.139": ["akld2d18u39-p",  "d18u39-p"],
    "10.31.81.140": ["akld2d18u40-p",  "d18u40-p"],
    #"10.31.81.141": ["akld2d18u41-p",  "d18u41-p"],
    #"10.31.81.142": ["akld2d18u42-p",  "d18u42-p"],

    "10.31.85.1": ["akld2e18u01-api","e18u01-api"],
    "10.31.85.2": ["akld2e18u02-api","e18u02-api"],
    "10.31.85.3": ["akld2e18u03-api","e18u03-api"],
    "10.31.85.4": ["akld2e18u04-api","e18u04-api"],
    "10.31.85.5": ["akld2e18u05-api","e18u05-api"],
    "10.31.85.6": ["akld2e18u06-api","e18u06-api"],
    "10.31.85.7": ["akld2e18u07-api","e18u07-api"],
    "10.31.85.8": ["akld2e18u08-api","e18u08-api"],
    "10.31.85.9": ["akld2e18u09-api","e18u09-api"],
    "10.31.85.10": ["akld2e18u10-api","e18u10-api"],
    "10.31.85.11": ["akld2e18u11-api","e18u11-api"],
    "10.31.85.12": ["akld2e18u12-api","e18u12-api"],
    "10.31.85.13": ["akld2e18u13-api","e18u13-api"],
    "10.31.85.14": ["akld2e18u14-api","e18u14-api"],
    "10.31.85.15": ["akld2e18u15-api","e18u15-api"],
    "10.31.85.16": ["akld2e18u16-api","e18u16-api"],
    "10.31.85.17": ["akld2e18u17-api","e18u17-api"],
    "10.31.85.18": ["akld2e18u18-api","e18u18-api"],
    "10.31.85.19": ["akld2e18u19-api","e18u19-api"],
    "10.31.85.20": ["akld2e18u20-api","e18u20-api"],
    #"10.31.85.21": ["akld2e18u21-api","e18u21-api"],
    #"10.31.85.22": ["akld2e18u22-api","e18u22-api"],
    "10.31.85.23": ["akld2e18u23-api","e18u23-api"],
    "10.31.85.24": ["akld2e18u24-api","e18u24-api"],
    "10.31.85.25": ["akld2e18u25-api","e18u25-api"],
    "10.31.85.26": ["akld2e18u26-api","e18u26-api"],
    "10.31.85.27": ["akld2e18u27-api","e18u27-api"],
    "10.31.85.28": ["akld2e18u28-api","e18u28-api"],
    "10.31.85.29": ["akld2e18u29-api","e18u29-api"],
    "10.31.85.30": ["akld2e18u30-api","e18u30-api"],
    "10.31.85.31": ["akld2e18u31-api","e18u31-api"],
    "10.31.85.32": ["akld2e18u32-api","e18u32-api"],
    "10.31.85.33": ["akld2e18u33-api","e18u33-api"],
    "10.31.85.34": ["akld2e18u34-api","e18u34-api"],
    "10.31.85.35": ["akld2e18u35-api","e18u35-api"],
    "10.31.85.36": ["akld2e18u36-api","e18u36-api"],
    "10.31.85.37": ["akld2e18u37-api","e18u37-api"],
    "10.31.85.38": ["akld2e18u38-api","e18u38-api"],
    "10.31.85.39": ["akld2e18u39-api","e18u39-api"],
    "10.31.85.40": ["akld2e18u40-api","e18u40-api"],
    "10.31.85.41": ["akld2e18u41-api","e18u41-api"],
    "10.31.85.42": ["akld2e18u42-api","e18u42-api"],

    #"10.31.85.101": ["akld2d18u01-api",  "d18u01-api"],
    "10.31.85.102": ["akld2d18u02-api",  "d18u02-api"],
    "10.31.85.103": ["akld2d18u03-api",  "d18u03-api"],
    "10.31.85.104": ["akld2d18u04-api",  "d18u04-api"],
    "10.31.85.105": ["akld2d18u05-api",  "d18u05-api"],
    "10.31.85.106": ["akld2d18u06-api",  "d18u06-api"],
    "10.31.85.107": ["akld2d18u07-api",  "d18u07-api"],
    "10.31.85.108": ["akld2d18u08-api",  "d18u08-api"],
    "10.31.85.109": ["akld2d18u09-api",  "d18u09-api"],
    "10.31.85.110": ["akld2d18u10-api",  "d18u10-api"],
    "10.31.85.111": ["akld2d18u11-api",  "d18u11-api"],
    "10.31.85.112": ["akld2d18u12-api",  "d18u12-api"],
    "10.31.85.113": ["akld2d18u13-api",  "d18u13-api"],
    "10.31.85.114": ["akld2d18u14-api",  "d18u14-api"],
    "10.31.85.115": ["akld2d18u15-api",  "d18u15-api"],
    "10.31.85.116": ["akld2d18u16-api",  "d18u16-api"],
    #"10.31.85.117": ["akld2d18u17-api",  "d18u17-api"],
    "10.31.85.118": ["akld2d18u18-api",  "d18u18-api"],
    #"10.31.85.119": ["akld2d18u19-api",  "d18u19-api"],
    #"10.31.85.120": ["akld2d18u20-api",  "d18u20-api"],
    #"10.31.85.121": ["akld2d18u21-api",  "d18u21-api"],
    "10.31.85.122": ["akld2d18u22-api",  "d18u22-api"],
    #"10.31.85.123": ["akld2d18u23-api",  "d18u23-api"],
    "10.31.85.124": ["akld2d18u24-api",  "d18u24-api"],
    #"10.31.85.125": ["akld2d18u25-api",  "d18u25-api"],
    "10.31.85.126": ["akld2d18u26-api",  "d18u26-api"],
    #"10.31.85.127": ["akld2d18u27-api",  "d18u27-api"],
    "10.31.85.128": ["akld2d18u28-api",  "d18u28-api"],
    #"10.31.85.129": ["akld2d18u29-api",  "d18u29-api"],
    "10.31.85.130": ["akld2d18u30-api",  "d18u30-api"],
    #"10.31.85.131": ["akld2d18u31-api",  "d18u31-api"],
    "10.31.85.132": ["akld2d18u32-api",  "d18u32-api"],
    #"10.31.85.133": ["akld2d18u33-api",  "d18u33-api"],
    "10.31.85.134": ["akld2d18u34-api",  "d18u34-api"],
    #"10.31.85.135": ["akld2d18u35-api",  "d18u35-api"],
    "10.31.85.136": ["akld2d18u36-api",  "d18u36-api"],
    #"10.31.85.137": ["akld2d18u37-api",  "d18u37-api"],
    "10.31.85.138": ["akld2d18u38-api",  "d18u38-api"],
    #"10.31.85.139": ["akld2d18u39-api",  "d18u39-api"],
    "10.31.85.140": ["akld2d18u40-api",  "d18u40-api"],
    #"10.31.85.141": ["akld2d18u41-api",  "d18u41-api"],
    #"10.31.85.142": ["akld2d18u42-api",  "d18u42-api"],

    "10.31.89.1": ["akld2e18u01-ceph","e18u01-ceph"],
    "10.31.89.2": ["akld2e18u02-ceph","e18u02-ceph"],
    "10.31.89.3": ["akld2e18u03-ceph","e18u03-ceph"],
    "10.31.89.4": ["akld2e18u04-ceph","e18u04-ceph"],
    "10.31.89.5": ["akld2e18u05-ceph","e18u05-ceph"],
    "10.31.89.6": ["akld2e18u06-ceph","e18u06-ceph"],
    "10.31.89.7": ["akld2e18u07-ceph","e18u07-ceph"],
    "10.31.89.8": ["akld2e18u08-ceph","e18u08-ceph"],
    "10.31.89.9": ["akld2e18u09-ceph","e18u09-ceph"],
    "10.31.89.10": ["akld2e18u10-ceph","e18u10-ceph"],
    "10.31.89.11": ["akld2e18u11-ceph","e18u11-ceph"],
    "10.31.89.12": ["akld2e18u12-ceph","e18u12-ceph"],
    "10.31.89.13": ["akld2e18u13-ceph","e18u13-ceph"],
    "10.31.89.14": ["akld2e18u14-ceph","e18u14-ceph"],
    "10.31.89.15": ["akld2e18u15-ceph","e18u15-ceph"],
    "10.31.89.16": ["akld2e18u16-ceph","e18u16-ceph"],
    "10.31.89.17": ["akld2e18u17-ceph","e18u17-ceph"],
    "10.31.89.18": ["akld2e18u18-ceph","e18u18-ceph"],
    "10.31.89.19": ["akld2e18u19-ceph","e18u19-ceph"],
    "10.31.89.20": ["akld2e18u20-ceph","e18u20-ceph"],
    #"10.31.89.21": ["akld2e18u21-ceph","e18u21-ceph"],
    #"10.31.89.22": ["akld2e18u22-ceph","e18u22-ceph"],
    "10.31.89.23": ["akld2e18u23-ceph","e18u23-ceph"],
    "10.31.89.24": ["akld2e18u24-ceph","e18u24-ceph"],
    "10.31.89.25": ["akld2e18u25-ceph","e18u25-ceph"],
    "10.31.89.26": ["akld2e18u26-ceph","e18u26-ceph"],
    "10.31.89.27": ["akld2e18u27-ceph","e18u27-ceph"],
    "10.31.89.28": ["akld2e18u28-ceph","e18u28-ceph"],
    "10.31.89.29": ["akld2e18u29-ceph","e18u29-ceph"],
    "10.31.89.30": ["akld2e18u30-ceph","e18u30-ceph"],
    "10.31.89.31": ["akld2e18u31-ceph","e18u31-ceph"],
    "10.31.89.32": ["akld2e18u32-ceph","e18u32-ceph"],
    "10.31.89.33": ["akld2e18u33-ceph","e18u33-ceph"],
    "10.31.89.34": ["akld2e18u34-ceph","e18u34-ceph"],
    "10.31.89.35": ["akld2e18u35-ceph","e18u35-ceph"],
    "10.31.89.36": ["akld2e18u36-ceph","e18u36-ceph"],
    "10.31.89.37": ["akld2e18u37-ceph","e18u37-ceph"],
    "10.31.89.38": ["akld2e18u38-ceph","e18u38-ceph"],
    "10.31.89.39": ["akld2e18u39-ceph","e18u39-ceph"],
    "10.31.89.40": ["akld2e18u40-ceph","e18u40-ceph"],
    "10.31.89.41": ["akld2e18u41-ceph","e18u41-ceph"],
    "10.31.89.42": ["akld2e18u42-ceph","e18u42-ceph"],

    #"10.31.89.101": ["akld2d18u01-ceph",  "d18u01-ceph"],
    "10.31.89.102": ["akld2d18u02-ceph",  "d18u02-ceph"],
    "10.31.89.103": ["akld2d18u03-ceph",  "d18u03-ceph"],
    "10.31.89.104": ["akld2d18u04-ceph",  "d18u04-ceph"],
    "10.31.89.105": ["akld2d18u05-ceph",  "d18u05-ceph"],
    "10.31.89.106": ["akld2d18u06-ceph",  "d18u06-ceph"],
    "10.31.89.107": ["akld2d18u07-ceph",  "d18u07-ceph"],
    "10.31.89.108": ["akld2d18u08-ceph",  "d18u08-ceph"],
    "10.31.89.109": ["akld2d18u09-ceph",  "d18u09-ceph"],
    "10.31.89.110": ["akld2d18u10-ceph",  "d18u10-ceph"],
    "10.31.89.111": ["akld2d18u11-ceph",  "d18u11-ceph"],
    "10.31.89.112": ["akld2d18u12-ceph",  "d18u12-ceph"],
    "10.31.89.113": ["akld2d18u13-ceph",  "d18u13-ceph"],
    "10.31.89.114": ["akld2d18u14-ceph",  "d18u14-ceph"],
    "10.31.89.115": ["akld2d18u15-ceph",  "d18u15-ceph"],
    "10.31.89.116": ["akld2d18u16-ceph",  "d18u16-ceph"],
    #"10.31.89.117": ["akld2d18u17-ceph",  "d18u17-ceph"],
    "10.31.89.118": ["akld2d18u18-ceph",  "d18u18-ceph"],
    #"10.31.89.119": ["akld2d18u19-ceph",  "d18u19-ceph"],
    #"10.31.89.120": ["akld2d18u20-ceph",  "d18u20-ceph"],
    #"10.31.89.121": ["akld2d18u21-ceph",  "d18u21-ceph"],
    "10.31.89.122": ["akld2d18u22-ceph",  "d18u22-ceph"],
    #"10.31.89.123": ["akld2d18u23-ceph",  "d18u23-ceph"],
    "10.31.89.124": ["akld2d18u24-ceph",  "d18u24-ceph"],
    #"10.31.89.125": ["akld2d18u25-ceph",  "d18u25-ceph"],
    "10.31.89.126": ["akld2d18u26-ceph",  "d18u26-ceph"],
    #"10.31.89.127": ["akld2d18u27-ceph",  "d18u27-ceph"],
    "10.31.89.128": ["akld2d18u28-ceph",  "d18u28-ceph"],
    #"10.31.89.129": ["akld2d18u29-ceph",  "d18u29-ceph"],
    "10.31.89.130": ["akld2d18u30-ceph",  "d18u30-ceph"],
    #"10.31.89.131": ["akld2d18u31-ceph",  "d18u31-ceph"],
    "10.31.89.132": ["akld2d18u32-ceph",  "d18u32-ceph"],
    #"10.31.89.133": ["akld2d18u33-ceph",  "d18u33-ceph"],
    "10.31.89.134": ["akld2d18u34-ceph",  "d18u34-ceph"],
    #"10.31.89.135": ["akld2d18u35-ceph",  "d18u35-ceph"],
    "10.31.89.136": ["akld2d18u36-ceph",  "d18u36-ceph"],
    #"10.31.89.137": ["akld2d18u37-ceph",  "d18u37-ceph"],
    "10.31.89.138": ["akld2d18u38-ceph",  "d18u38-ceph"],
    #"10.31.89.139": ["akld2d18u39-ceph",  "d18u39-ceph"],
    "10.31.89.140": ["akld2d18u40-ceph",  "d18u40-ceph"],
    #"10.31.89.141": ["akld2d18u41-ceph",  "d18u41-ceph"],
    #"10.31.89.142": ["akld2d18u42-ceph",  "d18u42-ceph"],
}

b15_b18_hosts = {
    "172.31.82.126": ["akld2b15u26-m", "b15u26-m"],
    "10.31.82.126": ["akld2b15u26-p", "b15u26-p", "akld2b15u26", "b15u26"],
    "172.31.82.25": ["akld2b18u25-m", "b18u25-m"],
    "10.31.82.25": ["akld2b18u25-p", "b18u25-p", "akld2b18u25", "b18u25"],
}

migration_alias = {
    "10.31.81.1": ["akld2e18u01-api", "akld2e18u01"],
    "10.31.81.2": ["akld2e18u02-api", "akld2e18u02"],
    "10.31.81.3": ["akld2e18u03-api", "akld2e18u03"],
    "10.31.81.4": ["akld2e18u04-api", "akld2e18u04"],
    "10.31.81.5": ["akld2e18u05-api", "akld2e18u05"],
    "10.31.81.6": ["akld2e18u06-api", "akld2e18u06"],
    "10.31.81.7": ["akld2e18u07-api", "akld2e18u07"],
    "10.31.81.8": ["akld2e18u08-api", "akld2e18u08"],
    "10.31.81.9": ["akld2e18u09-api", "akld2e18u09"],
    "10.31.81.10": ["akld2e18u10-api", "akld2e18u10"],
    "10.31.81.11": ["akld2e18u11-api", "akld2e18u11"],
    "10.31.81.12": ["akld2e18u12-api", "akld2e18u12"],
    "10.31.81.13": ["akld2e18u13-api", "akld2e18u13"],
    "10.31.81.14": ["akld2e18u14-api", "akld2e18u14"],
    "10.31.81.15": ["akld2e18u15-api", "akld2e18u15"],
    "10.31.81.16": ["akld2e18u16-api", "akld2e18u16"],
    "10.31.81.17": ["akld2e18u17-api", "akld2e18u17"],
    "10.31.81.18": ["akld2e18u18-api", "akld2e18u18"],
    "10.31.81.19": ["akld2e18u19-api", "akld2e18u19"],
    "10.31.81.20": ["akld2e18u20-api", "akld2e18u20"],
    #"10.31.81.21": ["akld2e18u21-api", "akld2e18u21"],
    #"10.31.81.22": ["akld2e18u22-api", "akld2e18u22"],
    "10.31.81.23": ["akld2e18u23-api", "akld2e18u23"],
    "10.31.81.24": ["akld2e18u24-api", "akld2e18u24"],
    "10.31.81.25": ["akld2e18u25-api", "akld2e18u25"],
    "10.31.81.26": ["akld2e18u26-api", "akld2e18u26"],
    "10.31.81.27": ["akld2e18u27-api", "akld2e18u27"],
    "10.31.81.28": ["akld2e18u28-api", "akld2e18u28"],
    "10.31.81.29": ["akld2e18u29-api", "akld2e18u29"],
    "10.31.81.30": ["akld2e18u30-api", "akld2e18u30"],
    "10.31.81.31": ["akld2e18u31-api", "akld2e18u31"],
    "10.31.81.32": ["akld2e18u32-api", "akld2e18u32"],
    "10.31.81.33": ["akld2e18u33-api", "akld2e18u33"],
    "10.31.81.34": ["akld2e18u34-api", "akld2e18u34"],
    "10.31.81.35": ["akld2e18u35-api", "akld2e18u35"],
    "10.31.81.36": ["akld2e18u36-api", "akld2e18u36"],
    "10.31.81.37": ["akld2e18u37-api", "akld2e18u37"],
    "10.31.81.38": ["akld2e18u38-api", "akld2e18u38"],
    "10.31.81.39": ["akld2e18u39-api", "akld2e18u39"],
    "10.31.81.40": ["akld2e18u40-api", "akld2e18u40"],
    "10.31.81.41": ["akld2e18u41-api", "akld2e18u41"],
    "10.31.81.42": ["akld2e18u42-api", "akld2e18u42"],

    #"10.31.81.101": ["akld2d18u01-api", "akld2d18u01"],
    "10.31.81.102": ["akld2d18u02-api", "akld2d18u02"],
    "10.31.81.103": ["akld2d18u03-api", "akld2d18u03"],
    "10.31.81.104": ["akld2d18u04-api", "akld2d18u04"],
    "10.31.81.105": ["akld2d18u05-api", "akld2d18u05"],
    "10.31.81.106": ["akld2d18u06-api", "akld2d18u06"],
    "10.31.81.107": ["akld2d18u07-api", "akld2d18u07"],
    "10.31.81.108": ["akld2d18u08-api", "akld2d18u08"],
    "10.31.81.109": ["akld2d18u09-api", "akld2d18u09"],
    "10.31.81.110": ["akld2d18u10-api", "akld2d18u10"],
    "10.31.81.111": ["akld2d18u11-api", "akld2d18u11"],
    "10.31.81.112": ["akld2d18u12-api", "akld2d18u12"],
    "10.31.81.113": ["akld2d18u13-api", "akld2d18u13"],
    "10.31.81.114": ["akld2d18u14-api", "akld2d18u14"],
    "10.31.81.115": ["akld2d18u15-api", "akld2d18u15"],
    "10.31.81.116": ["akld2d18u16-api", "akld2d18u16"],
    #"10.31.81.117": ["akld2d18u17-api", "akld2d18u17"],
    "10.31.81.118": ["akld2d18u18-api", "akld2d18u18"],
    #"10.31.81.119": ["akld2d18u19-api", "akld2d18u19"],
    #"10.31.81.120": ["akld2d18u20-api", "akld2d18u20"],
    #"10.31.81.121": ["akld2d18u21-api", "akld2d18u21"],
    "10.31.81.122": ["akld2d18u22-api", "akld2d18u22"],
    #"10.31.81.123": ["akld2d18u23-api", "akld2d18u23"],
    "10.31.81.124": ["akld2d18u24-api", "akld2d18u24"],
    #"10.31.81.125": ["akld2d18u25-api", "akld2d18u25"],
    "10.31.81.126": ["akld2d18u26-api", "akld2d18u26"],
    #"10.31.81.127": ["akld2d18u27-api", "akld2d18u27"],
    "10.31.81.128": ["akld2d18u28-api", "akld2d18u28"],
    #"10.31.81.129": ["akld2d18u29-api", "akld2d18u29"],
    "10.31.81.130": ["akld2d18u30-api", "akld2d18u30"],
    #"10.31.81.131": ["akld2d18u31-api", "akld2d18u31"],
    "10.31.81.132": ["akld2d18u32-api", "akld2d18u32"],
    #"10.31.81.133": ["akld2d18u33-api", "akld2d18u33"],
    "10.31.81.134": ["akld2d18u34-api", "akld2d18u34"],
    #"10.31.81.135": ["akld2d18u35-api", "akld2d18u35"],
    "10.31.81.136": ["akld2d18u36-api", "akld2d18u36"],
    #"10.31.81.137": ["akld2d18u37-api", "akld2d18u37"],
    "10.31.81.138": ["akld2d18u38-api", "akld2d18u38"],
    #"10.31.81.139": ["akld2d18u39-api", "akld2d18u39"],
    "10.31.81.140": ["akld2d18u40-api", "akld2d18u40"],
    #"10.31.81.141": ["akld2d18u41-api", "akld2d18u41"],
    #"10.31.81.142": ["akld2d18u42-api", "akld2d18u42"],
}

h15_i15_hosts = {
    "172.31.83.151": ["akld2h15u01-m", "h15u01-m"],
    "172.31.83.153": ["akld2h15u03-m", "h15u03-m"],
    "172.31.83.155": ["akld2h15u05-m", "h15u05-m"],
    "172.31.83.185": ["akld2h15u35-m", "h15u35-m"],
    "172.31.83.180": ["akld2h15x30-m", "h15x30-m", "h15x30"],
    "172.31.83.181": ["akld2h15x31-m", "h15x31-m", "h15x31"],
    "172.31.83.183": ["akld2h15x33-m", "h15x33-m", "h15x33"],
    
    "10.31.83.151": ["akld2h15u01-p", "h15u01-p", "ntr-sto15-p"],
    "10.31.83.153": ["akld2h15u03-p", "h15u03-p", "ntr-sto17-p"],
    "10.31.83.155": ["akld2h15u05-p", "h15u05-p", "ntr-sto19-p"],
    "10.31.83.185": ["akld2h15u35-p", "h15u35-p"],
    
    "10.31.87.185": ["akld2h15u35-api", "h15u35-api", "akld2h15u35", "h15u35"],

    "10.31.91.151": ["akld2h15u01-ceph", "h15u01-ceph", "ntr-sto15-ceph", "ntr-sto15", "sto15", "akld2h15u01", "h15u01"],
    "10.31.91.153": ["akld2h15u03-ceph", "h15u03-ceph", "ntr-sto17-ceph", "ntr-sto17", "sto17", "akld2h15u03", "h15u03"],
    "10.31.91.155": ["akld2h15u05-ceph", "h15u05-ceph", "ntr-sto19-ceph", "ntr-sto19", "sto19", "akld2h15u05", "h15u05"],
    "10.31.91.185": ["akld2h15u35-ceph", "h15u35-ceph"],

    "10.31.95.151": ["akld2h15u01-repl", "h15u01-repl", "ntr-sto15-repl"],
    "10.31.95.153": ["akld2h15u03-repl", "h15u03-repl", "ntr-sto17-repl"],
    "10.31.95.155": ["akld2h15u05-repl", "h15u05-repl", "ntr-sto19-repl"],

    "172.31.83.51": ["akld2i15u01-m", "i15u01-m"],
    "172.31.83.53": ["akld2i15u03-m", "i15u03-m"],
    "172.31.83.55": ["akld2i15u05-m", "i15u05-m"],
    "172.31.83.80": ["akld2i15x30-m", "i15x30-m", "i15x30"],
    "172.31.83.81": ["akld2i15x31-m", "i15x31-m", "i15x31"],
    "172.31.83.83": ["akld2i15x33-m", "i15x33-m", "i15x33"],
    
    "10.31.83.51": ["akld2i15u01-p", "i15u01-p", "ntr-sto16-p"],
    "10.31.83.53": ["akld2i15u03-p", "i15u03-p", "ntr-sto18-p"],
    "10.31.83.55": ["akld2i15u05-p", "i15u05-p", "ntr-sto20-p"],
    "10.31.83.85": ["akld2i15u35-p", "i15u35-p"],
    
    "10.31.91.51": ["akld2i15u01-ceph", "i15u01-ceph", "ntr-sto16-ceph", "ntr-sto16", "sto16", "akld2i15u01", "i15u01"],
    "10.31.91.53": ["akld2i15u03-ceph", "i15u03-ceph", "ntr-sto18-ceph", "ntr-sto18", "sto18", "akld2i15u03", "i15u03"],
    "10.31.91.55": ["akld2i15u05-ceph", "i15u05-ceph", "ntr-sto20-ceph", "ntr-sto20", "sto20", "akld2i15u01", "i15u05"],

    "10.31.95.51": ["akld2i15u01-repl", "i15u01-repl", "ntr-sto16-repl"],
    "10.31.95.53": ["akld2i15u03-repl", "i15u03-repl", "ntr-sto18-repl"],
    "10.31.95.55": ["akld2i15u05-repl", "i15u05-repl", "ntr-sto20-repl"],
}

h18_switches = {
    "172.31.83.146": ["akld2h18x46-m", "h18x46-m", "h18x46"],
    "172.31.83.147": ["akld2h18x47-m", "h18x47-m", "h18x47"],
}

rename_G18_entries_to_h18 = { # ITS changed the rack names on us :(
    "172.31.80.1": ["akld2g18x40", "ntr-x1-mgmt","x1-m","x1","g18x40-m","g18x40"],
    "172.31.80.2": ["akld2g18x37","ntr-x2-prov1","x2-m","x2","g18x37-m","g18x37"],
    "172.31.80.4": ["akld2g18x32","ntr-x4-core1","x4-m","x4","g18x32-m","g18x32"],
    "172.31.80.6": ["akld2g18x31","ntr-x6-core3","x6-m","x6","g18x31-m","g18x31"],

    "172.31.80.128": ["akld2g18u24-m","g18u24-m","d2ntrcop01-idrac","ntr-cop01-m","cop01-m"],
    "172.31.80.129": ["akld2g18u25-m","g18u25-m","d2ntrcop02-idrac","ntr-cop02-m","cop02-m"],
    "172.31.80.130": ["akld2g18u26-m","g18u26-m","d2ntrcop03-idrac","ntr-cop03-m","cop03-m"],
    "172.31.80.135": ["akld2g18u44-m","g18u44-m","d2ntrcop08-idrac","ntr-cop08-m","cop08-m"],
    "172.31.80.136": ["akld2g18u27-m","g18u27-m","d2ntrcop09-idrac","ntr-cop09-m","cop09-m"],
    "172.31.80.138": ["akld2g18u28-m","g18u28-m","d2ntrcop11-idrac","ntr-cop11-m","cop11-m"],

    "172.31.80.31": ["akld2g18a17-m","g18a17-m","d2ntradm01-idrac","ntr-adm01-m","adm01-m"],
    "172.31.80.41": ["akld2g18a18-m","g18a18-m","d2ntrctr01-idrac","ntr-ctr01-m","ctr01-m"],
    "172.31.80.43": ["akld2g18a19-m","g18a19-m","d2ntrctr03-idrac","ntr-ctr03-m","ctr03-m"],

    "172.31.80.64": ["akld2g18s01-m","g18s01-m","d2ntrsto01-idrac","ntr-sto01-m","sto01-m"],
    "172.31.80.65": ["akld2g18s03-m","g18s03-m","d2ntrsto02-idrac","ntr-sto02-m","sto02-m"],
    "172.31.80.66": ["akld2g18s05-m","g18s05-m","d2ntrsto03-idrac","ntr-sto03-m","sto03-m"],
    "172.31.80.67": ["akld2g18s07-m","g18s07-m","d2ntrsto04-idrac","ntr-sto04-m","sto04-m"],
    "172.31.80.72": ["akld2g18s09-m","g18s09-m","d2ntrsto09-idrac","ntr-sto09-m","sto09-m"],
    "172.31.80.74": ["akld2g18s11-m","g18s11-m","d2ntrsto11-idrac","ntr-sto11-m","sto11-m"],
    "172.31.80.76": ["akld2g18s13-m","g18s13-m","d2ntrsto13-idrac","ntr-sto13-m","sto13-m"],

    "10.31.80.31": ["akld2g18a17-p","g18a17-p", "ntr-adm01-p","adm01-p", "adm01"],
    "10.31.80.41": ["akld2g18a18-p","g18a18-p", "ntr-ctr01-p","ctr01-p", "ctr01"],
    "10.31.80.43": ["akld2g18a19-p","g18a19-p", "ntr-ctr03-p","ctr03-p", "ctr03"],

    "10.31.80.64": ["akld2g18s01-p","g18s01-p", "ntr-sto01-p","sto01-p", "sto01"],
    "10.31.80.65": ["akld2g18s03-p","g18s03-p", "ntr-sto02-p","sto02-p", "sto02"],
    "10.31.80.66": ["akld2g18s05-p","g18s05-p", "ntr-sto03-p","sto03-p", "sto03"],
    "10.31.80.67": ["akld2g18s07-p","g18s07-p", "ntr-sto04-p","sto04-p", "sto04"],
    "10.31.80.72": ["akld2g18s09-p","g18s09-p", "ntr-sto09-p","sto09-p", "sto09"],
    "10.31.80.74": ["akld2g18s11-p","g18s11-p", "ntr-sto11-p","sto11-p", "sto11"],
    "10.31.80.76": ["akld2g18s13-p","g18s13-p", "ntr-sto13-p","sto13-p", "sto13"],

    "10.31.88.64": ["akld2g18s01-ceph","g18s01-ceph", "ntr-sto01-ceph","sto01-ceph"],
    "10.31.88.65": ["akld2g18s03-ceph","g18s03-ceph", "ntr-sto02-ceph","sto02-ceph"],
    "10.31.88.66": ["akld2g18s05-ceph","g18s05-ceph", "ntr-sto03-ceph","sto03-ceph"],
    "10.31.88.67": ["akld2g18s07-ceph","g18s07-ceph", "ntr-sto04-ceph","sto04-ceph"],
    "10.31.88.72": ["akld2g18s09-ceph","g18s09-ceph", "ntr-sto09-ceph","sto09-ceph"],
    "10.31.88.74": ["akld2g18s11-ceph","g18s11-ceph", "ntr-sto11-ceph","sto11-ceph"],
    "10.31.88.76": ["akld2g18s13-ceph","g18s13-ceph", "ntr-sto13-ceph","sto13-ceph"],

    "10.31.92.64": ["akld2g18s01-repl","g18s01-repl", "ntr-sto01-repl","sto01-repl"],
    "10.31.92.65": ["akld2g18s03-repl","g18s03-repl", "ntr-sto02-repl","sto02-repl"],
    "10.31.92.66": ["akld2g18s05-repl","g18s05-repl", "ntr-sto03-repl","sto03-repl"],
    "10.31.92.67": ["akld2g18s07-repl","g18s07-repl", "ntr-sto04-repl","sto04-repl"],
    "10.31.92.72": ["akld2g18s09-repl","g18s09-repl", "ntr-sto09-repl","sto09-repl"],
    "10.31.92.74": ["akld2g18s11-repl","g18s11-repl", "ntr-sto11-repl","sto11-repl"],
    "10.31.92.76": ["akld2g18s13-repl","g18s13-repl", "ntr-sto13-repl","sto13-repl"],

    "10.31.80.128": ["akld2g18u24-p","g18u24-p", "ntr-cop01-p","cop01-p"],
    "10.31.80.129": ["akld2g18u25-p","g18u25-p", "ntr-cop02-p","cop02-p"],
    "10.31.80.130": ["akld2g18u26-p","g18u26-p", "ntr-cop03-p","cop03-p"],
    "10.31.80.135": ["akld2g18u44-p","g18u44-p", "ntr-cop08-p","cop08-p"],
    "10.31.80.136": ["akld2g18u27-p","g18u27-p", "ntr-cop09-p","cop09-p"],
    "10.31.80.138": ["akld2g18u28-p","g18u28-p", "ntr-cop11-p","cop11-p"],

    "10.31.84.128": ["akld2g18u24-api","g18u24-api", "ntr-cop01-api","cop01-api", "akld2g18u24", "cop01"],
    "10.31.84.129": ["akld2g18u25-api","g18u25-api", "ntr-cop02-api","cop02-api", "akld2g18u25", "cop02"],
    "10.31.84.130": ["akld2g18u26-api","g18u26-api", "ntr-cop03-api","cop03-api", "akld2g18u26", "cop03"],
    "10.31.84.135": ["akld2g18u44-api","g18u44-api", "ntr-cop08-api","cop08-api", "akld2g18u44", "cop08"],
    "10.31.84.136": ["akld2g18u27-api","g18u27-api", "ntr-cop09-api","cop09-api", "akld2g18u27", "cop09"],
    "10.31.84.138": ["akld2g18u28-api","g18u28-api", "ntr-cop11-api","cop11-api", "akld2g18u28", "cop11"],

    "10.31.88.128": ["akld2g18u24-ceph","g18u24-ceph", "ntr-cop01-ceph","cop01-ceph"],
    "10.31.88.129": ["akld2g18u25-ceph","g18u25-ceph", "ntr-cop02-ceph","cop02-ceph"],
    "10.31.88.130": ["akld2g18u26-ceph","g18u26-ceph", "ntr-cop03-ceph","cop03-ceph"],
    "10.31.88.135": ["akld2g18u44-ceph","g18u44-ceph", "ntr-cop08-ceph","cop08-ceph"],
    "10.31.88.136": ["akld2g18u27-ceph","g18u27-ceph", "ntr-cop09-ceph","cop09-ceph"],
    "10.31.88.138": ["akld2g18u28-ceph","g18u28-ceph", "ntr-cop11-ceph","cop11-ceph"],
}

rename_h18_entries_to_i18 = { # ITS changed the rack names on us :(

    "172.31.80.131": ["akld2h18u23-m","h18u23-m","d2ntrcop04-idrac","ntr-cop04-m","cop04-m"],
    "172.31.80.132": ["akld2h18u24-m","h18u24-m","d2ntrcop05-idrac","ntr-cop05-m","cop05-m"],
    "172.31.80.133": ["akld2h18u25-m","h18u25-m","d2ntrcop06-idrac","ntr-cop06-m","cop06-m"],
    "172.31.80.134": ["akld2h18u26-m","h18u26-m","d2ntrcop07-idrac","ntr-cop07-m","cop07-m"],
    "172.31.80.137": ["akld2h18u27-m","h18u27-m","d2ntrcop10-idrac","ntr-cop10-m","cop10-m"],

    "172.31.80.32": ["akld2h18a17-m","h18a17-m","d2ntradm02-idrac","ntr-adm02-m","adm02-m"],
    "172.31.80.42": ["akld2h18a18-m","h18a18-m","d2ntrctr02-idrac","ntr-ctr02-m","ctr02-m"],
    #
    "172.31.80.68": ["akld2h18s01-m","h18s01-m","d2ntrsto05-idrac","ntr-sto05-m","sto05-m"],
    "172.31.80.69": ["akld2h18s03-m","h18s03-m","d2ntrsto06-idrac","ntr-sto06-m","sto06-m"],
    "172.31.80.70": ["akld2h18s05-m","h18s05-m","d2ntrsto07-idrac","ntr-sto07-m","sto07-m"],
    "172.31.80.71": ["akld2h18s07-m","h18s07-m","d2ntrsto08-idrac","ntr-sto08-m","sto08-m"],
    "172.31.80.73": ["akld2h18s09-m","h18s09-m","d2ntrsto10-idrac","ntr-sto10-m","sto10-m"],
    "172.31.80.75": ["akld2h18s11-m","h18s11-m","d2ntrsto12-idrac","ntr-sto12-m","sto12-m"],
    "172.31.80.77": ["akld2h18s13-m","h18s13-m","d2ntrsto14-idrac","ntr-sto14-m","sto14-m"],

    "10.31.80.32": ["akld2h18a17-p","h18a17-p", "ntr-adm02-p","adm02-p", "adm02"],
    "10.31.80.42": ["akld2h18a18-p","h18a18-p", "ntr-ctr02-p","ctr02-p", "ctr02"],
    #
    "10.31.80.68": ["akld2h18s01-p","h18s01-p", "ntr-sto05-p","sto05-p", "sto05"],
    "10.31.80.69": ["akld2h18s03-p","h18s03-p", "ntr-sto06-p","sto06-p", "sto06"],
    "10.31.80.70": ["akld2h18s05-p","h18s05-p", "ntr-sto07-p","sto07-p", "sto07"],
    "10.31.80.71": ["akld2h18s07-p","h18s07-p", "ntr-sto08-p","sto08-p", "sto08"],
    "10.31.80.73": ["akld2h18s09-p","h18s09-p", "ntr-sto10-p","sto10-p", "sto10"],
    "10.31.80.75": ["akld2h18s11-p","h18s11-p", "ntr-sto12-p","sto12-p", "sto12"],
    "10.31.80.77": ["akld2h18s13-p","h18s13-p", "ntr-sto14-p","sto14-p", "sto14"],
    #
    "10.31.88.68": ["akld2h18s01-ceph","h18s01-ceph", "ntr-sto05-ceph","sto05-ceph"],
    "10.31.88.69": ["akld2h18s03-ceph","h18s03-ceph", "ntr-sto06-ceph","sto06-ceph"],
    "10.31.88.70": ["akld2h18s05-ceph","h18s05-ceph", "ntr-sto07-ceph","sto07-ceph"],
    "10.31.88.71": ["akld2h18s07-ceph","h18s07-ceph", "ntr-sto08-ceph","sto08-ceph"],
    "10.31.88.73": ["akld2h18s09-ceph","h18s09-ceph", "ntr-sto10-ceph","sto10-ceph"],
    "10.31.88.75": ["akld2h18s11-ceph","h18s11-ceph", "ntr-sto12-ceph","sto12-ceph"],
    "10.31.88.77": ["akld2h18s13-ceph","h18s13-ceph", "ntr-sto14-ceph","sto14-ceph"],
    #
    "10.31.92.68": ["akld2h18s01-repl","h18s01-repl", "ntr-sto05-repl","sto05-repl"],
    "10.31.92.69": ["akld2h18s03-repl","h18s03-repl", "ntr-sto06-repl","sto06-repl"],
    "10.31.92.70": ["akld2h18s05-repl","h18s05-repl", "ntr-sto07-repl","sto07-repl"],
    "10.31.92.71": ["akld2h18s07-repl","h18s07-repl", "ntr-sto08-repl","sto08-repl"],
    "10.31.92.73": ["akld2h18s09-repl","h18s09-repl", "ntr-sto10-repl","sto10-repl"],
    "10.31.92.75": ["akld2h18s11-repl","h18s11-repl", "ntr-sto12-repl","sto12-repl"],
    "10.31.92.77": ["akld2h18s13-repl","h18s13-repl", "ntr-sto14-repl","sto14-repl"],
    #
    "10.31.80.131": ["akld2h18u23-p","h18u23-p", "ntr-cop04-p","cop04-p"],
    "10.31.80.132": ["akld2h18u24-p","h18u24-p", "ntr-cop05-p","cop05-p"],
    "10.31.80.133": ["akld2h18u25-p","h18u25-p", "ntr-cop06-p","cop06-p"],
    "10.31.80.134": ["akld2h18u26-p","h18u26-p", "ntr-cop07-p","cop07-p"],
    "10.31.80.137": ["akld2h18u27-p","h18u27-p", "ntr-cop10-p","cop10-p"],
    #
    "10.31.84.131": ["akld2h18u23-api","h18u23-api", "ntr-cop04-api","cop04-api", "akld2h18u23", "cop04"],
    "10.31.84.132": ["akld2h18u24-api","h18u24-api", "ntr-cop05-api","cop05-api", "akld2h18u24", "cop05"],
    "10.31.84.133": ["akld2h18u25-api","h18u25-api", "ntr-cop06-api","cop06-api", "akld2h18u25", "cop06"],
    "10.31.84.134": ["akld2h18u26-api","h18u26-api", "ntr-cop07-api","cop07-api", "akld2h18u26", "cop07"],
    "10.31.84.137": ["akld2h18u27-api","h18u27-api", "ntr-cop10-api","cop10-api", "akld2h18u27", "cop10"],
    #
    "10.31.88.131": ["akld2h18u23-ceph","h18u23-ceph", "ntr-cop04-ceph","cop04-ceph"],
    "10.31.88.132": ["akld2h18u24-ceph","h18u24-ceph", "ntr-cop05-ceph","cop05-ceph"],
    "10.31.88.133": ["akld2h18u25-ceph","h18u25-ceph", "ntr-cop06-ceph","cop06-ceph"],
    "10.31.88.134": ["akld2h18u26-ceph","h18u26-ceph", "ntr-cop07-ceph","cop07-ceph"],
    "10.31.88.137": ["akld2h18u27-ceph","h18u27-ceph", "ntr-cop10-ceph","cop10-ceph"],
}

switch_renaming_from_h_to_i = { # ITS changed the rack names on us :(
    "172.31.80.3": ["akld2h18x27","ntr-x3-prov2","x3-m","x3","h18x37-m","h18x37","akld2h18x27-m"],
    "172.31.80.5": ["akld2h18x32","ntr-x5-core2","x5-m","x5","h18x32-m","h18x32", "akld2h18x32-m"],
    "172.31.80.7": ["akld2h18x31","ntr-x7-core4","x7-m","x7","h18x31-m","h18x31", "akld2h18x31-m"],
}

switch_renaming_from_g_to_h = { # ITS changed the rack names on us :(
    "172.31.80.1": ["akld2g18x40", "ntr-x1-mgmt","x1-m","x1","g18x40-m","g18x40", "akld2g18x40-m"],
    "172.31.80.2": ["akld2g18x37","ntr-x2-prov1","x2-m","x2","g18x37-m","g18x37", "akld2g18x37-m"],
    "172.31.80.4": ["akld2g18x32","ntr-x4-core1","x4-m","x4","g18x32-m","g18x32", "akld2g18x32-m"],
    "172.31.80.6": ["akld2g18x31","ntr-x6-core3","x6-m","x6","g18x31-m","g18x31", "akld2g18x31-m"],
}

def add_hosts(hosts):
    for ip in hosts:
        create_host_record(host_name = hosts[ip][0]+".nectar.auckland.ac.nz", ip=ip) 
        for n in range(1,len(hosts[ip])):
            add_host_alias(host_name=hosts[ip][0]+".nectar.auckland.ac.nz", alias=hosts[ip][n]+".nectar.auckland.ac.nz")
    print "done"

def add_aliases(hosts):
    for ip in hosts:
        for n in range(1,len(hosts[ip])):
            add_host_alias(host_name=hosts[ip][0]+".nectar.auckland.ac.nz", alias=hosts[ip][n]+".nectar.auckland.ac.nz")
    print "done"

def dump_hosts(hosts, default_domain=".nectar.auckland.ac.nz"):
    for ip in hosts:
        r = get_host_by_ip(ip_v4=ip)
        for h in r:
            print get_host(host_name=h , fields="ipv4addrs,name,dns_name,aliases,dns_aliases,configure_for_dns")
        #print get_host(host_name=hosts[ip][0]+default_domain , fields="ipv4addrs,name,dns_name,aliases,dns_aliases,configure_for_dns")
    print "done"
    
#add_aliases(hosts=migration_alias)
#x = { 
#    "130.216.189.3": ["ng2.auckland.ac.nz"], 
#}
#dump_hosts(hosts=x, default_domain='')
#add_hosts(h18_switches)

import re
def rename_hosts(hosts, from_expr, to_expr):
    for ip in hosts:
        for n in range(1,len(hosts[ip])):
            delete_host_alias(host_name=hosts[ip][0]+".nectar.auckland.ac.nz", alias=hosts[ip][n]+".nectar.auckland.ac.nz")
        delete_host_record(host_name=hosts[ip][0]+".nectar.auckland.ac.nz")
        
        new_hostname = re.sub(from_expr, to_expr, hosts[ip][0])
        create_host_record(host_name = new_hostname+".nectar.auckland.ac.nz", ip=ip) 
        for n in range(1,len(hosts[ip])):
            new_alias = re.sub(from_expr, to_expr, hosts[ip][n])
            add_host_alias(host_name=new_hostname+".nectar.auckland.ac.nz", alias=new_alias+".nectar.auckland.ac.nz")

#rename_hosts(rename_h18_entries_to_i18, "^(.*)h18[aus]", r"\1i18u")
#rename_hosts(switch_renaming_from_h_to_i, "^(.*)h18", r"\1i18")
#rename_hosts(rename_G18_entries_to_h18, "^(.*)g18[aus]", r"\1h18u")
#rename_hosts(switch_renaming_from_g_to_h, "^(.*)g18", r"\1h18")
#dump_hosts(hosts=switch_renaming_from_g_to_h)
delete_host_record('fred.nectar.auckland.ac.nz')
#delete_host_alias('ivm28.nectar.auckland.ac.nz', 'fred.nectar.auckland.ac.nz')