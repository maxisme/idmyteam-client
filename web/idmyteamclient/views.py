from django.shortcuts import render
from idmyteam.helpers import render

from web import settings


def welcome_handler(request):
    return render(
        request, "home/welcome.html", context={"socket_status": settings.SOCKET_STATUS}
    )
