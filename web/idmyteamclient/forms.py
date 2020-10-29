from django import forms
from django.contrib.auth.forms import UserCreationForm

from idmyteamclient.models import Member


class NewMemberForm(UserCreationForm):
    class Meta:
        model = Member
        fields = [
            "username",
            "password1",
            "password2",
            "permission"
        ]