from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.forms import UserCreationForm
from django.template import RequestContext
from django.contrib.auth import logout

import sys

registration_open = True

def register(request):
    if registration_open == True:
        form = UserCreationForm(request.POST)

        if request.method == 'POST':
            data = request.POST.copy()
            errors = form.get_validation_errors(data)

            sys.stderr.write("Got post\n")
            if not errors:
                sys.stderr.write("Valid user registration\n")
                new_user = form.save(data)
                return HttpResponseRedirect("/")
            else:
                sys.stderr.write("Invalid user registration\n")
        else:
            data, errors = {}, {}
            sys.stderr.write("No post\n")

        sys.stderr.write("Displaying something\n")
        return render_to_response(
            "html_user_management/register.html", 
            {'form': forms.formWrapper(form, data, errors)}, 
            context_instance=RequestContext(request))
    else:
        return render_to_response("html_user_management/register_disabled.html", 
                                  context_instance = RequestContext(request))

def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")
