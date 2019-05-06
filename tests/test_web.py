import tornado
from tornado.testing import AsyncHTTPTestCase

import server


class TestWebApp(AsyncHTTPTestCase):
    url_blacklist = []

    def get_app(self):
        server.server_settings['debug'] = False
        self.app = tornado.web.Application(server.web_urls.www_urls, **server.server_settings)
        return self.app

    def test_urls(self):
        for url in server.web_urls.www_urls:
            if url[1].__module__ != 'events' and url[0] not in self.url_blacklist:
                print(url[0])
                response = self.fetch(url[0])
                assert response.code == 200
