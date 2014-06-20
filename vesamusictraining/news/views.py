"""News view"""
from django.http import HttpResponse
from django.shortcuts import render
import json

from vesamusictraining.news.models import NewsItem

def show_news(request):
    """Render the news page"""
    news = NewsItem.objects.filter(
        language=request.LANGUAGE_CODE).order_by('-date')
    return render(
        request, "news.html",
        {"news": news})

def list_news(request, lang):
    """List news in JSON"""
    all_news = []
    for l in NewsItem.objects.filter(language=lang).order_by('-date'):
        res = {
            "title": l.title,
            "year": "%d" % l.date.year,
            "month": "%d" % l.date.month,
            "day": "%d" % l.date.day,
            "content": l.content,
            "language": l.language
            }
        all_news.append(res)

    return HttpResponse(content=json.dumps(all_news))

