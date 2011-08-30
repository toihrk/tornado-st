require "net/http"
require "json"

uri = URI.parse("https://example.com/")
http = Net::HTTP.new(uri.host, uri.port)

http.start do |http|
  request = Net::HTTP::Get.new(uri.request_uri)
  buf = ""
  http.request(request) do |response|
    response.read_body do |chunk|
      buf << chunk
      while (line = buf[/.+?(\r\n)+/m]) != nil
        begin
          p line 
          buf.sub!(line,"")
          line.strip!
          status = JSON.parse(line)
        rescue
          break 
        end
        p status
      end
    end
  end
end


