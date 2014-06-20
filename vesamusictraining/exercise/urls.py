"""Url definitions for exercise"""
from django.conf.urls import patterns, url, include

urlpatterns = patterns(
    'vesamusictraining.exercise.views',
    (r'^$', "choose_lecture"),
    url(r'^choose_lecture/$', "choose_lecture"),
    url(r'^show_lecture/(?P<lecture_name>.*?)/$', "show_lecture"),
    url(r'^show_results/(?P<lecture_name>.*?)/$', "show_results"),
    url(r'^get_question/(?P<lecture_name>.*?)/', "get_question"),
    url(r'^verify/(?P<lecture_name>.*?)/', "verify"),
    url(r'^complete_lecture/(?P<lecture_name>.*?)/', "complete_lecture")
)
