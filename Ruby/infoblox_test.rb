#!/usr/local/bin/ruby
require_relative 'infoblox.rb'

# Create entries in IPAM for all nectar VMs on external networks
def create_external_vm_hostnames
  # Classic network 1 130.216.216.0/23
  @infoblox.create_host_record(hostname: 'classic-net-1.nectar.auckland.ac.nz', ip_address: '130.216.216.0')
  @infoblox.create_host_record(hostname: 'classic-net-1-dhcp.nectar.auckland.ac.nz', ip_address: '130.216.216.1')
  @infoblox.create_host_record(hostname: 'classic-net-1-r1.nectar.auckland.ac.nz', ip_address: '130.216.217.252')
  @infoblox.create_host_record(hostname: 'classic-net-1-r2.nectar.auckland.ac.nz', ip_address: '130.216.217.253')
  @infoblox.create_host_record(hostname: 'classic-net-1-r.nectar.auckland.ac.nz', ip_address: '130.216.217.254')
  @infoblox.create_host_record(hostname: 'classic-net-1-bc.nectar.auckland.ac.nz', ip_address: '130.216.217.255')
  
  # Classic network 2 130.216.254.0/24
  @infoblox.create_host_record(hostname: 'classic-net-2.nectar.auckland.ac.nz', ip_address: '130.216.254.0')
  @infoblox.create_host_record(hostname: 'classic-net-2-dhcp.nectar.auckland.ac.nz', ip_address: '130.216.254.1')
  @infoblox.create_host_record(hostname: 'classic-net-2-r1.nectar.auckland.ac.nz', ip_address: '130.216.254.252')
  @infoblox.create_host_record(hostname: 'classic-net-2-r2.nectar.auckland.ac.nz', ip_address: '130.216.254.253')
  @infoblox.create_host_record(hostname: 'classic-net-2-r.nectar.auckland.ac.nz', ip_address: '130.216.254.254')
  @infoblox.create_host_record(hostname: 'classic-net-2-bc.nectar.auckland.ac.nz', ip_address: '130.216.254.255')

  # Mido net 130.216.218.0/23
  @infoblox.create_host_record(hostname: 'dynamic-net-1.nectar.auckland.ac.nz', ip_address: '130.216.218.255')
  @infoblox.create_host_record(hostname: 'dynamic-net-1-r.nectar.auckland.ac.nz', ip_address: '130.216.219.254')
  @infoblox.create_host_record(hostname: 'dynamic-net-1-bc.nectar.auckland.ac.nz', ip_address: '130.216.219.255')

  [216,217,254,218,219].each do |r|
    (0..255).each do |i|
      ip = "130.216.#{r}.#{i}"
      if @infoblox.get_host_by_ip(ip_address: ip) == 0
        hostname = "evm-#{r}-#{i}.nectar.auckland.ac.nz"
    
        puts "Create #{ip} #{hostname}"
        @infoblox.create_host_record(hostname: hostname, ip_address: ip)
    
      end
    end
  end
end

def print_ip_record(ip:, assigned_only: false)
  load_cnames if @reverse_cnames.nil?
  
  host_records = @infoblox.get_host_by_ip(ip_address: ip)
  if (assigned_only && ! host_records.empty?) || ! assigned_only
    print "#{ip} ["
    host_records.each do |hosts|
      f = true
      hosts.each do |hn|
        print f ? "#{hn}" : "; #{hn}"
        @infoblox.get_alias(hostname: hn) { |a| print ", ALIAS: #{a}" }
        unless @reverse_cnames[hn].nil?
          @reverse_cnames[hn].each { |a| print ", CNAME: #{a}" }
        end
      
        f = false
      end
    end
    puts ']'
  end
end

def print_rack_nets(rack:, count: 48, assigned_only: false)
  load_cnames if @reverse_cnames.nil?

  set_rack_ip_offsets
  set_subnets
  ['m','p','api','ceph','repl'].each do |suffix|
    # IP of the first u in the rack
    rack_u1_ip = (@ip_subnet[suffix] + @ip_offset[rack] + 1)

    puts "-#{suffix}"
    (rack_u1_ip..rack_u1_ip+(count-1)).each do |ip|
      print_ip_record(ip: ip, assigned_only: assigned_only)
    end
  end
end

def print_suffix_net(suffix:,  assigned_only: false)
  set_subnets
  dump_net(base_net: @ip_subnet[suffix].to_s, mask_bits: @ip_subnet[suffix].mask_length, assigned_only: true)
