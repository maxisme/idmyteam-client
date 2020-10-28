from django import template

register = template.Library()


@register.filter(is_safe=True)
def dict_key(d: dict, k):
    try:
        return d[k]
    except TypeError:
        return "help"


@register.filter()
def to_form_name(type, setting):
    return (type + "_" + setting).replace(" ", "-").lower()
