from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, logout
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns(
    '',
    # Examples:
    url(r'^$', "home.views.home"),
    # url(r'^music_training/', include('music_training.foo.urls')),
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('registration.urls')),
    url(r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
      {'document_root': settings.MEDIA_ROOT, 'show_indexes': False}),

    url(r'^exercise/', include('exercise.urls'))
)
