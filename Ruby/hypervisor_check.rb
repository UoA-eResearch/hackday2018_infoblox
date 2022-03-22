#!/usr/local/bin/ruby
require_relative 'infoblox.rb'

# Hacked up script, for a one off job of correcting IPAM records.
# There are lots of inconsistent host name usage in IPAM and in the server /etc/hosts
# There are also lots of missing entries in IPAM

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
    'v12'=> IPv4.new('172.31.88.0', 26), # vlan12..15 out of band segmenting this subnet due to switch bug
    'v13'=> IPv4.new('172.31.88.64', 26), # vlan12..15 out of band segmenting this subnet due to switch bug
    'v14'=> IPv4.new('172.31.88.128', 26), # vlan12..15 out of band segmenting this subnet due to switch bug
    'v15'=> IPv4.new('172.31.88.192', 26), # vlan12..15 out of band segmenting this subnet due to switch bug
    'p'=> IPv4.new('10.31.80.0', 22),   # vlan20 hardware provisioning network
    'api'=> IPv4.new('10.31.84.0', 22), # vlan40 cloud API network
    'uc'=> IPv4.new('10.31.100.0', 22), # vlan41 Undercloud API network
    'ceph'=> IPv4.new('10.31.88.0', 22),# vlan50 Ceph Storage network
    'enfs'=> IPv4.new('10.31.96.0', 22),# vlan51 External VMs connecting to NFS gateway for CephFS
    'infs'=> IPv4.new('10.31.104.0', 22),#vlan52 Internal VMs connectinog to NFS gateway for CephFS
    'nfs'=> IPv4.new('10.31.108.0', 22),# vlan53 NFS Servers for CephFS
    'repl'=> IPv4.new('10.31.92.0', 22),# vlan60 Ceph backend replication network
    'rados'=> IPv4.new('10.31.60.0', 22),# vlan61 Rados Private network
    'ovn' => IPv4.new('10.241.128.0', 20)# vlan100 OVN Nectar wide net
  }
end

# map to base address. These are legacy IP addresses, which are wrong for their rack
@cop_index = {
  'cop01' => '0.0.0.128',
  'cop02' => '0.0.0.129',
  'cop03' => '0.0.0.130',
  'cop04' => '0.0.0.131',
  'cop05' => '0.0.0.132',
  'cop06' => '0.0.0.133',
  'cop07' => '0.0.0.134',
  'cop08' => '0.0.0.135',
  'cop09' => '0.0.0.136',
  'cop10' => '0.0.0.137',
  'cop11' => '0.0.0.138',
  'adm01' => '0.0.0.31',
  'adm02' => '0.0.0.32',
}
# map to base address. These are legacy IP addresses, which are wrong for their rack
@sto_index = {
  'sto01' => '0.0.0.64',
  'sto02' => '0.0.0.65',
  'sto03' => '0.0.0.66',
  'sto04' => '0.0.0.67',
  'sto05' => '0.0.0.68',
  'sto06' => '0.0.0.69',
  'sto07' => '0.0.0.70',
  'sto08' => '0.0.0.71',
  'sto09' => '0.0.0.72',
  'sto10' => '0.0.0.73',
  'sto11' => '0.0.0.74',
  'sto12' => '0.0.0.75',
  'sto13' => '0.0.0.76',
  'sto14' => '0.0.0.77',
}
# Map to sto numbering. Adding stoXX shortcuts for the later storage nodes. 
# The shortcuts wont be the default hostname though, as that has to match the monitor's idea of the hostname.
@new_sto_index = {
  'h15u01' => 'sto15',
  'h15u03' => 'sto16',
  'h15u05' => 'sto17',
  'h15u07' => 'sto21',
  'h15u09' => 'sto22',
  'i15u01' => 'sto18',
  'i15u03' => 'sto19',
  'i15u05' => 'sto20',
  'i15u07' => 'sto23',
  'i15u09' => 'sto24',
}

