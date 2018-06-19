require 'net/http'
require 'net/https'
require 'uri'
require 'nokogiri'
require 'base64'

#Code from WIKK WebBrowser class under MIT Lic. https://github.com/wikarekare.

class WebBrowser
  
  class Error < RuntimeError
    attr_accessor :web_return_code
    def initialize(web_return_code:, message:)
      super(message)
      @web_return_code = web_return_code
    end
  end
  

  attr_reader :host
  attr_accessor :session
  attr_accessor :cookies
  attr_reader :page
  attr_accessor :referer
  attr_accessor :debug
  attr_accessor :verify_cert
  attr_accessor :port
  attr_accessor :use_ssl
  

  #Create a WebBrowser instance
  # @param host [String] the host we want to connect to
  # @param port [Fixnum] Optional http server port
  # @param use_ssl [Boolean] Use https, if true
  # @param verify_cert [Boolean] Validate certificate if true (Nb lots of embedded devices have self signed certs, so verify will fail)
  # @return [WebBrowser]
  def initialize(host:, port: nil, use_ssl: false, cookies: nil, verify_cert: true, debug: false)
    @host = host  #Need to do this, as passing nil is different to passing nothing to initialize!
    @cookies = cookies
    @debug = debug
    @use_ssl = use_ssl
    @port = port != nil ? port : ( use_ssl ? 443 : 80 )
    @verify_cert = verify_cert
  end

  #Create a WebBrowser instance, connect to the host via http, and yield the WebBrowser instance.
  #  Automatically closes the http session on returning from the block passed to it.
  # @param host [String] the host we want to connect to
  # @param port [Fixnum] (80) the port the remote web server is running on
  # @param block [Proc] 
  # @yieldparam [WebBrowser] the session descriptor for further calls.
  def self.http_session(host:, port: nil, debug: false, cookies: nil)
    wb = self.new(host: host, port: port, debug: debug, use_ssl: false, cookies: cookies)
    wb.http_session do
      yield wb
    end
  end

  #Create a WebBrowser instance, connect to the host via https, and yield the WebBrowser instance.
  #  Automatically closes the http session on returning from the block passed to it.
  # @param host [String] the host we want to connect to
  # @param port [Fixnum] (443) the port the remote web server is running on
  # @param verify_cert [Boolean] Validate certificate if true (Nb lots of embedded devices have self signed certs, so verify will fail)
  # @param block [Proc] 
  # @yieldparam [WebBrowser] the session descriptor for further calls.
  def self.https_session(host:, port: nil, verify_cert: true, cookies: nil, debug: false)
    wb = self.new(host: host, port: port, cookies: cookies, use_ssl: true, verify_cert: verify_cert, debug: debug)
    wb.http_session do
      yield wb
    end
  end

  #Creating a session for http connection
  #  attached block would then call get or post NET::HTTP calls
  # @param port [Fixnum] Optional http server port
  # @param use_ssl [Boolean] Use https, if true
  # @param verify_cert [Boolean] Validate certificate if true (Nb lots of embedded devices have self signed certs, so verify will fail)
  # @param block [Proc] 
  def http_session
    @http = Net::HTTP.new(@host, @port)   
    @http.set_debug_output($stdout) if @debug
    @http.use_ssl = @use_ssl      
    @http.verify_mode = OpenSSL::SSL::VERIFY_NONE  if ! @use_ssl || ! @verify_cert 
    @http.start do |session| #ensure we close the session after the block
      @session = session 
      yield 
    end
  end
  
  #Web basic authentication (not exactly secure)
  # @param user [String] Account name
  # @param password [String] Accounts password
  # @return [String] Base64 encoded concatentation of user + ':' + password
  def basic_authorization(user:, password:)
    #req.basic_auth( user, password) if  user != nil
    'Basic ' + Base64.encode64( "#{user}:#{password}" )
  end
  
  #Dropbox style token authentication
  # @param token [String] Token, as issued by dropbox
  # @return [String] Concatenation of 'Bearer ' + token
  def bearer_authorization(token:)
    "Bearer " + token
  end

  #send the query to the web server using an http get, and returns the response.
  #  Cookies in the response get preserved in @cookies, so they will be sent along with subsequent calls
  #  We are currently ignoring redirects from the PDU's we are querying.
  # @param query [String] The URL after the http://host/ bit and not usually not including parameters, if form_values are passed in
  # @param form_values [Hash{String=>Object-with-to_s}] The parameter passed to the web server eg. ?key1=value1&key2=value2...
  # @param authorization [String] If present, add Authorization header, using this string
  # @return [String] The Net::HTTPResponse.body text response from the web server
  def get_page(query: ,form_values: nil, authorization: nil)
    $stderr.puts "Debugging On" if @debug
    query += form_values_to_s(form_values, query.index('?') != nil) #Should be using req.set_form_data, but it seems to by stripping the leading / and then the query fails.
    url = URI.parse("#{@use_ssl ? "https" : "http"}://#{@host}/#{query}")
    $stderr.puts url if @debug
    
    req = Net::HTTP::Get.new(url.request_uri)  

    header = { 'HOST' => @host }
    header['Connection'] = 'keep-alive'
    header['Accept-Encoding'] = 'gzip, deflate'
    header['Accept'] = '*/*'
    header['User-Agent'] = 'curl/7.54.0'
    #header['Content-Type'] = content_type   
    header['Cookie'] = @cookies if @cookies != nil
    header['Authorization'] = authorization if authorization != nil
    req.initialize_http_header( header )

    response = @session.request(req)      
    $stderr.puts response.code.to_i if @debug
    if(response.code.to_i != 200)

      if(response.code.to_i == 302)
          #ignore the redirects.
          #$stderr.puts "302"
          #response.each {|key, val| $stderr.printf "%s = %s\n", key, val }  #Location seems to have cgi params removed. End up with .../cginame?&
          #$stderr.puts "Redirect to #{response['location']}"   #Location seems to have cgi params removed. End up with .../cginame?&
          if (response_text = response.response['set-cookie']) != nil
            @cookies =  response_text
          else
            @cookies = ''
          end
          #$stderr.puts
        return
      elsif response.code.to_i >= 400 && response.code.to_i < 500
        return response.body
      end
      raise Error.new(web_return_code: response.code, message: "#{response.code} #{response.message}")
    end

    if (response_text = response.response['set-cookie']) != nil
      @cookies =  response_text
    else
      @cookies = ''
    end

    return response.body
  end

  #send the query to the server and return the response. 
  # @param session [Net::HTTP] open connection to the web server.
  # @param host [String] Web site host name
  # @param query [String] URL, less the 'http://host/'  part
  # @param authorization [String] If present, add Authorization header, using this string
  # @param content_type [String] Posted content type
  # @param data [String] Text to add to body of post to the web server
  def post_page(query:, authorization: nil, content_type: 'application/x-www-form-urlencoded', data: nil)
    #query += form_values_to_s(form_values) #Should be using req.set_form_data, but it seems to by stripping the leading / and then the query fails.
   #puts query
    url = URI.parse("#{@use_ssl ? "https" : "http"}://#{@host}/#{query}")
    req = Net::HTTP::Post.new(url.path)
    header = {'HOST' => @host}
    header['User-Agent'] = 'curl/7.54.0'
    header['Authorization'] = authorization if authorization != nil
    header['Content-Type'] = content_type   
    header['Cookie'] = @cookies if @cookies != nil
    req.initialize_http_header( header )
    #puts req.methods
    #req.set_form_data(form_values, '&') if form_values != nil
    req.body = data == nil ? '' : data
  
      response = @session.request(req)
      if(response.code.to_i != 200)
        if(response.code.to_i == 302)
            #ignore the redirects. 
            #puts "302"
            #response.each {|key, val| printf "%s = %s\n", key, val }  #Location seems to have cgi params removed. End up with .../cginame?&
            #puts "Redirect of Post to #{response['location']}" #Location seems to have cgi params removed. End up with .../cginame?&
            if (response_text = response.response['set-cookie']) != nil
              @cookies =  response_text
            else
              @cookies = ''
            end
          return
        end
        raise Error.new(web_return_code: response.code, message: "#{response.code} #{response.message}")
      end

      if (response_text = response.response['set-cookie']) != nil
        @cookies =  response_text
      else
        @cookies = ''
      end

      @response = response
    
      return response.body
  end

  #Extract form field values from the html body.
  # @param body [String] The html response body
  # @return [Hash] Keys are the field names, values are the field values
  def extract_input_fields(body)
    entry = true
    @inputs = {}
    doc = Nokogiri::HTML(body)
    doc.xpath("//form/input").each do |f|
      @inputs[f.get_attribute('name')] = f.get_attribute('value')
    end
  end

  #Extract links from the html body.
  # @param body [String] The html response body
  # @return [Hash] Keys are the link text, values are the html links
  def extract_link_fields(body)
    entry = true
    @inputs = {}
    doc = Nokogiri::HTML(body)
    doc.xpath("//a").each do |f|
      return URI.parse( f.get_attribute('href') ).path if(f.get_attribute('name') == 'URL$1')
    end
    return nil
  end

  #Take a hash of the params to the post and generate a safe URL string.
  # @param form_values [Hash] Keys are the field names, values are the field values
  # @param has_q [Boolean] We have a leading ? for the html get, so don't need to add one.
  # @return [String] The 'safe' text for fields the get or post query to the web server
  def form_values_to_s(form_values=nil, has_q = false)
    return "" if form_values == nil
    s = (has_q == true ? "" : "?")
    first = true
    form_values.each do |key,value|
      s += "&" if !first
      s += "#{URI.escape(key)}=#{URI.escape(value)}"
      first = false
    end
    return s
  end
end

