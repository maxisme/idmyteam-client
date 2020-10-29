from django import template

register = template.Library()


@register.filter()
def dict_key(d: dict, k):
    return d[k]


@register.filter()
def to_form_name(type, setting):
    return (type + "_" + setting).replace(" ", "-").lower()


@register.filter()
def face_css(percentage):
    COLOUR_1 = "#bc2122"
    COLOUR_2 = "#db8d2e"
    
    return f"""
    background: -moz-linear-gradient(bottom, {COLOUR_2} 0%, {COLOUR_2} {percentage}, {COLOUR_1} {percentage}, {COLOUR_1} 100%);
    background: -webkit-linear-gradient(bottom, {COLOUR_2} 0%, {COLOUR_2} {percentage}, {COLOUR_1} {percentage}, {COLOUR_1} 100%);
    background: linear-gradient(to top, {COLOUR_2} 0%, {COLOUR_2} {percentage}, {COLOUR_1} {percentage}, {COLOUR_1} 100%);
    filter: progid:DXImageTransform.Microsoft.gradient( startColorstr={COLOUR_2}, endColorstr={COLOUR_1}, GradientType=0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;"""