# Create a host record, from the arguments, and per network rules.
# Ugly bit of code.
def gen_hostrecord(host:, rack:, u:, net:, ip: nil, extra_aliases: [], switch: false, **_ignore)
  set_rack_ip_offsets
  set_subnets
  rack.downcase!
  if u.is_a?(String)
    u_str = u
    u = ( /\A\D.*\z/ =~ u ? 0 : u.to_i )
  else
    u_str = "%02d"%u
  end
  aliases = []
  # puts "#{host} #{rack} #{u} #{net}"
  #
  # Legacy Cop node names and legacy adm nodes
  if @cop_index.key?(host)
    if net == 'api'  # Want the default hostname to be on this interface
      hostname = "ntr-#{host}.nectar.auckland.ac.nz"              # ntr-copXX
      aliases = [
        "#{host}",                       # copXX
        "akld2#{rack}u#{u_str}",         # akld2h18uXX
        "#{rack}u#{u_str}",              # h18uXX
        "ntr-#{host}-#{net}",            # ntr-copXX-api
        "#{host}-#{net}",                # copXX-api
        "akld2#{rack}u#{u_str}-#{net}",  # akld2h18uXX-api
        "#{rack}u#{u_str}-#{net}",       # h18uXX-api
      ]
      extra_aliases.each do |ea|
        aliases << ea unless aliases.include?(ea)
        aliases << "#{ea}-#{net}" unless aliases.include?("#{ea}-#{net}")
      end
    else
      hostname = "ntr-#{host}-#{net}.nectar.auckland.ac.nz"       # ntr-copXX-net
      aliases = [
        "#{host}-#{net}",                # copXX-net
        "akld2#{rack}u#{u_str}-#{net}",  # akld2h18uXX-net
        "#{rack}u#{u_str}-#{net}"        # h18uXX-net
      ]
      extra_aliases.each do |ea|
        aliases << "#{ea}-#{net}" unless aliases.include?("#{ea}-#{net}")
      end
    end
    ip ||= ( @ip_subnet[net] + IPv4.new(@cop_index[host]).to_i ).to_s
  #
  # Legacy storage node naming
  elsif @sto_index.key?(host) 
    if net == 'ceph'  # Want the default hostname to be on this interface
      hostname = "ntr-#{host}.nectar.auckland.ac.nz"              # ntr-stoXX
      aliases = [ 
        "akld2#{rack}u#{u_str}",         # akld2h18uXX
        "#{rack}u#{u_str}",              # h18uXX
        "ntr-#{host}-#{net}",            # ntr-stoXX-ceph
        "#{host}-#{net}",                # stoXX-ceph
        "akld2#{rack}u#{u_str}-#{net}",  # akld2h18uXX-ceph
        "#{rack}u#{u_str}-#{net}",       # h18uXX-ceph
      ]  
      extra_aliases.each do |ea|
        aliases << ea unless aliases.include?(ea)
        aliases << "#{ea}-#{net}" unless aliases.include?("#{ea}-#{net}")
      end
    else
      hostname = "ntr-#{host}-#{net}.nectar.auckland.ac.nz"       # ntr-stoXX-net
      aliases = [ 
        "#{host}-#{net}",                # stoXX-net
        "akld2#{rack}u#{u_str}-#{net}",  # akld2h18uXX-net
        "#{rack}u#{u_str}-#{net}",       # h18uXX-net
      ]  
      extra_aliases.each do |ea|
        aliases << "#{ea}-#{net}" unless aliases.include?("#{ea}-#{net}")
      end
    end
    ip ||= (@ip_subnet[net] + IPv4.new(@sto_index[host]).to_i ).to_s
  #
  # new storage node naming, with legacy aliases
  elsif @new_sto_index.key?(host)
    if net == 'ceph'  # Want the default hostname to be on this interface
      hostname = "akld2#{rack}u#{u_str}.nectar.auckland.ac.nz"# akld2h18uXX
      aliases = [
        "ntr-#{@new_sto_index[host]}",       # ntr-stoXX
        "#{@new_sto_index[host]}",           # stoXX
        "#{rack}u#{u_str}",                  # h18uXX
        "ntr-#{@new_sto_index[host]}-#{net}",# ntr-stoXX-ceph
        "#{@new_sto_index[host]}-#{net}",    # stoXX-ceph
        "akld2#{rack}u#{u_str}-#{net}",      # akld2h18uXX-ceph
        "#{rack}u#{u_str}-#{net}",           # h18uXX-ceph
      ]  
      extra_aliases.each do |ea|
        aliases << ea unless aliases.include?(ea)
        aliases << "#{ea}-#{net}" unless aliases.include?("#{ea}-#{net}")
      end
    else
      hostname = "akld2#{rack}u#{u_str}-#{net}.nectar.auckland.ac.nz"  # akld2h18uXX-net
      aliases = [ 
        "ntr-#{@new_sto_index[host]}-#{net}", # ntr-stoXX-net
        "#{@new_sto_index[host]}-#{net}",     # stoXX-net
        "#{rack}u#{u_str}-#{net}",            # h18uXX-net
      ]  
      extra_aliases.each do |ea|
        aliases << "#{ea}-#{net}" unless aliases.include?("#{ea}-#{net}")
      end
    end
    ip ||= (@ip_subnet[net] + @ip_offset[rack] + u).to_s
  #
  # All other hosts should be named by rack and u
  elsif switch
    if net == 'm'  # Want the default hostname to be on this interface
      hostname = "akld2#{rack}x#{u_str}.nectar.auckland.ac.nz"# akld2h18xXX
      aliases = [
        "#{rack}x#{u_str}",              # h18xXX
        "akld2#{rack}x#{u_str}-#{net}",  # akld2h18xXX-api
        "#{rack}x#{u_str}-#{net}",       # h18xXX-api
      ]
      # Add in extra aliases
      extra_aliases.each do |ea|
        aliases << ea unless aliases.include?(ea)
        aliases << "#{ea}-#{net}" unless aliases.include?("#{ea}-#{net}")
      end
    else
      hostname = "akld2#{rack}x#{u_str}-#{net}.nectar.auckland.ac.nz"  # akld2h18uXX-net
      aliases = [
        "#{rack}x#{u_str}-#{net}"        # h18xXX-net
      ]
      # Add in extra aliases
      extra_aliases.each do |ea|
        aliases << "#{ea}-#{net}" unless aliases.include?("#{ea}-#{net}")
      end
    end
    ip ||= (@ip_subnet[net] + @ip_offset[rack] + u).to_s
  else
    if net == 'api'  # Want the default hostname to be on this interface
      hostname = "akld2#{rack}u#{u_str}.nectar.auckland.ac.nz"# akld2h18uXX
      aliases = [
        "#{rack}u#{u_str}",              # h18uXX
        "akld2#{rack}u#{u_str}-#{net}",  # akld2h18uXX-api
        "#{rack}u#{u_str}-#{net}",       # h18uXX-api
      ]
      extra_aliases.each do |ea|
        aliases << ea unless aliases.include?(ea)
        aliases << "#{ea}-#{net}" unless aliases.include?("#{ea}-#{net}")
      end
    else
      hostname = "akld2#{rack}u#{u_str}-#{net}.nectar.auckland.ac.nz"  # akld2h18uXX-net
      aliases = [
        "#{rack}u#{u_str}-#{net}"        # h18uXX-net
      ]
      extra_aliases.each do |ea|
        aliases << "#{ea}-#{net}" unless aliases.include?("#{ea}-#{net}")
      end
    end
    ip ||= (@ip_subnet[net] + @ip_offset[rack] + u).to_s
  end
  
    
  return { hostname: hostname, ip: ip, aliases: aliases, cnames: [] }
