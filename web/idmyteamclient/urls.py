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
    path("stream", auth.stream_handler, name="stream"),
    path("members", views.welcome_handler, name="members"),
    path("script", views.welcome_handler, name="script"),
    path("classify", views.welcome_handler, name="classify"),
    path("settings", auth.settings_handler, name="settings"),
    path("logs", views.welcome_handler, name="logs"),
    path("logout", views.welcome_handler, name="logout"),
    path("login", views.welcome_handler, name="login"),
]
