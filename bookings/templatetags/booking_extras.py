from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except (ValueError, TypeError):
        return value

@register.filter
def dict_lookup(dictionary, key):
    """Look up a key in a dictionary"""
    for item in dictionary:
        if str(item.id) == str(key):
            return item
    return None
