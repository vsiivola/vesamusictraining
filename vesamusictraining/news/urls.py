from django.conf.urls import url, include
from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.show_news, name="show_news"),
    url(r'^list_news/(?P<lang>.*)$', views.list_news, name="list_news"),
]
