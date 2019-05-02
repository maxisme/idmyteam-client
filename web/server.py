import os
import logging
from tornado.ioloop import IOLoop, PeriodicCallback
import tornado.wsgi
import tornado.gen
import threading
from tornado.httpclient import HTTPRequest
import tornado.httpserver
import tornado.web

import web_urls

import view
from settings import config, functions
from client import SocketClient
from settings.log import LogDBHandler
import camera
# set logger
logging.basicConfig(level='INFO')
handler = LogDBHandler(functions.connect(config.DB["username"], config.DB["password"], config.DB["db"]))
logging.getLogger('').addHandler(handler)
logging.getLogger('').setLevel('INFO')
logging.getLogger('tornado.access').disabled = True

# web settings
server_settings = {
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "static_path": os.path.join(os.path.dirname(__file__), 'static'),
    "cookie_secret": config.cookie_secret,
    "xsrf_cookies": True,
    "debug": True,
    "default_handler_class": view.Error404
}
app = tornado.web.Application(web_urls.www_urls, **server_settings)


def connect_to_wss(reconnect=True):
    request = HTTPRequest('wss://idmy.team/socket', headers={
        'username':config.username,
        'credentials': config.credentials,
        'local-ip': functions.get_local_IP()
    })
    config.ws = SocketClient(request, reconnect)
    config.ws.connect()

def start_camera():
    config.CAMERA_THREAD = threading.Thread(target=camera.run, args=())
    config.CAMERA_THREAD.start()

def periodic_checks():
    # check socket
    if config.SOCKET_STATUS == config.SOCKET_CLOSED:
        connect_to_wss(False)

    # check camera thread
    if not config.CAMERA_THREAD or not config.CAMERA_THREAD.isAlive():
        logging.critical("Problem with camera please start with web server")
        start_camera()

def main():

    server = tornado.httpserver.HTTPServer(app)
    server.bind(8080)
    server.start(1)  # 1 cpu

    connect_to_wss()
    start_camera()
    logging.info("Web server started...")
    PeriodicCallback(periodic_checks, 2000).start()
    IOLoop.instance().start()


if __name__ == '__main__':
    main()
