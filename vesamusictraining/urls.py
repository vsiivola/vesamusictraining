from django.conf.urls import i18n, include, url
from django.contrib import admin
from django.urls import path
from django.views import static

# For internationalization
from django.views.i18n import JavaScriptCatalog

from . import home, user, settings

urlpatterns = [
    url('admin/', admin.site.urls),
    path('', home.views.home, name="home_views_home"),
    url(r'^static/(?P<path>.*?)$', static.serve,
        {'document_root': settings.STATIC_DIR, 'show_indexes': True}, name="static_page"),
    url(r'^accounts/', include('registration.backends.simple.urls'), name="accounts"),
    url(r'^exercise/', include('vesamusictraining.exercise.urls')),
    url(r'^news/', include('vesamusictraining.news.urls')),
    #url(r'^users/', user.views.home, name="vesamusictraining.user.views.home"),
    path('i18n/', include('django.conf.urls.i18n')), #path('i18n/', i18n, name="django_i18n"),
    path(r'jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog')
]
