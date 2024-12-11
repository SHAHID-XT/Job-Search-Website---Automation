from pathlib import Path
import os
import getpass

DEBUG = False
username = getpass.getuser()
WEBSITE_DOMAIN = "http://127.0.0.1"
DEBUG = True
DOMAIN = "127.0.0.1"
CSRF_COOKIE_SECURE = False
CSRF_TRUSTED_ORIGINS = ["http://*", "https://*"]

# WEBSITE_DOMAIN = "https://talenttrackers.online"
# DOMAIN = "talenttrackers.online"
# CSRF_COOKIE_PATH = "/"
# CSRF_COOKIE_DOMAIN = DOMAIN
# CSRF_COOKIE_SECURE = True
# CSRF_COOKIE_AGE = 3600
# CSRF_COOKIE_NAME = "csrf_cookie"
# CSRF_COOKIE_SAMESITE = "Strict"
# CSRF_TRUSTED_ORIGINS = ["http://talenttrackers.online", "https://talenttrackers.online"]

# if username == "FASTFRIEND" or username == "moham" or username == "shahid":
#     WEBSITE_DOMAIN = "http://127.0.0.1"
#     DEBUG = True
#     DOMAIN = "127.0.0.1"
#     CSRF_COOKIE_SECURE = False
#     CSRF_TRUSTED_ORIGINS = ["http://*", "https://*"]


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-x2u4p_y(z5so9z$p!yenh71eii19z9js50k(6(26+0_*yw__p+"

# SECURITY WARNING: don't run with debug turned on in production!


ALLOWED_HOSTS = ["*"]


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "django_user_agents",  # pip
    "base",
    "job",
    # "automatic",
    "analytics",
]

CUSTOM_TEMPLATES_APPS = ["base", "job"]

MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Whitenoise for serving static files in production
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "JOBFINDER.requests_limit_middlewares.CheckerMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "JOBFINDER.requests_limit_middlewares.FakeMiddleware",
    "JOBFINDER.middlewares.NotFoundMiddleware",
    "JOBFINDER.requests_limit_middlewares.RequestThrottleMiddleware",
    "JOBFINDER.analyticsmiddleware.AnalyticsMiddleware",
    "django_user_agents.middleware.UserAgentMiddleware",  # pip
    # custom context processors
]

if not DEBUG:
    WHITENOISE_USE_FINDERS = True

ROOT_URLCONF = "JOBFINDER.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "JOBFINDER.context_preprocessors.global_variables",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "JOBFINDER.wsgi.application"


TIMEOUT = 60000

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#         "OPTIONS": {
#             "timeout": 60,  # Timeout value in seconds (e.g., 40 seconds)
#         },
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "OPTIONS": {
            "timeout": 6000,  # Timeout value in seconds (e.g., 40 seconds)
        },
    }
}

GBTIDATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'jobs',
        'USER': 'django',
        'PASSWORD': '#Boka93',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET collation_connection = 'utf8mb4_unicode_ci'"
        },
    },
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"
USE_I18N = True

USE_TZ = True


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/public/"

# Additional locations of static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "public"),
]


# URL to use when referring to static files located in MEDIA_ROOT
MEDIA_URL = "/media/"


# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Static root directory for collecting static files
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Add your custom static directories to STATICFILES_DIRS
CUSTOM_TEMPS = [os.path.join(BASE_DIR, str(f), "public") for f in CUSTOM_TEMPLATES_APPS]
STATICFILES_DIRS.extend(CUSTOM_TEMPS)

# cache settings
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": os.path.join(BASE_DIR, "website_cache"),
    }
}
