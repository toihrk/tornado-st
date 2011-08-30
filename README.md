#  tornado.stream


## Install 

  move stream.py into Installed Tornado directory.

**Example**

  mv stream.py  /usr/local/lib/python2.7/site-packages/tornado-2.0-py2.7.egg/tornado/


## Usage

	import tornado.stream
	..
	class ExampleStreamHandler(tornado.stream.StreamHandler):
		def open(self):
			print "open"
			self.write_message("Hello, Python!")
		def on_close(self):
			print "close"

  Using the Same "tornado.websocket".

  [tornado.websocket](http://www.tornadoweb.org/documentation/websocket.html, "tornado.websocket")



