"""Custom template filters for dictionary access in templates."""
from django import template


register = template.Library()


@register.filter
def get_item(mapping, key):
    """Return dictionary item by key for template usage."""
    value = mapping.get(key)
    if hasattr(value, "quantity"):
        return value.quantity
    return value
