from typing import Dict

from django.contrib.auth import login, logout, authenticate
from django.urls import reverse
from idmyteam.helpers import render, SUCCESS_COOKIE_KEY, redirect

from functions import Shell
from idmyteamclient import forms
from idmyteamclient.decorators import permitted
from idmyteamclient.forms import NewMemberForm
from idmyteamclient.helpers import update_global_stats, Image
from idmyteamclient.models import Member
from idmyteamclient.structs import ClassifiedImage
from idmyteamclient.templatetags.tags import to_form_name
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
            if member and member.permitted(Member.Permission.LOW):
                login(request, member)
                return redirect("/")
    else:
        form = forms.LoginForm()

    return render(request, "forms/login.html", {"title": "Login", "form": form})


def logout_handler(request):
    logout(request)
    return redirect("/")


@permitted(Member.Permission.MEDIUM)
def stream_handler(request):
    settings.WS_URL = "hi"
    return render(
        request,
        "camera.html",
        {
            "title": "Camera",
            "camera_running": bool(int(settings.yaml["Camera"]["Run"]["val"])),
            "live_stream_on": bool(int(settings.yaml["Camera"]["Live Stream"]["val"])),
            "capture_log": settings.CAPTURE_LOG,
        },
    )


@permitted(Member.Permission.LOW)
def classify_handler(request, page=1, page_size=30):
    images = Image.get_stored_images(
        request.COOKIES.get("face_coordinates"), page, page_size, classifying=True
    )
    return render(
        request,
        "classify.html",
        {
            "title": "Classify Members",
            "page": page,
            "page_size": page_size,
            "members": Member.objects.all(),
            "image_bbox_js": _fetch_image_bbox_js(images),
            "images": images,
        },
    )


def _fetch_image_bbox_js(images: Dict[str, ClassifiedImage]):
    """
    returns the javascript code of the bbox for the classified images
    :return:
    """
    js = ""
    for img_path, image in images:
        if image.coordinates:
            # language=JavaScript
            js += f"""
            $('#portrait-{image.id}').selectAreas('add', toActualArea($('#portrait-{image.id}'), JSON.parse('{image.coordinates}'), true));
            $('#portrait-{image.id}').closest('span').attr('has_coords', '1');
            """
    return js


@permitted(Member.Permission.HIGH)
def settings_handler(request):
    if request.method == "POST":
        should_restart_camera = False
        all_settings = settings.yaml.get_all()
        for group in all_settings:
            for setting in all_settings[group]:
                form_name = to_form_name(group, setting)
                if form_name in request.POST or _setting_is_switch(
                    all_settings, group, setting
                ):
                    if (
                        _setting_is_switch(all_settings, group, setting)
                        and form_name not in request.POST
                    ):
                        # switch results are not passed in the post request so need to catch that they are missing
                        # and set to 0
                        val = 0
                    else:
                        val = request.POST[form_name]

                    # convert val to int if possible
                    try:
                        val = int(val)
                    except ValueError:
                        pass

                    # check value has changed
                    if settings.yaml.get(group, setting) != val:
                        settings.yaml.set(group, setting, val)
                        if setting in settings.CAMERA_RESTART_SETTINGS:
                            should_restart_camera = True

        if should_restart_camera:
            settings.RESTART_CAMERA = True

        settings.yaml.save()
        return redirect(reverse("settings"))
    else:
        update_global_stats()

        return render(
            request,
            "settings.html",
            {
                "title": "Settings",
                "settings": settings.yaml.get_all(),
                "stats": settings.stats,
                "stats_info": settings.STATS_INFO,
            },
        )


def _setting_is_switch(settings, group, setting) -> bool:
    return (
        "type" in settings[group][setting]
        and settings[group][setting]["type"] == "switch"
    )


@permitted(Member.Permission.HIGH, "POST")
@permitted(Member.Permission.MEDIUM)
def script_handler(request):
    error_message, success_message = "", ""
    if request.method == "POST":
        bash_script_content = request.POST["bash-script"]
        error_message = Shell.validate(bash_script_content, settings.SCRIPT_PATH)
        if error_message:
            error_message = f"<pre>{error_message.decode()}</pre>"
        else:
            success_message = "Updated script!"
        file_content = bash_script_content
    else:
        file_content = open(settings.SCRIPT_PATH, "r").read()

    return render(
        request,
        "script.html",
        {
            "title": "Script",
            "script_speed": 0.002,  # TODO get actual speed
            "file_content": file_content,
            "error_message": error_message,
            "success_message": success_message,
        },
    )


@permitted(Member.Permission.HIGH, "DELETE")
@permitted(Member.Permission.MEDIUM, "GET")
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


@permitted(Member.Permission.HIGH)
def change_member_password(request, member_id):
    member = Member.objects.get(id=member_id)
    if request.method == "POST":
        form = forms.ChangePasswordForm(request.POST)
        if form.is_valid():
            member.set_password(form.cleaned_data.get("password"))
            member.save()

            return redirect(
                reverse("members"),
                cookies={SUCCESS_COOKIE_KEY: f"You have changed {member}s password!"},
            )
    else:
        form = forms.ChangePasswordForm()

    return render(
        request,
        "forms/change-password.html",
        {"title": f"Change {member}'s password", "form": form},
    )


@permitted(Member.Permission.MEDIUM)
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


@permitted(Member.Permission.LOW)
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
