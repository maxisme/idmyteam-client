from settings import config
from tests.web_helpers import WebTest

import mock
from faker import Factory


class MemberGenerator(object):
    def __init__(self, perm="low"):
        fake = Factory.create()
        self.name = fake.name()
        self.password = fake.password()
        self.confirm = self.password
        self.permission = config.PERMISSIONS[perm]["level"]


class TestWebApp(WebTest):
    root_member = MemberGenerator("high")

    @mock.patch("view.BaseHandler.authed", return_value=True)
    def setUp(self, *args):
        super(TestWebApp, self).setUp()
        self.post("/member/add", self.root_member.__dict__)
        self.post("/login", self.root_member.__dict__)

    def tearDown(self):
        self.fetch("/logout")
        super(TestWebApp, self).tearDown()

    def test_login(self, *args):
        assert self.get_cookie("member"), "logged in"

    def test_no_perm(self):
        self.fetch("/logout")  # logout as root

        no_login_member = self._create_member(config.NO_PERM)

        # test not allowed to login if NO_PERM
        self.post("/login", no_login_member.__dict__)
        assert not self.get_cookie("member"), "logged in"

    def test_low_perm_member(self):
        self._test_perms("low")

    def test_medium_perm_member(self):
        self._test_perms("medium")

    def test_high_perm_member(self):
        self._test_perms("high")

    def _create_member(self, perm):
        # create new member with perm
        low_member = MemberGenerator(perm)
        self.post("/member/add", low_member.__dict__)
        self.fetch("/logout")  # logout as root
        assert not self.get_cookie("member")
        return low_member

    def _test_perms(self, perm):
        member = self._create_member(perm)

        # login as new member
        self.post("/login", member.__dict__)
        assert self.get_cookie("member"), "logged in"

        level = config.PERMISSIONS[perm]["level"]

        # test low endpoint
        code = self.fetch("/members", follow_redirects=False).code
        if level >= config.PERMISSIONS["low"]["level"]:
            assert code == 200
        else:
            assert code == 302

        # test medium endpoint
        code = self.fetch("/classify", follow_redirects=False).code
        if level >= config.PERMISSIONS["medium"]["level"]:
            assert code == 200
        else:
            assert code == 302

        # test high endpoint
        code = self.fetch("/member/add", follow_redirects=False).code
        if level >= config.PERMISSIONS["high"]["level"]:
            assert code == 200
        else:
            assert code == 302