end

# Create the @host_record Array (of host records), so we can iterate across all hosts.
# Hacked up, for a one off job of cleaning up IPAM
def gen_host_records()
  @host_record = []
  hosts = [
    { host: 'b15u22', rack: 'B15', u: '22', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'b15u24', rack: 'B15', u: '24', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'b15u26', rack: 'B15', u: '26', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'b15u28', rack: 'B15', u: '28', group: [ 'm', 'p',  'api', 'ceph'  ] },
    
    { host: 'cop01', rack: 'H18', u: '24', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'cop02', rack: 'H18', u: '25', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'cop03', rack: 'H18', u: '26', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'cop04', rack: 'I18', u: '23', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'cop05', rack: 'I18', u: '24', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'cop06', rack: 'I18', u: '25', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'cop07', rack: 'I18', u: '26', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'cop08', rack: 'H18', u: '44', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'cop09', rack: 'H18', u: '27', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'cop10', rack: 'I18', u: '27', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'cop11', rack: 'H18', u: '28', group: [ 'm', 'p',  'api', 'ceph'  ] },
    
    { host: 'd18u02', rack: 'D18', u: '02', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'd18u03', rack: 'D18', u: '03', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'd18u04', rack: 'D18', u: '04', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'd18u05', rack: 'D18', u: '05', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'd18u06', rack: 'D18', u: '06', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'd18u07', rack: 'D18', u: '07', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'd18u08', rack: 'D18', u: '08', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'd18u09', rack: 'D18', u: '09', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'd18u10', rack: 'D18', u: '10', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'd18u11', rack: 'D18', u: '11', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'd18u12', rack: 'D18', u: '12', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'd18u13', rack: 'D18', u: '13', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'd18u14', rack: 'D18', u: '14', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'd18u15', rack: 'D18', u: '15', group: [ 'm', 'p',  'api', 'ceph'  ] },
    # GPU
    { host: 'd18u16', rack: 'D18', u: '16', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'd18u18', rack: 'D18', u: '18', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'd18u22', rack: 'D18', u: '22', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'd18u24', rack: 'D18', u: '24', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'd18u26', rack: 'D18', u: '26', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'd18u28', rack: 'D18', u: '28', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'd18u30', rack: 'D18', u: '30', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'd18u32', rack: 'D18', u: '32', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'd18u34', rack: 'D18', u: '34', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'd18u36', rack: 'D18', u: '36', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'd18u38', rack: 'D18', u: '38', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'd18u40', rack: 'D18', u: '40', group: [ 'm', 'p',  'api', 'ceph'  ] },
    
    { host: 'e18u01', rack: 'E18', u: '01', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u02', rack: 'E18', u: '02', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u03', rack: 'E18', u: '03', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u04', rack: 'E18', u: '04', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u05', rack: 'E18', u: '05', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u06', rack: 'E18', u: '06', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u07', rack: 'E18', u: '07', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u08', rack: 'E18', u: '08', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u09', rack: 'E18', u: '09', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u10', rack: 'E18', u: '10', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u11', rack: 'E18', u: '11', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u12', rack: 'E18', u: '12', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u13', rack: 'E18', u: '13', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u14', rack: 'E18', u: '14', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u15', rack: 'E18', u: '15', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u16', rack: 'E18', u: '16', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u17', rack: 'E18', u: '17', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u18', rack: 'E18', u: '18', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u19', rack: 'E18', u: '19', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u20', rack: 'E18', u: '20', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u23', rack: 'E18', u: '23', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u24', rack: 'E18', u: '24', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u25', rack: 'E18', u: '25', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u26', rack: 'E18', u: '26', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u27', rack: 'E18', u: '27', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u28', rack: 'E18', u: '28', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u29', rack: 'E18', u: '29', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u30', rack: 'E18', u: '30', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u31', rack: 'E18', u: '31', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u32', rack: 'E18', u: '32', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u33', rack: 'E18', u: '33', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u34', rack: 'E18', u: '34', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u35', rack: 'E18', u: '35', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u36', rack: 'E18', u: '36', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u37', rack: 'E18', u: '37', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u38', rack: 'E18', u: '38', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u39', rack: 'E18', u: '39', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u40', rack: 'E18', u: '40', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u41', rack: 'E18', u: '41', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'e18u42', rack: 'E18', u: '42', group: [ 'm', 'p',  'api', 'ceph'  ] },
    
    { host: 'h15u23', rack: 'H15', u: '23', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'h15u24', rack: 'H15', u: '24', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'h15u25', rack: 'H15', u: '25', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'h15u26', rack: 'H15', u: '26', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'h15u27', rack: 'H15', u: '27', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'h15u28', rack: 'H15', u: '28', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'h15u35', rack: 'H15', u: '35', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'h15u39', rack: 'H15', u: '39', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'h15u40', rack: 'H15', u: '40', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'h15u41', rack: 'H15', u: '41', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'h15u42', rack: 'H15', u: '42', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'h15u43', rack: 'H15', u: '43', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'h15u44', rack: 'H15', u: '44', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'h15u45', rack: 'H15', u: '45', group: [ 'm', 'p',  'api', 'ceph'  ] },

    { host: 'i15u23', rack: 'I15', u: '23', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'i15u24', rack: 'I15', u: '24', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'i15u25', rack: 'I15', u: '25', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'i15u26', rack: 'I15', u: '26', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'i15u27', rack: 'I15', u: '27', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'i15u28', rack: 'I15', u: '28', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'i15u39', rack: 'I15', u: '39', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'i15u40', rack: 'I15', u: '40', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'i15u41', rack: 'I15', u: '41', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'i15u42', rack: 'I15', u: '42', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'i15u43', rack: 'I15', u: '43', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'i15u44', rack: 'I15', u: '44', group: [ 'm', 'p',  'api', 'ceph'  ] },
    { host: 'i15u45', rack: 'I15', u: '45', group: [ 'm', 'p',  'api', 'ceph'  ] },
    
    # Storage
    { host: 'h15u01', rack: 'H15', u: '01', group: [ 'm', 'p',   'ceph',  'repl'  ] },
    { host: 'h15u03', rack: 'H15', u: '03', group: [ 'm', 'p',   'ceph',  'repl'  ] },
    { host: 'h15u05', rack: 'H15', u: '05', group: [ 'm', 'p',   'ceph',  'repl'  ] },
    { host: 'h15u07', rack: 'H15', u: '07', group: [ 'm', 'p',   'ceph',  'repl'  ] },
    { host: 'h15u09', rack: 'H15', u: '09', group: [ 'm', 'p',   'ceph',  'repl'  ] },
    { host: 'i15u01', rack: 'I15', u: '01', group: [ 'm', 'p',   'ceph',  'repl'  ] },
    { host: 'i15u03', rack: 'I15', u: '03', group: [ 'm', 'p',   'ceph',  'repl'  ] },
    { host: 'i15u05', rack: 'I15', u: '05', group: [ 'm', 'p',   'ceph',  'repl'  ] },
    { host: 'i15u07', rack: 'I15', u: '07', group: [ 'm', 'p',   'ceph',  'repl'  ] },
    { host: 'i15u09', rack: 'I15', u: '09', group: [ 'm', 'p',   'ceph',  'repl'  ] }, 
    { host: 'sto01', rack: 'H18', u: '01', group: [ 'm', 'p',   'ceph',  'repl'  ] },
    { host: 'sto02', rack: 'H18', u: '03', group: [ 'm', 'p',   'ceph',  'repl'  ] },
    { host: 'sto03', rack: 'H18', u: '05', group: [ 'm', 'p',   'ceph',  'repl'  ] },
    { host: 'sto04', rack: 'H18', u: '07', group: [ 'm', 'p',   'ceph',  'repl'  ] },
    { host: 'sto05', rack: 'I18', u: '01', group: [ 'm', 'p',   'ceph',  'repl'  ] },
    { host: 'sto06', rack: 'I18', u: '03', group: [ 'm', 'p',   'ceph',  'repl'  ] },
    { host: 'sto07', rack: 'I18', u: '05', group: [ 'm', 'p',   'ceph',  'repl'  ] },
    { host: 'sto08', rack: 'I18', u: '07', group: [ 'm', 'p',   'ceph',  'repl'  ] },
    { host: 'sto09', rack: 'H18', u: '09', group: [ 'm', 'p',   'ceph',  'repl'  ] },
    { host: 'sto10', rack: 'I18', u: '09', group: [ 'm', 'p',   'ceph',  'repl'  ] },
    { host: 'sto11', rack: 'H18', u: '11', group: [ 'm', 'p',   'ceph',  'repl'  ] },
    { host: 'sto12', rack: 'I18', u: '11', group: [ 'm', 'p',   'ceph',  'repl'  ] },
    { host: 'sto13', rack: 'H18', u: '13', group: [ 'm', 'p',   'ceph',  'repl'  ] },
    { host: 'sto14', rack: 'I18', u: '13', group: [ 'm', 'p',   'ceph',  'repl'  ] },
    
    # Undercloud
    { host: 'adm01', rack: 'H18', u: '17', group: ['m','p'] },
    { host: 'adm02', rack: 'I18', u: '17', group: ['m','p'] },
    { host: 'uc01', rack: 'H18', u: '18', group: ['m', 'p', 'uc'], extra_aliases: [ 'uc01'] },
    { host: 'uc02', rack: 'I18', u: '18', group: ['m', 'p', 'uc'], extra_aliases: [ 'uc02'] },
    { host: 'uc03', rack: 'H18', u: '19', group: ['m', 'p', 'uc'], extra_aliases: [ 'uc03'] },
    { host: 'i15u34', rack: 'I15', u: '34', group: ['m','p', 'uc'], extra_aliases: [ 'uc04'] },
    { host: 'b18u25', rack: 'B18', u: '25', group: ['m', 'm2', 'p', 'api', 'ceph', 'uc']  },
    
    # Dell switches S3048 and S4048 with mgmt MAC bug 
    { host: 'h18x40', rack: 'H18', u: '40', group: [['m', '172.31.80.1'],
                                                    ['m2','172.31.84.1'],
                                                    ['v12', '172.31.88.1'],
                                                    ['v13', '172.31.88.65'],
                                                    ['v14', '172.31.88.129'],
                                                    ['v15', '172.31.88.193']
                                                   ],
                                            extra_aliases: [ 'x1', 'ntr-x1'], switch: true },
    { host: 'h18x39', rack: 'H18', u: '39', group: [['m2', '172.31.87.2'], ['m', '172.31.88.2']], extra_aliases: [ 'x2', 'ntr-x2'], switch: true },
    { host: 'i18x37', rack: 'I18', u: '37', group: [['m2', '172.31.87.3'], ['m', '172.31.88.3']], extra_aliases: [ 'x3', 'ntr-x3'], switch: true  },
    { host: 'h18x31', rack: 'H18', u: '31', group: [['m2', '172.31.87.4'], ['m', '172.31.88.4']], extra_aliases: [ 'x4', 'ntr-x4'], switch: true  },
    { host: 'i18x31', rack: 'I18', u: '31', group: [['m2', '172.31.87.5'], ['m', '172.31.88.5']], extra_aliases: [ 'x5', 'ntr-x5'], switch: true  },
    { host: 'h18x30', rack: 'H18', u: '30', group: [['m2', '172.31.87.6'], ['m', '172.31.88.6']], extra_aliases: [ 'x6', 'ntr-x6'], switch: true  },
    { host: 'i18x30', rack: 'I18', u: '30', group: [['m2', '172.31.87.7'], ['m', '172.31.88.7']], extra_aliases: [ 'x7', 'ntr-x7'], switch: true  },
    { host: 'd18x42', rack: 'D18', u: '42', group: [['m2', '172.31.87.8'], ['m', '172.31.88.8']], extra_aliases: [ 'x8', 'ntr-x8'], switch: true  },
    { host: 'd18x43', rack: 'D18', u: '43', group: [['m2', '172.31.87.9'], ['m', '172.31.88.9']], extra_aliases: [ 'x9', 'ntr-x9'], switch: true  },
    # Dell S5148F
    { host: 'e18x21', rack: 'E18', u: '21', group: [['m2', '172.31.87.10'], ['m', '172.31.88.10']], extra_aliases: [ 'x10', 'ntr-x10'], switch: true  },
    { host: 'e18x22', rack: 'E18', u: '22', group: [['m2', '172.31.87.11'], ['m', '172.31.88.11']], extra_aliases: [ 'x11', 'ntr-x11'], switch: true  },
    # IBM Switches
    { host: 'e18xb4', rack: 'E18', u: 'b4', group: [['m2', '172.31.87.12'], ['m', '172.31.80.12']], extra_aliases: [ 'x12', 'ntr-x12'], switch: true  },
    { host: 'd18xd4', rack: 'D18', u: 'd4', group: [['m2', '172.31.87.13'], ['m', '172.31.80.13']], extra_aliases: [ 'x13', 'ntr-x13'], switch: true  },
    { host: 'b18x19', rack: 'B18', u: '19', group: [['m2', '172.31.87.16'], ['m', '172.31.80.16']], extra_aliases: [ 'x16', 'ntr-x16'], switch: true  },
    { host: 'b18x20', rack: 'B18', u: '20', group: [['m2', '172.31.87.17'], ['m', '172.31.80.17']], extra_aliases: [ 'x17', 'ntr-x17'], switch: true  },
    { host: 'b18x21', rack: 'B18', u: '21', group: [['m2', '172.31.87.18'], ['m', '172.31.80.18']], extra_aliases: [ 'x18', 'ntr-x18'], switch: true  },
    { host: 'b15x42', rack: 'B15', u: '42', group: [['m2', '172.31.87.19'], ['m', '172.31.80.19']], extra_aliases: [ 'x19', 'ntr-x19'], switch: true  },
    { host: 'b15x41', rack: 'B15', u: '41', group: [['m2', '172.31.87.20'], ['m', '172.31.80.20']], extra_aliases: [ 'x20', 'ntr-x20'], switch: true  },
    # Dell S3048 with mgmt MAC bug V13
    { host: 'h15x33', rack: 'H15', u: '33', group: ['m2', ['m', '172.31.88.66']], extra_aliases: [ 'x23', 'ntr-x23'], switch: true  },
    { host: 'i15x33', rack: 'I15', u: '33', group: ['m2', ['m', '172.31.88.67']], extra_aliases: [ 'x26', 'ntr-x26'], switch: true  },
    # Dell S5248F where traffic passes through switches with Dell bug V14 and V15
    { host: 'h15x30', rack: 'H15', u: '30', group: ['m2', ['m', '172.31.88.130']], extra_aliases: [ 'x21', 'ntr-x21'], switch: true  },
    { host: 'h15x31', rack: 'H15', u: '31', group: ['m2', ['m', '172.31.88.131']], extra_aliases: [ 'x22', 'ntr-x22'], switch: true  },
    { host: 'i15x30', rack: 'I15', u: '30', group: ['m2', ['m', '172.31.88.194']], extra_aliases: [ 'x24', 'ntr-x24'], switch: true  },
    { host: 'i15x31', rack: 'I15', u: '31', group: ['m2', ['m', '172.31.88.195']], extra_aliases: [ 'x25', 'ntr-x25'], switch: true  },
    # Dell S5232F on standard IP addresses
    { host: 'h18x46', rack: 'H18', u: '46', group: ['m', 'm2', ['enfs', '10.31.99.252'], 
                                                               ['infs', '10.31.107.252'], 
                                                               ['nfs', '10.31.111.252']],
                                            extra_aliases: [ 'x27', 'ntr-x27'], switch: true  },
    { host: 'h18x47', rack: 'H18', u: '47', group: ['m', 'm2', ['enfs', '10.31.99.253'], 
                                                               ['infs', '10.31.107.253'], 
                                                               ['nfs', '10.31.111.253']],
                                            extra_aliases: [ 'x28', 'ntr-x28'], switch: true  },
#    { host: 'router-vip', rack: 'H18', u: '47', group: [ ['enfs', '10.31.99.254'], 
#                                                         ['infs', '10.31.107.254'], 
#                                                         ['nfs', '10.31.111.254']],
#                                           extra_aliases: [ ] },    
  ]
  
  # Iterate through the hosts array, and create an Array of host records.
  hosts.each do |hr|
    hr[:group].each  do |net_entry|
      if net_entry.is_a? Array
        net = net_entry[0]
        ip = net_entry[1]
      else
        net = net_entry
        ip = nil
      end
      @host_record << gen_hostrecord(net: net, ip: ip, **hr)
    end
  end
  
  host_domain = 'nectar.auckland.ac.nz'
  
  # Build indexes, so we can lookup hosts by hostname, alias or CNAME.
  @host_record_index = {}
  @host_record.each do |hr|
    # puts "hostname: #{hr[:hostname]}, ip: #{hr[:ip]}, aliases: #{hr[:aliases]}"
    @host_record_index[hr[:hostname]] = hr
    hr[:aliases].each do |a|
      @host_record_index["#{a}.#{host_domain}"] = hr
    end
    hr[:cnames].each do |cn|
      @host_record_index[cn] = hr
    end
  end
