#Running the django web app

The web app is based on django platform. You need to do some
preparations to get it running on you local computer

##Set up virtual python environment

This is not absolutely necessary, but is a good way to isolate the app
dependencies from the rest of the system.

For python > 3.3 you can use pyvenv-3.x (except for ubuntu 14.04, it
is broken). I am using ```virtualenv --python=python3.4 venv```.

You can activate the environment with ```source venv/bin/activate```

##Install python dependencies

The app needs the following python modules: django, pyyaml, south,
dj-database-url, dj-static, django-registration, django-toolbelt,
gunicorn, psycopg2, pystache, static. You can install them for example
with pip
```
pip3 install django pyyaml south dj-database-url dj-static django-registration django-toolbelt gunicorn psycopg2 pystache static
```

##Initialize the database

Follow the instructions in file 01-create_exercises.gmd to generate
the database initialization files (fixtures). You can install the
fixtures with
```python3 manage.py syncdb```

By default, this will create a local sqlite database in a file.

###South

South is a db migration tool. See
http://www.mikeball.us/blog/using-south-on-heroku/

Still haven't gotten this to work nicely with heroku. Some random notes:

```
python3 manage.py convert_to_south exercise
python3 manage.py schemamigration exercise --auto
python3 manage.py migrate exercise
```

## Compile the localization files

In directory vesamusictraining/, to compile the message files, run
```django-admin.py compilemessages```

## Run a local web server
You can run the local web app by starting a web server. Running
gunicorn directly
```gunicorn vesamusictraining.wsgi```
starts the service at [http://localhost:8000/](http://localhost:8000/)

Running ```foreman start```
starts the service at [http://localhost:5000/](http://localhost:5000/)


