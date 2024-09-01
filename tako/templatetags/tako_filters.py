from urllib.parse import urlencode

from django import template
from django.conf import settings
from django.utils.timezone import localtime

from ..models import DjangoJobExecution


register = template.Library()


@register.filter
def spectre_label_class(status):
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


def url_(path):
    return f'/{settings.TAKO_URL_PREFIX}{path}'


@register.filter
def job_url(id):
    return url_(f'/jobs/{id}')

@register.filter
def task_url(id):
    return url_(f'/tasks/{id}')

@register.filter
def executions_url(is_success):
    return url_(f'/executions?is_success={is_success}')


@register.filter
def url_query_with_page(args, page):
    newargs = dict(args)
    newargs['page'] = page
    return urlencode(newargs)


@register.filter
def admin_job_execution_url(id):
    return f'/admin/django_apscheduler/managerjobexecution/{id}/change/'


@register.filter
def admin_job_url(id):
    return f'/admin/django_apscheduler/managerjob/{id}/change/'


@register.filter
def admin_trigger_url(id):
    return f'/admin/django_apscheduler/managertrigger/{id}/change/'
