"""
Django settings for bittan project.

Generated by 'django-admin startproject' using Django 5.0.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from enum import Enum

import json
from urllib.parse import urlparse

# Loading environment variables 
load_dotenv()


class ENV_VAR_NAMES(Enum):
    # A URI from where the frontend is served. Should not end with a '/' 
    # Used for CORS-setup
    # E.g https://bittan.com
    BITTAN_FRONTEND_URL="BITTAN_FRONTEND_URL"

    # Example: https://api.bittan.com, used for swish callback
    BITTAN_BACKEND_URL="BITTAN_BACKEND_URL" 

    SWISH_API_URL="SWISH_API_URL"

    SWISH_PEM_FILE_PATH="SWISH_PEM_FILE_PATH"
    SWISH_KEY_FILE_PATH="SWISH_KEY_FILE_PATH"

    # The phone number to which the money should go to 
    SWISH_PAYEE_ALIAS="SWISH_PAYEE_ALIAS"
    SWISH_QR_GENERATOR_ENDPOINT="SWISH_QR_ENDPOINT" 

    DEBUG="DEBUG"

class EnvVars:
    __DEFAULTS = {
            ENV_VAR_NAMES.SWISH_API_URL.value: "https://mss.cpc.getswish.net/swish-cpcapi",
            ENV_VAR_NAMES.SWISH_PEM_FILE_PATH.value:  "./test_certificates/testcert.pem",
            ENV_VAR_NAMES.SWISH_KEY_FILE_PATH.value:  "./test_certificates/testcert.key",
            ENV_VAR_NAMES.SWISH_PAYEE_ALIAS.value:  "1234679304",
            ENV_VAR_NAMES.SWISH_QR_GENERATOR_ENDPOINT.value: "https://mpc.getswish.net/qrg-swish/api/v1/commerce",
            ENV_VAR_NAMES.BITTAN_FRONTEND_URL.value: "http://localhost:3000",
            ENV_VAR_NAMES.BITTAN_BACKEND_URL.value: "http://localhost:8000"
    }

    @staticmethod
    def get(var: ENV_VAR_NAMES):
        var_name = var.value
        if var_name in os.environ:
            return os.environ[var_name]

        if var_name in EnvVars.__DEFAULTS:
            return EnvVars.__DEFAULTS[var_name]

        raise Exception("The environment variable "+var_name+" was not set and has no default.")


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

DEBUG = EnvVars.get(ENV_VAR_NAMES.DEBUG)=="True"

ALLOWED_HOSTS = json.loads(os.getenv("ALLOWED_HOSTS"))


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
	'bittan',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bittan.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'bittan.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("DATABASE_NAME"),

        'USER': os.getenv("DATABASE_USER"),  
        'PASSWORD': os.getenv("DATABASE_PASSWORD"),  
        'HOST': os.getenv("DATABASE_HOST"),  
        'PORT': os.getenv("DATABASE_PORT"),  
        # 'OPTIONS': {  
        #    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"  
        # }  
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Stockholm'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "fileInfo": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "log-info.log",
            "formatter": "level_time",
        },
        "fileWarning": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": "log-warning.log",
            "formatter": "level_time",
        },
    },
    "formatters": {
        "level_time": {
            "format": "{levelname} {asctime} {message}",
            "style": "{",
        },
    },
    "loggers": {
        "": {
            "handlers": ["fileInfo", "fileWarning"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

_parsed_frontend_url = urlparse(EnvVars.get(ENV_VAR_NAMES.BITTAN_FRONTEND_URL))
_parsed_backend_url = urlparse(EnvVars.get(ENV_VAR_NAMES.BITTAN_BACKEND_URL))
CORS_ALLOWED_ORIGINS = [
   _parsed_frontend_url.scheme + "://" + _parsed_frontend_url.netloc,
   _parsed_backend_url.scheme + "://" + _parsed_backend_url.netloc,
]

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS.copy()

CORS_ALLOW_HEADERS = [
    'Bypass-tunnel-reminder',
    'content-type',
    'cookie'

]

