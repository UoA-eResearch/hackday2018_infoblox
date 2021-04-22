#!/usr/local/bin/ruby
require 'wikk_webbrowser'
require "wikk_json"
require 'json'

@conf = JSON.parse(File.read( "#{__dir__}/../conf/conf.json" ))

# Get IPAM host record info, from the ip address
def get_host(ip_address:)
  WIKK::WebBrowser.https_session(host: 'ipam.auckland.ac.nz', verify_cert: false, debug: false) do |wb|
     a = wb.basic_authorization(user: @conf['user'], password: @conf['password'])
     r = wb.get_page(query: "wapi/v2.5/ipv4address", form_values: {'ip_address'=>"#{ip_address}", 'network_view'=>'default'}, authorization: a)
     h = JSON.parse(r)
     l = 0
     h.each do |e|
       puts "#{ip_address} #{e['names']}"
       l += e['names'].length
     end
     return l
    # r = wb.get_page(query: "wapi/v2.5/record:host", form_values: {'name'=>'minty.nectar.auckland.ac.nz'}, authorization: a)
   #  puts r
  end
end

# Get the IPAM reference number from the hostname
def get_host_ref(hostname:)
  begin
    WIKK::WebBrowser.https_session(host: 'ipam.auckland.ac.nz', verify_cert: false, debug: false) do |wb|
       a = wb.basic_authorization(user: @conf['user'], password: @conf['password'])
       r = wb.get_page(query: "wapi/v2.5/record:host", form_values: {'name'=>"#{hostname}"}, authorization: a)
       j = JSON.parse(r)
       return j[0]['_ref']
    end
  rescue StandardError => e
    warn "get_host_ref(#{hostname}) #{e}"
    return nil
  end
end


def get_network(network: '130.216.161.0/24')
  fields = 'network,netmask'
  puts "Network dump #{network}"

  WIKK::WebBrowser.https_session(host: 'ipam.auckland.ac.nz', verify_cert: false, debug: false) do |wb|
     a = wb.basic_authorization(user: @conf['user'], password: @conf['password'])
     r = wb.get_page(query: "wapi/v2.5/network", form_values: {'network'=>"#{network}", 'network_view'=>'default', '_return_fields'=>fields}, authorization: a)
     puts r
  end
end

# Create an IPAM entry for the hostname and ip address
def create_host_record(hostname:, ip_address:, dhcp: false)
	payload = {
              "ipv4addrs" => [
                 { 
                   "ipv4addr" => ip_address,
                   "configure_for_dhcp" => dhcp
                 }
                ],
              "name" => hostname
            }.to_j
  begin
  WIKK::WebBrowser.https_session(host: 'ipam.auckland.ac.nz', verify_cert: false, debug: false) do |wb|
     a = wb.basic_authorization(user: @conf['user'], password: @conf['password'])
     r = wb.post_page( query: "wapi/v2.5/record:host?_return_fields=ipv4addrs", 
                       content_type: 'application/json; charset=UTF-8',
                       authorization: a,
                       data: payload 
                     )
     puts r
  end
  rescue StandardError => e
    puts "create_host_record(#{hostname}, #{ip}): #{e}"
  end
end

# Delete an IPAM host record, using IPAM internal ref number
def delete_host_record(ref:)
  begin
    WIKK::WebBrowser.https_session(host: 'ipam.auckland.ac.nz', verify_cert: false, debug: false) do |wb|
       a = wb.basic_authorization(user: @conf['user'], password: @conf['password'])
       r = wb.delete_req( query: "/wapi/v2.5/#{ref}", 
                          authorization: a
                        )
       puts r
    end
  rescue StandardError => e
    puts "delete_host_record(#{ref}): #{e}"
  end
end

def delete_by_hostname(hostname:)
  ref = get_host_ref( hostname: hostname )
  unless ref.nil?
    puts "deleting #{ref}"
    delete_host_record(ref: ref)
  end
end

# Create entries in IPAM for all nectar VMs on external networks
def create_hostnames
  # Classic network 1 130.216.216.0/23
  create_host_record(hostname: 'classic-net-1.nectar.auckland.ac.nz', ip_address: '130.216.216.0')
  create_host_record(hostname: 'classic-net-1-dhcp.nectar.auckland.ac.nz', ip_address: '130.216.216.1')
  create_host_record(hostname: 'classic-net-1-r1.nectar.auckland.ac.nz', ip_address: '130.216.217.252')
  create_host_record(hostname: 'classic-net-1-r2.nectar.auckland.ac.nz', ip_address: '130.216.217.253')
  create_host_record(hostname: 'classic-net-1-r.nectar.auckland.ac.nz', ip_address: '130.216.217.254')
  create_host_record(hostname: 'classic-net-1-bc.nectar.auckland.ac.nz', ip_address: '130.216.217.255')
  
  # Classic network 2 130.216.254.0/24
  create_host_record(hostname: 'classic-net-2.nectar.auckland.ac.nz', ip_address: '130.216.254.0')
  create_host_record(hostname: 'classic-net-2-dhcp.nectar.auckland.ac.nz', ip_address: '130.216.254.1')
  create_host_record(hostname: 'classic-net-2-r1.nectar.auckland.ac.nz', ip_address: '130.216.254.252')
  create_host_record(hostname: 'classic-net-2-r2.nectar.auckland.ac.nz', ip_address: '130.216.254.253')
  create_host_record(hostname: 'classic-net-2-r.nectar.auckland.ac.nz', ip_address: '130.216.254.254')
  create_host_record(hostname: 'classic-net-2-bc.nectar.auckland.ac.nz', ip_address: '130.216.254.255')

  # Mido net 130.216.218.0/23
  create_host_record(hostname: 'dynamic-net-1.nectar.auckland.ac.nz', ip_address: '130.216.218.255')
  create_host_record(hostname: 'dynamic-net-1-r.nectar.auckland.ac.nz', ip_address: '130.216.219.254')
  create_host_record(hostname: 'dynamic-net-1-bc.nectar.auckland.ac.nz', ip_address: '130.216.219.255')

  [216,217,254,218,219].each do |r|
    (0..255).each do |i|
      ip = "130.216.#{r}.#{i}"
      if get_host(ip_address: ip) == 0
        hostname = "evm-#{r}-#{i}.nectar.auckland.ac.nz"
    
        puts "Create #{ip} #{hostname}"
        create_host_record(hostname: hostname, ip_address: ip)
    
      end
    end
  end
end

# Dump hostnames allocated on internal Nectar/VMWare research VM nets
def dump_int
  [189,161].each do |r|
    (0..255).each do |i|
      ip = "130.216.#{r}.#{i}"
      get_host(ip_address: ip) 
    end
  end
end

# Dump hostnames allocated in IPAM on external Nectar networks
def dump_ext
  [216,217,254,218,219].each do |r|
    (0..255).each do |i|
      ip = "130.216.#{r}.#{i}"
      get_host(ip_address: ip) 
    end
  end
end

# Delete the IPAM entry for this hostname


#dump_ext
#dump_int