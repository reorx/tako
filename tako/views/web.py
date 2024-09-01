from django.http import HttpResponseRedirect
from django.utils import timezone
from django.views.generic import DetailView, ListView, TemplateView

# TODO import new run task function
# from .admin import run_task
from ..models.job import DjangoJobExecution
from ..templatetags.tako_filters import url_
from .base import ParamsMixin, executions_queryset, filter_execution_by_success


# TODO import models
# from .models import ManagerJob, ManagerJobExecution, ManagerTask, standard_status
# TODO import job_store
# from .myjobs import job_store


def index(req):
    return HttpResponseRedirect(url_('dashboard'))


class DashboardView(ParamsMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()

        limit = self.get_param('limit', int, 20)
        sub_limit = self.get_param('sub_limit', int, 10)

        qs = DjangoJobExecution.objects.select_related('job', 'job__task').all().order_by('-run_time')

        context.update(
            all_list=qs[:limit],
            success_list=filter_execution_by_success(qs, True)[:sub_limit],
            error_list=filter_execution_by_success(qs, False)[:sub_limit],
        )

        return context


class ExecutionsView(ParamsMixin, ListView):
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
        return executions_queryset(self, qs).order_by('-run_time')

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


class ExecutionItemView(DetailView):
    # model = ManagerJobExecution

    def get_template_names(self):
        return 'execution_item.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['execution'] = self.object
        return context
