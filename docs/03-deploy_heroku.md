#Deploying the web app on a heroku dyno

Heroku is a web app platform. This file contains some notes on hwo to
deploy the app on heroku.

##Set up for Heroku

Create a branch that will contain the app to be deployed.
```git checkout -b heroku-media```

Create a requirements file
```pip3 freeze > requirements```

Generate the content as explained in th file
01-create_exerises.gmd. Use `git add` to add the media files to the
repo. Also add the compiled localization resources. `git commit` the
files.

Fix the settings file. Change SECRET_KEY to something secret, debug to
False. Fix the following settings as well
```python
import dj_database_url
DATABASES['default'] =  dj_database_url.config()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
ALLOWED_HOSTS = ['*']

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'vesamusictraining', 'locale'),
    os.path.join(BASE_DIR, 'locale'),
    'locale',
)
```

Configure the heroku project as a git remote called heroku. Now you
can push the git branch with all the media files in it.
```git push heroku heroku-media:master```

Initialize the db
```heroku run python manage.py syncdb```

Start the dyno
```heroku ps:scale web=1```

##Miscellaneus notes

###Recreate the db (loses all info, also users)
```
heroku config | grep POSTGRESQL
heroku pg:reset HEROKU_POSTGRESQL_IVORY # Change the name to your db ID
heroku run python manage.py syncdb
```

###Manual sql connection
```
heroku pg:psql
```
Show table `\dt`, `\d+ exercise_lecture;`, `ALTER TABLE exercise_lecture ADD level real;`


