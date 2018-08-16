"""Url definitions for exercise"""
from django.conf.urls import url, include
from django.urls import path
from . import views

urlpatterns = [
    path('', views.choose_lecture, name="excercise_choose_lecture"),
    path('choose_lecture/', views.choose_lecture, name="excercise_choose_lecture2"),
    url(r'^show_lecture/(?P<lecture_name>.*?)/$', views.show_lecture, name="excercise_show_lecture"),
    url(r'^show_results/(?P<lecture_name>.*?)/$', views.show_results, name="excercise_show_results"),
    url(r'^get_question/(?P<lecture_name>.*?)/', views.get_question, name="excercise_get_question"),
    url(r'^verify/(?P<lecture_name>.*?)/', views.verify, name="exercise_verify"),
    url(r'^complete_lecture/(?P<lecture_name>.*?)/', views.complete_lecture, name="excercise_complete_lecture")
]
