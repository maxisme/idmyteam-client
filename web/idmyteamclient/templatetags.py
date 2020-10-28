from django import template

register = template.Library()


@register.filter(name='dict_key')
def dict_key(d: dict, k):
    try:
        return d[k]
    except TypeError:
        return "help"


@register.filter(name='to_form_name')
def to_form_name(type, setting):
    return (type + "_" + setting).replace(" ", "-").lower()
