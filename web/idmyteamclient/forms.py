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


class ChangePasswordForm(forms.Form):
    password = forms.CharField(
        min_length=8, widget=forms.PasswordInput(), required=True, label="Password"
    )
    confirm = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(),
        required=True,
        label="Confirm Password",
    )

    def clean(self):
        cleaned_data = super(ChangePasswordForm, self).clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm")

        if password != confirm:
            raise forms.ValidationError("Passwords do not match!")