end

# Dump hostnames allocated on internal Nectar/VMWare research VM nets
def dump_internal_nets(assigned_only: true)
  [189,161].each do |r|
    (0..255).each do |i|
      ip = "130.216.#{r}.#{i}"
      print_ip_record(ip: ip, assigned_only: assigned_only)
    end
  end
end

# Dump hostnames allocated in IPAM on external Nectar networks
def dump_external_nets(assigned_only: true)
  [216,217,254,218,219].each do |r|
    (0..255).each do |i|
      ip = "130.216.#{r}.#{i}"
      print_ip_record(ip: ip, assigned_only: assigned_only)
    end
  end
end

def dump_net(base_net: '10.31.80.0', mask_bits: 22, assigned_only: true)
  load_cnames if @reverse_cnames.nil?
  
  net = IPv4.new(base_net, mask_bits)
  net.each_ip do |ip|
    print_ip_record(ip: ip, assigned_only: assigned_only)
  end
end


def create_private_net_hostnames
#  [81,82,83].each do |basenet|
#    [['-m', '172.31.', 0],['-p', '10.31.', 0], ['-api','10.31.',4], ['-ceph', '10.31.', 8], ['-mido','']
# Delete the IPAM entry for this hostname
end


def add_missing_ceph_nodes
  @infoblox.create_host_record(hostname: 'nfsrgw01-p.nectar.auckland.ac.nz', ip_address: '10.31.80.24')
  @infoblox.create_host_record(hostname: 'nfsrgw01-ceph.nectar.auckland.ac.nz', ip_address: '10.31.88.24')
  @infoblox.create_host_record(hostname: 'nfsrgw01-enfs.nectar.auckland.ac.nz', ip_address: '10.31.96.24')
  @infoblox.add_cname(hostname: 'nfsrgw01-p.nectar.auckland.ac.nz', cname: 'nfsrgw01.nectar.auckland.ac.nz')

  @infoblox.create_host_record(hostname: 'manila-p.nectar.auckland.ac.nz', ip_address: '10.31.80.38')
  @infoblox.create_host_record(hostname: 'manila-api.nectar.auckland.ac.nz', ip_address: '10.31.84.38')
  @infoblox.create_host_record(hostname: 'manila-ceph.nectar.auckland.ac.nz', ip_address: '10.31.88.38')
  @infoblox.create_host_record(hostname: 'manila-nfs.nectar.auckland.ac.nz', ip_address: '10.31.108.38')
  @infoblox.add_cname(hostname: 'manila-p.nectar.auckland.ac.nz', cname: 'manila.nectar.auckland.ac.nz')

end

def set_rack_ip_offsets  # These Rack base addresses get added to 10.31.0.0 and 172.31.0.0
  base = IPv4.new('0.0.80.0').to_i
  @ip_offset ||= { # Rack, and IP address offset from base
    'b15'=> (IPv4.new('0.0.82.100') - base).to_i, 
    'd15'=> (IPv4.new('0.0.81.150') -base).to_i ,
    'e15'=> (IPv4.new('0.0.81.50') - base).to_i,
    'h15'=> (IPv4.new('0.0.83.150') - base).to_i,
    'i15'=> (IPv4.new('0.0.83.50') - base).to_i,
    'b18'=> (IPv4.new('0.0.82.0') - base).to_i,
    'd18'=> (IPv4.new('0.0.81.100') - base).to_i,
    'e18'=> (IPv4.new('0.0.81.0') - base).to_i,
    'h18'=> (IPv4.new('0.0.83.100') - base).to_i,
    'i18'=> (IPv4.new('0.0.83.0') - base).to_i
  }
end

def set_subnets
  @ip_subnet ||= { # hostname suffix => base_ip
    'm'=> IPv4.new('172.31.80.0', 22),  # vlan10 out of band management to switches, iDRACS, IMMs, ...
    'm2'=> IPv4.new('172.31.84.0', 22), # vlan11 inband management net to the switches (as a backup)
    'm3'=> IPv4.new('172.31.88.0', 22), # vlan12..15 out of band segmenting this subnet due to switch bug
    'p'=> IPv4.new('10.31.80.0', 22),   # vlan20 hardware provisioning network
    'api'=> IPv4.new('10.31.84.0', 22), # vlan40 cloud API network
    'uc'=> IPv4.new('10.31.100.0', 22), # vlan41 Undercloud API network
    'ceph'=> IPv4.new('10.31.88.0', 22),# vlan50 Ceph Storage network
    'enfs'=> IPv4.new('10.31.96.0', 22),# vlan51 External VMs connecting to NFS gateway for CephFS
    'infs'=> IPv4.new('10.31.104.0', 22),#vlan52 Internal VMs connectinog to NFS gateway for CephFS
    'nfs'=> IPv4.new('10.31.108.0', 22),# vlan53 NFS Servers for CephFS
    'repl'=> IPv4.new('10.31.92.0', 22),# vlan60 Ceph backend replication network
    'rados'=> IPv4.new('10.31.60.0', 22)# vlan61 Rados Private network
  }
