from tornado import httpclient
import tornado.ioloop
import tornado.web
import tornado.websocket
import logging
import time
import os
import json
import urllib
from tornado.log import access_log

ROBOT_ADDR = 'http://192.168.50.225:5500/move'

logger = logging.getLogger()
logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
fh = logging.FileHandler('log/server.log')
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
sh.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(sh)
logger.addHandler(fh)


class UpdateLogs():
    """
    let all callbacks write the message to client.
    """

    def __init__(self):
        self.callbacks = []
        self.message_cache = []

    def register(self, callback):
        self.callbacks.append(callback)

    def unregister(self, callback):
        self.callbacks.remove(callback)

    def trigger(self, message):
        self.message_cache.append(message)
        self.notify_callbacks()

    def  notify_callbacks(self):
        if len(self.callbacks) != 0:
            for c in self.callbacks:
                for message in self.message_cache:
                    logger.debug(type(message))
                    c(message)
            self.message_cache.clear()
        else:
            logger.info('No client connected, save message in cache.')


class EchoWebSocket(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
            return True

    def open(self):
        self.application.updatelogs.register(self.callback)

    def on_message(self, message):
        pass

    def on_close(self):
        self.application.updatelogs.unregister(self.callback)

    def callback(self, data):
        self.write_message(data)
        logger.debug('write_message!')


class ReceiveLogContent(tornado.web.RequestHandler):
    def post(self):
        content = self.get_argument('content')
        logger.debug(content)
        self.application.updatelogs.trigger(content)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

    async def post(self):
        action = self.get_body_argument('move')
        logger.info('[DIRECTION]: %s' % action)

        http_client = httpclient.AsyncHTTPClient()
        args = urllib.parse.urlencode({'move': action})
        request = httpclient.HTTPRequest(url=ROBOT_ADDR,  method='POST',  body=args)
        res = await  http_client.fetch(request)
        
        self.finish()



class Application(tornado.web.Application):
    def __init__(self):
        self.updatelogs = UpdateLogs()
        handlers = [
            (r'/', IndexHandler),
            (r'/log', ReceiveLogContent),
            (r'/websocket', EchoWebSocket)
        ]

        settings = {
            'template_path': 'templates',
            'static_path': 'static',
            'debug': True
        }

        tornado.web.Application.__init__(self, handlers, **settings)

    def log_request(self, handler):
        if "log_function" in self.settings:
            self.settings["log_function"](handler)
            return
        if handler.get_status() < 400:
            log_method = access_log.debug  # tornado 请求的信息不打印，将为debug级别。
        elif handler.get_status() < 500:
            log_method = access_log.warning
        else:
            log_method = access_log.error
        request_time = 1000.0 * handler.request.request_time()
        log_method(
            "%d %s %.2fms",
            handler.get_status(),
            handler._request_summary(),
            request_time,
        )


if __name__ == "__main__":
    logger.info('ROBOT address: %s ' % ROBOT_ADDR)
    app = Application()
    app.listen(5501)
    tornado.ioloop.IOLoop.current().start()


