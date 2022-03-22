#!/usr/local/bin/ruby
require 'wikk_webbrowser'
require "wikk_json"
require 'json'
require_relative 'ipv4.rb'

class InfoBlox
  def initialize
    @conf = JSON.parse(File.read( "#{__dir__}/../conf/conf.json" ))
  end

  # Cnames are a bit horrible to work with. Fetching them, requires a search.
  # The name field is the CNAME
  # the canonical field is the A records hostname, that the CNAME points to
  #
  # Searching by CNAME, with name~ (regular expression), gave one less record than searching by A record hostname with canonical~
  # as there is a record in the auckland.ac.nz domain pointing to a nectar.auckland.ac.nz record
  def get_cname(domain:)
    WIKK::WebBrowser.https_session(host: @conf['host'], verify_cert: false, debug: false) do |wb|
      a = wb.basic_authorization(user: @conf['user'], password: @conf['password'])
      r = wb.get_page(query: "wapi/v2.5/record:cname", form_values: { "name~"=>domain, '_max_results' => 5000,'_return_fields'=>'name,canonical'}, authorization: a)
      h = JSON.parse(r)
      # name is the cname
      # cononical is the hostname of the actual A record
      h.each { |cn| yield cn['name'], cn['canonical'] } if block_given?
    end
  end

  # Get IPAM host record info, from the ip address
  # @param ip_address [String] ip address to lookup.
  # @yield hostname [String] if a block is given
  # @return host_record [Array] of hosts entries, if no block is given
  def get_host_by_ip(ip_address:)
    host_record = []
    WIKK::WebBrowser.https_session(host: @conf['host'], verify_cert: false, debug: false) do |wb|
       a = wb.basic_authorization(user: @conf['user'], password: @conf['password'])
       r = wb.get_page(query: "wapi/v2.5/ipv4address", form_values: {'ip_address'=>"#{ip_address}", 'network_view'=>'default', '_return_fields'=>'names,network,ip_address'}, authorization: a)
       h = JSON.parse(r)
       h.each do |e|
        if block_given?
          yield e['names']
        else # Collect them all, to return at the end
          host_record << e['names'] unless e['names'].empty?
        end
       end
    end
    return host_record
  end

  # Get the IPAM reference number from the hostname
  def get_host_ref(hostname:)
    begin
      WIKK::WebBrowser.https_session(host: @conf['host'], verify_cert: false, debug: false) do |wb|
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

    WIKK::WebBrowser.https_session(host: @conf['host'], verify_cert: false, debug: false) do |wb|
       a = wb.basic_authorization(user: @conf['user'], password: @conf['password'])
       r = wb.get_page(query: "wapi/v2.5/network", form_values: {'network'=>"#{network}", 'network_view'=>'default', '_return_fields'=>fields}, authorization: a)
       puts r
    end
  end

  # Create an IPAM entry for the hostname and ip address
  # Nb. You can create two host entries on the same IP address, or use ALIASES
  # ALIASES will create multiple A records, but not create a reverse lookup entry
  # Multple host entries, on the same IP, will result in multiple A and reverse lookup entries
  # CNAMES create a CNAME entry, which is a hostname to hostname mapping.
  def create_host_record(hostname:, ip_address:, aliases: [], dhcp: false)
  	payload = {
                "ipv4addrs" => [
                  { 
                    "ipv4addr" => ip_address,
                    "configure_for_dhcp" => dhcp
                  }
                ],
                "name" => hostname
              }
    payload["aliases"] = aliases unless aliases.nil? || aliases.empty?
    

    begin
      WIKK::WebBrowser.https_session(host: @conf['host'], verify_cert: false, debug: false) do |wb|
        a = wb.basic_authorization(user: @conf['user'], password: @conf['password'])
        r = wb.post_page( query: "wapi/v2.5/record:host?_return_fields=ipv4addrs", 
                          content_type: 'application/json; charset=UTF-8',
                          authorization: a,
                          data: payload.to_j
                        )
        puts r
      end
    rescue StandardError => e
      backtrace = e.backtrace[0].split(":")
      puts "create_host_record(#{hostname}, #{ip_address}): (#{backtrace[-3]} #{backtrace[-2]}) #{e}"
    end
  end

  # Delete an IPAM host record, using IPAM internal ref number
  def delete_host_record(ref:)
    begin
      WIKK::WebBrowser.https_session(host: @conf['host'], verify_cert: false, debug: false) do |wb|
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
    #puts "Getting host ref for #{hostname}"
    ref = get_host_ref( hostname: hostname )
    unless ref.nil?
      puts "deleting #{ref}"
      delete_host_record(ref: ref)
    end
  end

  # Implements IBA REST API call to add an alias to IBA host record.
  # NB. Overwrites the existing ALIAS, with this new array of ALIASES
  # @param hostname [String] host record name in FQDN
  # @param alias_fqdn [String|Array] host record name in FQDN
  def set_host_aliases(hostname:, alias_fqdn:)
    ref = get_host_ref( hostname: hostname )
    aliases = alias_fqdn.kind_of?(Array) ? alias_fqdn : [ alias_fqdn ]
    
    # remove the hosts domain from the aliases
    t = hostname.split('.',2)
    aliases.map! { |a| a.gsub(".#{t[1]}", '') } if t.length == 2
  
  	payload = {
                "aliases" => aliases
              }.to_j
    begin
    WIKK::WebBrowser.https_session(host: @conf['host'], verify_cert: false, debug: false) do |wb|
       a = wb.basic_authorization(user: @conf['user'], password: @conf['password'])
       r = wb.put_req( query: "/wapi/v2.5/#{ref}", 
                         content_type: 'application/json; charset=UTF-8',
                         authorization: a,
                         data: payload 
                       )
       puts r
    end
    rescue StandardError => e
      puts "create_host_record(#{hostname}, #{alias_fqdn}): #{e}"
    end
  end

  # Fetches the host record, and extracts the ALIAS array
  # @yield alias [String]
  # @return aliases [Array]
  def get_alias(hostname:)
    host_record = [{ 'name' => hostname, 'aliases' => [] }]
    WIKK::WebBrowser.https_session(host: @conf['host'], verify_cert: false, debug: false) do |wb|
      a = wb.basic_authorization(user: @conf['user'], password: @conf['password'])
      r = wb.get_page(query: "wapi/v2.5/record:host", form_values: {'name'=>"#{hostname}", '_return_fields'=>'name,aliases'}, authorization: a)
      host_record = JSON.parse(r)

      if block_given?
        host_record.each do |hr|
          unless hr['aliases'].nil?
            hr['aliases'].each do |a|
              yield a
            end
          end
        end
      end
    end
    return host_record[0]['aliases'] # Should check here, to see if there were multiple host records returned.
  end

  # Implements IBA REST API call to add an alias to IBA host record.
  # @param hostname [String] host record name in FQDN
  # @param alias_fqdn [String|Array] host record name in FQDN
  def add_host_aliases(hostname:, alias_fqdn:)
    # Fetch the existing aliases
    current_aliases = get_alias(hostname: hostname)
    current_aliases ||= [] # incase we got a nil response
    
    new_aliases = alias_fqdn.kind_of?(Array) ? alias_fqdn : [ alias_fqdn ]

    have_new_aliases = false # No new aliases so far
    new_aliases.each do |na|
      if ! current_aliases.include?(na) 
        current_aliases << na # This is a new one to add
        have_new_aliases = true
      end
    end
    set_host_aliases(hostname: hostname, alias_fqdn:current_aliases) if have_new_aliases
  end

  # Implements IBA REST API call to add an alias to IBA host record
  # @param hostname [String] host record name in FQDN
  # @param alias_fqdn [String|Array] host record name in FQDN
  def delete_host_aliases(hostname:, alias_fqdn:)
    # Fetch the existing aliases
    current_aliases = get_alias(hostname: hostname)
    current_aliases ||= [] # incase we got a nil response
    
    rm_aliases = alias_fqdn.kind_of?(Array) ? alias_fqdn : [ alias_fqdn ]

    new_aliases = [] # No new aliases so far
    current_aliases.each do |ca|
      if ! rm_aliases.include?(ca) 
        new_aliases << ca
      end
    end
    set_host_aliases(hostname: hostname, alias_fqdn:new_aliases)
  end

  # Implements IBA REST API call to create IBA cname record
  # @param cname [String] canonical name in FQDN format
  # @param hostname [String] the hostname for a CNAME record in FQDN format
  def add_cname(hostname:, cname:)
  	payload = {
                "canonical" => hostname,
                "name" => cname
              }.to_j
    begin
      WIKK::WebBrowser.https_session(host: @conf['host'], verify_cert: false, debug: false) do |wb|
         a = wb.basic_authorization(user: @conf['user'], password: @conf['password'])
         r = wb.post_page( query: "wapi/v2.5/record:cname", 
                           content_type: 'application/json; charset=UTF-8',
                           authorization: a,
                           data: payload 
                         )
         puts r
      end
    rescue StandardError => e
      puts "create_host_record(#{hostname}, #{cname}): #{e}"
    end
  end

  # Get the IPAM reference number from the hostname
  def get_cname_ref(cname:)
    begin
      WIKK::WebBrowser.https_session(host: @conf['host'], verify_cert: false, debug: false) do |wb|
         a = wb.basic_authorization(user: @conf['user'], password: @conf['password'])
         r = wb.get_page(query: "wapi/v2.5/record:cname", form_values: {'name'=>"#{cname}"}, authorization: a)
         j = JSON.parse(r)
         return j[0]['_ref']
      end
    rescue StandardError => e
      warn "get_cname_ref(#{cname}): #{e}"
      return nil
    end
  end

  # Implements IBA REST API call to create IBA cname record
  # @param cname [String] canonical name in FQDN format
  # @param hostname [String] the hostname for a CNAME record in FQDN format
  def delete_cname(cname:)
    cname_ref = get_cname_ref(cname: cname)
    unless cname_ref.nil?
      begin
        WIKK::WebBrowser.https_session(host: @conf['host'], verify_cert: false, debug: false) do |wb|
           a = wb.basic_authorization(user: @conf['user'], password: @conf['password'])
           r = wb.delete_req( query: "/wapi/v2.5/#{cname_ref}", 
                              authorization: a
                            )
           puts r
        end
      rescue StandardError => e
        puts "delete_cname(#{cname}): #{e}"
      end
    end
  end
  
  def txt_record(txt_name:, text:)    
  	payload = {
                "text" => text,
                "name" => txt_name
              }.to_j
    begin
      WIKK::WebBrowser.https_session(host: @conf['host'], verify_cert: false, debug: false) do |wb|
         a = wb.basic_authorization(user: @conf['user'], password: @conf['password'])
         r = wb.post_page( query: "wapi/v2.5/record:txt", 
                           content_type: 'application/json; charset=UTF-8',
                           authorization: a,
                           data: payload 
                         )
         puts r
      end
    rescue StandardError => e
      puts "create_host_record(#{hostname}, #{cname}): #{e}"
    end
  end
end