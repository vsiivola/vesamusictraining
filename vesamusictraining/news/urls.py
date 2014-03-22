from django.conf.urls import patterns, url, include

urlpatterns = patterns('vesamusictraining.news.views',
                       url(r'^list_news/$', "list_news"),
                       )
