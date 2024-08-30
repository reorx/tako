"""
Django settings for tako project.

Generated by 'django-admin startproject' using Django 5.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path

from .utils.settings_env import EnvBase


## Env ##

class Env(EnvBase):
    DEBUG = (bool, True)
    APP_ENV = (str, 'local')
    SCRIPTS_DIR = (str, 'local_scripts')
    WORKERS_NUM = (int, 2)

    # Connections
    ## Database
    DB_URL = (str, '')  # not directly used, get db config by Env._env.db('DB_URL')
    ## Redis
    REDIS_URL = (str, 'redis://127.0.0.1:6379/1')

    # Logging
    LOG_LEVEL_APP = (str, 'INFO')
    LOG_LEVEL_DB = (str, 'INFO')
    LOG_FORMATTER_JSON = (bool, False)

    class Meta:
        env_file = os.environ.get('ENV_FILE', 'backend.env')


## Django basic ##

APP_DIR = Path(__file__).resolve().parent
BASE_DIR = APP_DIR.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%rop%my9(&2%9848_p(f)v)5rvv-+rt2!c!8zjzks8fxpurkhr'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = Env.DEBUG

ALLOWED_HOSTS = ['*']

# https://docs.djangoproject.com/en/4.2/ref/settings/#secure-proxy-ssl-header
# required when serving behind a nginx, and the nginx must have `proxy_set_header X-Forwarded-Proto $scheme;` set
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-trusted-origins
# only necessary if CSRF actually happens, e.g. request foo.example.com on example.com
if not DEBUG:
    CSRF_TRUSTED_ORIGINS = ['https://neocm.sechnic.net']

ADMIN_TITLE = 'neocm Admin'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tako',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tako.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['./tako/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tako.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


## Logging ##

# LOG_FORMAT = '[%(name)s] %(levelname)s %(message)s t=%(asctime)s p=%(pathname)s:%(lineno)d'
LOG_FORMAT = '%(asctime)s  %(levelname)s  %(name)-10s  %(message)s'

# LOG_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'
LOG_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

LOG_LEVEL_APP = Env.LOG_LEVEL_APP
LOG_LEVEL_DB = Env.LOG_LEVEL_DB
log_formatter = 'common'
if Env.LOG_FORMATTER_JSON or not DEBUG:
    log_formatter = 'json'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'app': {
            'handlers': ['stream'],
            'level': LOG_LEVEL_APP,
        },

        # Disable unnecessary 4xx log
        'django.request': {
            'level': 'ERROR',
            'handlers': ['stream'],
            'propagate': 0,
        },

        'django.db.backends': {
            'level': LOG_LEVEL_DB,
            'handlers': ['stream'],
            'propagate': 0,
        },
        # change level here if we want to see schema SQL like CREATE TABLE, ALTER TABLE, etc.
        'django.db.backends.schema': {
            'level': 'INFO',
            'handlers': ['stream'],
            'propagate': 0,
        },
    },
    'handlers': {
        'stream': {
            'class': 'logging.StreamHandler',
            'formatter': log_formatter,
        },
        'sql': {
            'class': 'logging.StreamHandler',
            'formatter': 'common',
            'level': 'DEBUG',
        },
    },
    'formatters': {
        'common': {
            'format': LOG_FORMAT,
            'datefmt': LOG_DATE_FORMAT,
        },
        # 'json': {
        #     '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
        #     'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
        #     'datefmt': LOG_DATE_FORMAT,
        #     'json_ensure_ascii': False,
        # },
    },
}


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