end

# Sets up the global @reverse_cnames
# @reverse_cnames is an array of host's CNAMEs
def load_cnames
  return unless @reverse_cnames.nil? # already loaded.
   
  @reverse_cnames = {}
  @infoblox.get_cname(domain: 'nectar.auckland.ac.nz') do |cn, host|
    @reverse_cnames[host] ||= []
    @reverse_cnames[host] << cn
  end
end


# Get the IP addresses A records (host records and Aliases), and any CNAMES mapping to the host records
# @param ip [String] IPV4 address we are looking up
# @return [Array] of host records for this IP
def full_host_record(ip:)
  load_cnames
  
  @forward_host_record ||= {}  # Global, as we want to do name lookups.
  return_record = []
  unless( (host_records = @infoblox.get_host_by_ip(ip_address: ip)).nil? )
    host_records.each do |hosts|
      hosts.each do |hn|
        # Assign an empty record, if we haven't seen this host before
        @forward_host_record[hn] ||= { hostname: hn, ip: '', aliases: [], cnames: [] }
        
        # Record the IP. There may be multiple IPs with one hostname.
        @forward_host_record[hn][:ip] = ip
        
        # The hostname might have CNAMES point to it
        unless @reverse_cnames[hn].nil?
          @reverse_cnames[hn].each do |cn| 
            @forward_host_record[hn][:cnames] << cn 
          end
        end
        
        # The hostname may have alternate hostname A records, stored in IPAM as ALIASES
        @infoblox.get_alias(hostname: hn) do |a| 
          short_alias = a.split('.',2)[0]
          @forward_host_record[hn][:aliases] << short_alias
          
          # The ALIASes might have CNAME records pointing to it
          unless @reverse_cnames[a].nil?
            # Record the ALIAS CNAMES against the parent hostname.
            @reverse_cnames[a].each do |cn| 
              @forward_host_record[hn][:cnames] << cn 
            end
          end
        end
        return_record << @forward_host_record[hn]
        
        # Add forward lookup entries for each ALIAS
        host_domain = hn.split('.',2)[1]
        @forward_host_record[hn][:aliases].each do |a|
          @forward_host_record["#{a}.#{host_domain}"] = @forward_host_record[hn]
        end
        
        # Add forward lookup entries for each CNAME
        @forward_host_record[hn][:cnames].each do |cn|
          @forward_host_record[cn] = @forward_host_record[hn]
        end
        
      end
    end
  end
  return return_record
