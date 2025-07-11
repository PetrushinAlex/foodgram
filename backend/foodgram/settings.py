import os
from pathlib import Path

from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

from api import constants


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", get_random_secret_key())

DEBUG = os.getenv("DEBUG", default=False) == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", default="127.0.0.1, localhost, *, foodgrammick.hopto.org").split(", ")

AUTH_USER_MODEL = "users.ExtendedUser"

INSTALLED_APPS = [
    "api.apps.ApiConfig",
    "users.apps.UsersConfig",
    "food.apps.FoodConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "djoser",
    "django_filters",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "foodgram.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "foodgram.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "postgres"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
        "HOST": os.getenv("DB_HOST", "db"),
        "PORT": int(os.getenv("DB_PORT", 5432)),
    },
}


REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_PAGINATION_CLASS":
        "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": constants.DEFAULT_PAGE_SIZE,
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


DJOSER = {
    "LOGIN_FIELD": "email",
    "SERIALIZERS": {
        "user_create": "djoser.serializers.UserCreateSerializer",
        "user": "api.serializers.UserSerializer",
        "current_user": "api.serializers.UserSerializer",
    },
    "PERMISSIONS": {
        "user": ["rest_framework.permissions.IsAuthenticated"],
        "user_list": ["rest_framework.permissions.AllowAny"],
    }
}


LANGUAGE_CODE = "ru"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"
MEDIA_URL = "/media/"
MEDIA_ROOT = "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED", default="https://*, http://*").split(", ")
