from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView, ListView, TemplateView

from ..api.types import CronTriggerDT, DateTriggerDT, IntervalTriggerDT
from ..models.job import DjangoJob, DjangoJobExecution
from ..models.task import Script, Task, TriggerType
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
        params = {}

        with_task = get_param(self.request, 'with_task', int)
        if with_task is not None:
            params['with_task'] = with_task

        self.request.params = params

        qs = DjangoJob.objects.select_related('task').all().order_by('-id')
        if with_task is not None:
            qs = qs.filter(task__isnull=not with_task)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            params=self.request.params,
            with_task_choices=[('', '---'), (1, 'Yes'), (0, 'No')],
        )
        return context


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
    model = DjangoJob

    slug_field = 'id'

    def get_template_names(self):
        return 'jobs_detail.html'


class TasksDetailView(DetailView):
    model = Task

    slug_field = 'id'

    def get_template_names(self):
        return 'tasks_detail.html'


class ScriptsDetailView(DetailView):
    model = Script

    slug_field = 'id'

    def get_template_names(self):
        return 'scripts_detail.html'


def get_tasks_edit_context(**kwargs):
    context = dict(
        scripts=Script.objects.all().order_by('-updated_at'),
        TriggerType=TriggerType,
        trigger_dt_map={
            TriggerType.cron: CronTriggerDT,
            TriggerType.interval: IntervalTriggerDT,
            TriggerType.date: DateTriggerDT,
        }
    )
    context.update(kwargs)
    return context


def tasks_edit_view(request, id):
    task = Task.objects.get(id=id)
    return render(request, 'tasks_edit.html', get_tasks_edit_context(object=task))


def tasks_create_view(request):
    return render(request, 'tasks_edit.html', get_tasks_edit_context(object={}))