end

def add_new_dell_r620s #Now the new R6525 AMD nodes 2021 purchase 3/4
  set_rack_ip_offsets
  set_subnets
  
  ['h15','i15'].each do |rack|
    (17..22).each do |u|
      ['m','p','api','ceph'].each do |suffix|
        hostname = "akld2%su%02d-%s.nectar.auckland.ac.nz"%[rack,u,suffix]
        cname = "%su%02d-%s.nectar.auckland.ac.nz"%[rack,u,suffix]
        ip = (@ip_subnet[suffix] + @ip_offset[rack] + u).to_s
        puts "#{hostname} #{cname} #{ip}"
        @infoblox.create_host_record(hostname: "%s"%hostname, ip_address: ip)
        @infoblox.add_cname(hostname: hostname, cname: cname)
        if suffix == 'api'
          # hypervisor hostname, without the -p
          hypervisor_cname = "%su%02d.nectar.auckland.ac.nz"%[rack,u]
          puts "hypervisor cname #{hypervisor_cname}"
          @infoblox.add_cname(hostname: hostname, cname: hypervisor_cname)
        end
      end
    end
  end
end

def cad01_fixup
  ip = '10.31.80.13'
  hostname='ntr-cad01.nectar.auckland.ac.nz'
  cname='cad01-p.nectar.auckland.ac.nz'
  @infoblox.add_cname(hostname: hostname, cname: cname)

  ip = '10.31.88.13'
  hostname='ntr-cad01-ceph.nectar.auckland.ac.nz'
  cname='cad01-ceph.nectar.auckland.ac.nz'
  @infoblox.add_cname(hostname: hostname, cname: cname)
end

def sto_fix
  (15..20).each do |sto|
    hostname="sto%d.nectar.auckland.ac.nz"%sto
    cname="sto%d-p.nectar.auckland.ac.nz"%sto
    @infoblox.add_cname(hostname: hostname, cname: cname)
  end
end

def switch_ip_changes
  
end

def add_new_dell_2021_purchase1_2(dry_run: true)
  set_rack_ip_offsets
  set_subnets
  
  ['h15','i15'].each do |rack|
    (39..45).each do |u|
      ['m','p','api','ceph'].each do |suffix| # Hypervisors have these vlans
        hostname = "akld2%su%02d-%s.nectar.auckland.ac.nz"%[rack,u,suffix]
        cname = "%su%02d-%s.nectar.auckland.ac.nz"%[rack,u,suffix]
        ip = (@ip_subnet[suffix] + @ip_offset[rack] + u).to_s
        puts "#{hostname} #{cname} #{ip}"
        unless dry_run
          @infoblox.create_host_record(hostname: "%s"%hostname, ip_address: ip)
          @infoblox.add_cname(hostname: hostname, cname: cname)
        end
        if suffix == 'api'
          # hypervisor hostname, without the -p
          hypervisor_cname = "%su%02d.nectar.auckland.ac.nz"%[rack,u]
          puts "hypervisor cname #{hypervisor_cname}"
          unless dry_run
            @infoblox.add_cname(hostname: hostname, cname: hypervisor_cname)
          end
        end
      end
    end
  end
end

def add_new_dell_2021_purchase3(dry_run: true)
  set_rack_ip_offsets
  set_subnets
  
  ['h15','i15'].each do |rack|
    (23..28).each do |u|
      ['m','p','api','ceph'].each do |suffix| # Hypervisors have these vlans
        hostname = "akld2%su%02d-%s.nectar.auckland.ac.nz"%[rack,u,suffix]
        cname = "%su%02d-%s.nectar.auckland.ac.nz"%[rack,u,suffix]
        ip = (@ip_subnet[suffix] + @ip_offset[rack] + u).to_s
        puts "#{hostname} #{cname} #{ip}"
        unless dry_run
          @infoblox.create_host_record(hostname: "%s"%hostname, ip_address: ip)
          @infoblox.add_cname(hostname: hostname, cname: cname)
        end
        if suffix == 'api'
          # hypervisor hostname, without the -p
          hypervisor_cname = "%su%02d.nectar.auckland.ac.nz"%[rack,u]
          puts "hypervisor cname #{hypervisor_cname}"
          unless dry_run
            @infoblox.add_cname(hostname: hostname, cname: hypervisor_cname)
          end
        end
      end
    end
  end
