from django import template

register = template.Library()

@register.filter(is_safe=True)
def create_range(value):
    return range(1, value+1)        # returns a list containing range made from given value in template
