from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.views.generic import DetailView
from django.views.generic.list import ListView

# TODO import new run task function
# from .admin import run_task
from ..helper.view import UtilMixin
from ..models.job import DjangoJobExecution
# TODO import models
# from .models import ManagerJob, ManagerJobExecution, ManagerTask, standard_status
# TODO import job_store
# from .myjobs import job_store


def index(req):
    return HttpResponseRedirect('/dashboard')


def filter_execution_by_success(qs, is_success):
    if is_success:
        qs = qs.filter(status=DjangoJobExecution.SUCCESS)
    else:
        qs = qs.filter(~Q(status=DjangoJobExecution.SUCCESS))
    return qs


class DashboardView(UtilMixin, ListView):
    model = DjangoJobExecution

    def get_template_names(self):
        return 'dashboard.html'

    def get_queryset(self):
        qs = super().get_queryset()
        limit = self.get_param('limit', int, 20)
        return qs[:limit]

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()

        limit = self.get_param('limit', int, 20)

        qs = DjangoJobExecution.objects.select_related('job', 'job__task').all()

        context['success_list'] = filter_execution_by_success(qs, True).order_by('-run_time')[:limit]
        context['exception_list'] = filter_execution_by_success(qs, False).order_by('-run_time')[:limit]
        return context


class ExecutionsView(UtilMixin, ListView):
    # model = ManagerJobExecution
    paginate_by = 25

    # custom attrs
    page_ellipsis = '...'
    page_num_limit = 30
    page_num_surround = 4

    def get_template_names(self):
        return 'executions.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return executions_get_queryset(self, qs).order_by('-run_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['qs_args'] = self.qs_args
        page_obj = context['page_obj']
        context['page_range'] = page_range(
            page_obj.paginator.page_range,
            page_obj.paginator.num_pages,
            self.page_num_limit,
            self.page_num_surround,
            page_obj.number,
            self.page_ellipsis,
        )
        context['page_ellipsis'] = self.page_ellipsis
        return context


def executions_get_queryset(self, qs):
    self.qs_args = []

    def append_qs_arg(k, v):
        if v is not None:
            self.qs_args.append((k, v))

    trigger_id = self.get_param('trigger_id', int)
    append_qs_arg('trigger_id', trigger_id)

    status_category = self.get_param('status_category', str)
    append_qs_arg('status_category', status_category)

    if trigger_id:
        qs = qs.filter(task_trigger_id=trigger_id)
    if status_category:
        qs = filter_execution_by_success(qs, status_category)

    return qs


class ExecutionItemView(DetailView):
    # model = ManagerJobExecution

    def get_template_names(self):
        return 'execution_item.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['execution'] = self.object
        return context
