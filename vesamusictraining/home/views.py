from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect

def home(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("exercise")
    return render(request, "index.html")
