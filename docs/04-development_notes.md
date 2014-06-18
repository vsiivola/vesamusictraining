#Notes

##Locale
To add new strings to be translated to locale files, run

```
django-admin.py makemessages -l fi
django-admin.py makemessages -d djangojs -l fi
```
for Django template files and javascript files, respectively.

## Running a local mail server for testing

You probably do not need to do this, unless you work on
improving the registration part of the app. You can run
a simple local mail server to pass on the mails generated
but the registration app with
```python -m smtpd -n -c DebuggingServer localhost:1025```
