require_relative 'webbrowser.rb'
require 'json'

conf = JSON.parse(File.read('../conf.json'))

WebBrowser::https_session(host: 'ipam.auckland.ac.nz', verify_cert: false, debug: false) do |wb|
   a = wb.basic_authorization(user: conf['user'], password: conf['password'])
   r = wb.get_page(query: "wapi/v2.5/ipv4address", form_values: {'ip_address'=>'130.216.216.98', 'network_view'=>'default'}, authorization: a)
   puts r
   r = wb.get_page(query: "wapi/v2.5/record:host", form_values: {'name'=>'minty.nectar.auckland.ac.nz'}, authorization: a)
   puts r
end

