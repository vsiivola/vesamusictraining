from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

def home(request):
  if request.user.is_authenticated():
    return HttpResponseRedirect("exercise")
  return render_to_response("index.html",
                            context_instance=RequestContext(request))
