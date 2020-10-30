from django.contrib.auth.forms import UserCreationForm
from django import forms

from idmyteamclient.models import Member


class NewMemberForm(UserCreationForm):
    class Meta:
        model = Member
        fields = ["username", "password1", "password2", "permission"]


class LoginForm(forms.Form):
    username = forms.CharField(required=True, label="Username")
    password = forms.CharField(
        min_length=8, widget=forms.PasswordInput(), required=True, label="Password"
    )

    class Meta:
        model = Member
        fields = ["username", "password"]
