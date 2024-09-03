from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from . import models
from .views import api, web


_ = models


tako_urls = [
    path('', web.index),
    path('dashboard', web.DashboardView.as_view(), name='dashboard'),
    # list
    path('executions', web.ExecutionsView.as_view(), name='executions'),
    path('jobs', web.JobsView.as_view(), name='jobs'),
    path('tasks', web.TasksView.as_view(), name='tasks'),
    # detail
    path('executions/<int:slug>', web.ExecutionsDetailView.as_view(), name='executions_detail'),
    path('jobs/<str:slug>', web.JobsDetailView.as_view(), name='jobs_detail'),
    path('tasks/<int:slug>', web.TasksDetailView.as_view(), name='tasks_detail'),
    path('scripts/<int:slug>', web.ScriptsDetailView.as_view(), name='scripts_detail'),
    # edit
    path('tasks/<int:id>/edit', web.tasks_edit_view, name='tasks_edit'),
    path('tasks/create', web.tasks_create_view, name='tasks_create'),

    path('api/', include([
        path('executions-tsdata', api.ExecutionsTSDataView.as_view(), name='api_executions_tsdata'),
    ]))

    # # task
    # path('api/task/execute', TaskExecuteView.as_view()),

    # # job
    # path('api/job/cancel', JobCancelView.as_view()),
]

tako_urlpath = path(settings.TAKO_URL_PREFIX, include(tako_urls))

urlpatterns = [
    path('admin/', admin.site.urls),
    tako_urlpath,
]
