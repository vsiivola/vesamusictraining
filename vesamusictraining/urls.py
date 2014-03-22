from django.conf.urls import patterns, include, url

# For user handling
#from django.contrib.auth.views import login, logout

from django.contrib import admin
admin.autodiscover()

# porting to py3, why is this needed
import sys, os
sys.path.append(os.path.dirname(__file__))

import settings

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'vesamusictraining.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', "vesamusictraining.home.views.home"),
    url(r'^static/(?P<path>.*?)$', 'django.views.static.serve', {'document_root': settings.STATIC_DIR, 'show_indexes': True}),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^exercise/', include('vesamusictraining.exercise.urls')),
    url(r'^users/', "vesamusictraining.user.views.home"),
)
