from django.shortcuts import render
import json
from django.http import HttpResponse

from vesamusictraining.news.models import NewsItem

def list_news(request):
    all_news = []
    for l in NewsItem.objects.all():
        res = {
            "title": l.title,
            "year": "%d" % l.date.year,
            "month": "%d" % l.date.month,
            "day": "%d" % l.date.day,
            "content": l.content,
            "language": l.language
            }
        all_news.append(res)

    return HttpResponse(content = json.dumps(all_news))
