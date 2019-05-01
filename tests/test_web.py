import tornado
from tornado.testing import AsyncHTTPTestCase

from web import web_urls, web


class TestWebApp(AsyncHTTPTestCase):
    url_blacklist = []

    def get_app(self):
        self.app = tornado.web.Application(web_urls.www_urls, **web.server_settings)
        return self.app

    def test_urls(self):
        for url in web_urls.www_urls:
            if url[1].__module__ != 'events' and url[0] not in self.url_blacklist:
                print(url[0])
                response = self.fetch(url[0])
                assert response.code == 200
