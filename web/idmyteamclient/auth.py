from django.contrib.auth import login, logout, authenticate
from django.urls import reverse
from idmyteam.helpers import render, SUCCESS_COOKIE_KEY, redirect

from idmyteamclient import forms
from idmyteamclient.forms import NewMemberForm
from idmyteamclient.helpers import update_global_stats
from idmyteamclient.models import Member
from web import settings


def login_handler(request):
    if request.method == "POST":
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            member: Member = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if member and member.permitted(Member.Permission.CLASSIFY):
                login(request, member)
                return redirect("/")
    else:
        form = forms.LoginForm()

    return render(request, "forms/login.html", {"title": "Login", "form": form})


def logout_handler(request):
    logout(request)
    return redirect("/")


def stream_handler(request):
    return render(
        request,
        "stream.html",
        {
            "title": "Stream",
            "camera_running": bool(int(settings.settings_yaml["Camera"]["Run"]["val"])),
            "live_stream_on": bool(
                int(settings.settings_yaml["Camera"]["Live Stream"]["val"])
            ),
            "capture_log": settings.CAPTURE_LOG,
        },
    )


def settings_handler(request):
    update_global_stats()

    return render(
        request,
        "settings.html",
        {
            "title": "Settings",
            "settings": settings.settings_yaml,
            "stats": settings.stats,
            "stats_info": settings.STATS_INFO,
        },
    )


def script_handler(request):
    return render(
        request,
        "script.html",
        {
            "title": "Script",
            "script_speed": 0.002,  # TODO get actual speed
            "file_content": open(settings.SCRIPT_PATH, "r").read(),
        },
    )


def member_handler(request, member_id: int):
    if request.method == "GET":
        member = Member.objects.get(id=member_id)
        if member:
            return render(
                request,
                "member.html",
                {
                    "title": member,
                    "member": member,
                },
            )
        return redirect(reverse("members"))
    elif request.method == "DELETE":
        if request.user.id == member_id:
            # can't delete logged in user
            return
        Member.objects.delete(id=member_id)


def add_member_handler(request):
    if request.method == "POST":
        form = forms.NewMemberForm(request.POST)
        if form.is_valid():
            member = Member.objects.create_user(
                username=form.cleaned_data.get("username"),
                password=form.cleaned_data.get("password1"),
                permission=form.cleaned_data.get("permission"),
            )
            if member:
                return redirect(
                    "/",
                    cookies={SUCCESS_COOKIE_KEY: "success"},
                )
    else:
        form = forms.NewMemberForm()

    return render(
        request,
        "forms/new-member.html",
        {
            "title": "Add Member",
            "form": form,
        },
    )


def members_handler(request):
    return render(
        request,
        "members.html",
        {
            "title": "Members",
            "min_training_images": settings.MIN_TRAINING_IMAGES_PER_MEMBER,
            "member_form": NewMemberForm(),
            "face_css": settings.PERMISSIONS,
            "members": Member.objects.all(),
        },
    )
