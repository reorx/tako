from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from ninja import NinjaAPI

from . import models
from .views import api, web


_ = models


tako_api_ninja = NinjaAPI()
tako_api_ninja.add_router('api', api.router)


urlpatterns = [
    path('admin/', admin.site.urls),
    path(settings.TAKO_URL_PREFIX, include(web.tako_web_urls)),
    path(settings.TAKO_URL_PREFIX, tako_api_ninja.urls),
]