end

def add_new_dell_2021_purchase1_2_sto(dry_run: true)
  set_rack_ip_offsets
  set_subnets
  
  hsto = 21
  isto = 22
  ['h15','i15'].each do |rack|
    (7..9).step(2) do |u|
      ['m','p','ceph','repl'].each do |suffix|  # Storage nodes have these vlans.
        hostname = "akld2%su%02d-%s.nectar.auckland.ac.nz"%[rack,u,suffix]
        cname = [ "%su%02d-%s.nectar.auckland.ac.nz"%[rack,u,suffix]
                ]
        if suffix == 'p'
          sto = rack == 'h15' ? hsto : isto
          cname << [ "akld2%su%02d.nectar.auckland.ac.nz"%[rack,u],
                     "%su%02d.nectar.auckland.ac.nz"%[rack,u],
                     "ntr-sto%02d.nectar.auckland.ac.nz"%[sto],
                     "sto%02d.nectar.auckland.ac.nz"%[sto]
                   ]
          hsto += 2 if rack == 'h15'
          isto += 2 if rack == 'i15'
        end
                
        ip = (@ip_subnet[suffix] + @ip_offset[rack] + u).to_s
        puts "#{hostname} #{cname} #{ip}"
        unless dry_run
          @infoblox.create_host_record(hostname: "%s"%hostname, ip_address: ip)
          cname.each do |cn|
            @infoblox.add_cname(hostname: hostname, cname: cn)
          end
        end
      end
    end
  end
end

def load_cnames
  @reverse_cnames = {}
  @infoblox.get_cname(domain: 'nectar.auckland.ac.nz') do |cn, host|
    @reverse_cnames[host] ||= []
    @reverse_cnames[host] << cn
  end
end

def fix_new_dell_2021_purchase1_2_3(dry_run: true)
  load_cnames
  selected = [] # [7,9]
  (17..28).each { |i| selected << i }
  (39..45).each { |i| selected << i }
  ['h15','i15'].each do |rack|
    selected.each do |u|
      ['api'].each do |suffix|  # Storage nodes have these vlans.
        hn = "akld2%su%02d-%s.nectar.auckland.ac.nz"%[rack,u,suffix]
        aliases = [
         "%su%02d-%s.nectar.auckland.ac.nz"%[rack,u,suffix],
         "akld2%su%02d.nectar.auckland.ac.nz"%[rack,u,suffix],
         "%su%02d.nectar.auckland.ac.nz"%[rack,u,suffix]
        ]
        puts hn if dry_run
        @infoblox.set_host_aliases(hostname: hn, alias_fqdn: aliases ) unless dry_run
        puts if dry_run
      end
    end
  end
end

def fix_misc(dry_run: true)
  load_cnames
  
  delete_these = [ # Hostnames to delete. 'hostname.domainname'
    
  ]
  
  add_these = { # ip => { hostname: [ 'hostname.domainname'], aliases: ['hostname', 'hostname', ... ]}
  }
  
  set_alias = { # 'hostname.domainname' => aliases: ['hostname', 'hostname', ... ]
  }
   
  delete_these.each do |hn|
    puts "Delete #{hn}"
    @infoblox.delete_by_hostname(hostname: hn)  unless dry_run
  end
  
  sleep 15
  
  add_these.each do |ip, host_record|
    puts "Add #{ip} #{host_record[:hostname][0]}"
    @infoblox.create_host_record(ip_address:  ip, hostname: host_record[:hostname][0], aliases: host_record[:aliases])  unless dry_run
  end
  
  set_alias.each do |hn, aliases|
    puts "update #{hn}: Aliases #{aliases}" if dry_run
    @infoblox.set_host_aliases(hostname: hn, alias_fqdn: aliases ) unless dry_run
  end

