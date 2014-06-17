"""Nothing interesting here, redirect to main page."""
from django.http import HttpResponseRedirect

def home(request):
    """Redirect to main page"""
    if request.user.is_authenticated():
        return HttpResponseRedirect("/")

