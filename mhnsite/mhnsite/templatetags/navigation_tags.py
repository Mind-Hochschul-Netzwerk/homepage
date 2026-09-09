from django import template

# import site:
from wagtail.models import Site

from mhnsite.models import FooterText

register = template.Library()


@register.simple_tag(takes_context=True)
def get_site_root(context):
    return Site.find_for_request(context["request"]).root_page
