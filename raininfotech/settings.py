import os
from dotenv import find_dotenv, load_dotenv
from pathlib import Path


dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(find_dotenv(), override=True)
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_PATH = Path(__file__).resolve().parent

MEDIA_URL = "/media/"
MEDIA_ROOT = PROJECT_PATH / "media"

STATIC_URL = "/static/"
STATIC_ROOT = PROJECT_PATH / "staticfiles"

ENV = os.environ

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ENV.get("SECRET_KEY")

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost").split(",")

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "users",
    "properties",
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

ROOT_URLCONF = "raininfotech.urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": ENV.get("NAME"),
        "USER": ENV.get("USER"),
        "PASSWORD": ENV.get("PASSWORD"),
        "HOST": ENV.get("HOST"),
        "PORT": ENV.get("PORT"),
    }
}

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

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "users.middleware.jwt_auth.JWTAuthentication",  # 👈 Your custom auth class
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": BASE_DIR / "django_cache",  # ✅ absolute path
    }
}


REDIS_BLACKLIST_EXPIRY_SECONDS = int(
    ENV.get("REDIS_BLACKLIST_EXPIRY_SECONDS", 60 * 60 * 24 * 7)
)  # 7 days
