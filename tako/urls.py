"""tako URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from . import models
from .views import web


_ = models


tako_urls = [
    path('', web.index),
    path('dashboard', web.DashboardView.as_view(), name='dashboard'),
    # path('executions', ExecutionsView.as_view(), name='executions'),
    # path('executions/<int:pk>', ExecutionItemView.as_view(), name='execution_item'),
    # path('executions-tsdata', ExecutionsTSDataView.as_view(), name='executions-tsdata'),

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
