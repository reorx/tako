from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView, ListView, TemplateView

from ..models.job import DjangoJob, DjangoJobExecution
from ..models.task import Task
from .base import filter_executions_qs, get_page_range, get_param


def index(req):
    return HttpResponseRedirect(reverse('dashboard'))


def base_execution_qs():
    return DjangoJobExecution.objects.select_related('job', 'job__task').all().order_by('-run_time')


class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()

        limit = get_param(self.request, 'limit', int, 20)
        sub_limit = get_param(self.request, 'sub_limit', int, 10)

        qs = base_execution_qs()

        context.update(
            all_list=qs[:limit],
            success_list=qs.filter(status=DjangoJobExecution.SUCCESS)[:sub_limit],
            error_list=qs.exclude(status=DjangoJobExecution.SUCCESS)[:sub_limit],
        )

        return context


class ExecutionsView(ListView):
    model = DjangoJobExecution
    paginate_by = 15

    # custom attrs
    page_ellipsis = '...'
    page_num_limit = 30
    page_num_surround = 4

    def get_template_names(self):
        return 'executions.html'

    def get_queryset(self):
        return filter_executions_qs(
            self.request,
            base_execution_qs()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_obj = context['page_obj']
        context['page_range'] = get_page_range(
            page_obj.paginator.page_range,
            page_obj.paginator.num_pages,
            self.page_num_limit,
            self.page_num_surround,
            page_obj.number,
            self.page_ellipsis,
        )
        context.update(
            params=self.request.params,
            params_statuses=self.request.params.get('status', []),
            page_ellipsis=self.page_ellipsis,
            DjangoJobExecution=DjangoJobExecution,
        )
        return context


class JobsView(ListView):
    model = DjangoJob

    def get_template_names(self):
        return 'jobs.html'

    def get_queryset(self):
        return DjangoJob.objects.select_related('task').all().order_by('-id')


class TasksView(ListView):
    model = Task

    def get_template_names(self):
        return 'tasks.html'

    def get_queryset(self):
        return Task.objects.select_related('job', 'script').defer('script__content').all().order_by('-updated_at')


class ExecutionsDetailView(DetailView):
    model = DjangoJobExecution

    slug_field = 'id'

    def get_template_names(self):
        return 'executions_detail.html'


class JobsDetailView(DetailView):
    def get_template_names(self):
        return 'jobs_detail.html'


class TasksDetailView(DetailView):
    def get_template_names(self):
        return 'tasks_detail.html'


class ScriptsDetailView(DetailView):
    def get_template_names(self):
        return 'scripts_detail.html'
