from django.template.defaulttags import register

from django import template

register = template.Library()

# used in receipts.html to extract totals


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)