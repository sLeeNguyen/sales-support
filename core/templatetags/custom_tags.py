from django import template

from core.utils import server_timezone

register = template.Library()


@register.filter()
def to_int(value):
    return int(value)
