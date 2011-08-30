import functools
import hashlib
import logging
import struct
import time
import tornado.escape
import tornado.web

class StreamHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        tornado.web.RequestHandler.__init__(self, application, request,
                                            **kwargs)
        self.stream = request.connection.stream
        self.client_terminated = False
        self._waiting = None

    def _execute(self, transforms, *args, **kwargs):
        self.open_args = args
        self.open_kwargs = kwargs
        self.stream.write(tornado.escape.utf8(
            "HTTP/1.1 200\r\n\r\n"
            ))
        self.async_callback(self.open)(*self.open_args, **self.open_kwargs)

    def write_message(self, message):
        if isinstance(message, dict):
            message = tornado.escape.json_encode(message)
        if isinstance(message, unicode):
            message = message.encode("utf-8")
        assert isinstance(message, str)
        self.stream.write(message + "\r\n")

    def open(self, *args, **kwargs):
        pass
    def on_message(self, message):
        raise NotImplementedError

    def on_close(self):
        pass


    def close(self):
        if self.client_terminated and self._waiting:
            tornado.ioloop.IOLoop.instance().remove_timeout(self._waiting)
            self.stream.close()
        else:
            self.stream.write("\xff\x00")
            self._waiting = tornado.ioloop.IOLoop.instance().add_timeout(
                                time.time() + 5, self._abort)

    def async_callback(self, callback, *args, **kwargs):
        if args or kwargs:
            callback = functools.partial(callback, *args, **kwargs)
        def wrapper(*args, **kwargs):
            try:
                return callback(*args, **kwargs)
            except Exception, e:
                logging.error("Uncaught exception in %s",
                              self.request.path, exc_info=True)
                self._abort()
        return wrapper

    def _abort(self):
        self.client_terminated = True
        self.stream.close()

    def _on_frame_type(self, byte):
        frame_type = ord(byte)
        if frame_type == 0x00:
            self.stream.read_until("\xff", self._on_end_delimiter)
        elif frame_type == 0xff:
            self.stream.read_bytes(1, self._on_length_indicator)
        else:
            self._abort()

    def _on_end_delimiter(self, frame):
        if not self.client_terminated:
            self.async_callback(self.on_message)(
                    frame[:-1].decode("utf-8", "replace"))
        if not self.client_terminated:
            self._receive_message()

    def _on_length_indicator(self, byte):
        if ord(byte) != 0x00:
            self._abort()
            return
        self.client_terminated = True
        self.close()

    def on_connection_close(self):
        self.client_terminated = True
        self.on_close()

    def _not_supported(self, *args, **kwargs):
        raise Exception("Method not supported for Web Sockets")


for method in ["write", "redirect", "set_header", "send_error", "set_cookie",
               "set_status", "flush", "finish"]:
    setattr(StreamHandler, method, StreamHandler._not_supported)
