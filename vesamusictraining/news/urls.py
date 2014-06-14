from django.conf.urls import patterns, url, include

urlpatterns = patterns('vesamusictraining.news.views',
                       url(r'^$', "show_news"),
                       url(r'^list_news/(?P<lang>.*)$', "list_news"),
                       )