end

# Adds to global @reverse_host_records, for this subnet.
# Side effect of adding to global @forward_host_record 
# @param suffix [String] One of the -m, -p, -api, ... network suffixes (without the leading -)
# @param assigned_only [Boolean] Only interested in IP addresses with host entries
# @return Host records for just this subnet.
def net_by_suffix(suffix:,  assigned_only: false)
  set_subnets
  return net_by_ip_range(base_net: @ip_subnet[suffix].to_s, mask_bits: @ip_subnet[suffix].mask_length, assigned_only: true)
end

# Adds to global @reverse_host_records, for this subnet.
# Side effect of adding to global @forward_host_record 
# @param base_net [String] Network IP address
# @param mask_bits [Integer] Number of bits in mask 
# @param assigned_only [Boolean] Only interested in IP addresses with host entries
# @return Host records for just this subnet.
def net_by_ip_range(base_net: '10.31.80.0', mask_bits: 22, assigned_only: true)  
  net = IPv4.new(base_net, mask_bits)
  @reverse_host_records ||= {} 
  host_records = []

  net.each_ip do |ip|
    rev_record = full_host_record( ip: ip )
    next if assigned_only && (rev_record.nil? || rev_record.empty?)
    @reverse_host_records[ip] = rev_record
    host_records << rev_record
  end
  
  return host_records
