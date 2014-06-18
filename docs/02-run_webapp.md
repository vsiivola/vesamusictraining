#Running the django web app

The web app is based on django platform. You need to do some preparations to get it running on you local computer

##Set up virtual python environment

This is not absolutely necessary, but is a good way to isolate the
app dependencies from the rest of the system.

For python > 3.3 you can use pyvenv-3.x (except for ubuntu 14.04, it is broken). I am using
```virtualenv --python=python3.4 venv```

You can activate the environment with
```source venv/bin/activate```

##Install python dependencies

The app needs the following python modules: django, pyyaml, south, dj-database-url, dj-static, django-registration, django-toolbelt, gunicorn, psycopg2, pystache, static. You can install them for example with pip
```pip3 install django pyyaml south dj-database-url dj-static django-registration django-toolbelt gunicorn psycopg2 pystache static```

##Initialize the database

Follow the instructions in file 01-create_exercises.gmd to generate the database initialization files (fixtures). You can install the fixtures with
```python3 manage.py syncdb```

By default, this will create a local sqlite database in a file.

###South

South is a db migration tool. Some random notes follow, proper instructions need to be written.

Initialize with
```python manage.py schemamigration exercise --initial```
and apply changes with
```python manage.py schemamigration exercise --auto```

## Compile the localization files

In `vesamusictraining/`, to generate message files for templates, run
```django-admin.py makemessages -l fi```
To generate message files for javascript, run
```django-admin.py makemessages -d djangojs -l fi```
To compile the message files, run
```django-admin.py compilemessages```

## Run a local web server
You can run the local web app by starting a web server. Running gunicorn directly
```gunicorn vesamusictraining.wsgi```
starts the service at http://localhost:8000

Running
    foreman start
starts the service at http://localhost:5000

## Miscellaneus notes

### Running a local mail server for testing

You probably do not need to do this, unless you work on
improving the registration part of the app. You can run
a simple local mail server to pass on the mails generated
but the registration app with
```python -m smtpd -n -c DebuggingServer localhost:1025```
