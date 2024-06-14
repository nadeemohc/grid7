# store/templatetags/pagination_tags.py

from django import template

register = template.Library()

@register.inclusion_tag('pagination.html', takes_context=True)
def render_pagination(context):
    page_obj = context.get('page_obj')
    request = context.get('request')

    if not page_obj:
        return {}

    pagination_data = {
        'page_obj': page_obj,
        'request': request,
    }
    return pagination_data
