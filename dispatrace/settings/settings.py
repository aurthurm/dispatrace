
import os
from django.db import models
import django_heroku 

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'cd^p)6p15nokou5h+@w_=5n@=+@dq@_l*ke5*hxe_(u)^go=v4'
DEBUG = True
ALLOWED_HOSTS = ['dispatrace.herokuapp.com', 'localhost']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'simple_history', # not in use::: just in case
    'reversion',
    'ckeditor',
    'ckeditor_uploader',
    'attachments',
    'guardian',
    'ajax_select',
    'session_security',
    'django_bootstrap_breadcrumbs',
    'view_breadcrumbs',

    'profiles.apps.ProfilesConfig',
    'memoir.apps.MemoirConfig',
    'notice.apps.NoticeConfig',
    'fuel.apps.FuelConfig',

    'notify',
    # 'django_archive',
    'dbbackup', # https://django-dbbackup.readthedocs.io/en/stable/installation.html
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'session_security.middleware.SessionSecurityMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'reversion.middleware.RevisionMiddleware',
]

ROOT_URLCONF = 'dispatrace.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR + '/templates/',
        ],
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

WSGI_APPLICATION = 'dispatrace.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dispatrace',
        'USER': 'aurthur',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
    }
}

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
    # {
    #     'NAME': 'dispatrace.validators.DispatracePasswordValidator',
    # },
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Harare'
USE_I18N = True
USE_L10N = True
USE_TZ = True


STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'dispatrace/static'),
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

SITE_ID = 1
CKEDITOR_UPLOAD_PATH = "uploads/"

LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/'

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': [["Format", "Font", "FontSize", "Bold", "Italic", "Underline", "SpellChecker"],
                ['NumberedList', 'BulletedList', "Indent", "Outdent", 'JustifyLeft', 'JustifyCenter',
                 'JustifyRight'],
                ["Link", "Unlink"], ['Undo', 'Redo'],
                ["Maximize"]],
        'width': 'auto',
    },
    'awesome_ckeditor': {
        'toolbar': [["Format", "Font", "FontSize", "Bold", "Italic", "Underline", "SpellChecker"],
                ['NumberedList', 'BulletedList', "Indent", "Outdent", 'JustifyLeft', 'JustifyCenter',
                 'JustifyRight'],
                ["Link", "Unlink"], ['Undo', 'Redo'],
                ["Maximize"]],
        'width': 'auto',
    },
}

# Django guardian requires
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # default
    'guardian.backends.ObjectPermissionBackend',
)

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# SESSION_COOKIE_AGE = 18000
SESSION_EXPIRE_AT_BROWSER_CLOSE=True
SESSION_SECURITY_EXPIRE_AFTER=15*60
SESSION_SECURITY_WARN_AFTER=13*60

django_heroku.settings(locals())