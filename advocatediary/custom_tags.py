# app_name/templatetags/custom_tags.py

from django import template
import datetime

register = template.Library()

@register.simple_tag
def get_year_range(start_year, end_year=None):
    if end_year is None:
        end_year = datetime.datetime.now().year
    return range(start_year, end_year + 1)