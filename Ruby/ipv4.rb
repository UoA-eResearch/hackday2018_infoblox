class IPv4
  attr_reader :host         # [Integer] IPv4 Address
  attr_reader :last_host    # [Integer] Second to last IPv4 Address for this mask
  attr_reader :network      # [Integer] first IPv4 address for this mask
  attr_reader :broadcast    # [Integer] last IPv4 address for this mask
  attr_reader :mask         # [Integer] IPv4 Mask 
  attr_reader :mask_bytes   # [Array]   Integer values, for each byte
  attr_reader :mask_length  # [Integer] mask length i.e. 24 for /24
  
  def initialize(host, mask = 32)
    @mask, @mask_length, @mask_bytes = process_mask(mask)
    if host.class == String
      ip = host.split(/\./)
      (0..3).each { |i| ip[i] = '0' if ip[i] == nil}
      @host = ((ip[0].to_i << 24) | (ip[1].to_i << 16) | (ip[2].to_i << 8) | ip[3].to_i)
    elsif host.class == Integer
      @host = host
    else
      @host = nil
      return
    end
    @network = @host & @mask
    @broadcast = (~@network & ~@mask & 0xFFFFFFFF) | @network
    @last_host =  @broadcast - 1
  end
  
  def process_mask(mask)
    if mask.class == String
      return process_string_mask(mask)
    elsif mask.class == Integer
      return process_int_mask(mask)
    else
      raise "Unknown Mask type #{mask.class}"
    end
  end
  
  # Takes an Integer mask, and returns the length in bits
  # @param [Integer] Integer Mask (0xFF000000)
  # @return [Integer] Mask length in bits (8)
  def calc_mask_length(mask)
    mask_length = 0
    (1..32).each do |i|
      mask_length += 1 if(mask&0x1) == 1
      mask = mask >> 1
    end
    return mask_length
  end
  
  def length
    broadcast.to_i - network.to_i + 1
  end
  
  # Turns mask string into an Integer mask, mask length and Integer array
  # @param mask [String] Mask of the form '255.0.0.0'
  # @return [Array] Integer Mask (0xFF000000), Mask Length (8), Mask Integer Array ([0xFF,0,0,0])
  def process_string_mask(mask)
    return nil,nil,nil if mask.class != String
    mask_bytes = mask.split('.') # Make into a byte array
    mask_bytes.collect! {|b| b.to_i} # Convert the string bytes into integers
    # Turn the byte array into a single integer.
    mask = (@mask_bytes[0] << 24) + (@mask_bytes[1] << 16) + (@mask_bytes[2] << 8) + @mask_bytes[3]
    mask_length = calc_mask_length(@mask)
    
    return mask, mask_length, mask_bytes
  end
  
  # Turns mask into an Integer mask, mask length and Integer array
  # @param mask [Integer] Either an Integer mask (0xFF000000), or the mask length (8) as an Integer
  # @return [Array] Integer Mask (0xFF000000), Mask Length (8), Mask Integer Array ([0xFF, 0,0,0])
  def process_int_mask(mask)
    return nil,nil,nil if mask.class != Integer
    if (mask & 0x800000) != 0  # Assume it is a full mask
      mask_length = calc_mask_length(@mask)
    else # Assume it is the mask length
      mask_length = mask
      mask = 0xFFFFFFFF << (32 - mask_length)
    end
    
    mask_bytes = []
    mask_bytes[3] = mask & 255
    mask_bytes[2] = (mask >> 8) & 255
    mask_bytes[1] = (mask >> 16) & 255
    mask_bytes[0] = (mask >> 24) & 255
    
    return mask, mask_length, mask_bytes
  end
  
  # Store IP address in @host
  # @param value [String|Integer] Accepts "x.x.x.x" or a network order Integer IP address
  def host=(value)
    if value.class == String
      ip = s.split(/\./)
      (0..3).each { |i| ip[i] = '0' if ip[i] == nil}
      @host = ((ip[0].to_i << 24) | (ip[1].to_i << 16) | (ip[2].to_i << 8) | ip[3].to_i) & mask
    else
      @host=value
    end
  end
  
  def to_s(mask = 32) # 32 being a host ip address. Can also be a String, or Integer Mask
    mask, mask_length, mask_bytes = process_mask(mask)
    if @host
      ip = (@host & mask)
      "#{(ip >> 24)&255}.#{(ip >> 16)&255}.#{(ip >> 8)&255}.#{ip&255}"
    else
      ""
    end
  end
  
  def network(mask)
    self.class.new(@host, mask)
  end
  
  def broadcast(mask)
    self.class.new(@host & mask | ~mask)
  end
  
  def to_i
    @host
  end
  
  def self.mask_to_i(s)
      ip = s.split(/\./)
      ((ip[0].to_i << 24) | (ip[1].to_i << 16) | (ip[2].to_i << 8) | ip[3].to_i)
  end
  
  def self.maskbits_to_i(n)
      0xffffffff >> (32 -n) << (32 - n)
  end
  
  def +(i)
    x = self.class.new(@host + i)
  end

  def -(i)
    x = self.class.new(@host - i)
  end

  def revptr(bytes)
    rip = ["#{@host&255}", "#{(@host >> 8)&255}", "#{(@host >> 16)&255}", "#{(@host >> 24)&255}"] 
    rip[0,4-bytes].join(".")
  end
  
  def revnet(bytes)
    rip = ["#{@host&255}", "#{(@host >> 8)&255}", "#{(@host >> 16)&255}", "#{(@host >> 24)&255}"] 
    rip[4-bytes,bytes].join(".")
  end
  
  # Test if IP addresses are the same
  # @param i [IPV4] address to check against local ip address
  # @return [Boolean]
  def ==(i)
    @host == i.host
  end
  
  def notnil?
    @host != nil
  end
  
  # Test to see if one network is a subnet of another
  # @param net [IPV4] Net we want to check
  # @return [Boolean]
  def issubnet?(net)
    # If the net ip address is identical to the local ip address
    # when they both use the same mask, then it is either the same network
    # or a subnet
    (@host & @mask) == (net.host & @mask)
  end
  
  def to_bytes(address)
    bytes = []
    bytes[3] = address & 255
    bytes[2] = (address >> 8) & 255
    bytes[1] = (address >> 16) & 255
    bytes[0] = (address >> 24) & 255
    return bytes
  end

  def ip_to_s(address)
    bytes = to_bytes(address)
    "#{bytes[0]}.#{bytes[1]}.#{bytes[2]}.#{bytes[3]}"
  end
  
  def each_ip
    ((@network+1)..@last_host).each { |ip| yield ip_to_s(ip) }
  end
  
  def <=>(ip)
    @host.to_i <=> ip.to_i
  end
  
  def succ
    self.class.new(@host + 1)
  end
end
