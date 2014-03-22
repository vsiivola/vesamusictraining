from django.shortcuts import render
import json
from django.http import HttpResponse

from vesamusictraining.news.models import NewsItem

def list_news(request, lang):
    all_news = []
    for l in NewsItem.objects.filter(language=lang):
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

# These are just for the page redirect
from django.shortcuts import render_to_response
from django.template import RequestContext

def home(request):
  return render_to_response("news.html",
                            context_instance=RequestContext(request))
