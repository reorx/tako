from urllib.parse import urlencode

from django import template
from django.utils.timezone import localtime

from ..models import DjangoJobExecution


register = template.Library()


@register.filter
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


@register.filter
def duration(v):
    if v is not None:
        return f'{v}s'
    return '-'


iso_time_format = '%Y-%m-%d %H:%M:%S%z'


@register.filter
def iso_time(t):
    if not t:
        return '-'
    return localtime(t).strftime(iso_time_format)


@register.filter
def status_params(status, reverse=False):
    if reverse:
        statuses = set(DjangoJobExecution.STATUSES) - {status}
    else:
        statuses = status
    return {
        'status': statuses,
    }


@register.filter
def encode_params_with_page(params, page=None):
    newparams = dict(params)
    if page is not None:
        newparams['page'] = page
    return urlencode(newparams, True)


@register.filter
def admin_job_execution_url(id):
    return f'/admin/django_apscheduler/managerjobexecution/{id}/change/'


@register.filter
def admin_job_url(id):
    return f'/admin/django_apscheduler/managerjob/{id}/change/'


@register.filter
def admin_trigger_url(id):
    return f'/admin/django_apscheduler/managertrigger/{id}/change/'
