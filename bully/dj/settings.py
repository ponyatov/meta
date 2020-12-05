import config

SECRET_KEY   = config.SECRET_KEY
DEBUG        = True
ROOT_URLCONF = "dj.urls"

from pathlib import Path
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

STATIC_URL        = '/static/'
STATICFILES_DIRS  = [BASE_DIR/'static']

TEMPLATES = [
    {
        'BACKEND'  : 'django.template.backends.django.DjangoTemplates',
        'DIRS'     : [BASE_DIR/'templates'], # req for /template resolve
        'APP_DIRS' : True, # req for admin/login.html template
        'OPTIONS'  : {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ]
        }
    }
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': BASE_DIR/'bully.sqlite3',
    }
}

LANGUAGE_CODE = 'ru-ru'
DATE_FORMAT = '%d/%m/%Y'
DATETIME_FORMAT = '%m/%d/%Y %H:%M:%S'