end

# Create a cached copy of the existing DNS entries in IPAM
def load_all_subnets
  set_rack_ip_offsets
  set_subnets
  
  @subnet = {}
  @ip_subnet.keys.each do |net|
    @subnet[net] = net_by_suffix(suffix: net)
  end
end

# Compare and fix entries, that we defined above in gen_host_records(),
# with the records stored in IPAM.
# Report instance of:
#   * an IPAM record, with no @host_record entry
#   * @host_record[:hostname] that are ALIAS or CNAME records in IPAM
#   * @host_record that are missing from IPAM (and correct this)
#   * @host_record that have a reverse IP entry, but no hostname entry in IPAM
#   * @host_record[:ip] IP addresses that do not match the IPAM host record IP
def dns_check
  gen_host_records  # These are the hosts we have
  load_all_subnets  # These are the DNS entries
  
  # We want a standard layout, with the hypervisor API entries being 
  @host_record.each do |hr|  # Array of host record Hash's
    hn = hr[:hostname]
    shn = hn.split('.',2)[0]   # Remove the domain
    forward_hr = @forward_host_record[hn] # Find Host Record
    if forward_hr.nil?
      # We have no IPAM entry for this hostname
      if (rhr = @reverse_host_records[hr[:ip]])
        puts "Only Reverse IPAM entry for #{shn}: #{rhr}"
        @infoblox.create_host_record(ip_address:  hr[:ip], hostname: hn, aliases: hr[:aliases])
      else
        puts "No IPAM entry for hostrecord: #{hr}"
        @infoblox.create_host_record(ip_address:  hr[:ip], hostname: hn, aliases: hr[:aliases])
      end
    else
      # We have an IPAM record for this hostname
      if forward_hr[:ip] != hr[:ip]
        puts "IP mismatch #{shn} #{hr[:ip]} != #{forward_hr[:ip]} for IPAM: #{forward_hr}"
      elsif forward_hr[:hostname] != hn
        # Reference must be via ALIASES or CNAMES
        if forward_hr[:aliases].include?(shn)
          puts "Hostname #{shn} is an ALIAS. IPAM: #{forward_hr}"
        elsif forward_hr[:cnames].include?(hn)
          puts "Hostname #{shn} is a CNAME. IPAM: #{forward_hr}"
        end
      end
    end
  end
  
  # We want to find IPAM entries, not matching existing @host_record entries
  @reverse_host_records.each do |ip, ahr| # Hash to array of host records from IPAM, indexed by IP
    ahr.each do |hr| # One IP can have multiple host records, with associated ALIAS and CNAME records
      local_hr = @host_record_index[hr[:hostname]]
      if local_hr.nil?
        puts "No local entry #{hr[:hostname]} for #{hr}"
      end
    end
  end
end

@infoblox = InfoBlox.new
# And do stuff, depending on the results of the last run.

#p full_host_record(ip: '172.31.80.31')

#load_all_subnets
#p @forward_host_record['ntr-cop01-api.nectar.auckland.ac.nz']

#gen_host_records
#@host_record.each do |hr|
#  puts hr
#end
#p @host_record_index['ntr-cop01-p.nectar.auckland.ac.nz']
#p @host_record_index['cop01-p.nectar.auckland.ac.nz']

#dns_check