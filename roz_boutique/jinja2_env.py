from django.templatetags.static import static
from django.urls import reverse, NoReverseMatch
from django.middleware.csrf import get_token
from django.utils.safestring import mark_safe
from jinja2 import Environment


def url_for(endpoint, **kwargs):
    if endpoint == "static":
        return static(kwargs.get("filename", ""))
    try:
        return reverse(endpoint, kwargs=kwargs if kwargs else None)
    except NoReverseMatch:
        return "#"


def roz_csrf_input(request):
    token = get_token(request)
    return mark_safe(f'<input type="hidden" name="csrfmiddlewaretoken" value="{token}">')


def environment(**options):
    env = Environment(**options)
    env.globals.update({"url_for": url_for, "roz_csrf_input": roz_csrf_input})
    return env
