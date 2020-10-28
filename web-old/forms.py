from wtforms import Form, PasswordField, SelectField, StringField, validators

from settings import config


class CustomForm(Form):
    def __init__(self, *args, **kwargs):
        args = self.SimpleMultiDict(*args)
        super(CustomForm, self).__init__(args, **kwargs)

    def validate(self):
        status = super(CustomForm, self).validate()
        for field in self._fields:
            f = self._fields[field]
            if f.errors:
                if not f.render_kw:
                    f.render_kw = {}
                if "class" in f.render_kw:
                    f.render_kw["class"] += " invalid"
                else:
                    f.render_kw["class"] = "invalid"
        return status

    class SimpleMultiDict(dict):
        def getlist(self, key):
            arr = []
            for k in self[key]:
                arr.append(k.decode("utf-8"))
            return arr

        def __repr__(self):
            return type(self).__name__ + "(" + dict.__repr__(self) + ")"


class LoginForm(CustomForm):
    name = StringField("Name", [validators.InputRequired()])
    password = PasswordField("Password", [validators.InputRequired()])


class NewMemberForm(CustomForm):
    name = StringField("Name", [validators.Length(min=3), validators.InputRequired()])
    choices = [
        (
            str(config.PERMISSIONS[perm]["level"]),
            perm.capitalize() + " - " + config.PERMISSIONS[perm]["description"],
        )
        for perm in config.PERMISSIONS
    ]
    permission = SelectField(
        "Permissions", [validators.InputRequired()], choices=choices
    )
    password = PasswordField(
        "Password", [validators.EqualTo("confirm", message="Passwords must match")]
    )
    confirm = PasswordField("Confirm Password")


class NewMemberPasswordForm(CustomForm):
    password = PasswordField(
        "Password",
        [
            validators.InputRequired(),
            validators.Length(min=8),
            validators.EqualTo("confirm", message="Passwords must match"),
        ],
    )
    confirm = PasswordField("Confirm Password")
