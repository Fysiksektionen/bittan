from django import template
import logging

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, "")
