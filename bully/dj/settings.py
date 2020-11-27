import config

SECRET_KEY    = config.SECRET_KEY
DEBUG         = True
ROOT_URLCONF  = "dj.urls"

from pathlib import Path
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/'templates'], # req for /template resolve
        'APP_DIRS': True, # req for admin/login.html template
        
    }
]
