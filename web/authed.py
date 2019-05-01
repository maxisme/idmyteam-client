import json

import view
from settings import functions, config
import forms


class LoginHandler(view.BaseHandler):
    def get(self):
        self.tmpl['form'] = forms.LoginForm()
        self._screen()

    def _screen(self):
        self.tmpl['title'] = "Member Login"
        self.render('helpers/form.html', **self.tmpl)

    def post(self):
        self.tmpl['form'] = form = forms.LoginForm(self.request.arguments)
        if form.validate():
            name = form.name.data
            password = form.password.data
            member = functions.Member.get_by_name(self.db_connect(), name)
            if member and member.get('perm') != config.NO_PERM and functions.Member.login(member, password):
                self.set_secure_cookie('member', json.dumps(member))
                return self.redirect("/members")
            else:
                self.flash_error('Wrong username or password!')
        return self._screen()

