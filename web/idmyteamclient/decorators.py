from functools import wraps

from django.shortcuts import redirect
from django.urls import reverse

from idmyteamclient.models import Member


def permitted(perm: Member.Permission, request_method=None):
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if request_method and request.method not in request_method:
                return func(request, *args, **kwargs)

            try:
                member: Member = request.user
                if member.permitted(perm):
                    return func(request, *args, **kwargs)
            except AttributeError:
                pass
            return redirect(reverse("login"))

        return inner

    return decorator
