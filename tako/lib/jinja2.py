from urllib.parse import urlencode

from django.templatetags.static import static
from django.urls import reverse
from django.utils.timezone import localtime
from jinja2 import Environment

from ..models import DjangoJobExecution


filters = {}
context = {}


def environment(**options):
    env = Environment(**options)

    def url(name, *args):
        return reverse(name, args=args)

    env.globals.update(
        {
            "static": static,
            "url": url,
        }
    )
    env.globals.update(context)
    env.filters.update(filters)
    return env


def register_filter(f):
    filters[f.__name__] = f
    return f


def register_context(f):
    context[f.__name__] = f
    return f


@register_filter
def spectre_label_class(status):
    return get_spectre_label_class(status)


def get_spectre_label_class(status):
    if status == DjangoJobExecution.SUCCESS:
        return 'label-success'
    if status == DjangoJobExecution.ERROR:
        return 'label-error'
    elif status == DjangoJobExecution.SENT:
        return 'label-secondary'
    return 'label-warning'


@register_filter
def duration(v):
    if v is not None:
        return f'{v}s'
    return '-'


iso_time_format = '%Y-%m-%d %H:%M:%S%z'


@register_filter
def iso_time(t):
    if not t:
        return '-'
    return localtime(t).strftime(iso_time_format)


@register_context
def status_params(status, reverse=False):
    if reverse:
        statuses = set(DjangoJobExecution.STATUSES) - {status}
    else:
        statuses = status
    return {
        'status': statuses,
    }


@register_context
def encode_params_with_page(params, page=None):
    newparams = dict(params)
    if page is not None:
        newparams['page'] = page
    return urlencode(newparams, True)


@register_filter
def admin_job_execution_url(id):
    return f'/admin/django_apscheduler/managerjobexecution/{id}/change/'


@register_filter
def admin_job_url(id):
    return f'/admin/django_apscheduler/managerjob/{id}/change/'


@register_filter
def admin_trigger_url(id):
    return f'/admin/django_apscheduler/managertrigger/{id}/change/'
