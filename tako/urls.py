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
from django.contrib import admin
from django.urls import path

from . import models
from .views import (
    index
)


_ = models


title = 'Reports Tasks Manager'
admin.site.site_header = title
admin.site.site_title = title
admin.site.index_title = title
admin.site.site_url = '/dashboard'


urlpatterns = [
    path('', index),
    path('admin/', admin.site.urls),
    # path('login', LoginView.as_view()),
    # path('logout', LogoutView.as_view()),
    # path('dashboard', DashboardView.as_view(), name='dashboard'),
    # path('executions', ExecutionsView.as_view(), name='executions'),
    # path('executions/<int:pk>', ExecutionItemView.as_view(), name='execution_item'),
    # path('executions-tsdata', ExecutionsTSDataView.as_view(), name='executions-tsdata'),

    # # task
    # path('api/task/execute', TaskExecuteView.as_view()),

    # # job
    # path('api/job/cancel', JobCancelView.as_view()),
]