end

 
def fix_new_dell_2021_sto_nodes(dry_run: true)
 selected = [1,3,5,7,9]
 sto_index_map = {
   'h15' => [15,16,17,21,22],
   'i15' => [18,19,20,23,24]
 }
 ['h15','i15'].each do |rack|
   selected.each_with_index do | u, u_index |
     ['m','p','ceph','repl'].each do |suffix|  # Storage nodes have these vlans.
       hn = "akld2%su%02d-%s.nectar.auckland.ac.nz"%[rack,u,suffix]
       sto_index = sto_index_map[rack][u_index]
       aliases = [
         "%su%02d-%s.nectar.auckland.ac.nz"%[rack,u,suffix],              # Short rack-u name
         "sto%02d-%s.nectar.auckland.ac.nz"%[sto_index,suffix],           # storage name
         "ntr-sto%02d-%s.nectar.auckland.ac.nz"%[sto_index,suffix]        # ntr- storage name
       ]
       if suffix == 'p'
         aliases << "akld2%su%02d.nectar.auckland.ac.nz"%[rack,u,suffix] # full name, less the suffix for the -p only
         aliases << "%su%02d.nectar.auckland.ac.nz"%[rack,u,suffix]       # short name, less the suffix for the -p only
         aliases << "sto%02d.nectar.auckland.ac.nz"%[sto_index]           # storage name, less the suffix for the -p only
         aliases << "ntr-sto%02d.nectar.auckland.ac.nz"%[sto_index]           # storage name, less the suffix for the -p only
       end
       puts "#{hn}: Aliases #{aliases}" if dry_run
       @infoblox.set_host_aliases(hostname: hn, alias_fqdn: aliases ) unless dry_run
       puts if dry_run
     end
   end
 end
end

# Cnames are hard to work with, so use ALIASES instead.
def drop_cnames
  return # done
  [
  ].each do |cn|
     @infoblox.delete_cname(cname: cn)
  end
end

def add_mytardis_test_host
  @infoblox.create_host_record(hostname: 'test-mytardis.nectar.auckland.ac.nz', ip_address:  '130.216.218.238')
  sleep(15)
  print_ip_record(ip: '130.216.218.238', assigned_only: false)
end

@infoblox = InfoBlox.new()

#@infoblox.txt_record(txt_name: '_acme-challenge.hdsheep.cer.auckland.ac.nz', text: 'xxxxxxxxxxxxxxxxxxxx')
#fix_misc(dry_run: false)
#sleep 15

#print_suffix_net(suffix: 'nfs')

#add_mytardis_test_host

#dump_net(base_net: '130.216.216.0', mask_bits: 23, assigned_only: true)
#dump_net(base_net: '130.216.218.0', mask_bits: 23, assigned_only: true)

#print_rack_nets(rack: 'h18')
#dump_external_nets
#dump_internal_nets

#add_new_dell_2021_purchase1_2(dry_run: false)
#add_new_dell_2021_purchase1_2_sto(dry_run: false)
#add_new_dell_2021_purchase3(dry_run: false)

#puts get_host_ref(hostname: 'akld2h15u03-p.nectar.auckland.ac.nz') # host A record
#puts get_host_ref(hostname: 'sto16.nectar.auckalnd.ac.nz.nectar.auckland.ac.nz') # IPAM ALIAS throws exception

#@infoblox.set_host_aliases(hostname: 'akld2h15u03-p.nectar.auckland.ac.nz', alias_fqdn: 'sto16')
#@infoblox.add_host_aliases(hostname: 'akld2h15u03-p.nectar.auckland.ac.nz', 
#                            alias_fqdn: [ 'h15u03-p.nectar.auckland.ac.nz', 
#                                           'sto16.nectar.auckland.ac.nz', 
#                                           'ntr-sto16.nectar.auckland.ac.nz', 
#                                           'akld2h15u03.nectar.auckland.ac.nz', 
#                                           'h15u03.nectar.auckland.ac.nz'
#                                         ]
#                          )
#load_cnames
#fix_new_dell_2021_purchase1_2_3(dry_run: false)
#fix_misc(dry_run: false)
#fix_new_dell_2021_sto_nodes(dry_run: false)
#exit 0

#drop_cnames
#sleep(15)
#load_cnames if @reverse_cnames.nil?
#@reverse_cnames.each do |rcn, cnames|
#  puts "#{rcn} CNAMES: #{cnames}"
#end
#exit 0


#add_missing_ceph_nodes
#add_new_dell_r620s
#cad01_fixup
#sto_fix
