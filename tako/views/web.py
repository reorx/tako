from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from django.utils import timezone
from django.views.generic import DetailView, ListView, TemplateView

from ..api.task import trigger_dt_map
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

        qs = DjangoJob.objects.select_related('task').annotate(
            executions_count=Count('executions')
        ).all().order_by('-id')
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
        return Task.objects.select_related('job', 'script').defer('script__content').annotate(
            executions_count=Count('job__executions')
        ).all().order_by('-updated_at')


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
        trigger_dt_map=trigger_dt_map,
    )
    context.update(kwargs)
    return context


def tasks_edit_view(request, id):
    task = Task.objects.get(id=id)
    return render(request, 'tasks_edit.html', get_tasks_edit_context(object=task, is_create=False))


def tasks_create_view(request):
    return render(request, 'tasks_edit.html', get_tasks_edit_context(object={}, is_create=True))


def scripts_edit_view(request, id):
    script = Script.objects.get(id=id)
    return render(request, 'scripts_edit.html', dict(object=script, is_create=False))


def scripts_create_view(request):
    return render(request, 'scripts_edit.html', dict(object={}, is_create=True))



tako_web_urls = [
    path('', index),
    path('dashboard', DashboardView.as_view(), name='dashboard'),
    # list
    path('executions', ExecutionsView.as_view(), name='executions'),
    path('jobs', JobsView.as_view(), name='jobs'),
    path('tasks', TasksView.as_view(), name='tasks'),
    # detail
    path('executions/<int:slug>', ExecutionsDetailView.as_view(), name='executions_detail'),
    path('jobs/<str:slug>', JobsDetailView.as_view(), name='jobs_detail'),
    path('tasks/<int:slug>', TasksDetailView.as_view(), name='tasks_detail'),
    path('scripts/<int:slug>', ScriptsDetailView.as_view(), name='scripts_detail'),
    # edit
    path('tasks/<int:id>/edit', tasks_edit_view, name='tasks_edit'),
    path('tasks/create', tasks_create_view, name='tasks_create'),
    path('scripts/create', scripts_create_view, name='scripts_create'),
    path('scripts/<int:id>/edit', scripts_edit_view, name='scripts_edit'),
]
