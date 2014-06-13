from django.conf.urls import patterns, url, include

urlpatterns = patterns('vesamusictraining.exercise.views',
                       url(r'^choose_lecture/$', "choose_lecture"),
                       url(r'^show_lecture/(?P<lecture_name>.*?)$', "show_lecture"),
                       (r'^$', "exercise"),
                       url(r'^list_lectures/$', "list_lectures"),
                       url(r'^(?P<lecture_name>.*?)/lecture/', "lecture"),
                       url(r'^(?P<lecture_name>.*?)/verify/', "verify"),
                       url(r'^(?P<lecture_name>.*?)/complete/', "register_completion")
                       )
