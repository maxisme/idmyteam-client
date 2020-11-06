from django import template
from django.forms import forms

from idmyteamclient.models import Member
from web.settings import MIN_TRAINING_IMAGES_PER_MEMBER

register = template.Library()

COLOUR_1 = "#bc2122"
COLOUR_2 = "#db8d2e"


@register.filter()
def dict_key(d: dict, k):
    return d[k]


@register.filter()
def to_form_name(group, setting):
    return (group + "_" + setting).replace(" ", "-").lower()


@register.filter()
def face_css(val):
    """
    takes either a string percentage (e.g 14%)
    or a member: Member
    :param val:
    :return:
    """
    if isinstance(val, Member):
        percentage = str((val.num_trained / MIN_TRAINING_IMAGES_PER_MEMBER) * 100) + "%"
    elif val:
        percentage = val
    else:
        raise Exception("Must pass percentage or member")

    return f"""
    background: -moz-linear-gradient(bottom, {COLOUR_2} 0%, {COLOUR_2} {percentage}, {COLOUR_1} {percentage}, {COLOUR_1} 100%);
    background: -webkit-linear-gradient(bottom, {COLOUR_2} 0%, {COLOUR_2} {percentage}, {COLOUR_1} {percentage}, {COLOUR_1} 100%);
    background: linear-gradient(to top, {COLOUR_2} 0%, {COLOUR_2} {percentage}, {COLOUR_1} {percentage}, {COLOUR_1} 100%);
    filter: progid:DXImageTransform.Microsoft.gradient( startColorstr={COLOUR_2}, endColorstr={COLOUR_1}, GradientType=0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;"""


@register.filter()
def permitted(member: Member, perm: str):
    return member.permitted(perm)


@register.filter()
def set_initial_form_field(field: forms.Field, val):
    field.initial = val
    return field
