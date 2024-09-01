from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from . import models
from .views import api, web


_ = models


tako_urls = [
    path('', web.index),
    path('dashboard', web.DashboardView.as_view(), name='dashboard'),
    path('executions', web.ExecutionsView.as_view(), name='executions'),
    # path('executions/<int:pk>', ExecutionItemView.as_view(), name='execution_item'),
    path('api/', include([
        path('executions-tsdata', api.ExecutionsTSDataView.as_view(), name='executions-tsdata'),
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
