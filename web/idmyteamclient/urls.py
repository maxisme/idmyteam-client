"""web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from idmyteamclient import views
from idmyteamclient import auth

urlpatterns = [
    path("", views.welcome_handler, name="welcome"),
    path("camera", auth.stream_handler, name="camera"),
    path("add-member", auth.add_member_handler, name="add-member"),
    path("member/<int:member_id>", auth.member_handler, name="member"),
    path("member/<int:member_id>/train", auth.member_handler, name="train"),
    path(
        "member/<int:member_id>/password", auth.change_member_password, name="password"
    ),
    path("members", auth.members_handler, name="members"),
    path("script", auth.script_handler, name="script"),
    path("classify", auth.classify_handler, name="classify"),
    path("classify/<int:page>", auth.classify_handler, name="classify"),
    path("settings", auth.settings_handler, name="settings"),
    path("logs", views.welcome_handler, name="logs"),
    path("logout", auth.logout_handler, name="logout"),
    path("login", auth.login_handler, name="login"),
]
